import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import (
    BlogCategory,
    BlogPost,
    Certification,
    ContactMessage,
    Education,
    Event,
    EventMedia,
    Experience,
    Profile,
    ProfileRole,
    Project,
    Service,
    Skill,
    SocialLink,
    Technology,
    Testimonial,
    VisitorLog,
)


class ProfileRoleInline(admin.TabularInline):
    model = ProfileRole
    extra = 1
    min_num = 1
    validate_min = True


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email')
    inlines = [ProfileRoleInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'featured', 'created_at')
    list_filter = ('featured',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'created_at')
    list_filter = ('published', 'category')


class EventMediaInline(admin.TabularInline):
    model = EventMedia
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "event_date", "is_published")
    list_filter = ("event_type", "is_published", "event_date")
    search_fields = ("title", "description", "location")
    inlines = [EventMediaInline]


@admin.register(EventMedia)
class EventMediaAdmin(admin.ModelAdmin):
    list_display = ("event", "media_type", "created_at")
    list_filter = ("media_type", "created_at")


@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "ip_address",
        "method",
        "path",
        "browser",
        "os",
        "time_spent_seconds",
    )
    list_filter = ("user", "timestamp", "ip_address", "browser", "os", "method")
    search_fields = ("ip_address", "path", "session_id", "user_agent", "user__username")
    readonly_fields = (
        "user",
        "ip_address",
        "user_agent",
        "browser",
        "os",
        "path",
        "method",
        "timestamp",
        "session_id",
        "time_spent_seconds",
    )
    actions = ("export_as_csv",)
    date_hierarchy = "timestamp"

    @admin.action(description="Exporter les logs selectionnes en CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="visitor_logs.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "id",
                "timestamp",
                "username",
                "ip_address",
                "method",
                "path",
                "browser",
                "os",
                "session_id",
                "time_spent_seconds",
                "user_agent",
            ]
        )

        for log in queryset.order_by("-timestamp"):
            writer.writerow(
                [
                    log.id,
                    log.timestamp.isoformat(),
                    log.user.username if log.user else "",
                    log.ip_address,
                    log.method,
                    log.path,
                    log.browser,
                    log.os,
                    log.session_id,
                    log.time_spent_seconds if log.time_spent_seconds is not None else "",
                    log.user_agent,
                ]
            )
        return response


admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Certification)
admin.site.register(Technology)
admin.site.register(BlogCategory)
admin.site.register(Testimonial)
admin.site.register(Service)
admin.site.register(SocialLink)
admin.site.register(ContactMessage)
