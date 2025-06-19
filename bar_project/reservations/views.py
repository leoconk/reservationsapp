from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Table, Reservation
from .forms import ReservationForm
from datetime import datetime, timedelta
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after register
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

class DirectReservationForm(forms.Form):
    name = forms.CharField(label="Nombre", max_length=100)
    time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    def __init__(self, *args, **kwargs):
        self.selected_date = kwargs.pop('selected_date', None)
        super().__init__(*args, **kwargs)
        if self.selected_date:
            self.fields['time'].label = f"Select a time for {self.selected_date.strftime('%d/%m/%Y')}"

def home(request):
    message = ""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            num_people = form.cleaned_data['num_people']
            start_time = form.cleaned_data['start_time']
            end_time = start_time + timedelta(hours=1)  # Dummy end time

            for table in Table.objects.filter(capacity__gte=num_people):
                conflicts = Reservation.objects.filter(
                    table=table,
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                if not conflicts.exists():
                    Reservation.objects.create(table=table, start_time=start_time, end_time=end_time, name="Anonymous")
                    messages.success(request, "Reservation confirmed successfully!")
                return redirect('home')

            message = "No available tables for that time and group size."
    else:
        form = ReservationForm()

    return render(request, 'reservations/home.html', {
        'form': form,
        'message': message,
        'show_table_list_button': True
    })

def table_list(request):
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    start_of_day = datetime.combine(selected_date, datetime.min.time())
    end_of_day = datetime.combine(selected_date, datetime.max.time())

    tables = Table.objects.all()
    table_data = []
    for table in tables:
        reservations = Reservation.objects.filter(
            table=table,
            start_time__gte=start_of_day,
            start_time__lte=end_of_day
        ).order_by('start_time')

        slots = [
            {
                "time": f"{res.start_time.strftime('%H:%M')}–{res.end_time.strftime('%H:%M')} ({res.name})",
                "booked": True,
                "reservation_id": res.id
            } for res in reservations
        ]

        table_data.append({
            "id": table.id,
            "capacity": table.capacity,
            "slots": slots
        })

    return render(request, 'reservations/table_list.html', {
        'table_data': table_data,
        'selected_date': selected_date,
        'show_home_button': True
    })


def reserve_table(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    else:
        selected_date = timezone.now().date()

    if request.method == 'POST':
        form = DirectReservationForm(request.POST, selected_date=selected_date)
        if form.is_valid():
            name = form.cleaned_data['name']
            time = form.cleaned_data['time']
            start_time = datetime.combine(selected_date, time)
            end_time = start_time.replace(minute=(start_time.minute + 59) % 60)  # Dummy 1-hour slot

            conflicts = Reservation.objects.filter(
                table=table,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if not conflicts.exists():
                Reservation.objects.create(
                    table=table,
                    start_time=start_time,
                    end_time=end_time,
                    name=name
                )
                messages.success(request, "Table reserved successfully!")
                return redirect(f"{reverse('table_list')}?date={selected_date}")

            form.add_error(None, "This table is already reserved during the selected time.")
    else:
        form = DirectReservationForm(selected_date=selected_date)

    return render(request, 'reservations/reserve_table.html', {
        'form': form,
        'table': table,
        'selected_date': selected_date
    })
@login_required
def user_dashboard(request):
    selected_date = request.GET.get('date')
    reservations = Reservation.objects.all().order_by('-start_time')

    if selected_date:
        try:
            selected = datetime.strptime(selected_date, '%Y-%m-%d').date()
            reservations = reservations.filter(start_time__date=selected)
        except ValueError:
            pass

    return render(request, 'reservations/dashboard.html', {
        'reservations': reservations,
        'selected_date': selected_date,
    })

@require_POST
@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.delete()
    messages.success(request, "Reservation cancelled successfully.")
    return redirect('table_list')
