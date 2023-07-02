from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.routers import DefaultRouter
from .views import (
  main_page,
  rooms_filter,
  RegisterView,
  CustomLoginView,
  BookRoomView,
  UserProfileDetailView,
  cancel_booking,
  ReviewView,
  RoomViewSet,
  BookingViewSet,
  ReviewViewSet,
)

app_name = "my_hotel"

routers = DefaultRouter()
routers.register('rooms', RoomViewSet)
routers.register('bookings', BookingViewSet)
routers.register('reviews', ReviewViewSet)

urlpatterns = [
    path("", main_page, name="main"),
    path("api/", include(routers.urls)),
    path("rooms", rooms_filter, name="rooms"),
    path('rooms/<int:pk>/', BookRoomView.as_view(), name='room_detail'),
    path('rooms/<int:pk>/review', ReviewView.as_view(), name='review'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', UserProfileDetailView.as_view(), name='profile'),
    path('cancel_booking/<int:pk>/', cancel_booking, name='cancel_booking'),

]
