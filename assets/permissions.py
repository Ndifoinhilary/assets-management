from rest_framework import permissions


class IsOwnerOrAdminPermission(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """

    def has_permission(self, request, view):
        """Check if the user has permission to access the view"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if a user has permission to access a specific object"""
        # Admin users have full access
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Object must have a 'user' attribute for ownership check
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # For models without a user field, deny access to regular users
        return False


class IsOwnerOrReadOnlyPermission(permissions.BasePermission):
    """
    Custom permission to allow read access to all authenticated users,
    but write access only to owners or admins.
    """

    def has_permission(self, request, view):
        """Check if the user has permission to access the view"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check if a user has permission to access a specific object"""
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for owners or admins
        if request.user.is_staff or request.user.is_superuser:
            return True

        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False


class IsAdminOrCreateOnlyPermission(permissions.BasePermission):
    """
    Custom permission that allows anyone to create objects,
    but only admins to modify or delete them.
    """

    def has_permission(self, request, view):
        """Check if the user has permission to access the view"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow creation for authenticated users
        if view.action == 'create':
            return True

        # Only admins can perform other actions
        return request.user.is_staff or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        """Check if a user has permission to access a specific object"""
        # Only admins can access individual objects
        return request.user.is_staff or request.user.is_superuser