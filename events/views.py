from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Event, RSVP, Review, UserProfile
from .serializers import (
    EventSerializer, EventDetailSerializer, RSVPSerializer,
    ReviewSerializer, UserRegistrationSerializer, UserProfileSerializer
)
from .permissions import IsOrganizerOrReadOnly, IsPublicOrInvited, IsOwnerOrReadOnly
from .tasks import send_rsvp_email, send_review_notification


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user with profile."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Event CRUD operations.
    
    list: Get all public events (paginated)
    retrieve: Get details of a specific event
    create: Create a new event (authenticated users only)
    update: Update an event (organizer only)
    destroy: Delete an event (organizer only)
    """
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsOrganizerOrReadOnly, IsPublicOrInvited]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'is_public', 'organizer__username']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']

    def get_queryset(self):
        """
        Return public events for all users.
        For authenticated users, also return private events they're invited to.
        """
        user = self.request.user
        
        if user.is_authenticated:
            # Public events + private events organized by user + private events user is invited to
            return Event.objects.filter(
                Q(is_public=True) |
                Q(organizer=user) |
                Q(invited_users=user)
            ).distinct()
        else:
            # Only public events for unauthenticated users
            return Event.objects.filter(is_public=True)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer

    def perform_create(self, serializer):
        """Set the organizer to the current user."""
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rsvp(self, request, pk=None):
        """
        RSVP to an event.
        POST /api/events/{id}/rsvp/
        Body: {"status": "Going"}
        """
        event = self.get_object()
        status_value = request.data.get('status', 'Going')

        if status_value not in ['Going', 'Maybe', 'Not Going']:
            return Response(
                {'error': 'Invalid status. Choose from: Going, Maybe, Not Going'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rsvp, created = RSVP.objects.update_or_create(
            event=event,
            user=request.user,
            defaults={'status': status_value}
        )

        # Send async email notification
        send_rsvp_email.delay(rsvp.id)

        serializer = RSVPSerializer(rsvp)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'], url_path='rsvp/(?P<user_id>[^/.]+)', permission_classes=[IsAuthenticated])
    def update_rsvp(self, request, pk=None, user_id=None):
        """
        Update RSVP status.
        PATCH /api/events/{event_id}/rsvp/{user_id}/
        Body: {"status": "Maybe"}
        """
        event = self.get_object()
        
        # Only allow users to update their own RSVP
        if str(request.user.id) != user_id:
            return Response(
                {'error': 'You can only update your own RSVP'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            rsvp = RSVP.objects.get(event=event, user=request.user)
        except RSVP.DoesNotExist:
            return Response(
                {'error': 'RSVP not found. Please RSVP first.'},
                status=status.HTTP_404_NOT_FOUND
            )

        status_value = request.data.get('status')
        if status_value:
            if status_value not in ['Going', 'Maybe', 'Not Going']:
                return Response(
                    {'error': 'Invalid status. Choose from: Going, Maybe, Not Going'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            rsvp.status = status_value
            rsvp.save()

        serializer = RSVPSerializer(rsvp)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated])
    def reviews(self, request, pk=None):
        """
        Get reviews for an event or add a review.
        GET /api/events/{id}/reviews/
        POST /api/events/{id}/reviews/
        Body: {"rating": 5, "comment": "Great event!"}
        """
        event = self.get_object()

        if request.method == 'GET':
            reviews = event.reviews.all()
            page = self.paginate_queryset(reviews)
            if page is not None:
                serializer = ReviewSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            # Check if user already reviewed this event
            if Review.objects.filter(event=event, user=request.user).exists():
                return Response(
                    {'error': 'You have already reviewed this event'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(event=event, user=request.user)
                
                # Send async notification to organizer
                send_review_notification.delay(serializer.data['id'])
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user profiles.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
