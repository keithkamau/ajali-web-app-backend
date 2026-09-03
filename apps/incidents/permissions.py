from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsIncidentOwner(BasePermission):
    """Allow access only to the owner of the incident."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj.user == request.user


class IsAdminOrOwner(BasePermission):
    """Allow access to admin users or the incident owner."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'incident'):
            return obj.incident.user == request.user
        return False