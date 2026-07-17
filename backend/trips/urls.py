from django.urls import path

from . import views

urlpatterns = [
    path('health/', views.health_check, name='health-check'),
    path('trips/plan/', views.PlanTripView.as_view(), name='plan-trip'),
    path('locations/autocomplete/', views.LocationAutocompleteView.as_view(), name='location-autocomplete'),
]
