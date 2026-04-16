from django.contrib import admin
from .models import Trip, Budget, Place, Itinerary, VlogNote, Photo


class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 1


class PlaceInline(admin.TabularInline):
    model = Place
    extra = 1


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ['trip_name', 'destination', 'user', 'start_date', 'end_date', 'travel_mode']
    list_filter = ['travel_mode', 'start_date']
    search_fields = ['trip_name', 'destination', 'user__username']
    inlines = [BudgetInline, PlaceInline]


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['trip', 'category', 'estimated_cost', 'actual_cost', 'date']
    list_filter = ['category']


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ['place_name', 'trip', 'status', 'priority']
    list_filter = ['status']


@admin.register(Itinerary)
class ItineraryAdmin(admin.ModelAdmin):
    list_display = ['trip', 'day_number', 'time_slot', 'activity']
    list_filter = ['day_number']


@admin.register(VlogNote)
class VlogNoteAdmin(admin.ModelAdmin):
    list_display = ['script_title', 'trip', 'day_number', 'created_at']


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['trip', 'day_number', 'caption', 'uploaded_at']
