from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('courses/', views.course_list_view, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.course_enroll_view, name='course_enroll'),
    path('courses/<int:course_id>/drop/', views.course_drop_view, name='course_drop'),
]
