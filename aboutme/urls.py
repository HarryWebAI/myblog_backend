from django.urls import path
from .views import AboutMeView, UpdateAboutMeView

urlpatterns = [
    path('', AboutMeView.as_view(), name='aboutme'),
    path('update/', UpdateAboutMeView.as_view(), name='update_aboutme'),
]
