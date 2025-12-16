from django.conf import settings
from django.shortcuts import redirect


class RemoveTrailingSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('GET', 'HEAD'):
            if request.path != '/' and request.path.endswith('/'):
                ignore_prefixes = getattr(settings, 'REMOVE_SLASH_IGNORE_PREFIXES', ['/admin/'])

                if not any(request.path.startswith(prefix) for prefix in ignore_prefixes):
                    new_url = request.path.rstrip('/')
                    if request.GET:
                        new_url += f'?{request.META["QUERY_STRING"]}'

                    return redirect(new_url, permanent=True)

        return self.get_response(request)