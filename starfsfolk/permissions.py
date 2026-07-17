from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """Heimild aðeins fyrir Super Admin"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.notendategund == 'SUPER_ADMIN'
        )


class IsSubAdminOrSuperAdmin(permissions.BasePermission):
    """Heimild fyrir Sub Admin og Super Admin"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.notendategund in ['SUB_ADMIN', 'SUPER_ADMIN']
        )


class IsStarfsmaður(permissions.BasePermission):
    """Heimild fyrir alla starfsmenn"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.er_starfsmadur
        )
