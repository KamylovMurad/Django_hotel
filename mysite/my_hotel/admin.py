from django.contrib import admin
from .models import Room, Review, Booking


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'capacity', 'created_at', 'is_popular']
    search_fields = "name", "price"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['room', 'author', 'rating', 'created_at']
    search_fields = "room", "author", 'rating'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['room', 'user', 'start_date', 'end_date', 'status']
    search_fields = 'room', 'user', 'created_at'
    list_filter = ['user', 'room', 'status']
