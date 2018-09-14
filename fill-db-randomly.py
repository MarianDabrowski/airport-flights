from airport.models import Airplane, Flight, AirplaneCrew, Airport
from random import randint, shuffle
from datetime import datetime as dt, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError

NUM_AIR_PLANES = 40
NUM_FLIGHTS = 20
NUM_FIRST_NAMES = 10
NUM_LAST_NAMES = 10
NUMBER_MULT = 17

f = open('csv-files/capitals.csv', 'r')
capital_cities = [line.split(',')[-1].strip() for line in f][1:]
f.close()

f = open('csv-files/firstnames.csv', 'r')
first_names = [line.strip() for line in f][1:]
f.close()

f = open('csv-files/last_names.csv', 'r')
last_names = [line.strip() for line in f][1:]
f.close()

for city in capital_cities:
    Airport.objects.create(airportsName=city)

for i in range(NUM_AIR_PLANES):
    print("Airplane: {}".format(i))
    num = NUMBER_MULT * i + 1
    airplane = Airplane(regNum=num, numPlaces=randint(20, 50))
    airplane.full_clean()
    airplane.save()

    for j in range(NUM_FLIGHTS):
        inserted = False
        while not inserted:
            departurePlace = randint(1, len(capital_cities))
            arrivalPlace = randint(1, len(capital_cities))
            while departurePlace == arrivalPlace:
                arrivalPlace = randint(1, len(capital_cities))
            departureTime = dt.now(tz=timezone.utc) + timedelta(days=randint(5, 500), hours=randint(0, 24))
            arrivalTime = departureTime + timedelta(minutes=randint(30, 300))
            departure = Airport.objects.get(pk=departurePlace)
            arrival = Airport.objects.get(pk=arrivalPlace)

            flight = Flight(airplane=airplane, departureAirport=departure,\
                       arrivalAirport=arrival, departureTime=departureTime, arrivalTime=arrivalTime)
            try:
                flight.full_clean()
                inserted = True
            except ValidationError:
                pass

            flight.save()


print("insering crews")
shuffle(first_names)
shuffle(last_names)

for first_name in first_names[:NUM_FIRST_NAMES]:
    for last_name in last_names[:NUM_LAST_NAMES]:
        AirplaneCrew.objects.create(captainsName=first_name, captainsSurname=last_name)