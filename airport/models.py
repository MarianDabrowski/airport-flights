from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from datetime import timedelta


class Airplane(models.Model):
    regNum = models.CharField(max_length=255, unique=True)
    numPlaces = models.IntegerField()

    def clean(self):
        if self.numPlaces < 0:
            raise ValidationError('Airplane, number of places must be greater than 0!')

    def __str__(self):
        return 'Airplane %s' % self.regNum


class Passenger(models.Model):
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)

    class Meta:
        unique_together = ('name', 'surname')

    def __str__(self):
        return 'Passenger %s %s' % (self.name, self.surname)


class AirplaneCrew(models.Model):
    captainsName = models.CharField(max_length=255)
    captainsSurname = models.CharField(max_length=255)

    class Meta:
        unique_together = ('captainsName', 'captainsSurname')

    def __str__(self):
        return 'AirplaneCrew %s %s' % (self.captainsName, self.captainsSurname)

class Airport(models.Model):
    airportsName = models.CharField(max_length=255)

    def __str__(self):
        return self.airportsName


class Flight(models.Model):
    departureAirport = models.ForeignKey(Airport, related_name = 'departure' , on_delete=models.CASCADE)
    arrivalAirport = models.ForeignKey(Airport, related_name = 'arrival', on_delete=models.CASCADE)
    departureTime = models.DateTimeField()
    arrivalTime = models.DateTimeField()
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    crew = models.ForeignKey(AirplaneCrew, on_delete=models.CASCADE, null=True, blank=True, default=None)

    def clean(self):
        if self.arrivalTime < self.departureTime:
            raise ValidationError('Flight, arrival time is sooner than departure time!')
        dateDiff = self.arrivalTime - self.departureTime
        if dateDiff < timedelta(minutes=30):
            raise ValidationError('Flight, too short, at least 30 minutes!')

        flights = Flight.objects.exclude(pk=self.pk)
        flightsInTheSameTime = flights.filter(
            Q(departureTime__range=[self.departureTime, self.arrivalTime]) |
            Q(arrivalTime__range=[self.departureTime, self.arrivalTime]))
        if flightsInTheSameTime.filter(airplane=self.airplane).exists():
            raise ValidationError('Flight, airplane can not be used in more than 1 flight at the same time!')

        if flightsInTheSameTime.filter(crew=self.crew).exists():
            raise ValidationError('Flight, crew can not be used in more than 1 flight at the same time!')

        flightsInStartDay = flights.filter(airplane=self.airplane).filter(
            Q(departureTime__day=self.departureTime.day) | Q(arrivalTime__day=self.departureTime.day))
        if flightsInStartDay.values('pk').distinct().count() == 4:
            raise ValidationError('Flight, can not have more than 4 flights in the same day for one airplane!')
        flightsInEndDay = flights.filter(airplane=self.airplane).filter(
            Q(departureTime__day=self.arrivalTime.day) | Q(arrivalTime__day=self.arrivalTime.day))
        if flightsInEndDay.values('pk').distinct().count() == 4:
            raise ValidationError('Flight, can not have more than 4 flights in the same day for one airplane!')

    def __str__(self):
        return 'Flight from %s to %s' % (self.departureAirport, self.arrivalAirport)


class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)

    def clean(self):
        currPassengersNum = Ticket.objects.filter(flight=self.flight).count()
        airplanePlaces = Flight.objects.get(pk=self.flight.pk).airplane.numPlaces
        if currPassengersNum == airplanePlaces:
            raise ValidationError('There are no places left in the airplane!')
