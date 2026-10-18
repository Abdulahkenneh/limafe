# from django.db import models
# from django.contrib.auth.models import AbstractUser, Group, Permission
# from django.utils.translation import gettext_lazy as _
# from uuid import uuid4
# import uuid
# from django.core.mail import send_mail
# from django.conf import settings
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType



# from django.db import models
# from django.contrib.auth.models import AbstractUser, Group, Permission
# from django.utils.translation import gettext_lazy as _
# from uuid import uuid4
# import uuid
# from django.core.mail import send_mail
# from django.conf import settings
# from django.contrib.contenttypes.fields import GenericForeignKey
# from django.contrib.contenttypes.models import ContentType
# from django.urls import reverse
# from django.utils import timezone




# class CustomUser(AbstractUser):
#     ROLE_CHOICES = (
#         ('admin', 'Admin'),
#         ('member', 'Member'),
#         ('guest', 'Guest'),
#     )

#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     is_two_factor_enabled = models.BooleanField(default=False)
#     phone_number = models.CharField(max_length=15, blank=True, null=True)
#     address = models.TextField(blank=True, null=True)
#     chapter = models.ForeignKey('Chapter', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
#     is_good_standing = models.BooleanField(default=True)
#     profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
#     bio = models.TextField(blank=True, null=True)

#     def digital_id(self):
#         return {
#             "uuid": str(self.uuid),
#             "username": self.username,
#             "full_name": f"{self.first_name} {self.last_name}".strip(),
#             "role": self.role,
#             "chapter": self.chapter.name if self.chapter else None,
#             "positions": [pos.name for pos in self.positions.all()],
#             "phone_number": self.phone_number,
#             "profile_image": self.profile_image.url if self.profile_image else None,
#             "date_joined": self.date_joined.isoformat() if self.date_joined else None
#         }


#     def get_absolute_url(self):
#         return reverse('user-profile', kwargs={'uuid': str(self.uuid)})

#     def __str__(self):
#         return self.username

#     class Meta:
#         verbose_name = 'Registered User'
#         verbose_name_plural = 'Registered Users'


# class Position(models.Model):
#     POSITION_TYPES = (
#         ('executive', 'Executive Committee'),
#         ('board', 'Board of Directors'),
#         ('standing_committee', 'Standing Committee'),
#         ('autonomous_commission', 'Autonomous Commission'),
#     )
#     name = models.CharField(max_length=255)  # e.g., 'President', 'Social Affairs Committee Chair'
#     type = models.CharField(max_length=200, choices=POSITION_TYPES)
#     term_start = models.DateField(blank=True, null=True)
#     term_end = models.DateField(blank=True, null=True)
#     holder = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='positions')
#     committee = models.ForeignKey('Committee', on_delete=models.SET_NULL, null=True, blank=True, related_name='positions')

#     def __str__(self):
#         return f"{self.name} ({self.type})"


# class Chapter(models.Model):

#     name = models.CharField(max_length=255)  # e.g., 'Netherlands Chapter'
#     country = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     logo = models.ImageField(upload_to='profiles/', blank=True, null=True)
#     is_good_standing = models.BooleanField(default=True)  # Financial and moral obligations
#     representatives = models.ManyToManyField(CustomUser, related_name='chapters_leadership', blank=True)  # For Board reps

#     positions = models.ManyToManyField(Position, related_name='chapter_elections')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def get_absolute_url(self):
#         return reverse('chapter_detail', kwargs={'pk': self.pk})

#     def __str__(self):
#         return self.name

# # Positions and Committees


# class Committee(models.Model):

#     COMMITTEE_TYPES = (
#         ('social_affairs', 'Social Affairs'),
#         ('education_public_affairs', 'Education and Public Affairs'),
#         ('finance', 'Finance'),
#         ('Administration', 'Administration'),
#         ('media_communication', 'Media and Communication'),
#         ('election', 'Election Commission'),
#         ('audit', 'Audit Commission'),
#         ('ad_hoc', 'Ad-Hoc'),
#     )

#     name = models.CharField(max_length=255)
#     type = models.CharField(max_length=30, choices=COMMITTEE_TYPES)
#     description = models.TextField()
#     chair = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='chaired_committees')

#     members = models.ManyToManyField(CustomUser, related_name='committees', blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)


#     def __str__(self):
#         return self.name

# from django.db import models

# class Membership(models.Model):
#     SEX_CHOICES = (
#         ('M', 'Male'),
#         ('F', 'Female'),
#     )

#     MARITAL_STATUS_CHOICES = (
#         ('single', 'Single'),
#         ('married', 'Married'),
#         ('divorced', 'Divorced'),
#         ('widowed', 'Widowed'),
#         ('other', 'Other'),
#     )

#     # CRITICAL FIX: Add related_name
#     user = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name='memberships'  # This must match what your view expects!
#     )

#     chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)

#     join_date = models.DateField(auto_now_add=True, blank=True, null=True)

#     dues_paid = models.BooleanField(default=False, blank=True, null=True)
#     dues_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.00,
#         blank=True
#     )
#     payment_date = models.DateField(null=True, blank=True)

#     is_active = models.BooleanField(default=False)

#     # Personal info
#     sex = models.CharField(
#         max_length=1,
#         choices=SEX_CHOICES,
#         null=True,
#         blank=True
#     )

#     # Household info
#     marital_status = models.CharField(
#         max_length=10,
#         choices=MARITAL_STATUS_CHOICES,
#         null=True,
#         blank=True
#     )
#     number_of_children = models.PositiveIntegerField(default=0,null=True, blank=True)
#     number_of_dependents = models.PositiveIntegerField(default=0,null=True, blank=True)

#     household_size = models.PositiveIntegerField(
#         help_text="Total people living in the household",
#         default=1, null=True, blank=True
#     )

#     # FIXED: Correct is_member method
#     def is_member(self):
#         """Return True if membership is active"""
#         return self.is_active

#     def __str__(self):
#         return f"{self.user} - {self.chapter}"

#     class Meta:
#         # Optional: Add ordering
#         ordering = ['-join_date']
#         # Optional: Ensure one active membership per user
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['user'],
#                 condition=models.Q(is_active=True),
#                 name='unique_active_membership'
#             )
#         ]

# # Elections Management
# class Election(models.Model):
#     title = models.CharField(max_length=255)  # e.g., '2025 General Election'
#     start_date = models.DateField(blank=True, null=True)
#     end_date = models.DateField(blank=True, null=True)
#     description = models.TextField()
#     positions = models.ManyToManyField(Position, related_name='elections')
#     commission = models.ForeignKey(Committee, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 'election'})

# class Candidate(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     election = models.ForeignKey(Election, on_delete=models.CASCADE)
#     position = models.ForeignKey(Position, on_delete=models.CASCADE)
#     approved = models.BooleanField(default=False)  # By IEC
#     votes = models.IntegerField(default=0)

# # Dynamic Content Management
# class Page(models.Model):
#     title = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)
#     content = models.TextField()
#     author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     version = models.IntegerField(default=1)  # For content versioning

#     def save(self, *args, **kwargs):
#         if self.pk:
#             self.version += 1
#         super().save(*args, **kwargs)

# class Post(models.Model):
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
#     thumbnail = models.ImageField(upload_to='profiles/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     version = models.IntegerField(default=1)

#     def save(self, *args, **kwargs):
#         if self.pk:
#             self.version += 1
#         super().save(*args, **kwargs)

# class Media(models.Model):
#     file = models.FileField(upload_to='media/')
#     alt_text = models.CharField(max_length=255, blank=True)
#     uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
#     chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

# class Project(models.Model):  # For Programs/Projects with gallery
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     images = models.ManyToManyField(Media, related_name='projects')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

# # Event Management (including Conventions/Meetings)
# class Event(models.Model):
#     EVENT_TYPES = (
#         ('convention', 'Annual General Meeting/Convention'),
#         ('meeting', 'General Meeting'),
#         ('emergency', 'Emergency Meeting'),
#         ('social', 'Social Event'),
#         ('other', 'Other'),
#     )
#     title = models.CharField(max_length=255)
#     type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
#     description = models.TextField()
#     start_time = models.DateTimeField()
#     end_time = models.DateTimeField()
#     location = models.CharField(max_length=255, blank=True)
#     organizer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     quorum_met = models.BooleanField(default=False)  # Track quorum for meetings
#     images = models.ImageField(upload_to='images/',blank=True, null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def send_reminder(self):
#         # Logic for 24h reminder via Celery or similar
#         pass

# class Booking(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     verification_code = models.CharField(max_length=10, default=uuid4().hex[:10])
#     booked_at = models.DateTimeField(auto_now_add=True)
#     is_accredited_delegate = models.BooleanField(default=False)  # For voting rights

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         # Send confirmation email
#         send_mail(
#             'Event Booking Confirmation',
#             f'Your verification code: {self.verification_code}',
#             settings.DEFAULT_FROM_EMAIL,
#             [self.user.email],
#         )

# from django.db.models import Q

# # Donation & Payment (including Dues)
# class Donation(models.Model):
#     DONATION_TYPES = (
#         ('dues', 'Membership Dues'),
#         ('donation', 'General Donation'),
#         ('fundraising', 'Fundraising Event'),
#     )

#     user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     goal_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
#     raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
#     deadline = models.DateField(blank=True, null=True)
#     featured_image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
#     chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
#     type = models.CharField(max_length=20, choices=DONATION_TYPES, default='donation')
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     transaction_id = models.CharField(max_length=255, blank=True)  # From Stripe/PayPal
#     created_at = models.DateTimeField(auto_now_add=True)
#     receipt_sent = models.BooleanField(default=False)



#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         if not self.receipt_sent and self.user:
#             send_mail(
#                 'Donation Receipt',
#                 f'Thank you for your {self.get_type_display()} of {self.amount}!',
#                 settings.DEFAULT_FROM_EMAIL,
#                 [self.user.email],
#             )
#             self.receipt_sent = True
#             super().save(update_fields=['receipt_sent'])



# # Communication & Engagement
# class Message(models.Model):
#     sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
#     receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
#     content = models.TextField()
#     sent_at = models.DateTimeField(auto_now_add=True)
#     read = models.BooleanField(default=False)

# class Newsletter(models.Model):
#     subject = models.CharField(max_length=255)
#     content = models.TextField()
#     sent_at = models.DateTimeField(null=True, blank=True)
#     subscribers = models.ManyToManyField(CustomUser, related_name='newsletters')

# class ContactSubmission(models.Model):
#     name = models.CharField(max_length=255)
#     email = models.EmailField()
#     message = models.TextField()
#     submitted_at = models.DateTimeField(auto_now_add=True)
#     replied = models.BooleanField(default=False)

# # Conflict Resolution (e.g., Ad-Hoc Elder Committee)
# class ConflictResolution(models.Model):
#     description = models.TextField()
#     involved_parties = models.ManyToManyField(CustomUser, related_name='conflicts')
#     committee = models.ForeignKey(Committee, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 'ad_hoc'})
#     resolved = models.BooleanField(default=False)
#     resolution_date = models.DateField(null=True, blank=True)

# # Data & Analytics - Use models for custom tracking if needed

# class Analytic(models.Model):
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#     views = models.IntegerField(default=0)  # Extend for registrations, donations, etc.


# class Campaign(models.Model):
#     title = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True)
#     description = models.TextField()
#     goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
#     raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
#     deadline = models.DateField()
#     featured_image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
#     is_active = models.BooleanField(default=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title



# class Slider(models.Model):
#     title = models.CharField(max_length=255)
#     sub_title = models.CharField(max_length=255, blank=True, null=True)
#     title_highlight = models.CharField(max_length=100, blank=True, null=True)  # the <span> part
#     title_suffix = models.CharField(max_length=255, blank=True, null=True)
#     description = models.TextField()
#     image = models.ImageField(upload_to='sliders/')
#     order = models.IntegerField(default=0)
#     is_active = models.BooleanField(default=True)

#     class Meta:
#         ordering = ['order']
#         verbose_name = 'Hero Slider'
#         verbose_name_plural = 'Hero Sliders'

#     def __str__(self):
#         return self.title


# # models.py - Add this model
# from django.db import models
# from django.utils import timezone


# class ConnectionRequest(models.Model):
#     STATUS_CHOICES = (
#         ('pending', 'Pending'),
#         ('accepted', 'Accepted'),
#         ('rejected', 'Rejected'),
#         ('blocked', 'Blocked'),
#     )

#     sender = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name='sent_connection_requests'
#     )
#     receiver = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name='received_connection_requests'
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=STATUS_CHOICES,
#         default='pending'
#     )
#     message = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ['sender', 'receiver']
#         ordering = ['-created_at']
#         verbose_name = 'Connection Request'
#         verbose_name_plural = 'Connection Requests'

#     def __str__(self):
#         return f"{self.sender} → {self.receiver} ({self.status})"

#     def save(self, *args, **kwargs):
#         # Prevent users from connecting with themselves
#         if self.sender == self.receiver:
#             raise ValueError("Cannot send connection request to yourself.")
#         super().save(*args, **kwargs)

#     def accept(self):
#         """Accept the connection request"""
#         self.status = 'accepted'
#         self.save()

#         # Create a bidirectional connection
#         Connection.objects.get_or_create(
#             user1=self.sender,
#             user2=self.receiver,
#             defaults={'connection_type': 'mutual'}
#         )

#     def reject(self):
#         """Reject the connection request"""
#         self.status = 'rejected'
#         self.save()

#     def block(self):
#         """Block the connection request"""
#         self.status = 'blocked'
#         self.save()

#     def is_pending(self):
#         return self.status == 'pending'

#     def is_accepted(self):
#         return self.status == 'accepted'


# class Connection(models.Model):
#     """Represents an established mutual connection between two users"""
#     CONNECTION_TYPES = (
#         ('mutual', 'Mutual Connection'),
#         ('professional', 'Professional'),
#         ('friend', 'Friend'),
#         ('colleague', 'Colleague'),
#     )

#     user1 = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name='connections_user1'
#     )
#     user2 = models.ForeignKey(
#         CustomUser,
#         on_delete=models.CASCADE,
#         related_name='connections_user2'
#     )
#     connection_type = models.CharField(
#         max_length=20,
#         choices=CONNECTION_TYPES,
#         default='mutual'
#     )
#     created_at = models.DateTimeField(default=timezone.now)
#     notes = models.TextField(blank=True, null=True)

#     class Meta:
#         unique_together = ['user1', 'user2']
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"{self.user1} ↔ {self.user2}"

#     def save(self, *args, **kwargs):
#         # Ensure user1 ID is always less than user2 ID to prevent duplicates
#         if self.user1_id > self.user2_id:
#             self.user1, self.user2 = self.user2, self.user1
#         super().save(*args, **kwargs)

#     def other_user(self, current_user):
#         """Get the other user in the connection"""
#         if current_user == self.user1:
#             return self.user2
#         return self.user1












from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_two_factor_enabled = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    chapter = models.ForeignKey('Chapter', on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    is_good_standing = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def digital_id(self):
        return {
            "uuid": str(self.uuid),
            "username": self.username,
            "full_name": f"{self.first_name} {self.last_name}".strip(),
            "role": self.role,
            "chapter": self.chapter.name if self.chapter else None,
            "positions": [pos.name for pos in self.positions.all()],
            "phone_number": self.phone_number,
            "profile_image": self.profile_image.url if self.profile_image else None,
            "date_joined": self.date_joined.isoformat() if self.date_joined else None
        }

    def get_absolute_url(self):
        return reverse('user-profile', kwargs={'uuid': str(self.uuid)})

    def get_current_chapter_position(self):
        """Get the user's current position within their chapter"""
        return self.positions.filter(level='chapter',
                                      term_end__gte=timezone.now().date()).first()

    def get_current_executive_position(self):
        """Get the user's current executive board position"""
        return self.positions.filter(level='international',
                                      term_end__gte=timezone.now().date()).first()

    def is_chapter_leader(self):
        """Check if user holds any leadership position in their chapter"""
        return self.positions.filter(level='chapter').exists()

    def is_executive_board_member(self):
        """Check if user is on the executive board"""
        return self.positions.filter(level='international').exists()

    def serves_on_both_levels(self):
        """Check if user serves on both chapter and executive levels"""
        return self.is_chapter_leader() and self.is_executive_board_member()

    def get_executive_board_membership(self):
        """Get the user's current executive board membership details"""
        return self.board_memberships.filter(is_active=True).first()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Registered User'
        verbose_name_plural = 'Registered Users'


class ExecutiveBoard(models.Model):
    """Higher leadership structure that oversees all chapters"""
    name = models.CharField(max_length=255, default="International Executive Board")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Track the election/formation date
    formed_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_current_members(self):
        """Get all current executive board members with their positions"""
        return self.board_members.filter(
            models.Q(term_end__isnull=True) | models.Q(term_end__gte=timezone.now().date()),
            is_active=True
        )

    def add_chapter_representative(self, user, chapter, board_position, chapter_position=None):
        """Add a chapter leader as a representative to the executive board"""
        if chapter_position and not user.positions.filter(pk=chapter_position.pk).exists():
            raise ValueError(f"{user} does not hold the position {chapter_position} in their chapter")

        return BoardMembership.objects.create(
            user=user,
            executive_board=self,
            chapter=chapter,
            board_position=board_position,
            chapter_position=chapter_position,
            represents_chapter=True
        )

    def get_chapter_representatives(self):
        """Get all chapter representatives on the executive board"""
        return self.board_members.filter(represents_chapter=True, is_active=True)

    def get_leadership_hierarchy(self):
        """Get the complete leadership hierarchy"""
        hierarchy = {
            'executive_board': {
                'president': self.positions.filter(name__iexact='President').first(),
                'vice_president': self.positions.filter(name__iexact='Vice President').first(),
                'secretary': self.positions.filter(name__iexact='Secretary').first(),
                'treasurer': self.positions.filter(name__iexact='Treasurer').first(),
                'other_positions': self.positions.exclude(
                    name__in=['President', 'Vice President', 'Secretary', 'Treasurer']
                ),
                'chapter_representatives': self.get_chapter_representatives()
            },
            'chapters': Chapter.objects.all()
        }
        return hierarchy

    class Meta:
        verbose_name = "Executive Board"
        verbose_name_plural = "Executive Boards"


class Position(models.Model):
    POSITION_TYPES = (
        ('executive', 'Executive Committee'),
        ('board', 'Board of Directors'),
        ('standing_committee', 'Standing Committee'),
        ('autonomous_commission', 'Autonomous Commission'),
    )

    POSITION_LEVELS = (
        ('chapter', 'Chapter Level'),
        ('national', 'National Level'),
        ('international', 'International/Executive Board Level'),
    )

    name = models.CharField(max_length=255)  # e.g., 'President', 'Social Affairs Committee Chair'
    type = models.CharField(max_length=200, choices=POSITION_TYPES)
    level = models.CharField(max_length=20, choices=POSITION_LEVELS, default='chapter')
    term_start = models.DateField(blank=True, null=True)
    term_end = models.DateField(blank=True, null=True)
    holder = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='positions')
    committee = models.ForeignKey('Committee', on_delete=models.SET_NULL, null=True, blank=True, related_name='positions')

    # For executive board positions
    executive_board = models.ForeignKey(ExecutiveBoard, on_delete=models.SET_NULL, null=True, blank=True, related_name='positions')

    # To track if this position automatically includes executive board membership
    includes_executive_membership = models.BooleanField(default=False)

    # Order/precedence (e.g., President has higher precedence than Secretary)
    precedence_order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.get_level_display()})"


class Chapter(models.Model):
    name = models.CharField(max_length=255)  # e.g., 'Netherlands Chapter'
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_good_standing = models.BooleanField(default=True)  # Financial and moral obligations
    representatives = models.ManyToManyField(CustomUser, related_name='chapters_leadership', blank=True)  # For Board reps
    positions = models.ManyToManyField(Position, related_name='chapter_elections')
    created_at = models.DateTimeField(auto_now_add=True)

    # New fields for leadership structure
    executive_board_representative = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='represented_chapter'
    )

    # Track which executive board this chapter reports to
    parent_executive_board = models.ForeignKey(
        ExecutiveBoard,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='member_chapters'
    )

    def get_chapter_leadership(self):
        """Get all leadership positions within this chapter"""
        return self.positions.filter(level='chapter')

    def get_representatives_on_executive_board(self):
        """Get chapter members who also serve on executive board"""
        return self.members.filter(positions__level='international')

    def get_absolute_url(self):
        return reverse('chapter_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name


class BoardMembership(models.Model):
    """Tracks when a chapter leader also serves on the executive board"""
    MEMBERSHIP_ROLES = (
        ('voting_member', 'Voting Member'),
        ('ex_officio', 'Ex-Officio Member'),
        ('observer', 'Observer'),
        ('advisor', 'Advisor'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='board_memberships')
    executive_board = models.ForeignKey(ExecutiveBoard, on_delete=models.CASCADE, related_name='board_members')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='board_representatives', null=True, blank=True)

    # The position this person holds on the executive board
    board_position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='board_memberships')

    # The chapter position they hold (if any)
    chapter_position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='executive_representations')

    role_type = models.CharField(max_length=20, choices=MEMBERSHIP_ROLES, default='voting_member')

    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Track if they represent their chapter on the board
    represents_chapter = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Board Membership"
        verbose_name_plural = "Board Memberships"
        unique_together = ['user', 'executive_board', 'start_date']  # One active membership per board

    def __str__(self):
        chapter_repr = f" (representing {self.chapter.name})" if self.represents_chapter and self.chapter else ""
        return f"{self.user.username} - {self.executive_board.name}{chapter_repr}"

    def is_current(self):
        """Check if this membership is currently active"""
        if not self.is_active:
            return False
        if self.end_date and self.end_date < timezone.now().date():
            return False
        return True


class Committee(models.Model):
    COMMITTEE_TYPES = (
        ('social_affairs', 'Social Affairs'),
        ('education_public_affairs', 'Education and Public Affairs'),
        ('finance', 'Finance'),
        ('Administration', 'Administration'),
        ('media_communication', 'Media and Communication'),
        ('election', 'Election Commission'),
        ('audit', 'Audit Commission'),
        ('ad_hoc', 'Ad-Hoc'),
    )

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=COMMITTEE_TYPES)
    description = models.TextField()
    chair = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='chaired_committees')
    members = models.ManyToManyField(CustomUser, related_name='committees', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    MARITAL_STATUS_CHOICES = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('other', 'Other'),
    )

    # CRITICAL FIX: Add related_name
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='memberships'  # This must match what your view expects!
    )

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    join_date = models.DateField(auto_now_add=True, blank=True, null=True)
    dues_paid = models.BooleanField(default=False, blank=True, null=True)
    dues_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        blank=True
    )
    payment_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    # Personal info
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
        null=True,
        blank=True
    )

    # Household info
    marital_status = models.CharField(
        max_length=10,
        choices=MARITAL_STATUS_CHOICES,
        null=True,
        blank=True
    )
    number_of_children = models.PositiveIntegerField(default=0,null=True, blank=True)
    number_of_dependents = models.PositiveIntegerField(default=0,null=True, blank=True)

    household_size = models.PositiveIntegerField(
        help_text="Total people living in the household",
        default=1, null=True, blank=True
    )

    # FIXED: Correct is_member method
    def is_member(self):
        """Return True if membership is active"""
        return self.is_active

    def __str__(self):
        return f"{self.user} - {self.chapter}"

    class Meta:
        # Optional: Add ordering
        ordering = ['-join_date']
        # Optional: Ensure one active membership per user
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_active=True),
                name='unique_active_membership'
            )
        ]


# Elections Management
class Election(models.Model):
    title = models.CharField(max_length=255)  # e.g., '2025 General Election'
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField()
    positions = models.ManyToManyField(Position, related_name='elections')
    commission = models.ForeignKey(Committee, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 'election'})


class Candidate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)  # By IEC
    votes = models.IntegerField(default=0)


# Dynamic Content Management
class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)  # For content versioning

    def save(self, *args, **kwargs):
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    thumbnail = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.pk:
            self.version += 1
        super().save(*args, **kwargs)


class Media(models.Model):
    file = models.FileField(upload_to='media/')
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Project(models.Model):  # For Programs/Projects with gallery
    title = models.CharField(max_length=255)
    description = models.TextField()
    images = models.ManyToManyField(Media, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Event Management (including Conventions/Meetings)
class Event(models.Model):
    EVENT_TYPES = (
        ('convention', 'Annual General Meeting/Convention'),
        ('meeting', 'General Meeting'),
        ('emergency', 'Emergency Meeting'),
        ('social', 'Social Event'),
        ('other', 'Other'),
    )
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    organizer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    quorum_met = models.BooleanField(default=False)  # Track quorum for meetings
    images = models.ImageField(upload_to='images/',blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)

    def send_reminder(self):
        # Logic for 24h reminder via Celery or similar
        pass


class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=10, default=uuid4().hex[:10])
    booked_at = models.DateTimeField(auto_now_add=True)
    is_accredited_delegate = models.BooleanField(default=False)  # For voting rights

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Send confirmation email
        send_mail(
            'Event Booking Confirmation',
            f'Your verification code: {self.verification_code}',
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
        )


# Donation & Payment (including Dues)
class Donation(models.Model):
    DONATION_TYPES = (
        ('dues', 'Membership Dues'),
        ('donation', 'General Donation'),
        ('fundraising', 'Fundraising Event'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deadline = models.DateField(blank=True, null=True)
    featured_image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=20, choices=DONATION_TYPES, default='donation')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, blank=True)  # From Stripe/PayPal
    created_at = models.DateTimeField(auto_now_add=True)
    receipt_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.receipt_sent and self.user:
            send_mail(
                'Donation Receipt',
                f'Thank you for your {self.get_type_display()} of {self.amount}!',
                settings.DEFAULT_FROM_EMAIL,
                [self.user.email],
            )
            self.receipt_sent = True
            super().save(update_fields=['receipt_sent'])


# Communication & Engagement
class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)


class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(null=True, blank=True)
    subscribers = models.ManyToManyField(CustomUser, related_name='newsletters')


class ContactSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)


# Conflict Resolution (e.g., Ad-Hoc Elder Committee)
class ConflictResolution(models.Model):
    description = models.TextField()
    involved_parties = models.ManyToManyField(CustomUser, related_name='conflicts')
    committee = models.ForeignKey(Committee, on_delete=models.SET_NULL, null=True, limit_choices_to={'type': 'ad_hoc'})
    resolved = models.BooleanField(default=False)
    resolution_date = models.DateField(null=True, blank=True)


# Data & Analytics - Use models for custom tracking if needed
class Analytic(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    views = models.IntegerField(default=0)  # Extend for registrations, donations, etc.


class Campaign(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    goal_amount = models.DecimalField(max_digits=12, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deadline = models.DateField()
    featured_image = models.ImageField(upload_to='campaigns/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Slider(models.Model):
    title = models.CharField(max_length=255)
    sub_title = models.CharField(max_length=255, blank=True, null=True)
    title_highlight = models.CharField(max_length=100, blank=True, null=True)  # the <span> part
    title_suffix = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='sliders/')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Hero Slider'
        verbose_name_plural = 'Hero Sliders'

    def __str__(self):
        return self.title


class ConnectionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('blocked', 'Blocked'),
    )

    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sent_connection_requests'
    )
    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='received_connection_requests'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['sender', 'receiver']
        ordering = ['-created_at']
        verbose_name = 'Connection Request'
        verbose_name_plural = 'Connection Requests'

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.status})"

    def save(self, *args, **kwargs):
        # Prevent users from connecting with themselves
        if self.sender == self.receiver:
            raise ValueError("Cannot send connection request to yourself.")
        super().save(*args, **kwargs)

    def accept(self):
        """Accept the connection request"""
        self.status = 'accepted'
        self.save()

        # Create a bidirectional connection
        Connection.objects.get_or_create(
            user1=self.sender,
            user2=self.receiver,
            defaults={'connection_type': 'mutual'}
        )

    def reject(self):
        """Reject the connection request"""
        self.status = 'rejected'
        self.save()

    def block(self):
        """Block the connection request"""
        self.status = 'blocked'
        self.save()

    def is_pending(self):
        return self.status == 'pending'

    def is_accepted(self):
        return self.status == 'accepted'


class Connection(models.Model):
    """Represents an established mutual connection between two users"""
    CONNECTION_TYPES = (
        ('mutual', 'Mutual Connection'),
        ('professional', 'Professional'),
        ('friend', 'Friend'),
        ('colleague', 'Colleague'),
    )

    user1 = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='connections_user1'
    )
    user2 = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='connections_user2'
    )
    connection_type = models.CharField(
        max_length=20,
        choices=CONNECTION_TYPES,
        default='mutual'
    )
    created_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['user1', 'user2']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user1} ↔ {self.user2}"

    def save(self, *args, **kwargs):
        # Ensure user1 ID is always less than user2 ID to prevent duplicates
        if self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)

    def other_user(self, current_user):
        """Get the other user in the connection"""
        if current_user == self.user1:
            return self.user2
        return self.user1







