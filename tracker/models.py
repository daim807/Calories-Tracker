from django.db import models
from django.contrib.auth.models import User
import datetime

class UserProfile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female")
    ]

    ACTIVITY_CHOICES = [
        ("sedentary", "Sedentary (little or no exercise)"),
        ("light", "Lightly active (light exercise 1–3 days/week)"),
        ("moderate", "Moderately active (3–5 days/week)"),
        ("active", "Active (6–7 days/week)"),
        ("very_active", "Very active (intense exercise daily)"),
    ]

    GOAL_CHOICES = [
        ("lose", "Lose Weight"),
        ("maintain", "Maintain Weight"),
        ("gain", "Gain Weight"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    height = models.FloatField(help_text="Height in centimeters")
    current_weight = models.FloatField(help_text="Current weight in kg")
    target_weight = models.FloatField(help_text="Target weight in kg")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES, default="maintain")

    def __str__(self):
        return self.user.username

    def calculate_daily_calorie_goal(self):
        """Calculate daily calorie need using Mifflin-St Jeor Equation,
           adjusted for user's goal (lose/maintain/gain)."""
        if self.gender == "male":
            bmr = 10 * self.current_weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.current_weight + 6.25 * self.height - 5 * self.age - 161

        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }

        multiplier = activity_multipliers.get(self.activity_level, 1.2)
        calorie_need = bmr * multiplier

        # Adjust for goal
        if self.goal == "lose":
            calorie_need -= 500
        elif self.goal == "gain":
            calorie_need += 500

        return round(calorie_need, 2)

class Food(models.Model):
    name = models.CharField(max_length=100)
    calories_per_100g = models.FloatField()

    def __str__(self):
        return self.name

class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity_in_grams = models.FloatField()
    calories = models.FloatField(default=0)
    date = models.DateField(default=datetime.date.today)

    def save(self, *args, **kwargs):
        # Automatically calculate calories based on food and quantity
        self.calories = round((self.quantity_in_grams / 100) * self.food.calories_per_100g, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food.name} - {self.quantity_in_grams}g on {self.date}"
class WeightLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField(help_text="Weight in kg")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.weight} kg on {self.date}"
class DailyLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food = models.CharField(max_length=255)
    quantity_in_grams = models.FloatField()
    calories = models.FloatField(default=0)
    date = models.DateField(default=datetime.date.today)