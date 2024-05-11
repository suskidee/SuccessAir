from datetime import datetime, date

from django.conf import settings
from django.db import models
import uuid
from django.utils import timezone


class Cities(models.Model):
    cities = models.CharField(max_length=20)

    def __str__(self):
        return self.cities


class Route(models.Model):
    origin = models.ForeignKey(Cities, on_delete=models.PROTECT, related_name='origin_routes')
    destination = models.ForeignKey(Cities, on_delete=models.PROTECT, related_name='destination_routes')
    departure_time = models.TimeField(null=False, blank=False)
    departure_date = models.DateField(null=False, blank=False, default=date.today)
    arrival_time = models.TimeField(null=False, blank=False)
    arrival_date = models.DateField(null=False, blank=False,default=date.today )
    price = models.FloatField(default=100.00)
    total_seats = models.IntegerField(default=1, null=False, blank=False)
    tickets_sold = models.IntegerField(default=0)
    is_seat_remaining = models.BooleanField(default=True)

    def check_seat_availability(self):
        if self.tickets_sold >= self.total_seats:
            self.is_seat_remaining = False
        else:
            self.is_seat_remaining = True
        self.save()

    def remaining(self):
        return self.total_seats - self.tickets_sold

    def is_flight_in_past(self):
        departure_date = self.departure_date
        departure_time = self.departure_time
        departure_datetime = datetime.combine(departure_date, departure_time)
        departure_datetime = timezone.make_aware(departure_datetime, timezone.get_default_timezone())
        return departure_datetime < timezone.now()


class Pending(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    flight = models.ForeignKey(Route, on_delete=models.CASCADE)
    no_of_passengers = models.IntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_cost = self.flight.price * self.no_of_passengers
        super().save(*args, **kwargs)


class Booking(models.Model):
    flight_no = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    flight = models.ForeignKey(Route, on_delete=models.CASCADE)
    no_of_passengers = models.IntegerField(default=1)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    placed_at = models.DateTimeField(auto_now_add=True)
    check_in = models.BooleanField(default=False)

    def is_flight_in_past(self):
        departure_date = self.flight.departure_date
        departure_time = self.flight.departure_time
        departure_datetime = datetime.combine(departure_date, departure_time)
        departure_datetime = timezone.make_aware(departure_datetime, timezone.get_default_timezone())
        return departure_datetime < timezone.now()
