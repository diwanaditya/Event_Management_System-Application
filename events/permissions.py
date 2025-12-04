from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow organizers of an event to edit or delete it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the organizer of the event
        return obj.organizer == request.user


class IsPublicOrInvited(permissions.BasePermission):
    """
    Custom permission to restrict access to private events to invited users only.
    """
    
    def has_object_permission(self, request, view, obj):
        # Public events are accessible to everyone
        if obj.is_public:
            return True
        
        # Private events are only accessible to the organizer and invited users
        if request.user.is_authenticated:
            return (
                obj.organizer == request.user or
                request.user in obj.invited_users.all()
            )
        
        return False


class IsEventParticipant(permissions.BasePermission):
    """
    Custom permission to check if user has RSVP'd to an event before reviewing.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For POST requests, check if user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow organizer to view all reviews
        if obj.event.organizer == request.user:
            return True
        
        # For reviews, only the review author can edit/delete
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user
