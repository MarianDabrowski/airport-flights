from django.test import TestCase
from .models import Flight, AirplaneCrew, Airplane, Airport
from django.contrib.auth.models import User
from datetime import datetime as dt, timedelta
from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class RestApiTest(TestCase):
    date = dt.strptime('2018-12-22', '%Y-%m-%d').astimezone(timezone.utc)

    def setUp(self):
        User.objects.create_user(username='a', password='a')
        departure = Airport(airportsName='Sukhumi')
        arrival = Airport(airportsName='Warsaw')
        departure.save()
        arrival.save()
        names = ['John', 'Aaron', 'Wayne', 'Carlos', 'Thomas']
        lastNames = ['1', '2', '3', '4', '5']

        for i in range(5):
            a = Airplane.objects.create(regNum=i + 1, numPlaces=20)
            b = AirplaneCrew.objects.create(captainsName=names[i], captainsSurname=lastNames[i])
            Flight.objects.create(departureAirport=departure, arrivalAirport=arrival, airplane=a, crew=b,\
                                  departureTime=self.date, arrivalTime=self.date + timedelta(hours=4))

    def testGetCrews(self):
        response = self.client.get('/api/get_crews/', data={
            'day': self.date.day,
            'month': self.date.month,
            'year': self.date.year,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'{"crews": [{"flightId": 1, "crew": "John 1"}, ' +
                         b'{"flightId": 2, "crew": "Aaron 2"}, ' + b'{"flightId": 3, "crew": "Wayne 3"}, ' +
                         b'{"flightId": 4, "crew": "Carlos 4"}, ' + b'{"flightId": 5, "crew": "Thomas 5"}]}')

    def testChangeCrewNoError(self):
        crew = AirplaneCrew.objects.create(captainsName="Wayne", captainsSurname="Rooney")
        response = self.client.post('/api/change_flight_crew/', data={
            'flightId': Flight.objects.get(airplane__regNum=5).id,
            'captainsName': 'Wayne',
            'captainsSurname': 'Rooney',
            'username': 'a',
            'password': 'a',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Flight.objects.get(airplane__regNum=5).crew_id, crew.id)

    def testChangeCrewError(self):
        response = self.client.post('/api/change_flight_crew/', data={
            'flightId': Flight.objects.get(airplane__regNum=1).id,
            'captainsName': 'John',
            'captainsSurname': '2',
            'username': 'a',
            'password': 'a',
        })
        self.assertEqual(response.status_code, 403)
