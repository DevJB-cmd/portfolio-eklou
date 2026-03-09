from .models import Profile


def branding(request):
    return {"site_profile": Profile.objects.first()}
