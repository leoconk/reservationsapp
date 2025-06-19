from django import forms
from .models import Reservation
from .models import Table

class ReservationForm(forms.Form):
    num_people = forms.IntegerField(min_value=1, label="Number of People")
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    duration_minutes = forms.IntegerField(min_value=15, label="Duration (minutes)")
class DirectReservationForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=100)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    duration_minutes = forms.IntegerField(min_value=15, label="Duration (minutes)")