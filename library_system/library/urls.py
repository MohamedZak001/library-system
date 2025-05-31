from django.urls import path

from . import views

urlpatterns = [
    path('authors/', views.ListAuthorAPIView.as_view(), name='authors'),
    path('authors/loaded/', views.ListLoadedAuthorAPIView.as_view(), name='authors-loaded'),
    path('libraries/', views.ListLibraryAPIView.as_view(), name='libraries'),
    path('books/', views.ListBooksAPIView.as_view(), name='books'),
    path('books/<uuid:book_uuid>/borrow/', views.BorrowBookAPIView.as_view(), name='borrow'),
    path('books/<uuid:book_uuid>/borrows/<uuid:borrow_uuid>/return/', views.BookReturnView.as_view(), name='return'),
]
