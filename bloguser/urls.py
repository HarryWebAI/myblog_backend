from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserModelViewSet, LoginView, InitCodeView, RegisterView, AvatarUploadView, AgreeUserView, ActiveUserView, ResetPasswordView

router = DefaultRouter()
router.register(r'user', UserModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('initcode/', InitCodeView.as_view()),
    path('register/', RegisterView.as_view()),
    path('avatar/upload/', AvatarUploadView.as_view()),
    path('agreeuser/', AgreeUserView.as_view()),
    path('activeuser/', ActiveUserView.as_view()),
    path('resetpassword/', ResetPasswordView.as_view()),
]
