from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Trip(models.Model):
    TRAVEL_MODE_CHOICES = [
        ('flight', 'Flight'), ('train', 'Train'), ('bus', 'Bus'),
        ('car', 'Car'), ('bike', 'Bike'), ('cruise', 'Cruise'), ('mixed', 'Mixed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips')
    trip_name = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    travel_mode = models.CharField(max_length=20, choices=TRAVEL_MODE_CHOICES, default='mixed')
    cover_image = models.ImageField(upload_to='trip_covers/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date cannot be before start date.")

    def duration(self):
        return (self.end_date - self.start_date).days + 1

    def total_estimated(self):
        from django.db.models import Sum
        return self.budgets.aggregate(total=Sum('estimated_cost'))['total'] or 0

    def total_actual(self):
        from django.db.models import Sum
        return self.budgets.aggregate(total=Sum('actual_cost'))['total'] or 0

    def remaining_budget(self):
        return self.total_estimated() - self.total_actual()

    def __str__(self):
        return f"{self.trip_name} → {self.destination}"

    class Meta:
        ordering = ['-start_date']


class Budget(models.Model):
    CATEGORY_CHOICES = [
        ('transport', 'Transport'), ('food', 'Food & Dining'),
        ('hotel', 'Hotel / Stay'), ('shopping', 'Shopping'),
        ('tickets', 'Tickets / Entry'), ('misc', 'Miscellaneous'),
    ]
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date = models.DateField(default=timezone.now)

    def difference(self):
        return self.estimated_cost - self.actual_cost

    def __str__(self):
        return f"{self.trip.trip_name} - {self.get_category_display()}"

    class Meta:
        ordering = ['date', 'category']


class Place(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('visited', 'Visited'), ('skipped', 'Skipped')]
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='places')
    place_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    priority = models.IntegerField(default=1, help_text="1=High, 2=Medium, 3=Low")

    def __str__(self):
        return f"{self.place_name} [{self.get_status_display()}]"

    class Meta:
        ordering = ['priority', 'place_name']


class Itinerary(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='itineraries')
    day_number = models.PositiveIntegerField()
    time_slot = models.TimeField()
    activity = models.CharField(max_length=300)
    notes = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Day {self.day_number} | {self.time_slot} - {self.activity}"

    class Meta:
        ordering = ['day_number', 'time_slot']


class VlogNote(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='vlog_notes')
    day_number = models.PositiveIntegerField()
    script_title = models.CharField(max_length=200)
    content_notes = models.TextField()
    hook = models.CharField(max_length=300, blank=True)
    thumbnail_idea = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Day {self.day_number}: {self.script_title}"

    class Meta:
        ordering = ['day_number', 'created_at']


class Photo(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='photos')
    day_number = models.PositiveIntegerField()
    image = models.ImageField(upload_to='trip_photos/%Y/%m/')
    caption = models.CharField(max_length=300, blank=True)
    location_tag = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo - Day {self.day_number} | {self.trip.trip_name}"

    class Meta:
        ordering = ['day_number', 'uploaded_at']
