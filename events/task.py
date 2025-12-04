from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import RSVP, Review, Event
from datetime import timedelta
from django.utils import timezone


@shared_task
def send_rsvp_email(rsvp_id):
    """
    Send email notification when user RSVPs to an event.
    """
    try:
        rsvp = RSVP.objects.get(id=rsvp_id)
        
        subject = f'RSVP Confirmation: {rsvp.event.title}'
        message = f"""
        Hi {rsvp.user.username},
        
        Thank you for RSVPing to "{rsvp.event.title}"!
        
        Status: {rsvp.status}
        Event Details:
        - Location: {rsvp.event.location}
        - Start: {rsvp.event.start_time.strftime('%B %d, %Y at %I:%M %p')}
        - End: {rsvp.event.end_time.strftime('%B %d, %Y at %I:%M %p')}
        
        We look forward to seeing you there!
        
        Best regards,
        Event Management Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [rsvp.user.email],
            fail_silently=False,
        )
        
        return f"RSVP email sent to {rsvp.user.email}"
    except RSVP.DoesNotExist:
        return f"RSVP with id {rsvp_id} does not exist"
    except Exception as e:
        return f"Error sending RSVP email: {str(e)}"


@shared_task
def send_review_notification(review_id):
    """
    Send email notification to event organizer when someone reviews their event.
    """
    try:
        review = Review.objects.get(id=review_id)
        organizer = review.event.organizer
        
        subject = f'New Review for Your Event: {review.event.title}'
        message = f"""
        Hi {organizer.username},
        
        {review.user.username} has left a review for your event "{review.event.title}".
        
        Rating: {'⭐' * review.rating} ({review.rating}/5)
        Comment: {review.comment}
        
        Keep up the great work!
        
        Best regards,
        Event Management Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [organizer.email],
            fail_silently=False,
        )
        
        return f"Review notification sent to {organizer.email}"
    except Review.DoesNotExist:
        return f"Review with id {review_id} does not exist"
    except Exception as e:
        return f"Error sending review notification: {str(e)}"


@shared_task
def send_event_reminder():
    """
    Send reminder emails to all users who RSVP'd 'Going' for events starting in 24 hours.
    This task should be run periodically (e.g., every hour) via Celery Beat.
    """
    now = timezone.now()
    tomorrow = now + timedelta(hours=24)
    
    # Get events starting in the next 24 hours
    upcoming_events = Event.objects.filter(
        start_time__gte=now,
        start_time__lte=tomorrow
    )
    
    sent_count = 0
    for event in upcoming_events:
        # Get all users who RSVP'd 'Going'
        going_rsvps = RSVP.objects.filter(event=event, status='Going')
        
        for rsvp in going_rsvps:
            subject = f'Reminder: {event.title} starts tomorrow!'
            message = f"""
            Hi {rsvp.user.username},
            
            This is a friendly reminder that the event "{event.title}" is starting soon!
            
            Event Details:
            - Location: {event.location}
            - Start: {event.start_time.strftime('%B %d, %Y at %I:%M %p')}
            - End: {event.end_time.strftime('%B %d, %Y at %I:%M %p')}
            
            See you there!
            
            Best regards,
            Event Management Team
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [rsvp.user.email],
                    fail_silently=False,
                )
                sent_count += 1
            except Exception as e:
                print(f"Failed to send reminder to {rsvp.user.email}: {str(e)}")
    
    return f"Sent {sent_count} event reminders"
