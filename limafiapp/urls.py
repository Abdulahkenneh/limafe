# limafi_site/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
# Import all views from their respective apps
# Assuming apps exist, but if flat structure, adjust imports to from views import * or similar

from .views import (
    SignupView, CustomLoginView,  UserUpdateView, PasswordRecoveryView, logout_view
)

from .views import (
    PageListView, PageDetailView, PageCreateView, PageUpdateView, PageDeleteView,
    PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView,
    ProjectListView, ProjectDetailView, ProjectCreateView, ProjectUpdateView, ProjectDeleteView,
    MediaUploadView,download_user_id,ExecutiveBoardDetailView,
)
from . import views
from .views import (
    EventListView, EventDetailView, EventCreateView, EventUpdateView, EventDeleteView,
    BookingCreateView, EventReportView
)

from .views import DonationListView, DonationCreateView

from .views import MessageListView, MessageCreateView, NewsletterCreateView, ContactView

from .views import AnalyticsDashboardView,HomeView

urlpatterns = [
                  path('', HomeView.as_view(), name='home'),
                  # Accounts URLs
                  path('accounts/signup/', SignupView.as_view(), name='signup'),
                  path('accounts/login/', CustomLoginView.as_view(), name='login'),
                  path('accounts/logout/', logout_view, name='logout'),

                  path('accounts/profile/', MyProfileView.as_view(), name='my-profile'),



                  path('connections/', connection_list, name='connection_list'),
                  path('accounts/profile/<uuid:uuid>/', UserProfileView.as_view(), name='user-profile'),
                  path('accounts/update/', UserUpdateView.as_view(), name='user_update'),
                  path('accounts/password_reset/', PasswordRecoveryView.as_view(), name='password_reset'),
                  path('accounts/connect/<uuid:uuid>/',send_connection_request, name='send_connection_request'),
                  path('accounts/my-activities/', my_events, name='my_events'),
                  path('accounts/update-cover/',update_cover_photo, name='update_cover'),
                  path('chapters/<int:pk>/',ChapterDetailView.as_view(), name='chapter_detail'),
                  path('messages/new/', MessageCreateView.as_view(), name='message_create'),

                  # Content URLs
                  path('content/pages/', PageListView.as_view(), name='page_list'),
                  path('content/pages/<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
                  path('content/pages/create/', PageCreateView.as_view(), name='page_create'),
                  path('content/pages/<slug:slug>/update/', PageUpdateView.as_view(), name='page_update'),
                  path('content/pages/<slug:slug>/delete/', PageDeleteView.as_view(), name='page_delete'),

                  path('content/posts/', PostListView.as_view(), name='post_list'),

                  path('content/posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
                  path('content/posts/create/', PostCreateView.as_view(), name='post_create'),
                  path('content/posts/<int:pk>/update/', PostUpdateView.as_view(), name='post_update'),
                  path('content/posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),

                  path('content/projects/', ProjectListView.as_view(), name='project_list'),
                  path('content/projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
                  path('content/projects/create/', ProjectCreateView.as_view(), name='project_create'),
                  path('content/projects/<int:pk>/update/', ProjectUpdateView.as_view(), name='project_update'),
                  path('content/projects/<int:pk>/delete/', ProjectDeleteView.as_view(), name='project_delete'),
                  path('content/media/upload/', MediaUploadView.as_view(), name='media_upload'),
                  path('gallery/', GalleryListView.as_view(), name='gallery_list'),

                  # Events URLs
                  path('events/', EventListView.as_view(), name='event_list'),
                  path('events/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
                  path('events/create/', EventCreateView.as_view(), name='event_create'),
                  path('events/<int:pk>/update/', EventUpdateView.as_view(), name='event_update'),
                  path('events/<int:pk>/delete/', EventDeleteView.as_view(), name='event_delete'),
                  path('events/<int:event_id>/book/', BookingCreateView.as_view(), name='booking_create'),
                  path('events/<int:pk>/report/', EventReportView.as_view(), name='event_report'),

                  # Donations URLs
                  path('donations/', DonationListView.as_view(), name='donation_list'),
                  path('donations/create/', DonationCreateView.as_view(), name='donation_create'),

                  # Communications URLs
                  path('communications/messages/', MessageListView.as_view(), name='message_list'),
                  path('communications/messages/create/', MessageCreateView.as_view(), name='message_create'),
                  path('communications/newsletters/create/', NewsletterCreateView.as_view(), name='newsletter_create'),
                  path('communications/contact/', ContactView.as_view(), name='contact'),

                    # Governance URLs

                    # Chapters
                    path('chapters/', ChapterListView.as_view(), name='chapter_list'),
                    path('chapters/<int:pk>/', ChapterDetailView.as_view(), name='chapter_detail'),
                    path('chapters/create/', ChapterCreateView.as_view(), name='chapter_create'),
                    path('chapters/<int:pk>/update/', ChapterUpdateView.as_view(), name='chapter_update'),
                    path('chapters/<int:pk>/delete/', ChapterDeleteView.as_view(), name='chapter_delete'),

                    # Committees
                    path('committees/', CommitteeListView.as_view(), name='committee_list'),
                    path('committees/<int:pk>/', CommitteeDetailView.as_view(), name='committee_detail'),
                    path('committees/create/', CommitteeCreateView.as_view(), name='committee_create'),
                    path('committees/<int:pk>/update/', CommitteeUpdateView.as_view(), name='committee_update'),
                    path('committees/<int:pk>/delete/', CommitteeDeleteView.as_view(), name='committee_delete'),

                    # Positions
                    path('positions/', PositionListView.as_view(), name='position_list'),
                    path('positions/<int:pk>/', PositionDetailView.as_view(), name='position_detail'),
                    path('positions/create/', PositionCreateView.as_view(), name='position_create'),
                    path('positions/<int:pk>/update/', PositionUpdateView.as_view(), name='position_update'),
                    path('positions/<int:pk>/delete/', PositionDeleteView.as_view(), name='position_delete'),

                    path('accounts/profile/<uuid:uuid>/download-id/',  download_user_id,name='download-user-id'),
                    path('accounts/profile/<uuid:uuid>/qrcode/', UserDigitalIDQRCodeView.as_view(), name='user-profile-qrcode'),
                    path('accounts/profile/admin/<uuid:uuid>/download-id/',download_admin_user_id,name='download-admin-user-id'),





                    # teams
                    path('team/', TeamListView.as_view(), name='team_list'),
                    path('about',about_view, name ='about-us'),
                    path('terms',terms_view, name ='terms-of-use'),
                    # Memberships
                    path('memberships/', MembershipListView.as_view(), name='membership_list'),
                    path('memberships/request/', MembershipSend.as_view(), name='membership_request_sent'),
                    path('memberships/create/', MembershipCreateView.as_view(), name='membership_create'),
                    path('memberships/<int:pk>/update/', MembershipUpdateView.as_view(), name='membership_update'),
                    path('memberships/<int:pk>/delete/', MembershipDeleteView.as_view(), name='membership_delete'),

                    # Elections
                    path('elections/', ElectionListView.as_view(), name='election_list'),
                    path('elections/<int:pk>/', ElectionDetailView.as_view(), name='election_detail'),
                    path('elections/create/', ElectionCreateView.as_view(), name='election_create'),
                    path('elections/<int:pk>/update/', ElectionUpdateView.as_view(), name='election_update'),
                    path('elections/<int:pk>/delete/', ElectionDeleteView.as_view(), name='election_delete'),

                    # Candidates
                    path('candidates/', CandidateListView.as_view(), name='candidate_list'),
                    path('candidates/create/', CandidateCreateView.as_view(), name='candidate_create'),
                    path('candidates/<int:pk>/update/', CandidateUpdateView.as_view(), name='candidate_update'),
                    path('candidates/<int:pk>/delete/', CandidateDeleteView.as_view(), name='candidate_delete'),

                    # Conflicts
                    path('conflicts/', ConflictListView.as_view(), name='conflict_list'),
                    path('conflicts/<int:pk>/', ConflictDetailView.as_view(), name='conflict_detail'),
                    path('conflicts/create/', ConflictCreateView.as_view(), name='conflict_create'),
                    path('conflicts/<int:pk>/update/', ConflictUpdateView.as_view(), name='conflict_update'),
                    path('conflicts/<int:pk>/delete/', ConflictDeleteView.as_view(), name='conflict_delete'),

                  # Analytics URLs

                  # Event payment URLs
                  path('events/<int:pk>/checkout/', views.create_event_checkout_session, name='event_checkout'),
                  path('events/<int:pk>/payment-success/', views.event_payment_success, name='event_payment_success'),
                  path('events/<int:pk>/payment-cancel/', views.event_payment_cancel, name='event_payment_cancel'),

                  # Donation URLs
                  path('donations/checkout/', views.create_donation_checkout_session, name='donation_checkout'),
                  path('donations/checkout/<int:pk>/', views.create_donation_checkout_session,
                       name='campaign_checkout'),
                  path('donations/payment-success/', views.donation_payment_success, name='donation_payment_success'),

                  # Membership dues URLs
                  path('membership/pay-dues/', views.create_dues_checkout_session, name='pay_dues'),
                  path('membership/dues-payment-success/', views.dues_payment_success, name='dues_payment_success'),
                  path('accounts/profile/<uuid:uuid>/download-id/', download_user_id, name='download-user-id'),






                  path('analytics/dashboard/', AnalyticsDashboardView.as_view(), name='analytics_dashboard'),

                  path('executive-boards/',
         views.ExecutiveBoardListView.as_view(),
         name='executive_board_list'),

                  path('executive-boards/<int:pk>/',
         views.ExecutiveBoardDetailView.as_view(),
         name='executive_board_detail'),


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)