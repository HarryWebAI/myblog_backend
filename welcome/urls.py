from django.urls import path
from .views import WelcomeView, UpdateWelcomeView

urlpatterns = [
    path('', WelcomeView.as_view(), name='welcome'),
    path('update/', UpdateWelcomeView.as_view(), name='update-welcome'),
] 