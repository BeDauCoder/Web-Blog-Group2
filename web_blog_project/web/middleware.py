from django.conf import settings
from django.core.exceptions import PermissionDenied

class UploadFileSizeLimit:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.FILES:
            for file in request.FILES.values():
                if file.size > settings.MAX_UPLOAD_SIZE:
                    raise PermissionDenied(f"File size exceeds the limit allowed ({settings.MAX_UPLOAD_SIZE / (1024 * 1024)} MB) and cannot be saved.")
        response = self.get_response(request)
        return response
