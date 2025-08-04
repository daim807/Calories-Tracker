from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile, DailyLog, WeightLog
from .forms import FoodEntryForm, UserProfileForm, WeightLogForm
from .openrouter_client import ask_openrouter
import datetime
import re

# --------------------------
# Calorie Estimator View
def home_view(request):
    return render(request, 'tracker/home.html')

@login_required
def calorie_estimator_view(request):
    estimated_calories = None
    food_input = ""

    if request.method == 'POST':
        food_input = request.POST.get('food_input')
        if food_input:
            estimated_calories = ask_openrouter(f"Estimate calories for: {food_input}")

    return render(request, 'tracker/calorie_estimator.html', {
        'estimated_calories': estimated_calories,
        'food_input': food_input,
    })

# --------------------------
# Ask AI View

def ask_ai_view(request):
    answer = None
    if request.method == "POST":
        question = request.POST.get("question")
        if question:
            answer = ask_openrouter(question)
    return render(request, "ask_ai.html", {"answer": answer})

# --------------------------
# Authentication Views

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'tracker/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('edit_profile')
    else:
        form = UserCreationForm()
    return render(request, 'tracker/register.html', {'form': form})

# --------------------------
# Edit Profile View

@login_required
def edit_profile_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        profile = UserProfile(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'tracker/edit_profile.html', {'form': form})

# --------------------------
# Dashboard View

def extract_number(text):
    """Extract the first float-like number from a string using regex."""
    match = re.search(r'\d+(\.\d+)?', text)
    if match:
        return float(match.group())
    raise ValueError(f"No valid number found in: {text}")

@login_required
def dashboard_view(request):
    user = request.user
    today = datetime.date.today()

    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'age': 25,
            'gender': 'male',
            'height': 170,
            'current_weight': 70,
            'target_weight': 65,
            'activity_level': 'moderate',
            'goal': 'maintain',
        }
    )

    # Get duration_days from form or default (assume 30 days if not provided)
    # We store duration_days in session or profile temporarily or handle from POST form, for now defaulting
    duration_days = 30  # Default to 30 days

    if request.method == 'POST' and 'duration_days' in request.POST:
        try:
            duration_days = int(request.POST.get('duration_days', 30))
        except ValueError:
            duration_days = 30

    # Calculate BMR
    if profile.gender == 'male':
        bmr = 10 * profile.current_weight + 6.25 * profile.height - 5 * profile.age + 5
    else:
        bmr = 10 * profile.current_weight + 6.25 * profile.height - 5 * profile.age - 161

    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'very_active': 1.9,
    }
    multiplier = activity_multipliers.get(profile.activity_level, 1.2)
    maintenance = bmr * multiplier

    # Calculate required calorie adjustment based on target weight and duration
    weight_diff = profile.target_weight - profile.current_weight
    # 1 kg fat ≈ 7700 calories
    total_calorie_change = weight_diff * 7700
    daily_calorie_change = total_calorie_change / duration_days if duration_days > 0 else 0

    # Calculate goal calories adjusted for duration
    goal = maintenance + daily_calorie_change

    if profile.goal == 'maintain':
        goal = maintenance  # override goal if maintain

    if request.method == 'POST':
        form = FoodEntryForm(request.POST)
        if form.is_valid():
            food = form.cleaned_data['food']
            quantity = form.cleaned_data['quantity_in_grams']
            prompt = f"How many calories in {quantity} grams of {food}? Only return a number."

            try:
                ai_response = ask_openrouter(prompt)
                calories = extract_number(ai_response)

                food_log = form.save(commit=False)
                food_log.user = user
                food_log.date = today
                food_log.calories = calories
                food_log.save()

                messages.success(
                    request,
                    f"✅ {food} ({quantity}g) contains {calories} calories. Entry added to your calorie tracker."
                )
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Error estimating calories: {e}")
        else:
            messages.error(request, "Invalid food entry.")
    else:
        form = FoodEntryForm()

    logs = DailyLog.objects.filter(user=user, date=today)
    total_consumed = sum(log.calories for log in logs)
    remaining = max(0, goal - total_consumed)

    latest_weight_log = WeightLog.objects.filter(user=user).order_by('-date').first()

    goal_message = ""
    if weight_diff < 0:
        goal_message = f"🔻 To lose weight, consume approx. {round(goal)} kcal/day over {duration_days} days"
    elif weight_diff > 0:
        goal_message = f"🔺 To gain weight, consume approx. {round(goal)} kcal/day over {duration_days} days"
    else:
        goal_message = f"☑ To maintain weight, consume approx. {round(goal)} kcal/day"

    context = {
        'form': form,
        'logs': logs,
        'total': round(total_consumed, 2),
        'remaining': round(remaining, 2),
        'goal': round(goal),
        'goal_message': goal_message,
        'profile': profile,
        'bmr': round(bmr),
        'maintenance': round(maintenance),
        'latest_weight_log': latest_weight_log,
        'today': today,
        'duration_days': duration_days,  # pass this so template can show/use it
    }

    return render(request, 'tracker/dashboard.html', context)

# --------------------------
# Food Log View
@login_required
def foodlog_view(request):
    if request.method == 'POST':
        form = FoodEntryForm(request.POST)
        if form.is_valid():
            food = form.cleaned_data['food']
            quantity = form.cleaned_data['quantity_in_grams']
            prompt = f"How many calories in {quantity} grams of {food}? Only return a number."

            try:
                ai_response = ask_openrouter(prompt)
                calories = float(''.join(filter(lambda x: x.isdigit() or x == '.', ai_response)))

                food_log = form.save(commit=False)
                food_log.user = request.user
                food_log.date = datetime.date.today()
                food_log.calories = calories
                food_log.save()

                messages.success(
                    request,
                    f"✅ {food} ({quantity}g) contains {calories} calories. Entry added to your calorie tracker."
                )
                return redirect('food-log')
            except Exception as e:
                messages.error(request, f"AI error: {e}")
        else:
            messages.error(request, "Invalid food log form.")
    else:
        form = FoodEntryForm()

    logs = DailyLog.objects.filter(user=request.user).order_by('-date')
    return render(request, 'tracker/food_log.html', {'form': form, 'logs': logs})

# --------------------------
# Weight Log View

@login_required
def weight_log_view(request):
    if request.method == 'POST':
        form = WeightLogForm(request.POST)
        if form.is_valid():
            weight_log = form.save(commit=False)
            weight_log.user = request.user
            weight_log.save()
            return redirect('weight-log')
    else:
        form = WeightLogForm()

    weights = WeightLog.objects.filter(user=request.user).order_by('-date')
    return render(request, 'tracker/weight_log.html', {'form': form, 'weights': weights})
