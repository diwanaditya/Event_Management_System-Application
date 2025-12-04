from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, Event, RSVP, Review


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'full_name', 'bio', 'location', 'profile_picture', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'full_name', 'bio', 'location']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        full_name = validated_data.pop('full_name', '')
        bio = validated_data.pop('bio', '')
        location = validated_data.pop('location', '')

        user = User.objects.create_user(**validated_data)
        
        UserProfile.objects.create(
            user=user,
            full_name=full_name,
            bio=bio,
            location=location
        )
        
        return user


class OrganizerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name']


class EventSerializer(serializers.ModelSerializer):
    organizer = OrganizerSerializer(read_only=True)
    rsvp_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'organizer', 'location',
            'start_time', 'end_time', 'is_public', 'created_at',
            'updated_at', 'rsvp_count', 'average_rating'
        ]
        read_only_fields = ['id', 'organizer', 'created_at', 'updated_at']

    def validate(self, attrs):
        if 'start_time' in attrs and 'end_time' in attrs:
            if attrs['end_time'] <= attrs['start_time']:
                raise serializers.ValidationError("End time must be after start time.")
        return attrs

    def create(self, validated_data):
        validated_data['organizer'] = self.context['request'].user
        return super().create(validated_data)


class EventDetailSerializer(EventSerializer):
    invited_users = OrganizerSerializer(many=True, read_only=True)
    
    class Meta(EventSerializer.Meta):
        fields = EventSerializer.Meta.fields + ['invited_users']


class RSVPSerializer(serializers.ModelSerializer):
    user = OrganizerSerializer(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'event', 'event_title', 'user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'event', 'user', 'created_at', 'updated_at']

    def validate_status(self, value):
        if value not in ['Going', 'Maybe', 'Not Going']:
            raise serializers.ValidationError("Invalid status. Choose from 'Going', 'Maybe', or 'Not Going'.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    user = OrganizerSerializer(read_only=True)
    event_title = serializers.CharField(source='event.title', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'event', 'event_title', 'user', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'event', 'user', 'created_at', 'updated_at']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
