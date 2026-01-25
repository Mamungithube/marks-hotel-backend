from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission for Admin users only
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsFinanceUser(permissions.BasePermission):
    """
    Permission for Finance team
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_finance or request.user.is_admin
        )


class IsStaffUser(permissions.BasePermission):
    """
    Permission for Staff users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_hotel_staff or request.user.is_admin
        )


class IsCustomerUser(permissions.BasePermission):
    """
    Permission for Customer users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_customer


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission - owner or admin can access
    """
    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.is_admin:
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Read-only for all, write for admin only
    """
    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admin
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Read-only for all authenticated, write for staff/admin
    """
    def has_permission(self, request, view):
        # Read permissions for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions for staff or admin
        return request.user and request.user.is_authenticated and (
            request.user.is_hotel_staff or request.user.is_admin
        )