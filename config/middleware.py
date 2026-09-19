from django.http import HttpResponse

class StealthAdminMiddleware:
    """
    Intercepts traffic to admin/dashboard routes. If the user is not 
    authenticated or not a staff member, it returns an absolute blank screen.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. ALLOW the admin login page so you can actually authenticate
        if request.path.startswith('/admin/login/'):
            return self.get_response(request)

        # 2. Block everything else under these paths
        protected_prefixes = ['/admin/', '/dashboard/']
        
        if any(request.path.startswith(prefix) for prefix in protected_prefixes):
            if not request.user.is_authenticated or not request.user.is_staff:
                # Returns a literal blank screen with zero HTML source code
                return HttpResponse("", status=403)
                
        return self.get_response(request)