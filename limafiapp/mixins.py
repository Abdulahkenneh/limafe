# limafiapp/mixins.py
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to require admin privileges"""

    def test_func(self):
        # Check if user is authenticated and is staff/admin
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Please login to access this page.")
            return redirect('login')
        else:
            messages.error(self.request, "You don't have permission to access this page.")
            return redirect('home')