from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
	"""
		User permission in accessing api
	"""

	def has_permission(self, request, view):
		if request.method == 'GET':
			return True
		return super(IsAdmin, self).has_permission(request, view)