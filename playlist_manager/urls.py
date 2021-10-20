from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from playlist_manager import views


urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("attractions/", views.AttractionListView.as_view(), name="attraction-list"),
    path("tracks/", views.TrackListView.as_view(), name="track-list"),
    
    path('attractions/select/<str:pk>/', views.select_attraction, name='select_attraction'),
    path('attractions/remove/<str:pk>/', views.remove_attraction, name='remove_attraction'),
    
    path('attractions/select-origin/<str:pk>/', views.select_attraction_origin, name='select_attraction_origin'),
    path('attractions/remove-origin/<str:pk>/', views.remove_attraction_origin, name='remove_attraction_origin'),
    
    path('attractions/select-destination/<str:pk>/', views.select_attraction_destination, name='select_attraction_destination'),
    path('attractions/remove-destination/<str:pk>/', views.remove_attraction_destination, name='remove_attraction_destination'),

    path('results/', views.result_view, name='results')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
