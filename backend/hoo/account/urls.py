from django.conf.urls import url, include
from django.contrib import admin
from account import views

urlpatterns = [
    url(r'^register_resident/', views.register_resident.as_view(), name='register_resident'),
    url(r'^update_resident/', views.update_resident.as_view(), name='update_resident'),
    url(r'^create_visit/', views.create_visit.as_view(), name='create_visit'),
    url(r'^all_visits/', views.visit_list.as_view(), name='visit_list'),
    url(r'^all_residents/', views.resident_list.as_view(), name='resident_list'),
    url(r'^microsoft_list/', views.microsoft_list.as_view(), name='microsoft_list'),
    url(r'^update_visit/', views.update_visit.as_view(), name='update_visit'),
    url(r'^create_message/', views.create_message.as_view(), name='create_message'),
    url(r'^update_message/', views.update_message.as_view(), name='update_message'),
    url(r'^visit_by_id/', views.visit_by_id.as_view(), name='visit_by_id'),


]