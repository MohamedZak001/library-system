from datetime import date

from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from django.contrib.gis.db.models.functions import Distance
from rest_framework.permissions import IsAuthenticated

from .filters import LibraryFilterSet, AuthorFilterSet, BookFilterSet
from .models import Library, Book, Author, Borrow
from .serializers import LibrarySerializer, BorrowBookSerializer, BookReturnSerializer, ListBookSerializer, \
    ListAuthorSerializer, ListLoadedAuthorSerializer
from rest_framework.response import Response

from .tasks import send_confirmation_email
from .throttles import BookBorrowRateThrottle, BookReturnRateThrottle


@extend_schema(tags=["Libraries"])
class ListLibraryAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LibrarySerializer
    queryset = Library.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = LibraryFilterSet

    def list(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)
        user = self.request.user
        queryset = queryset.annotate(distance=Distance('location', user.location)).order_by('distance')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Authors"])
class ListAuthorAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListAuthorSerializer
    queryset = Author.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorFilterSet

    def list(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)
        print(queryset)
        queryset = queryset.annotate(books_count=Count('books')).order_by('books_count')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Books"])
class ListBooksAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListBookSerializer
    queryset = Book.objects.prefetch_related("library", "authors")
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookFilterSet

    def list(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Authors"])
class ListLoadedAuthorAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ListLoadedAuthorSerializer
    queryset = Author.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = AuthorFilterSet

    def list(self, request, *args, **kwargs):
        queryset = super().get_queryset()
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Books"])
class BorrowBookAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BorrowBookSerializer
    throttle_classes = [BookBorrowRateThrottle]
    queryset = Book.objects.all()
    lookup_field = "uuid"
    lookup_url_kwarg = "book_uuid"

    def create(self, request, *args, **kwargs):
        book = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"book": book, "request": request})
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # update the available books copies
            book.available_copies -= 1
            book.save()

            # create the borrow object
            borrow = Borrow.objects.create(
                user=request.user,
                book=book,
                return_date=serializer.validated_data.get("return_date"),
                borrow_date=date.today()
            )
            # send the confirmation email
            transaction.on_commit(lambda: send_confirmation_email.apply_async((borrow.id,)))

        return Response(self.get_serializer(instance=borrow).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Books"])
class BookReturnView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [BookReturnRateThrottle]
    serializer_class = BookReturnSerializer
    queryset = Borrow.objects.select_related('book')
    lookup_field = "uuid"

    def get_object(self):
        return get_object_or_404(
            Borrow,
            uuid=self.kwargs['borrow_uuid'],
            book__uuid=self.kwargs['book_uuid'],
            user=self.request.user
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter((Q(status=Borrow.BorrowStatus.BORROWED) | Q(status=Borrow.BorrowStatus.OVERDUE)))

    def post(self, request, *args, **kwargs):
        borrow = self.get_object()
        book = borrow.book

        with transaction.atomic():
            # update the book available copies
            book.available_copies += 1
            book.save()

            # Update borrow status
            borrow.status = Borrow.BorrowStatus.RETURNED
            borrow.actual_return_date = date.today()
            borrow.save()

        return Response(self.get_serializer(instance=borrow).data, status=status.HTTP_200_OK)










