from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from .models import Trip, Budget, Place, Itinerary, VlogNote, Photo
from .forms import (SignupForm, ProfileForm, TripForm, BudgetForm,
                    PlaceForm, ItineraryForm, VlogNoteForm, PhotoForm)


# ─── AUTH VIEWS ───────────────────────────────────────────────────────────────

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = SignupForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome aboard! Start planning your first trip.")
        return redirect('dashboard')
    return render(request, 'auth/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, "Invalid username or password.")
    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    return render(request, 'auth/profile.html', {'form': form})


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    trips = Trip.objects.filter(user=request.user)
    total_trips = trips.count()
    # Aggregate stats across all trips
    total_estimated = sum(t.total_estimated() for t in trips)
    total_spent = sum(t.total_actual() for t in trips)
    context = {
        'trips': trips[:6],  # latest 6
        'total_trips': total_trips,
        'total_estimated': total_estimated,
        'total_spent': total_spent,
        'remaining': total_estimated - total_spent,
    }
    return render(request, 'dashboard.html', context)


# ─── TRIP VIEWS ───────────────────────────────────────────────────────────────

class TripListView(LoginRequiredMixin, ListView):
    model = Trip
    template_name = 'trips/trip_list.html'
    context_object_name = 'trips'

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)


class TripDetailView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'trips/trip_detail.html'
    context_object_name = 'trip'

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        trip = self.object
        # Budget summary per category
        budget_by_cat = trip.budgets.values('category').annotate(
            est=Sum('estimated_cost'), actual=Sum('actual_cost')
        )
        ctx['budget_by_cat'] = budget_by_cat
        ctx['places_pending'] = trip.places.filter(status='pending').count()
        ctx['places_visited'] = trip.places.filter(status='visited').count()
        # Group itinerary by day
        days = {}
        for item in trip.itineraries.all():
            days.setdefault(item.day_number, []).append(item)
        ctx['itinerary_days'] = dict(sorted(days.items()))
        # Group vlog notes by day
        vlog_days = {}
        for note in trip.vlog_notes.all():
            vlog_days.setdefault(note.day_number, []).append(note)
        ctx['vlog_days'] = dict(sorted(vlog_days.items()))
        return ctx


class TripCreateView(LoginRequiredMixin, CreateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'
    success_url = reverse_lazy('trip_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Trip created! Now add your budget and places.")
        return super().form_valid(form)


class TripUpdateView(LoginRequiredMixin, UpdateView):
    model = Trip
    form_class = TripForm
    template_name = 'trips/trip_form.html'

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('trip_detail', kwargs={'pk': self.object.pk})


class TripDeleteView(LoginRequiredMixin, DeleteView):
    model = Trip
    template_name = 'trips/trip_confirm_delete.html'
    success_url = reverse_lazy('trip_list')

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)


# ─── BUDGET VIEWS ─────────────────────────────────────────────────────────────

@login_required
def budget_list(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    budgets = trip.budgets.all()
    # Category-level summary for chart data
    summary = budgets.values('category').annotate(
        est=Sum('estimated_cost'), actual=Sum('actual_cost')
    )
    context = {
        'trip': trip,
        'budgets': budgets,
        'summary': list(summary),
        'total_estimated': trip.total_estimated(),
        'total_actual': trip.total_actual(),
        'remaining': trip.remaining_budget(),
    }
    return render(request, 'budgets/budget_list.html', context)


@login_required
def budget_create(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    form = BudgetForm(request.POST or None)
    if form.is_valid():
        budget = form.save(commit=False)
        budget.trip = trip
        budget.save()
        messages.success(request, "Budget entry added.")
        return redirect('budget_list', trip_pk=trip.pk)
    return render(request, 'budgets/budget_form.html', {'form': form, 'trip': trip})


@login_required
def budget_update(request, pk):
    budget = get_object_or_404(Budget, pk=pk, trip__user=request.user)
    form = BudgetForm(request.POST or None, instance=budget)
    if form.is_valid():
        form.save()
        messages.success(request, "Budget entry updated.")
        return redirect('budget_list', trip_pk=budget.trip.pk)
    return render(request, 'budgets/budget_form.html', {'form': form, 'trip': budget.trip})


@login_required
def budget_delete(request, pk):
    budget = get_object_or_404(Budget, pk=pk, trip__user=request.user)
    trip_pk = budget.trip.pk
    if request.method == 'POST':
        budget.delete()
        messages.success(request, "Budget entry removed.")
    return redirect('budget_list', trip_pk=trip_pk)


# ─── PLACE VIEWS ──────────────────────────────────────────────────────────────

@login_required
def place_list(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    status_filter = request.GET.get('status', '')
    places = trip.places.all()
    if status_filter:
        places = places.filter(status=status_filter)
    return render(request, 'places/place_list.html', {
        'trip': trip, 'places': places, 'status_filter': status_filter
    })


@login_required
def place_create(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    form = PlaceForm(request.POST or None)
    if form.is_valid():
        place = form.save(commit=False)
        place.trip = trip
        place.save()
        messages.success(request, "Place added.")
        return redirect('place_list', trip_pk=trip.pk)
    return render(request, 'places/place_form.html', {'form': form, 'trip': trip})


@login_required
def place_update_status(request, pk):
    """Quick AJAX status toggle."""
    place = get_object_or_404(Place, pk=pk, trip__user=request.user)
    if request.method == 'POST':
        place.status = request.POST.get('status', place.status)
        place.save()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': place.status})
        messages.success(request, f"{place.place_name} marked as {place.get_status_display()}.")
    return redirect('place_list', trip_pk=place.trip.pk)


@login_required
def place_delete(request, pk):
    place = get_object_or_404(Place, pk=pk, trip__user=request.user)
    trip_pk = place.trip.pk
    if request.method == 'POST':
        place.delete()
        messages.success(request, "Place removed.")
    return redirect('place_list', trip_pk=trip_pk)


# ─── ITINERARY VIEWS ──────────────────────────────────────────────────────────

@login_required
def itinerary_list(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    items = trip.itineraries.all()
    days = {}
    for item in items:
        days.setdefault(item.day_number, []).append(item)
    return render(request, 'itinerary/itinerary_list.html', {
        'trip': trip, 'days': dict(sorted(days.items()))
    })


@login_required
def itinerary_create(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    form = ItineraryForm(request.POST or None)
    if form.is_valid():
        item = form.save(commit=False)
        item.trip = trip
        item.save()
        messages.success(request, "Activity added to itinerary.")
        return redirect('itinerary_list', trip_pk=trip.pk)
    return render(request, 'itinerary/itinerary_form.html', {'form': form, 'trip': trip})


@login_required
def itinerary_delete(request, pk):
    item = get_object_or_404(Itinerary, pk=pk, trip__user=request.user)
    trip_pk = item.trip.pk
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Activity removed.")
    return redirect('itinerary_list', trip_pk=trip_pk)


# ─── VLOG NOTE VIEWS ──────────────────────────────────────────────────────────

@login_required
def vlog_list(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    notes = trip.vlog_notes.all()
    days = {}
    for note in notes:
        days.setdefault(note.day_number, []).append(note)
    return render(request, 'vlogs/vlog_list.html', {
        'trip': trip, 'days': dict(sorted(days.items()))
    })


@login_required
def vlog_create(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    form = VlogNoteForm(request.POST or None)
    if form.is_valid():
        note = form.save(commit=False)
        note.trip = trip
        note.save()
        messages.success(request, "Vlog note saved.")
        return redirect('vlog_list', trip_pk=trip.pk)
    return render(request, 'vlogs/vlog_form.html', {'form': form, 'trip': trip})


@login_required
def vlog_update(request, pk):
    note = get_object_or_404(VlogNote, pk=pk, trip__user=request.user)
    form = VlogNoteForm(request.POST or None, instance=note)
    if form.is_valid():
        form.save()
        messages.success(request, "Vlog note updated.")
        return redirect('vlog_list', trip_pk=note.trip.pk)
    return render(request, 'vlogs/vlog_form.html', {'form': form, 'trip': note.trip})


@login_required
def vlog_delete(request, pk):
    note = get_object_or_404(VlogNote, pk=pk, trip__user=request.user)
    trip_pk = note.trip.pk
    if request.method == 'POST':
        note.delete()
        messages.success(request, "Vlog note deleted.")
    return redirect('vlog_list', trip_pk=trip_pk)


# ─── PHOTO VIEWS ──────────────────────────────────────────────────────────────

@login_required
def photo_gallery(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    photos = trip.photos.all()
    days = {}
    for photo in photos:
        days.setdefault(photo.day_number, []).append(photo)
    return render(request, 'photos/photo_gallery.html', {
        'trip': trip, 'days': dict(sorted(days.items())), 'total': photos.count()
    })


@login_required
def photo_upload(request, trip_pk):
    trip = get_object_or_404(Trip, pk=trip_pk, user=request.user)
    form = PhotoForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        photo = form.save(commit=False)
        photo.trip = trip
        photo.save()
        messages.success(request, "Photo uploaded!")
        return redirect('photo_gallery', trip_pk=trip.pk)
    return render(request, 'photos/photo_form.html', {'form': form, 'trip': trip})


@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk, trip__user=request.user)
    trip_pk = photo.trip.pk
    if request.method == 'POST':
        photo.image.delete(save=False)
        photo.delete()
        messages.success(request, "Photo deleted.")
    return redirect('photo_gallery', trip_pk=trip_pk)
