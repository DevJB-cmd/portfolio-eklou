import json

from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from .forms import ContactForm
from .models import (
    BlogCategory,
    BlogPost,
    Certification,
    Education,
    Event,
    Experience,
    Profile,
    Project,
    Service,
    Skill,
    SocialLink,
    Testimonial,
    VisitorLog,
)


# ==============================
# HOME
# ==============================

def home(request):
    profile = Profile.objects.first()
    skills = Skill.objects.all()
    experiences = Experience.objects.all().order_by('-start_date')
    educations = Education.objects.all().order_by('-start_year')
    certifications = Certification.objects.all()
    services = Service.objects.all()
    projects = Project.objects.all().prefetch_related('technologies')
    testimonials = Testimonial.objects.all()
    social_links = SocialLink.objects.all()

    role_names = list(profile.roles.values_list("name", flat=True)) if profile else []
    typed_items = ", ".join(role_names)
    if not typed_items:
        typed_items = ", ".join(list(skills.values_list('name', flat=True)[:4]))
    if not typed_items:
        typed_items = "Designer, Developpeur, Freelancer"

    years_experience = 0
    if experiences:
        earliest_start = experiences.last().start_date
        years_experience = max(0, experiences.first().start_date.year - earliest_start.year)

    portfolio_categories = []
    for project in projects:
        tech_names = [tech.name for tech in project.technologies.all()]
        primary = tech_names[0] if tech_names else "Work"
        category_slug = slugify(primary) or "work"
        project.filter_class = f"filter-{category_slug}"
        project.display_category = primary
        project.tags = tech_names[:2]
        if not any(cat["slug"] == category_slug for cat in portfolio_categories):
            portfolio_categories.append({"slug": category_slug, "name": primary})

    context = {
        'profile': profile,
        'skills': skills,
        'experiences': experiences,
        'educations': educations,
        'certifications': certifications,
        'services': services,
        'projects': projects,
        'testimonials': testimonials,
        'social_links': social_links,
        'typed_items': typed_items,
        'years_experience': years_experience,
        'portfolio_categories': portfolio_categories,
        'contact_form': ContactForm(),
    }

    return render(request, 'monportfolio/home.html', context)


# ==============================
# PROJECT DETAIL
# ==============================

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'monportfolio/project_detail.html', {'project': project})


# ==============================
# BLOG
# ==============================

def blog(request):
    posts = BlogPost.objects.filter(published=True).order_by('-created_at')
    categories = BlogCategory.objects.all()

    return render(request, 'monportfolio/blog.html', {
        'posts': posts,
        'categories': categories
    })


def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'monportfolio/blog_detail.html', {'post': post})


# ==============================
# EVENTS
# ==============================

def events(request):
    events_list = Event.objects.filter(is_published=True).prefetch_related("media_items")
    profile = Profile.objects.first()
    social_links = SocialLink.objects.all()
    return render(
        request,
        "monportfolio/events.html",
        {"events_list": events_list, "profile": profile, "social_links": social_links},
    )


def event_detail(request, pk):
    event = get_object_or_404(
        Event.objects.filter(is_published=True).prefetch_related("media_items"), pk=pk
    )
    profile = Profile.objects.first()
    social_links = SocialLink.objects.all()
    return render(
        request,
        "monportfolio/event_detail.html",
        {"event": event, "profile": profile, "social_links": social_links},
    )


# ==============================
# CONTACT
# ==============================

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Message envoye avec succes.")
            return redirect('home')
        messages.error(request, "Le formulaire contient des erreurs.")
    else:
        form = ContactForm()

    return render(request, 'monportfolio/contact.html', {"form": form})


@require_POST
def track_time_spent(request):
    if not request.session.session_key:
        request.session.save()

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Payload invalide.")

    path = (payload.get("path") or "").strip()
    time_spent_seconds = payload.get("time_spent_seconds")

    if not path:
        return HttpResponseBadRequest("Path manquant.")
    if not isinstance(time_spent_seconds, int) or time_spent_seconds < 0:
        return HttpResponseBadRequest("Duree invalide.")

    visitor_log = (
        VisitorLog.objects.filter(session_id=request.session.session_key, path=path)
        .order_by("-timestamp")
        .first()
    )
    if visitor_log:
        visitor_log.time_spent_seconds = time_spent_seconds
        visitor_log.save(update_fields=["time_spent_seconds"])

    return JsonResponse({"status": "ok"})
