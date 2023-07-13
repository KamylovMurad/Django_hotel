from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView
from .models import Room, Booking, Profile, Review
from .forms import CustomUserCreationForm, BookingForm, ReviewForm
from django.db.models import Q
from django.contrib.auth.views import LoginView
from rest_framework.viewsets import ModelViewSet
from .serializers import RoomSerializer, ReviewSerializer, BookingSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,

    ]
    search_fields = ['room', 'user']
    filterset_fields = [
        'room',
        'user',
        'created_at',
        'start_date',
        'end_date',
        'status',
    ]
    ordering_fields = [
        'room',
        'user',
    ]


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,

    ]
    search_fields = ['name', 'descriprion']
    filterset_fields = [
        'name',
        'price',
        'capacity',
        'type',
        'created_at',
        'is_popular',
    ]
    ordering_fields = [
        'name',
        'price',
        'capacity',
    ]


def main_page(request: HttpRequest) -> HttpResponse:
    popular = Room.objects.filter(is_popular=True)
    context = {
        'popular_rooms': popular,
    }
    return render(request, 'my_hotel/main_page.html', context)


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == 'POST':
        if booking.status != 'confirmed':
            booking.status = 'cancelled'
            booking.save()
            return redirect('my_hotel:profile')


def rooms_filter(request: HttpRequest) -> HttpResponse:
    error_message = None
    queryset = Room.objects.all()
    types = list(set(room.type for room in queryset))
    capacity = list(set(room.capacity for room in queryset))
    if request.method == 'POST':
        sort_by = request.POST.get('sort_by', '-created_at')
        queryset = queryset.order_by(sort_by)
        selected_capacity = request.POST.get('capacity')
        selected_category = request.POST.get('category')
        search_query = request.POST.get('search')
        min_price = request.POST.get('min_price')
        max_price = request.POST.get('max_price')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if selected_category:
            queryset = queryset.filter(type=selected_category)
        if search_query:
            queryset = queryset.filter(name__exact=search_query)
        if selected_capacity:
            queryset = queryset.filter(capacity=selected_capacity)
        if start_date and end_date:
            if start_date > end_date:
                error_message = "Укажите корректную дату"

            else:
                reservations = Booking.objects.filter(
                    start_date__lte=end_date,
                    end_date__gte=start_date
                )
                reservations = reservations.filter(
                    Q(status='booked') | Q(status='confirmed')
                )
                reserved_room_ids = reservations.values_list('room', flat=True)
                queryset = queryset.exclude(id__in=reserved_room_ids)

    context = {
        'rooms': queryset,
        'error': error_message,
        'types': types,
        'capacity': capacity
    }

    return render(request, 'my_hotel/rooms_filter.html', context)


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "my_hotel/register.html"
    success_url = reverse_lazy("my_hotel:main")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('my_hotel:main'))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


class CustomLoginView(LoginView):
    template_name = 'my_hotel/login.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('my_hotel:main')
        return super().dispatch(request, *args, **kwargs)


def book_room(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return redirect('my_hotel:main')
    else:
        form = BookingForm()
    return render(request, 'booking.html', {'form': form})


class BookRoomView(CreateView):
    error_message = None
    form_class = BookingForm
    template_name = 'my_hotel/room_detail.html'
    success_url = reverse_lazy('my_hotel:main')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room = self.get_room()
        reviews = Review.objects.filter(room=room)
        context['room'] = room
        context['reviews'] = reviews
        return context

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            room = self.get_room()
            start_date = self.request.POST.get('start_date')
            end_date = self.request.POST.get('end_date')
            print(start_date, end_date)
            if start_date and end_date:
                if start_date > end_date:
                    error_message = "Укажите корректную дату"
                    form.add_error(None, error_message)
                    return self.form_invalid(form)
                if self.is_room_booked(room, start_date, end_date):
                    error_message = "Этот номер уже занят на указанные даты."
                    form.add_error(None, error_message)
                    return self.form_invalid(form)
                form.instance.user = self.request.user
                form.instance.room = room
                self.object = form.save()
                return super().form_valid(form)
        else:
            return redirect('my_hotel:login')

    def get_room(self):
        room_id = self.kwargs['pk']
        room = Room.objects.get(pk=room_id)
        return room

    def is_room_booked(self, room, start_date, end_date):
        bookings = Booking.objects.filter(
            room=room)
        bookings = bookings.filter(
            Q(status='booked') | Q(status='confirmed'),
            Q(start_date__lte=start_date, end_date__gte=start_date) |
            Q(start_date__lte=end_date, end_date__gte=end_date) |
            Q(start_date__gte=start_date, end_date__lte=end_date)
        )
        return bookings.exists()


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'my_hotel/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = Booking.objects.filter(
            user=self.request.user).order_by('-created_at')
        context['bookings'] = bookings
        return context


class ReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'my_hotel/review.html'

    def form_valid(self, form):
        room_id = self.kwargs.get('pk')
        room = get_object_or_404(Room, id=room_id)
        form.instance.room = room
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        room_id = self.kwargs.get('pk')
        return reverse_lazy('my_hotel:room_detail', kwargs={'pk': room_id})
