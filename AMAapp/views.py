
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DetailView, ListView, TemplateView, DeleteView
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
import csv
import stripe
from .models import *
from .forms import *
from django.conf import settings
from django.db import models
from django.utils import timezone
# Assume all forms and models are in forms.py and models.py
from .forms import SignupForm, LoginForm, UserUpdateForm, PasswordRecoveryForm, PageForm, PostForm, ProjectForm, MediaUploadForm, EventForm, BookingForm, DonationForm, MessageForm, NewsletterForm, ContactForm
from .models import CustomUser,ExecutiveBoard,BoardMembership, Page, Post, Project, Media, Event, Booking, Donation, Message, Newsletter, ContactSubmission, Analytic

stripe.api_key = settings.STRIPE_SECRET_KEY

# views.py (or wherever your views are defined)
from django.views.generic import TemplateView
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import (
    Post,
    Donation,
    Project,
    Event,
    Page,
    Chapter,
    CustomUser,
    Position,
    Media,
    Membership,
)

from collections import OrderedDict
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Core dynamic sections from your updated template
        context['campaigns'] = Campaign.objects.filter(is_active=True).order_by('-created_at')[:6]

        context['upcoming_events'] = Event.objects.filter(
            start_time__gte=timezone.now()
        ).order_by('start_time')[:6]

        context['latest_posts'] = Post.objects.select_related('author').order_by('-created_at')[:3]

        positions = Position.objects.filter(
            type='executive'
        ).select_related('holder', 'committee').order_by('holder_id', 'name')

        # Remove duplicates by holder
        unique_by_holder = OrderedDict()
        for position in positions:
            if position.holder and position.holder.id not in unique_by_holder:
                unique_by_holder[position.holder.id] = position

        context['leadership_positions'] = list(unique_by_holder.values())


        context['gallery_medias'] = Media.objects.order_by('-created_at')[:9]

        context['about_page'] = Page.objects.filter(slug='about-us').first()

        # Counters - fully dynamic & accurately based on your actual models
        context['project_count'] = Project.objects.count()
        context['chapter_count'] = Chapter.objects.filter(is_good_standing=True).count()
        context['member_count'] = Membership.objects.count()  # Most accurate - counts actual memberships
        context['volunteer_count'] = Membership.objects.filter(
            dues_paid=True).count()  # or use member_count if you prefer

        # Optional but recommended additions (highly useful)
        context['featured_projects'] = Project.objects.order_by('-created_at')[
                                       :3]  # if you want to show featured projects elsewhere
        context['recent_posts_all'] = Post.objects.select_related('author').order_by('-created_at')[
                                      :6]  # fallback if needed

        # Optional: Hero Slider (recommended model addition below - totally worth it)
        # context['hero_sliders'] = Slider.objects.all().order_by('order')
        context['hero_sliders'] = Slider.objects.filter(is_active=True).order_by('order')

        return context

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role == 'admin'

# Accounts views
class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'signup.html'
    success_url = '/accounts/profile/'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)

        return response

class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'login.html'


class UserProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "profile.html"
    context_object_name = "profile_user"

    def get_object(self):
        return get_object_or_404(CustomUser, uuid=self.kwargs.get("uuid"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["membership"] = (
            Membership.objects
            .filter(user=self.object)
            .order_by("-id")
            .first()
        )

        return context



# class MyProfileView(LoginRequiredMixin, DetailView):
#     model = CustomUser
#     template_name = "profile.html"
#     context_object_name = "profile_user"

#     def get_object(self):
#         return self.request.user

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["memberships"] = Membership.objects.filter(
#             user=self.object
#         )
#         return context


class MyProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "profile.html"
    context_object_name = "profile_user"

    def get_object(self):
        # Check if UUID is provided in URL
        user_uuid = self.kwargs.get('uuid')
        if user_uuid:
            try:
                return CustomUser.objects.get(uuid=user_uuid)
            except CustomUser.DoesNotExist:
                raise Http404("User does not exist")
        # If no UUID, return current user
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object  # The user whose profile is being viewed
        current_user = self.request.user  # The logged-in user

        # Get all memberships for the PROFILE user
        # Use direct filter to avoid related_name issues
        memberships = Membership.objects.filter(user=profile_user)

        # Get active memberships
        active_memberships = memberships.filter(is_active=True)

        # Determine statuses
        has_active = active_memberships.exists()
        has_any = memberships.exists()

        is_active_member = has_active
        is_pending_member = has_any and not has_active  # Has memberships but none active
        is_non_member = not has_any  # No memberships at all

        # Get the latest membership if exists
        latest_membership = memberships.order_by('-id').first()

        # Check if current user is viewing their own profile
        is_own_profile = (current_user == profile_user)

        context.update({
            "memberships": memberships,
            "is_active_member": is_active_member,
            "is_pending_member": is_pending_member,
            "is_non_member": is_non_member,
            "latest_membership": latest_membership,
            "is_own_profile": is_own_profile,
            "current_user": current_user,
        })
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = UserUpdateForm
    template_name = 'user_update.html'
    success_url = '/accounts/profile/'

    def get_object(self):
        return self.request.user

class PasswordRecoveryView(PasswordResetView):
    form_class = PasswordRecoveryForm
    template_name = 'password_reset.html'

def logout_view(request):
    logout(request)
    return redirect('/')

# Content views
class PageListView(ListView):
    model = Page
    template_name = 'page_list.html'

class PageDetailView(DetailView):
    model = Page
    template_name = 'page_detail.html'

class PageCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = 'page_form.html'
    success_url = '/content/pages/'

class PageUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Page
    form_class = PageForm
    template_name = 'page_form.html'
    success_url = '/content/pages/'

class PageDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Page
    success_url = '/content/pages/'

class PostListView(ListView):
    model = Post
    template_name = 'post_list.html'


from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth


class PostDetailView(DetailView):
    model = Post
    template_name = 'post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # Get recent posts (excluding current post)
        context['recent_posts'] = Post.objects.exclude(
            pk=post.pk
        ).order_by('-created_at')[:5]

        # Get archive months with post counts
        archive = Post.objects.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            post_count=Count('pk')
        ).order_by('-month')

        context['archive_months'] = [
            {
                'year': item['month'].year,
                'month': item['month'].month,
                'post_count': item['post_count']
            }
            for item in archive[:12]  # Last 12 months
        ]

        return context

class PostCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = '/content/posts/'

class PostUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_form.html'
    success_url = '/content/posts/'

class PostDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'  # Add this line
    success_url = '/content/posts/'

class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'

class ProjectCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
    success_url = '/content/projects/'

class ProjectUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'project_form.html'
    success_url = '/content/projects/'

class ProjectDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Project
    success_url = '/content/projects/'

class MediaUploadView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Media
    form_class = MediaUploadForm
    template_name = 'media_form.html'
    success_url = '/content/media/'

# Events views (added as missing)
class EventListView(ListView):
    model = Event
    template_name = 'event_list.html'

class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'

class EventCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    success_url = '/events/'

class EventUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'event_form.html'
    success_url = '/events/'

class EventDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Event
    template_name=   'event_confirm_delete.html'
    success_url = '/events/'

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.event = Event.objects.get(pk=self.kwargs['event_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return f'/events/{self.kwargs["event_id"]}/'

class EventReportView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = Event
    def get(self, request, *args, **kwargs):
        event = self.get_object()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{event.title}_attendees.csv"'
        writer = csv.writer(response)
        writer.writerow(['User', 'Booked At'])
        for booking in event.booking_set.all():
            writer.writerow([booking.user.username, booking.booked_at])
        return response

# Donations views
class DonationListView(LoginRequiredMixin, ListView):
    model = Donation
    template_name = 'donation_list.html'

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Donation.objects.all()
        return Donation.objects.filter(user=self.request.user)

class DonationCreateView(CreateView):
    model = Donation
    form_class = DonationForm
    template_name = 'donation_form.html'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
        try:
            token = self.request.POST['stripeToken']
            charge = stripe.Charge.create(
                amount=int(form.instance.amount * 100),
                currency='eur',
                description='Donation to AMA',
                source=token,
            )
            form.instance.transaction_id = charge.id
        except stripe.error.StripeError:
            return render(self.request, self.template_name, {'form': form, 'error': 'Payment failed'})
        return super().form_valid(form)

    def get_success_url(self):
        return '/donations/'

# Communications views
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'message_list.html'

    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user) | Message.objects.filter(sender=self.request.user)

class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'message_form.html'
    success_url = '/communications/messages/'

    def form_valid(self, form):
        form.instance.sender = self.request.user
        return super().form_valid(form)

class NewsletterCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'newsletter_form.html'
    success_url = '/communications/newsletters/'

class ContactView(CreateView):
    model = ContactSubmission
    form_class = ContactForm
    template_name = 'contact.html'
    success_url = '/'

# Analytics views
class AnalyticsDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_visits'] = Analytic.objects.aggregate(models.Sum('views'))['views__sum'] or 0
        context['total_registrations'] = CustomUser.objects.count()
        context['total_donations'] = Donation.objects.aggregate(models.Sum('amount'))['amount__sum'] or 0
        context['total_events'] = Event.objects.count()
        context['total_bookings'] = Booking.objects.count()
        return context



from django.views.generic import ListView, DetailView
from django.db.models import Count, Prefetch, Q
from .models import Chapter, CustomUser, Membership, Committee, Position


# class ChapterListView(ListView):
#     model = Chapter
#     template_name = 'chapter_list.html'
#     context_object_name = 'chapters'

#     def get_queryset(self):
#         # Prefetch members and optimize queries
#         return Chapter.objects.annotate(
#             member_count=Count('members')
#         ).select_related(
#             # Add any related fields if needed
#         ).prefetch_related(
#             Prefetch('members', queryset=CustomUser.objects.select_related(
#                 'membership_set'
#             ).prefetch_related(
#                 'positions',
#                 'committees'
#             ))
#         ).order_by('name')




class ChapterListView(ListView):
    model = Chapter
    template_name = 'chapter_list.html'
    context_object_name = 'chapters'
    paginate_by = 12

    def get_queryset(self):
        # Get all chapters with optimized queries
        chapters = Chapter.objects.annotate(
            total_members=Count('members', distinct=True),
            # Use 'membership' (singular) instead of 'memberships'
            active_members=Count('membership',
                filter=Q(membership__is_active=True),
                distinct=True
            ),
            leader_count=Count('representatives', distinct=True)
        ).prefetch_related(
            # Prefetch members
            Prefetch('members', queryset=CustomUser.objects.only(
                'id', 'first_name', 'last_name', 'profile_image'
            )),
            Prefetch('representatives', queryset=CustomUser.objects.only(
                'id', 'first_name', 'last_name', 'profile_image'
            ))
        ).order_by('name')

        return chapters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get some statistics for the page
        context['total_chapters'] = Chapter.objects.count()

        # Count active members across all chapters
        context['total_members_across_chapters'] = Membership.objects.filter(
            is_active=True
        ).values('user').distinct().count()

        # Get featured chapters (most active members)
        context['featured_chapters'] = Chapter.objects.annotate(
            active_member_count=Count('membership', filter=Q(membership__is_active=True))
        ).order_by('-active_member_count')[:3]

        return context

# class ChapterDetailView(DetailView):
#     model = Chapter
#     template_name = 'chapter_detail.html'
#     context_object_name = 'chapter'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         chapter = self.object

#         # Get all active memberships for this chapter with user data
#         active_memberships = Membership.objects.filter(
#             chapter=chapter,
#             is_active=True
#         ).select_related('user')

#         # Get user IDs from active memberships
#         user_ids = [m.user.id for m in active_memberships]

#         # Get users with prefetched positions and committees
#         users_with_prefetch = CustomUser.objects.filter(
#             id__in=user_ids
#         ).prefetch_related(
#             Prefetch('positions', queryset=Position.objects.all()),
#             Prefetch('committees', queryset=Committee.objects.all())
#         )

#         # Create a dictionary for quick user lookup
#         users_dict = {user.id: user for user in users_with_prefetch}

#         # Get representatives for this chapter
#         representatives = chapter.representatives.all()

#         # Process memberships
#         leaders = []
#         regular_members = []

#         for membership in active_memberships:
#             user = users_dict.get(membership.user.id, membership.user)

#             # Check if user is a representative
#             is_leader = user in representatives

#             member_data = {
#                 'user': user,
#                 'membership': membership,
#                 'is_leader': is_leader
#             }

#             if is_leader:
#                 leaders.append(member_data)
#             else:
#                 regular_members.append(member_data)

#         # Get counts
#         total_member_count = chapter.members.count()
#         active_member_count = len(leaders) + len(regular_members)
#         leader_count = len(leaders)

#         # Get chapter established year
#         established_year = chapter.created_at.year if chapter.created_at else None

#         context.update({
#             'chapter': chapter,
#             'leaders': leaders,
#             'regular_members': regular_members,
#             'active_member_count': active_member_count,
#             'total_member_count': total_member_count,
#             'leader_count': leader_count,
#             'established_year': established_year,
#         })

#         return context




from django.db.models import Prefetch

# class ChapterDetailView(DetailView):
#     model = Chapter
#     template_name = 'chapter_detail.html'
#     context_object_name = 'chapter'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         chapter = self.object

#         # Get all active memberships for this chapter
#         active_memberships = Membership.objects.filter(
#             chapter=chapter,
#             is_active=True
#         ).select_related('user')

#         # Get user IDs from active memberships
#         user_ids = [m.user.id for m in active_memberships]

#         # Prefetch positions and committees
#         users_with_prefetch = CustomUser.objects.filter(
#             id__in=user_ids
#         ).prefetch_related(
#             Prefetch('positions', queryset=Position.objects.all()),
#             Prefetch('committees', queryset=Committee.objects.all())
#         )

#         # Map users by ID for quick access
#         users_dict = {user.id: user for user in users_with_prefetch}

#         # Get chapter representatives
#         representatives = chapter.representatives.all()

#         leaders = []
#         regular_members = []

#         for membership in active_memberships:
#             user = users_dict.get(membership.user.id, membership.user)

#             # Determine first position (if any)
#             first_position = user.positions.first()  # returns None if no positions

#             is_leader = user in representatives

#             member_data = {
#                 'user': user,
#                 'membership': membership,
#                 'is_leader': is_leader,
#                 'first_position': first_position
#             }

#             if is_leader:
#                 leaders.append(member_data)
#             else:
#                 regular_members.append(member_data)

#         context.update({
#             'chapter': chapter,
#             'leaders': leaders,
#             'regular_members': regular_members,
#             'active_member_count': len(leaders) + len(regular_members),
#             'total_member_count': chapter.members.count(),
#             'leader_count': len(leaders),
#             'established_year': chapter.created_at.year if chapter.created_at else None,
#         })

#         return context
from django.db.models import Prefetch

class ChapterDetailView(DetailView):
    model = Chapter
    template_name = 'chapter_detail.html'
    context_object_name = 'chapter'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object

        # Get all active memberships for this chapter
        active_memberships = Membership.objects.filter(
            chapter=chapter,
            is_active=True
        ).select_related('user')

        # Get user IDs
        user_ids = [m.user.id for m in active_memberships]

        # Fetch users
        users_with_prefetch = CustomUser.objects.filter(
            id__in=user_ids
        ).prefetch_related(
            Prefetch(
                'positions',
                queryset=Position.objects.filter(chapter_elections=chapter),
                to_attr='chapter_positions'
            )
        )

        # Map users by ID
        users_dict = {user.id: user for user in users_with_prefetch}

        # Get chapter representatives
        representatives = chapter.representatives.all()

        leaders = []
        regular_members = []

        for membership in active_memberships:
            user = users_dict.get(membership.user.id, membership.user)

            # Filter positions to only those held by this user
            user_positions = [pos for pos in getattr(user, 'chapter_positions', []) if pos.holder_id == user.id]
            first_position = user_positions[0] if user_positions else None

            is_leader = user in representatives

            member_data = {
                'user': user,
                'membership': membership,
                'is_leader': is_leader,
                'first_position': first_position
            }

            if is_leader:
                leaders.append(member_data)
            else:
                regular_members.append(member_data)

        context.update({
            'chapter': chapter,
            'leaders': leaders,
            'regular_members': regular_members,
            'active_member_count': len(leaders) + len(regular_members),
            'total_member_count': chapter.members.count(),
            'leader_count': len(leaders),
            'established_year': chapter.created_at.year if chapter.created_at else None,
        })

        return context
class ChapterCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Chapter
    fields = '__all__'
    template_name = 'chapter_form.html'
    success_url = '/chapters/'


class ChapterUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Chapter
    fields = '__all__'
    template_name = 'chapter_form.html'
    success_url = '/chapters/'


class ChapterDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Chapter
    template_name = 'chapter_confirm_delete.html'
    success_url = '/chapters/'


class CommitteeListView(ListView):
    model = Committee
    template_name = 'committee_list.html'


class CommitteeDetailView(DetailView):
    model = Committee
    template_name = 'committee_detail.html'


class CommitteeCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Committee
    fields = '__all__'
    template_name = 'committee_form.html'
    success_url = '/committees/'


class CommitteeUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Committee
    fields = '__all__'
    template_name = 'committee_form.html'
    success_url = '/committees/'


class CommitteeDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Committee
    template_name = 'committee_confirm_delete.html'
    success_url = '/committees/'


class PositionListView(ListView):
    model = Position
    template_name = 'position_list.html'


class PositionDetailView(DetailView):
    model = Position
    template_name = 'position_detail.html'


class PositionCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Position
    fields = '__all__'
    template_name = 'position_form.html'
    success_url = '/positions/'


class PositionUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Position
    fields = '__all__'
    template_name = 'position_form.html'
    success_url = '/positions/'


class PositionDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Position
    template_name = 'position_confirm_delete.html'
    success_url = '/positions/'



class MembershipListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Membership
    template_name = 'membership_list.html'


from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Membership, Chapter, CustomUser, Position


# class TeamListView(ListView):
#     model = Membership
#     template_name = 'team_list.html'
#     context_object_name = 'all_members'
#
#     def get_queryset(self):
#         return  Membership.objects.select_related('user', 'chapter').filter(is_active=True)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Get all chapters
#         chapters = Chapter.objects.all()
#         executive_commitees = Committee.objects.filter(name='Executive commitee')
#         board_of_directors = Committee.objects.filter(name='Board of Directors')
#         context['chapters'] = chapters
#         context['executive_commitees'] = executive_commitees
#         context['board_of_directors'] = board_of_directors
#
#
#         # Separate leaders and regular members
#         all_memberships = context['all_members']
#         leaders = []
#         regular_members = []
#
#         for membership in all_memberships:
#             user = membership.user
#
#             # Check if user is a leader (admin, has positions, or is chapter representative)
#             if (user.role == 'admin' or
#                     user.positions.exists() or
#                     user.chapters_leadership.exists()):
#                 leaders.append(membership)
#             else:
#                 regular_members.append(membership)
#
#         context['leaders'] = leaders
#         context['regular_members'] = regular_members
#
#         # Get members without chapters
#         context['no_chapter_members'] = Membership.objects.filter(chapter__isnull=True,is_active=True)
#
#         return context


from django.views.generic import ListView
from .models import Membership, Chapter, Committee, CustomUser


from django.views.generic import ListView
from .models import Membership, Chapter, Committee, CustomUser

from django.views.generic import ListView
from django.db.models import Q
from .models import Membership, Committee, Chapter, CustomUser

class TeamListView(ListView):
    model = Membership
    template_name = 'team_list.html'
    context_object_name = 'all_members'

    def get_queryset(self):
        return (
            Membership.objects
            .select_related('user', 'chapter')
            .filter(is_active=True)
            .order_by('user__first_name', 'user__last_name')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get committees - find by name
        executive_committee = Committee.objects.filter(
            Q(name__iexact='Executive Committee')
        ).first()

        board_of_directors = Committee.objects.filter(
            Q(name__iexact='Board of Directors') |
            Q(name__iexact='Board') |
            Q(type='board')
        ).first()

        # Get all chapters
        context['chapters'] = Chapter.objects.all()

        # Store committees as single objects (not querysets)
        context['executive_committee'] = executive_committee
        context['board_of_directors'] = board_of_directors

        # For template compatibility with your loops
        # Create lists containing the committee (or empty list)
        if executive_committee:
            context['executive_commitees'] = [executive_committee]
        else:
            context['executive_commitees'] = []

        if board_of_directors:
            context['board_of_directors'] = [board_of_directors]  # Note: using same key name
        else:
            context['board_of_directors'] = []

        # Get active memberships with no chapter
        context['no_chapter_members'] = Membership.objects.filter(
            chapter__isnull=True,
            is_active=True
        )

        # Prepare lists for leaders and regular members
        leaders = []
        regular_members = []

        # Get executive user IDs if committee exists
        executive_user_ids = set()
        if executive_committee:
            executive_user_ids = set(executive_committee.members.values_list('id', flat=True))

        # Get board user IDs if committee exists
        board_user_ids = set()
        if board_of_directors:
            board_user_ids = set(board_of_directors.members.values_list('id', flat=True))

        for membership in context['all_members']:
            user = membership.user

            # Check if user is executive or board
            is_executive = user.id in executive_user_ids
            is_board = user.id in board_user_ids

            # Skip executive and board members (they have their own sections)
            if is_executive or is_board:
                continue

            # Check if user is a chapter leader
            # Note: chapters_leadership is the ManyToManyField for chapter representatives
            is_chapter_leader = (
                user.chapters_leadership.exists() or
                user.positions.exists()
            )

            if is_chapter_leader:
                leaders.append(membership)
            else:
                regular_members.append(membership)

        context['leaders'] = leaders
        context['regular_members'] = regular_members

        return context


from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Membership, CustomUser, Chapter
from .forms import MembershipForm  # Make sure to import your form
from .mixins import AdminRequiredMixin  # Assuming you have this mixin




# AMAapp/views.py
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Membership, CustomUser, Chapter
from .forms import MembershipForm

# Create a simple admin mixin using Django's built-in
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or
            self.request.user.is_superuser
        )



class MembershipCreateView(LoginRequiredMixin, CreateView):
    model = Membership
    form_class = MembershipForm
    template_name = 'membership_form.html'
    success_url = reverse_lazy('membership_request_sent')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        current_user = self.request.user
        chapter = form.cleaned_data.get('chapter')

        # Prevent duplicate memberships
        if Membership.objects.filter(user=current_user, chapter=chapter).exists():
            messages.error(
                self.request,
                f"You are already a member of {chapter.name}."
            )
            return self.form_invalid(form)

        # Assign user before save
        form.instance.user = current_user

        response = super().form_valid(form)

        messages.success(
            self.request,
            f"Membership request sent successfully for {chapter.name}."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Please correct the errors below."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': 'Join a Chapter',
            'action': 'create',
            'current_user': self.request.user,
        })
        return context


class MembershipUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Membership
    form_class = MembershipForm  # Use custom form for consistency
    template_name = 'membership_form.html'
    success_url = reverse_lazy('membership_request_sent')

    def get_form_kwargs(self):
        """Pass the instance to the form"""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def form_valid(self, form):
        # Get the original membership before update
        original_membership = self.get_object()
        new_user = form.cleaned_data.get('user')
        new_chapter = form.cleaned_data.get('chapter')

        # Check if the membership combination changed
        if original_membership.user != new_user or original_membership.chapter != new_chapter:
            # Check if the new combination already exists
            if Membership.objects.filter(user=new_user, chapter=new_chapter).exists():
                messages.error(
                    self.request,
                    f"❌ {new_user.username} is already a member of {new_chapter.name}."
                )
                return self.form_invalid(form)

        # Call parent form_valid to save the instance
        response = super().form_valid(form)

        # Add success message
        messages.success(
            self.request,
            f"✏️ Successfully updated membership for {self.object.user.username}."
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            "⚠️ Please correct the errors below."
        )
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Edit Membership: {self.object.user.username}"
        context['action'] = "update"
        context['object'] = self.object  # Pass the membership object
        return context



class MembershipSend(LoginRequiredMixin, TemplateView):
    template_name = 'membership_request_sent.html'


class MembershipDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Membership
    template_name = 'membership_confirm_delete.html'
    success_url = '/memberships/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Delete Membership: {self.object.user.username}"
        return context

    def delete(self, request, *args, **kwargs):
        # Store user info for success message before deletion
        membership = self.get_object()
        user_name = membership.user.username
        chapter_name = membership.chapter.name

        # Call parent delete method
        response = super().delete(request, *args, **kwargs)

        # Add success message
        messages.success(
            request,
            f"🗑️ Successfully removed {user_name} from {chapter_name}."
        )
        return response

class ElectionListView(ListView):
    model = Election
    template_name = 'election_list.html'


class ElectionDetailView(DetailView):
    model = Election
    template_name = 'election_detail.html'


class ElectionCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Election
    fields = '__all__'
    template_name = 'election_form.html'
    success_url = '/elections/'


class ElectionUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Election
    fields = '__all__'
    template_name = 'election_form.html'
    success_url = '/elections/'


class ElectionDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Election
    template_name = 'election_confirm_delete.html'
    success_url = '/elections/'



class CandidateListView(LoginRequiredMixin, ListView):
    model = Candidate
    template_name = 'candidate_list.html'


class CandidateCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Candidate
    fields = '__all__'
    template_name = 'candidate_form.html'
    success_url = '/candidates/'


class CandidateUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Candidate
    fields = '__all__'
    template_name = 'candidate_form.html'
    success_url = '/candidates/'


class CandidateDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Candidate
    template_name = 'candidate_confirm_delete.html'
    success_url = '/candidates/'




class ConflictListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = ConflictResolution
    template_name = 'conflict_list.html'


class ConflictDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = ConflictResolution
    template_name = 'conflict_detail.html'


class ConflictCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = ConflictResolution
    fields = '__all__'
    template_name = 'conflict_form.html'
    success_url = '/conflicts/'


class ConflictUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = ConflictResolution
    fields = '__all__'
    template_name = 'conflict_form.html'
    success_url = '/conflicts/'


class ConflictDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = ConflictResolution
    template_name = 'conflict_confirm_delete.html'
    success_url = '/conflicts/'


from django.contrib.auth import get_user_model

User = get_user_model()

def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'profile_user': user
    }
    return render(request, 'profile.html', context)




from django.views.generic import ListView
from .models import Media, Chapter

class GalleryListView(ListView):
    model = Media
    template_name = 'gellery_list.html'
    context_object_name = 'media_list'
    paginate_by = 12  # Show 12 items per page

    def get_queryset(self):
        return Media.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get all chapters that have media
        chapters = Chapter.objects.filter(media__isnull=False).distinct()
        context['chapters'] = chapters
        # Get media without chapters
        context['no_chapter_media'] = Media.objects.filter(chapter__isnull=True)

        return context


def about_view(request):
    return render(request, 'about.html')

def terms_view(request):
    return render(request, 'terms.html')


import logging
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Event, Booking
from django.core.mail import send_mail
from uuid import uuid4
from django.views.decorators.http import require_POST
# Configure logging
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# =============================================================================
# EVENT PAYMENT VIEWS
# =============================================================================

@login_required
@require_POST
def create_event_checkout_session(request, pk):
    """Event booking payment"""
    event = get_object_or_404(Event, pk=pk)

    # Check if user has already booked this event
    if Booking.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, f"You have already booked '{event.title}'")
        return redirect('event_detail', pk=event.pk)

    # Check if event has already passed
    if event.start_time < timezone.now():
        messages.error(request, f"Event '{event.title}' has already passed")
        return redirect('event_detail', pk=event.pk)

    # Convert price to cents for Stripe
    price_in_cents = int(event.price * 100)

    # Get domain for redirect URLs
    domain = request.build_absolute_uri('/')[:-1]  # Gets current domain without trailing slash
    domain = 'http://dataskillacademy.com'

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",  # or use event.currency if you add that field
                    "product_data": {
                        "name": f"{event.title} - {event.get_type_display()}",
                        "description": f"Event Date: {event.start_time.date()} at {event.location or 'TBD'}",
                        "images": [event.images.url] if event.images else [],
                    },
                    "unit_amount": price_in_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{domain}/events/{event.pk}/payment-success/?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{domain}/events/{event.pk}/",
            metadata={
                "event_id": str(event.id),
                "event_type": event.type,
                "user_id": str(request.user.id),
                "user_email": request.user.email,
                "purpose": "event_booking",
            },
            customer_email=request.user.email,  # Pre-fill email
            expires_at=int((timezone.now() + timezone.timedelta(hours=1)).timestamp()),  # Session expires in 1 hour
        )

        # Store session ID in user's session for verification
        request.session['stripe_checkout_session_id'] = checkout_session.id
        request.session['event_id'] = str(event.id)

        return redirect(checkout_session.url)

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error creating checkout session: {str(e)}")
        messages.error(request, f"Payment processing error: {str(e)}")
        return redirect('event_detail', pk=event.pk)

    except Exception as e:
        logger.exception("Failed to create Stripe Checkout session")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('event_detail', pk=event.pk)


@login_required
def event_payment_success(request, pk):
    """Event payment success - create booking after successful payment"""
    event = get_object_or_404(Event, pk=pk)

    # Get session ID from URL or session
    session_id = request.GET.get('session_id') or request.session.get('stripe_checkout_session_id')

    if not session_id:
        messages.error(request, "No payment session found")
        return redirect('event_detail', pk=event.pk)

    try:
        # Verify the Stripe session
        stripe_session = stripe.checkout.Session.retrieve(session_id)

        # Check if payment was successful
        if stripe_session.payment_status != 'paid':
            messages.error(request, "Payment was not successful")
            return redirect('event_detail', pk=event.pk)

        # Verify this session belongs to current user and event
        if (stripe_session.metadata.get('user_id') != str(request.user.id) or
                stripe_session.metadata.get('event_id') != str(event.id)):
            messages.error(request, "Payment verification failed")
            return redirect('event_detail', pk=event.pk)

        # Check if booking already exists (idempotency)
        booking, created = Booking.objects.get_or_create(
            event=event,
            user=request.user,
            defaults={
                'verification_code': uuid4().hex[:10].upper(),
                'is_accredited_delegate': request.user.is_good_standing,
            }
        )

        if created:
            # Send confirmation email
            try:
                send_mail(
                    subject=f'Event Booking Confirmation - {event.title}',
                    message=f"""
Dear {request.user.get_full_name() or request.user.username},

Thank you for registering for: {event.title}

📅 Event Details:
- Date: {event.start_time.date()}
- Time: {event.start_time.time()} - {event.end_time.time()}
- Location: {event.location or 'To be announced'}
- Type: {event.get_type_display()}

✅ Your Booking Details:
- Verification Code: {booking.verification_code}
- Booking ID: {booking.id}
- Booking Date: {booking.booked_at.date()}

Please bring your verification code for check-in.

Best regards,
AMA Team
                    """,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send confirmation email: {str(e)}")
                # Don't show error to user, just log it

            messages.success(
                request,
                f"✅ Successfully booked '{event.title}'! Check your email for confirmation."
            )

            # Clear session data
            request.session.pop('stripe_checkout_session_id', None)
            request.session.pop('event_id', None)
        else:
            messages.info(
                request,
                f"ℹ️ You are already registered for '{event.title}'."
            )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error verifying payment: {str(e)}")
        messages.error(request, "Payment verification failed. Please contact support.")
        return redirect('event_detail', pk=event.pk)

    except Exception as e:
        logger.exception("Error creating booking after payment")
        messages.error(request, "Error processing your booking. Please contact support.")
        return redirect('event_detail', pk=event.pk)

    context = {
        "event": event,
        "booking": booking,
        "session_id": session_id,
    }

    return render(request, "events/payment_success.html", context)


@login_required
def event_payment_cancel(request, pk):
    """Event payment cancelled"""
    event = get_object_or_404(Event, pk=pk)
    messages.info(request, f"Booking for '{event.title}' was cancelled.")

    # Clear session data
    request.session.pop('stripe_checkout_session_id', None)
    request.session.pop('event_id', None)

    return redirect('event_detail', pk=event.pk)

# =============================================================================
# DONATION CHECKOUT VIEWS
# =============================================================================

@login_required
def create_donation_checkout_session(request, pk=None):
    """Handle donation payments (one-time or for specific campaigns)"""
    if pk:
        # Specific donation campaign
        donation = get_object_or_404(Donation, pk=pk)
        title = donation.title
        description = donation.description
        amount = request.POST.get('amount') or donation.amount
    else:
        # General donation
        title = "AMA General Donation"
        description = "Support AMA's mission and activities"
        amount = request.POST.get('amount', 25.00)  # Default $25

    # Convert to cents
    amount_in_cents = int(float(amount) * 100)

    domain = request.build_absolute_uri('/')[:-1]

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": title,
                        "description": description[:100] + "..." if len(description) > 100 else description,
                    },
                    "unit_amount": amount_in_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{domain}/donations/payment-success/",
            cancel_url=f"{domain}/donations/",
            metadata={
                "user_id": str(request.user.id),
                "purpose": "donation",
                "campaign_id": str(pk) if pk else "general",
                "amount": str(amount),
            },
            customer_email=request.user.email,
        )
        return redirect(checkout_session.url)

    except Exception as e:
        logger.exception("❌ Donation checkout error")
        messages.error(request, "Error processing donation")
        return redirect('donation_list' if pk else 'home')


@login_required
def donation_payment_success(request):
    """Handle successful donation payment"""
    # Note: For production, use Stripe webhook to verify payment
    # This is a simplified version

    try:
        # Create donation record
        donation = Donation.objects.create(
            user=request.user,
            title="General Donation",
            amount=0.00,  # Should get from Stripe webhook
            type="donation",
            receipt_sent=False,
        )

        messages.success(request, "✅ Thank you for your donation!")

    except Exception as e:
        logger.exception("❌ Error recording donation")
        messages.error(request, "Error recording donation. Please contact support.")

    return render(request, "donations/payment_success.html")


# =============================================================================
# MEMBERSHIP DUES PAYMENT VIEWS
# =============================================================================

@login_required
def create_dues_checkout_session(request):
    """Handle membership dues payment"""
    user = request.user

    # Get user's membership
    try:
        membership = Membership.objects.get(user=user)
        dues_amount = membership.dues_amount or 50.00  # Default $50 if not set
    except Membership.DoesNotExist:
        dues_amount = 50.00  # Default dues amount

    # Convert to cents
    amount_in_cents = int(dues_amount * 100)

    domain = request.build_absolute_uri('/')[:-1]

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "AMA Membership Dues",
                        "description": f"Annual membership dues for {user.get_full_name() or user.username}",
                    },
                    "unit_amount": amount_in_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{domain}/membership/dues-payment-success/",
            cancel_url=f"{domain}/profile/",
            metadata={
                "user_id": str(user.id),
                "purpose": "membership_dues",
                "amount": str(dues_amount),
            },
            customer_email=user.email,
        )
        return redirect(checkout_session.url)

    except Exception as e:
        logger.exception("❌ Dues payment error")
        messages.error(request, "Error processing dues payment")
        return redirect('profile')


@login_required
def dues_payment_success(request):
    """Handle successful dues payment"""
    user = request.user

    try:
        # Update membership record
        membership = Membership.objects.get(user=user)
        membership.dues_paid = True
        membership.payment_date = timezone.now().date()
        membership.save()

        # Send receipt
        send_mail(
            'Membership Dues Payment Confirmation - AMA',
            f"""
Dear {user.get_full_name() or user.username},

Thank you for paying your annual membership dues.

Your membership is now in good standing until {timezone.now().date().replace(year=timezone.now().date().year + 1)}.

If you have any questions, please contact your chapter representative.

Best regards,
AMA Finance Committee
            """,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=True,
        )

        messages.success(request, "✅ Membership dues payment successful! Check your email for receipt.")

    except Membership.DoesNotExist:
        messages.error(request, "❌ No membership found")

    except Exception as e:
        logger.exception("❌ Error updating membership dues")
        messages.error(request, "Error updating membership status")

    return redirect('profile')


def user_has_booked_event(user, event):
    """Check if user has already booked this event"""
    if not user.is_authenticated:
        return False
    return Booking.objects.filter(user=user, event=event).exists()


# views.py - Add these views for complete functionality
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Message, ConnectionRequest


@login_required
def send_connection_request(request, uuid):
    """Send connection request to another user"""
    receiver = get_object_or_404(CustomUser, uuid=uuid)

    # Check if connection already exists
    if ConnectionRequest.objects.filter(sender=request.user, receiver=receiver).exists():
        messages.info(request, "Connection request already sent.")
        return redirect('user-profile', uuid=uuid)

    # Create connection request
    connection = ConnectionRequest.objects.create(
        sender=request.user,
        receiver=receiver,
        message=request.POST.get('message', '')
    )

    messages.success(request, f"Connection request sent to {receiver.get_full_name()}!")
    return redirect('user-profile', uuid=uuid)


@login_required
def update_cover_photo(request):
    """Handle cover photo upload"""
    if request.method == 'POST':
        user = request.user

        if 'cover_photo' in request.FILES:
            user.cover_image = request.FILES['cover_photo']
            user.save()
            messages.success(request, "Cover photo updated successfully!")
        elif 'remove_cover' in request.POST:
            user.cover_image.delete(save=True)
            messages.success(request, "Cover photo removed!")

        return redirect('my-profile')

    return redirect('my-profile')

@login_required
def my_events(request):
    """View user's events and activities"""
    user = request.user
    context = {
        'bookings': user.booking_set.all().order_by('-booked_at'),
        'donations': user.donation_set.all().order_by('-created_at'),
        'messages': user.sent_messages.all().order_by('-sent_at')[:10],
    }
    return render(request, 'profile/my_activities.html', context)


@login_required
def connection_list(request):
    """
    View to list all connections for the current user.
    """
    user = request.user
    # Get connections where the user is user1 or user2
    connections = Connection.objects.filter(user1=user) | Connection.objects.filter(user2=user)
    connections = connections.order_by('-created_at')

    context = {
        'connections': connections,
        'user': user,
    }
    return render(request, 'connection_list.html', context)


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
import qrcode
import io
from .models import CustomUser
from .serializers import DigitalIDSerializer


class UserDigitalIDView(APIView):
    """Return the clean digital ID JSON."""

    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DigitalIDSerializer(user)
        return Response(serializer.data)


# views.py
from django.views import View
from django.http import HttpResponse
from django.urls import reverse
import qrcode
import io
from .models import CustomUser

class UserDigitalIDQRCodeView(View):
    """Generate a QR code linking to the user's profile via UUID."""
    def get(self, request, uuid):
        try:
            user = CustomUser.objects.get(uuid=uuid)
        except CustomUser.DoesNotExist:
            return HttpResponse("User not found", status=404)

        # Build absolute URL to the profile
        profile_url = request.build_absolute_uri(
            reverse('user-profile', kwargs={'uuid': user.uuid})
        )

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=4
        )
        qr.add_data(profile_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert image to HTTP response
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return HttpResponse(buffer, content_type="image/png")




from django.http import HttpResponse
from .models import CustomUser
from .utils import generate_user_id_pdf,generate_admin_user_id_pdf

def download_user_id(request, uuid):
    try:
        user = CustomUser.objects.get(uuid=uuid)
    except CustomUser.DoesNotExist:
        return HttpResponse("User not found", status=404)

    # Generate PDF
    pdf_buffer = generate_user_id_pdf(user)

    # Return PDF as HTTP response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{user.username}_LIMAFE_ID.pdf"'
    return response



def download_admin_user_id(request, uuid):
    try:
        user = CustomUser.objects.get(uuid=uuid)

    except CustomUser.DoesNotExist:
        return HttpResponse("User not found", status=404)


    # Generate PDF
    pdf_buffer = generate_admin_user_id_pdf(user)

    # Return PDF as HTTP response
    response = HttpResponse(pdf_buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{user.username}_LIMAFE_ID.pdf"'
    return response



class ExecutiveBoardListView(LoginRequiredMixin, ListView):
    model = ExecutiveBoard
    template_name = 'executive_board_list.html'
    context_object_name = 'boards'
    paginate_by = 10

    def get_queryset(self):
        queryset = ExecutiveBoard.objects.all()
        # Filter by active status if specified
        active_filter = self.request.GET.get('active')
        if active_filter == 'true':
            queryset = queryset.filter(is_active=True)
        elif active_filter == 'false':
            queryset = queryset.filter(is_active=False)
        return queryset



class BoardMembershipListView(LoginRequiredMixin, ListView):
    model = BoardMembership
    template_name = 'board_membership_list.html'
    context_object_name = 'memberships'
    paginate_by = 20

    def get_queryset(self):
        queryset = BoardMembership.objects.select_related(
            'user', 'executive_board', 'board_position', 'chapter', 'chapter_position'
        ).all()

        # Filter by executive board
        board_id = self.request.GET.get('board')
        if board_id:
            queryset = queryset.filter(executive_board_id=board_id)

        # Filter by active status
        active = self.request.GET.get('active')
        if active == 'true':
            queryset = queryset.filter(is_active=True)
        elif active == 'false':
            queryset = queryset.filter(is_active=False)

        # Filter by represents_chapter
        represents = self.request.GET.get('represents_chapter')
        if represents == 'true':
            queryset = queryset.filter(represents_chapter=True)

        # Filter by user
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by role type
        role_type = self.request.GET.get('role_type')
        if role_type:
            queryset = queryset.filter(role_type=role_type)

        return queryset.order_by('-is_active', '-start_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['executive_boards'] = ExecutiveBoard.objects.filter(is_active=True)
        context['role_choices'] = BoardMembership.MEMBERSHIP_ROLES
        context['current_filters'] = {
            'board': self.request.GET.get('board', ''),
            'active': self.request.GET.get('active', ''),
            'represents_chapter': self.request.GET.get('represents_chapter', ''),
            'role_type': self.request.GET.get('role_type', ''),
        }
        return context



class ExecutiveBoardDetailView(LoginRequiredMixin, DetailView):
    model = ExecutiveBoard
    template_name = 'executive_board_detail.html'
    context_object_name = 'board'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_object()

        # Get current active members
        context['current_members'] = board.board_members.filter(
            is_active=True
        ).select_related('user', 'board_position', 'chapter')

        # Get past members
        context['past_members'] = board.board_members.filter(
            is_active=False
        ).select_related('user', 'board_position', 'chapter')

        # Get chapter representatives
        context['chapter_reps'] = board.get_chapter_representatives()

        # Get leadership hierarchy
        context['leadership_hierarchy'] = board.get_leadership_hierarchy()

        # Get positions on this board
        context['positions'] = board.positions.all().order_by('precedence_order')

        # Get member chapters
        context['member_chapters'] = board.member_chapters.all()

        # Check if user can edit
        context['can_edit'] = self.request.user.is_staff or self.request.user.role == 'admin'

        return context


