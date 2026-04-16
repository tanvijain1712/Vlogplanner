from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Trip, Budget, Place, Itinerary, VlogNote, Photo


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = ['trip_name', 'destination', 'start_date', 'end_date', 'travel_mode', 'cover_image']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end and end < start:
            raise forms.ValidationError("End date must be after start date.")
        return cleaned_data


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'description', 'estimated_cost', 'actual_cost', 'date']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}


class PlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ['place_name', 'description', 'status', 'priority']


class ItineraryForm(forms.ModelForm):
    class Meta:
        model = Itinerary
        fields = ['day_number', 'time_slot', 'activity', 'notes', 'location']
        widgets = {'time_slot': forms.TimeInput(attrs={'type': 'time'})}


class VlogNoteForm(forms.ModelForm):
    class Meta:
        model = VlogNote
        fields = ['day_number', 'script_title', 'content_notes', 'hook', 'thumbnail_idea']
        widgets = {
            'content_notes': forms.Textarea(attrs={'rows': 6}),
            'hook': forms.Textarea(attrs={'rows': 2}),
        }


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['day_number', 'image', 'caption', 'location_tag']
