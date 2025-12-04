from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import timedelta
from .models import UserProfile, Event, RSVP, Review


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
    
    def test_user_profile_creation(self):
        """Test that user profile is created with user"""
        profile = UserProfile.objects.create(
            user=self.user,
            full_name='Test User',
            bio='Test bio',
            location='Test City'
        )
        self.assertEqual(str(profile), "testuser's Profile")
        self.assertEqual(profile.full_name, 'Test User')


class EventModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='organizer', password='testpass123')
        self.start_time = timezone.now() + timedelta(days=1)
        self.end_time = self.start_time + timedelta(hours=2)
    
    def test_event_creation(self):
        """Test event creation with valid data"""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.user,
            location='Test Location',
            start_time=self.start_time,
            end_time=self.end_time,
            is_public=True
        )
        self.assertEqual(str(event), 'Test Event')
        self.assertEqual(event.organizer, self.user)
    
    def test_event_rsvp_count(self):
        """Test RSVP count property"""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.user,
            location='Test Location',
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        user2 = User.objects.create_user(username='user2', password='pass123')
        RSVP.objects.create(event=event, user=user2, status='Going')
        
        self.assertEqual(event.rsvp_count, 1)


class RSVPModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.organizer = User.objects.create_user(username='organizer', password='testpass123')
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.organizer,
            location='Test Location',
            start_time=start_time,
            end_time=end_time
        )
    
    def test_rsvp_creation(self):
        """Test RSVP creation"""
        rsvp = RSVP.objects.create(
            event=self.event,
            user=self.user,
            status='Going'
        )
        self.assertEqual(rsvp.status, 'Going')
        self.assertEqual(str(rsvp), f"testuser - Test Event (Going)")
    
    def test_unique_rsvp_constraint(self):
        """Test that a user cannot RSVP twice to the same event"""
        RSVP.objects.create(event=self.event, user=self.user, status='Going')
        
        with self.assertRaises(Exception):
            RSVP.objects.create(event=self.event, user=self.user, status='Maybe')


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.organizer = User.objects.create_user(username='organizer', password='testpass123')
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.organizer,
            location='Test Location',
            start_time=start_time,
            end_time=end_time
        )
    
    def test_review_creation(self):
        """Test review creation"""
        review = Review.objects.create(
            event=self.event,
            user=self.user,
            rating=5,
            comment='Great event!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(str(review), "testuser - Test Event (5★)")


class EventAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        UserProfile.objects.create(user=self.user, full_name='Test User')
        
        self.start_time = timezone.now() + timedelta(days=1)
        self.end_time = self.start_time + timedelta(hours=2)
        
        # Get JWT token
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_event(self):
        """Test creating an event via API"""
        data = {
            'title': 'API Test Event',
            'description': 'Test description',
            'location': 'Test Location',
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'is_public': True
        }
        response = self.client.post('/api/events/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().title, 'API Test Event')
    
    def test_list_events(self):
        """Test listing events via API"""
        Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.user,
            location='Test Location',
            start_time=self.start_time,
            end_time=self.end_time,
            is_public=True
        )
        
        response = self.client.get('/api/events/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_update_event_as_organizer(self):
        """Test updating event as organizer"""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.user,
            location='Test Location',
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        data = {'title': 'Updated Event Title'}
        response = self.client.patch(f'/api/events/{event.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        event.refresh_from_db()
        self.assertEqual(event.title, 'Updated Event Title')
    
    def test_delete_event_as_organizer(self):
        """Test deleting event as organizer"""
        event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.user,
            location='Test Location',
            start_time=self.start_time,
            end_time=self.end_time
        )
        
        response = self.client.delete(f'/api/events/{event.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)


class RSVPAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.organizer = User.objects.create_user(username='organizer', password='testpass123')
        
        UserProfile.objects.create(user=self.user, full_name='Test User')
        UserProfile.objects.create(user=self.organizer, full_name='Organizer')
        
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.organizer,
            location='Test Location',
            start_time=start_time,
            end_time=end_time,
            is_public=True
        )
        
        # Get JWT token
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_rsvp_to_event(self):
        """Test RSVPing to an event"""
        data = {'status': 'Going'}
        response = self.client.post(f'/api/events/{self.event.id}/rsvp/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RSVP.objects.count(), 1)
        self.assertEqual(RSVP.objects.get().status, 'Going')
    
    def test_update_rsvp(self):
        """Test updating RSVP status"""
        RSVP.objects.create(event=self.event, user=self.user, status='Going')
        
        data = {'status': 'Maybe'}
        response = self.client.patch(
            f'/api/events/{self.event.id}/rsvp/{self.user.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(RSVP.objects.get().status, 'Maybe')


class ReviewAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.organizer = User.objects.create_user(username='organizer', password='testpass123')
        
        UserProfile.objects.create(user=self.user, full_name='Test User')
        UserProfile.objects.create(user=self.organizer, full_name='Organizer')
        
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        
        self.event = Event.objects.create(
            title='Test Event',
            description='Test description',
            organizer=self.organizer,
            location='Test Location',
            start_time=start_time,
            end_time=end_time,
            is_public=True
        )
        
        # Get JWT token
        response = self.client.post('/api/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_create_review(self):
        """Test creating a review for an event"""
        data = {
            'rating': 5,
            'comment': 'Excellent event!'
        }
        response = self.client.post(f'/api/events/{self.event.id}/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().rating, 5)
    
    def test_list_reviews(self):
        """Test listing reviews for an event"""
        Review.objects.create(
            event=self.event,
            user=self.user,
            rating=4,
            comment='Good event'
        )
        
        response = self.client.get(f'/api/events/{self.event.id}/reviews/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
