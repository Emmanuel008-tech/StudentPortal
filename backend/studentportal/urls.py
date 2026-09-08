"""
studentportal URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_view, name='landing'),
    path('about/', views.about_view, name='about'),
    path('features/', views.features_view, name='features'),
    path('contact/', views.contact_view, name='contact'),

    # Direct / canonical staff portal routes (accessible via {% url 'staff_login' %})
    path('accounts/staff-login/', accounts_views.staff_login_view, name='staff_login'),
    path('staff-login/', accounts_views.staff_login_view),
    path('accounts/staff/', accounts_views.staff_dashboard_view, name='staff_dashboard'),
    path('staff/', accounts_views.staff_dashboard_view),

    path('accounts/', include('accounts.urls')),
    path('academics/', include('academics.urls')),
    path('dashboard/', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
