from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from .validators import (
    validate_document_upload,
    validate_image_upload,
    validate_video_upload,
)

# Create your models here.


# =====================================
# PROFIL PRINCIPAL
# =====================================

class Profile(models.Model):
    full_name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to='branding/', blank=True, null=True, validators=[validate_image_upload])
    hero_image = models.ImageField(upload_to='profile/', blank=True, null=True, validators=[validate_image_upload])
    cv_image = models.ImageField(upload_to='profile/', blank=True, null=True, validators=[validate_image_upload])
    title = models.CharField(max_length=200)
    bio = models.TextField()
    profile_image = models.ImageField(upload_to='profile/', validators=[validate_image_upload])
    cv = models.FileField(upload_to='cv/', validators=[validate_document_upload])
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.full_name


class ProfileRole(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="roles")
    name = models.CharField(max_length=80)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


# =====================================
# COMPÉTENCES
# =====================================

class Skill(models.Model):
    name = models.CharField(max_length=100)
    percentage = models.IntegerField()

    def __str__(self):
        return self.name


# =====================================
# EXPÉRIENCES PROFESSIONNELLES
# =====================================

class Experience(models.Model):
    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.position} - {self.company}"


# =====================================
# FORMATION
# =====================================

class Education(models.Model):
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    start_year = models.IntegerField()
    end_year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} - {self.institution}"


# =====================================
# CERTIFICATIONS
# =====================================

class Certification(models.Model):
    title = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    date_obtained = models.DateField()
    certificate_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title


# =====================================
# PROJETS
# =====================================

class Technology(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', validators=[validate_image_upload])
    technologies = models.ManyToManyField(Technology)
    github_link = models.URLField(blank=True, null=True)
    live_link = models.URLField(blank=True, null=True)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =====================================
# BLOG / EVENEMENTS
# =====================================

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True, validators=[validate_image_upload])
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# =====================================
# TÉMOIGNAGES
# =====================================

class Testimonial(models.Model):
    name = models.CharField(max_length=150)
    position = models.CharField(max_length=200)
    message = models.TextField()
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True, validators=[validate_image_upload])

    def __str__(self):
        return self.name


# =====================================
# SERVICES PROPOSÉS
# =====================================

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, help_text="Ex: fa-code")

    def __str__(self):
        return self.title


# =====================================
# RÉSEAUX SOCIAUX
# =====================================

class SocialLink(models.Model):
    platform = models.CharField(max_length=100)
    url = models.URLField()

    def __str__(self):
        return self.platform


# =====================================
# CONTACT
# =====================================

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ("meeting", "Rencontre"),
        ("outing", "Sortie"),
        ("challenge", "Challenge"),
        ("competition", "Competition"),
        ("other", "Autre"),
    ]

    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default="other")
    description = models.TextField()
    event_date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    cover_image = models.ImageField(upload_to="events/covers/", blank=True, null=True, validators=[validate_image_upload])
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]

    def __str__(self):
        return self.title


class EventMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("image", "Image"),
        ("video", "Video"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="media_items")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    image = models.ImageField(upload_to="events/media/images/", blank=True, null=True, validators=[validate_image_upload])
    video_file = models.FileField(upload_to="events/media/videos/", blank=True, null=True, validators=[validate_video_upload])
    video_url = models.URLField(blank=True, null=True)
    caption = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def clean(self):
        if self.media_type == "image" and not self.image:
            raise ValidationError("Pour un media de type image, vous devez ajouter une image.")
        if self.media_type == "video" and not self.video_file and not self.video_url:
            raise ValidationError("Pour un media de type video, ajoutez un fichier video ou un lien video.")

    def __str__(self):
        return f"{self.event.title} - {self.media_type}"


class VisitorLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visitor_logs",
    )
    ip_address = models.CharField(max_length=45)
    user_agent = models.TextField(blank=True)
    browser = models.CharField(max_length=120, blank=True)
    os = models.CharField(max_length=120, blank=True)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=120, blank=True)
    time_spent_seconds = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["timestamp"]),
            models.Index(fields=["ip_address"]),
            models.Index(fields=["path"]),
            models.Index(fields=["session_id"]),
        ]

    def __str__(self):
        username = self.user.username if self.user else "anonymous"
        return f"{username} {self.method} {self.path} ({self.ip_address})"
