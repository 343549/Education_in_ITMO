from django.urls import path

from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('region/<int:region_id>/', views.region_detail, name='region_detail'),
    path('region/<int:region_id>/analyze/', views.analyze_region, name='analyze_region'),
]

