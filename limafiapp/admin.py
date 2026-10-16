# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Slider, Campaign,BoardMembership, ConnectionRequest, Message,ExecutiveBoard
from django.db import models
from django.utils.html import format_html

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'chapter', 'is_good_standing', 'profile_image_preview', 'is_staff', 'is_active')

    readonly_fields = ('uuid', 'date_joined', 'last_login', 'profile_image_preview')

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': (
            'role', 'uuid', 'is_two_factor_enabled','bio',
            'phone_number', 'address', 'chapter', 'is_good_standing', 'profile_image', 'profile_image_preview'
        )}),
    )

    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.profile_image.url)
        return "No Image"

    profile_image_preview.short_description = 'Profile Image'
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('chapter')

admin.site.register(CustomUser)
# content/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Page, Post, Media, Project


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'created_at', 'updated_at', 'version', 'content_preview')
    search_fields = ('title', 'content', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('author', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'version')
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return format_html('<span title="{}">{}</span>',
                           obj.content,
                           obj.content[:100] + '...' if len(obj.content) > 100 else obj.content)

    content_preview.short_description = 'Content Preview'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'version', 'content_preview')
    search_fields = ('title', 'content')
    list_filter = ('author', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'version')
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content

    content_preview.short_description = 'Content Preview'


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('file', 'file_preview', 'alt_text', 'uploaded_by', 'created_at', 'file_type')
    search_fields = ('alt_text', 'file')
    list_filter = ('uploaded_by', 'created_at')
    readonly_fields = ('created_at', 'file_preview_admin')
    date_hierarchy = 'created_at'

    def file_preview(self, obj):
        if obj.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.file.url)
        return "File"

    file_preview.short_description = 'Preview'

    def file_preview_admin(self, obj):
        if obj.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            return format_html('<img src="{}" width="200" height="200" style="object-fit: cover;" />', obj.file.url)
        return f"File: {obj.file.name}"

    file_preview_admin.short_description = 'File Preview'

    def file_type(self, obj):
        return obj.file.name.split('.')[-1].upper() if '.' in obj.file.name else 'Unknown'

    file_type.short_description = 'Type'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'images_count', 'description_preview')
    search_fields = ('title', 'description')
    filter_horizontal = ('images',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def images_count(self, obj):
        return obj.images.count()

    images_count.short_description = 'Images'

    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description

    description_preview.short_description = 'Description'


# events/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Event, Booking


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('user', 'verification_code', 'booked_at', 'is_accredited_delegate')
    readonly_fields = ('verification_code', 'booked_at')
    show_change_link = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'start_time', 'end_time', 'location', 'organizer', 'attendee_count', 'quorum_met',
                    'status')
    search_fields = ('title', 'description', 'location')
    list_filter = ('type', 'start_time', 'organizer', 'quorum_met')
    readonly_fields = ('created_at', 'attendee_count_display')
    inlines = [BookingInline]
    date_hierarchy = 'start_time'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'type', 'description', 'organizer')
        }),
        ('Time & Location', {
            'fields': ('start_time', 'end_time', 'location')
        }),
        ('Status', {
            'fields': ('quorum_met', 'attendee_count_display', 'created_at')
        }),
    )

    def attendee_count(self, obj):
        return obj.booking_set.count()

    attendee_count.short_description = 'Attendees'

    def attendee_count_display(self, obj):
        return obj.booking_set.count()

    attendee_count_display.short_description = 'Total Attendees'

    def status(self, obj):
        now = timezone.now()
        if obj.start_time > now:
            return 'Upcoming'
        elif obj.start_time <= now <= obj.end_time:
            return 'Ongoing'
        else:
            return 'Completed'

    status.short_description = 'Status'

    actions = ['generate_attendee_report', 'mark_quorum_met']

    def generate_attendee_report(self, request, queryset):
        # Placeholder for report generation logic
        self.message_user(request, f"Generating reports for {queryset.count()} events")

    generate_attendee_report.short_description = "Generate attendee reports"

    def mark_quorum_met(self, request, queryset):
        updated = queryset.update(quorum_met=True)
        self.message_user(request, f"Marked quorum as met for {updated} events")

    mark_quorum_met.short_description = "Mark quorum as met"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'verification_code', 'booked_at', 'is_accredited_delegate')
    search_fields = ('user__username', 'event__title', 'verification_code')
    list_filter = ('event', 'booked_at', 'is_accredited_delegate')
    readonly_fields = ('verification_code', 'booked_at')
    date_hierarchy = 'booked_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('event', 'user')


# donations/admin.py
from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'amount', 'chapter', 'transaction_id', 'created_at', 'receipt_sent')
    search_fields = ('user__username', 'transaction_id', 'chapter__name')
    list_filter = ('type', 'created_at', 'receipt_sent', 'chapter')
    readonly_fields = ('transaction_id', 'created_at')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'chapter')

    actions = ['resend_receipt', 'mark_receipt_sent']

    def resend_receipt(self, request, queryset):
        for donation in queryset:
            if donation.user and not donation.receipt_sent:
                send_mail(
                    f'Donation Receipt - {donation.get_type_display()}',
                    f'Thank you for your {donation.get_type_display()} of ${donation.amount}!',
                    settings.DEFAULT_FROM_EMAIL,
                    [donation.user.email],
                )
                donation.receipt_sent = True
                donation.save(update_fields=['receipt_sent'])

        self.message_user(request, f"Receipts resent for {queryset.count()} donations")

    resend_receipt.short_description = "Resend receipt for selected donations"

    def mark_receipt_sent(self, request, queryset):
        updated = queryset.update(receipt_sent=True)
        self.message_user(request, f"Marked {updated} donations as receipt sent")

    mark_receipt_sent.short_description = "Mark receipt as sent"


# communications/admin.py
from django.contrib import admin
from django.core.mail import send_mass_mail
from django.conf import settings
from .models import Message, Newsletter, ContactSubmission


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content_preview', 'sent_at', 'read')
    search_fields = ('sender__username', 'receiver__username', 'content')
    list_filter = ('sent_at', 'read')
    readonly_fields = ('sent_at',)
    date_hierarchy = 'sent_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'receiver')

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content

    content_preview.short_description = 'Message'

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(read=True)
        self.message_user(request, f"Marked {updated} messages as read")

    mark_as_read.short_description = "Mark as read"

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(read=False)
        self.message_user(request, f"Marked {updated} messages as unread")

    mark_as_unread.short_description = "Mark as unread"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sent_at', 'subscribers_count', 'is_sent')
    search_fields = ('subject', 'content')
    list_filter = ('sent_at',)
    readonly_fields = ('sent_at',)
    filter_horizontal = ('subscribers',)
    date_hierarchy = 'sent_at'

    def subscribers_count(self, obj):
        return obj.subscribers.count()

    subscribers_count.short_description = 'Subscribers'

    def is_sent(self, obj):
        return obj.sent_at is not None

    is_sent.boolean = True
    is_sent.short_description = 'Sent'

    actions = ['send_newsletter', 'duplicate_newsletter']

    def send_newsletter(self, request, queryset):
        from django.utils import timezone
        for newsletter in queryset:
            if not newsletter.sent_at:
                # Simple email sending implementation
                subscribers_emails = list(newsletter.subscribers.values_list('email', flat=True))
                if subscribers_emails:
                    email_message = (
                        newsletter.subject,
                        newsletter.content,
                        settings.DEFAULT_FROM_EMAIL,
                        subscribers_emails
                    )
                    try:
                        send_mass_mail([email_message])
                        newsletter.sent_at = timezone.now()
                        newsletter.save()
                    except Exception as e:
                        self.message_user(request, f"Error sending newsletter: {str(e)}", level='error')

        self.message_user(request, "Newsletters sent successfully")

    send_newsletter.short_description = "Send selected newsletters"

    def duplicate_newsletter(self, request, queryset):
        for newsletter in queryset:
            newsletter.pk = None
            newsletter.subject = f"Copy of {newsletter.subject}"
            newsletter.sent_at = None
            newsletter.save()
        self.message_user(request, f"Duplicated {queryset.count()} newsletters")

    duplicate_newsletter.short_description = "Duplicate selected newsletters"


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message_preview', 'submitted_at', 'replied')
    search_fields = ('name', 'email', 'message')
    list_filter = ('submitted_at', 'replied')
    readonly_fields = ('submitted_at',)
    date_hierarchy = 'submitted_at'

    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message

    message_preview.short_description = 'Message'

    actions = ['mark_as_replied', 'mark_as_unreplied']

    def mark_as_replied(self, request, queryset):
        updated = queryset.update(replied=True)
        self.message_user(request, f"Marked {updated} submissions as replied")

    mark_as_replied.short_description = "Mark as replied"

    def mark_as_unreplied(self, request, queryset):
        updated = queryset.update(replied=False)
        self.message_user(request, f"Marked {updated} submissions as unreplied")

    mark_as_unreplied.short_description = "Mark as unreplied"


# analytics/admin.py
from django.contrib import admin
from .models import Analytic


@admin.register(Analytic)
class AnalyticAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'content_object', 'views', 'last_updated')
    search_fields = ('content_type__model',)
    list_filter = ('content_type',)
    readonly_fields = ('content_type', 'object_id', 'content_object', 'last_updated')

    def last_updated(self, obj):
        # Assuming you have a field for last view timestamp
        return "Recently"  # Replace with actual field if exists

    last_updated.short_description = 'Last Activity'

    def has_add_permission(self, request):
        return False  # Analytics are typically auto-generated

    def has_change_permission(self, request, obj=None):
        return False  # Analytics are typically read-only


# chapters/admin.py
from django.contrib import admin
from .models import Chapter, Membership

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'country',
        'member_count',
        'active_member_count',
        'is_good_standing',
        'created_at'
    )
    list_filter = ('country', 'is_good_standing', 'created_at')
    search_fields = ('name', 'country', 'description')

    # 🔧 FIX: expose positions so they are selectable & savable
    filter_horizontal = ('representatives', 'positions')

    readonly_fields = (
        'created_at',
        'member_count_display',
        'active_member_count_display'
    )
    date_hierarchy = 'created_at'

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = 'Total Members'

    def member_count_display(self, obj):
        return obj.members.count()

    member_count_display.short_description = 'Total Members'

    def active_member_count(self, obj):
        return obj.members.filter(is_good_standing=True).count()

    active_member_count.short_description = 'Active Members'

    def active_member_count_display(self, obj):
        return obj.members.filter(is_good_standing=True).count()

    active_member_count_display.short_description = 'Active Members'


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'join_date', 'dues_paid', 'dues_amount', 'payment_date')
    list_filter = ('dues_paid', 'join_date', 'chapter')
    search_fields = ('user__username', 'chapter__name')
    readonly_fields = ('join_date',)
    date_hierarchy = 'join_date'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'chapter')

    actions = ['mark_dues_paid', 'mark_dues_unpaid']

    def mark_dues_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(dues_paid=True, payment_date=timezone.now().date())
        self.message_user(request, f"Marked {updated} memberships as dues paid")

    mark_dues_paid.short_description = "Mark dues as paid"

    def mark_dues_unpaid(self, request, queryset):
        updated = queryset.update(dues_paid=False, payment_date=None)
        self.message_user(request, f"Marked {updated} memberships as dues unpaid")

    mark_dues_unpaid.short_description = "Mark dues as unpaid"


# committees/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Committee, Position
from django.contrib import admin
from django.utils import timezone
from .models import Committee, Position


class PositionInline(admin.TabularInline):
    model = Position
    extra = 0
    fields = ('name', 'type', 'holder', 'term_start', 'term_end', 'is_active_display')
    readonly_fields = ('is_active_display',)

    def is_active_display(self, obj):
        today = timezone.now().date()

        if not obj.term_start or not obj.term_end:
            return False

        return obj.term_start <= today <= obj.term_end

    is_active_display.boolean = True
    is_active_display.short_description = 'Active'


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'chair', 'member_count', 'position_count', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)
    inlines = [PositionInline]
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = 'Members'

    def position_count(self, obj):
        return obj.positions.count()

    position_count.short_description = 'Positions'


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'type', 'committee', 'holder',
        'term_start', 'term_end', 'is_active', 'days_remaining'
    )
    list_filter = ('type', 'term_start', 'term_end', 'committee')
    search_fields = ('name', 'holder__username', 'committee__name')
    readonly_fields = ('days_remaining_display',)
    date_hierarchy = 'term_start'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('holder', 'committee')

    def is_active(self, obj):
        today = timezone.now().date()

        if not obj.term_start or not obj.term_end:
            return False

        return obj.term_start <= today <= obj.term_end

    is_active.boolean = True
    is_active.short_description = 'Active'

    def days_remaining(self, obj):
        from datetime import date
        today = date.today()

        if not obj.term_end:
            return "No end date"

        if obj.term_end < today:
            return "Expired"

        remaining = (obj.term_end - today).days
        return f"{remaining} days"

    days_remaining.short_description = 'Term Ends In'

    def days_remaining_display(self, obj):
        return self.days_remaining(obj)

    days_remaining_display.short_description = 'Days Remaining'


# elections/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import Election, Candidate


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 0
    fields = ('user', 'position', 'approved', 'votes', 'vote_percentage')
    readonly_fields = ('vote_percentage',)

    def vote_percentage(self, obj):
        total_votes = obj.election.candidate_set.aggregate(total=models.Sum('votes'))['total'] or 0
        if total_votes > 0:
            return f"{(obj.votes / total_votes * 100):.1f}%"
        return "0%"

    vote_percentage.short_description = 'Vote %'


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'commission', 'candidate_count', 'is_active', 'is_upcoming',
                    'is_completed')
    list_filter = ('start_date', 'end_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('positions',)
    inlines = [CandidateInline]
    readonly_fields = ('candidate_count_display', 'status')
    date_hierarchy = 'start_date'

    def candidate_count(self, obj):
        return obj.candidate_set.count()

    candidate_count.short_description = 'Candidates'

    def candidate_count_display(self, obj):
        return obj.candidate_set.count()

    candidate_count_display.short_description = 'Total Candidates'

    def is_active(self, obj):
        return obj.start_date <= timezone.now().date() <= obj.end_date

    is_active.boolean = True
    is_active.short_description = 'Active'

    def is_upcoming(self, obj):
        return obj.start_date > timezone.now().date()

    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming'

    def is_completed(self, obj):
        return obj.end_date < timezone.now().date()

    is_completed.boolean = True
    is_completed.short_description = 'Completed'

    def status(self, obj):
        if obj.start_date > timezone.now().date():
            return "Upcoming"
        elif obj.start_date <= timezone.now().date() <= obj.end_date:
            return "Active"
        else:
            return "Completed"

    status.short_description = 'Status'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('user', 'election', 'position', 'approved', 'votes', 'vote_percentage')
    list_filter = ('approved', 'election', 'position')
    search_fields = ('user__username', 'position__name', 'election__title')
    readonly_fields = ('vote_percentage_display',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'election', 'position')

    def vote_percentage(self, obj):
        total_votes = obj.election.candidate_set.aggregate(total=models.Sum('votes'))['total'] or 0
        if total_votes > 0:
            return f"{(obj.votes / total_votes * 100):.1f}%"
        return "0%"

    vote_percentage.short_description = 'Vote %'

    def vote_percentage_display(self, obj):
        return self.vote_percentage(obj)

    vote_percentage_display.short_description = 'Vote Percentage'

    actions = ['approve_candidates', 'disapprove_candidates', 'reset_votes']

    def approve_candidates(self, request, queryset):
        updated = queryset.update(approved=True)
        self.message_user(request, f"Approved {updated} candidates")

    approve_candidates.short_description = "Approve selected candidates"

    def disapprove_candidates(self, request, queryset):
        updated = queryset.update(approved=False)
        self.message_user(request, f"Disapproved {updated} candidates")

    disapprove_candidates.short_description = "Disapprove selected candidates"

    def reset_votes(self, request, queryset):
        updated = queryset.update(votes=0)
        self.message_user(request, f"Reset votes for {updated} candidates")

    reset_votes.short_description = "Reset votes to zero"


# conflict_resolution/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import ConflictResolution


@admin.register(ConflictResolution)
class ConflictResolutionAdmin(admin.ModelAdmin):
    list_display = ('description_preview', 'committee', 'involved_parties_count', 'resolved', 'resolution_date',
                    'days_open')
    list_filter = ('resolved', 'resolution_date', 'committee')
    search_fields = ('description', 'involved_parties__username', 'committee__name')
    filter_horizontal = ('involved_parties',)
    readonly_fields = ('days_open_display',)
    date_hierarchy = 'resolution_date'

    def description_preview(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description

    description_preview.short_description = 'Description'

    def involved_parties_count(self, obj):
        return obj.involved_parties.count()

    involved_parties_count.short_description = 'Parties Involved'

    def days_open(self, obj):
        if obj.resolved and obj.resolution_date:
            return "Resolved"
        from datetime import date
        today = date.today()
        days = (today - obj.creation_date.date()).days if hasattr(obj, 'creation_date') else "Unknown"
        return f"{days} days" if isinstance(days, int) else days

    days_open.short_description = 'Days Open'

    def days_open_display(self, obj):
        return self.days_open(obj)

    days_open_display.short_description = 'Days Open'

    actions = ['mark_resolved', 'mark_unresolved']

    def mark_resolved(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(resolved=True, resolution_date=timezone.now().date())
        self.message_user(request, f"Marked {updated} conflicts as resolved")

    mark_resolved.short_description = "Mark selected conflicts as resolved"

    def mark_unresolved(self, request, queryset):
        updated = queryset.update(resolved=False, resolution_date=None)
        self.message_user(request, f"Marked {updated} conflicts as unresolved")

    mark_unresolved.short_description = "Mark selected conflicts as unresolved"


admin.site.register(Slider)
admin.site.register(ExecutiveBoard)
admin.site.register(Campaign)
admin.site.register(ConnectionRequest)
admin.site.register(BoardMembership)
