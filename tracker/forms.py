from django import forms
from .models import DailyLog, UserProfile, WeightLog
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    DURATION_CHOICES = [
        (30, '1 Month'),
        (90, '3 Months'),
        (180, '6 Months'),
    ]
    duration_days = forms.ChoiceField(
        choices=DURATION_CHOICES, 
        label="Time Duration to Reach Target Weight",
        required=True,
        initial=30
    )

    class Meta:
        model = UserProfile
        fields = ['age', 'current_weight', 'target_weight', 'height', 'gender', 'activity_level', 'goal']

class FoodEntryForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = ['food', 'quantity_in_grams']
        widgets = {
            'quantity_in_grams': forms.NumberInput(attrs={'placeholder': 'Enter quantity in grams'})
        }

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class WeightLogForm(forms.ModelForm):
    class Meta:
        model = WeightLog
        fields = ['weight']
        widgets = {
            'weight': forms.NumberInput(attrs={'placeholder': 'Enter your weight in kg'})
        }
