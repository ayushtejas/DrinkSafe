from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self,request,view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only for admin/superuser
        print(request.user)
        return request.user and (request.user.is_organisation_admin or request.user.is_superuser)
