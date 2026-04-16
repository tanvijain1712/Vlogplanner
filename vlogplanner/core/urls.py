from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Trips
    path('trips/', views.TripListView.as_view(), name='trip_list'),
    path('trips/new/', views.TripCreateView.as_view(), name='trip_create'),
    path('trips/<int:pk>/', views.TripDetailView.as_view(), name='trip_detail'),
    path('trips/<int:pk>/edit/', views.TripUpdateView.as_view(), name='trip_update'),
    path('trips/<int:pk>/delete/', views.TripDeleteView.as_view(), name='trip_delete'),

    # Budget
    path('trips/<int:trip_pk>/budget/', views.budget_list, name='budget_list'),
    path('trips/<int:trip_pk>/budget/add/', views.budget_create, name='budget_create'),
    path('budget/<int:pk>/edit/', views.budget_update, name='budget_update'),
    path('budget/<int:pk>/delete/', views.budget_delete, name='budget_delete'),

    # Places
    path('trips/<int:trip_pk>/places/', views.place_list, name='place_list'),
    path('trips/<int:trip_pk>/places/add/', views.place_create, name='place_create'),
    path('places/<int:pk>/status/', views.place_update_status, name='place_status'),
    path('places/<int:pk>/delete/', views.place_delete, name='place_delete'),

    # Itinerary
    path('trips/<int:trip_pk>/itinerary/', views.itinerary_list, name='itinerary_list'),
    path('trips/<int:trip_pk>/itinerary/add/', views.itinerary_create, name='itinerary_create'),
    path('itinerary/<int:pk>/delete/', views.itinerary_delete, name='itinerary_delete'),

    # Vlog Notes
    path('trips/<int:trip_pk>/vlogs/', views.vlog_list, name='vlog_list'),
    path('trips/<int:trip_pk>/vlogs/add/', views.vlog_create, name='vlog_create'),
    path('vlogs/<int:pk>/edit/', views.vlog_update, name='vlog_update'),
    path('vlogs/<int:pk>/delete/', views.vlog_delete, name='vlog_delete'),

    # Photos
    path('trips/<int:trip_pk>/photos/', views.photo_gallery, name='photo_gallery'),
    path('trips/<int:trip_pk>/photos/upload/', views.photo_upload, name='photo_upload'),
    path('photos/<int:pk>/delete/', views.photo_delete, name='photo_delete'),
]
