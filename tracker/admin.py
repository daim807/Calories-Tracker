from django.contrib import admin
from .models import UserProfile, Food, DailyLog

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_weight', 'target_weight', 'activity_level']

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'calories_per_100g']
    search_fields = ['name']

@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'food', 'quantity_in_grams', 'date', 'calories')

    list_filter = ['date']
