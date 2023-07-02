from rest_framework import serializers
from .models import Room, Review, Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = (
          'pk',
          'name',
          'description',
          'price',
          'capacity',
          'type',
          'created_at',
          'preview',
          'is_popular',
        )


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
          'pk',
          'room',
          'user',
          'created_at',
          'start_date',
          'end_date',
          'status',
        )


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
          'pk',
          'room',
          'author',
          'created_at',
          'comment',
          'rating'
        )
