import django_filters
from django_filters import BaseInFilter, CharFilter

from library.models import Library, Author, Category, Book


class MultipleCharFiled(BaseInFilter, CharFilter):
    pass

class LibraryFilterSet(django_filters.FilterSet):
    categories = MultipleCharFiled(
        field_name='books__category__name',
        lookup_expr='in',
        distinct=True
    )

    authors = MultipleCharFiled(
        field_name='books__authors__name',
        lookup_expr='in',
        distinct=True
    )

    class Meta:
        model = Library
        fields = ['categories', 'authors']


class AuthorFilterSet(django_filters.FilterSet):

    library = django_filters.CharFilter(
        field_name='books__library__name',
        lookup_expr='icontains',
        distinct=True
    )

    category = django_filters.CharFilter(
        field_name='books__category__name',
        lookup_expr='icontains',
        distinct=True
    )

    class Meta:
        model = Author
        fields = ['library', 'category']


class BookFilterSet(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name='category__name',
        lookup_expr='icontains',
        distinct=True
    )

    library = django_filters.CharFilter(
        field_name='library__name',
        lookup_expr='icontains',
        distinct=True
    )

    author = django_filters.CharFilter(
        field_name='authors__name',
        lookup_expr='icontains',
        distinct=True
    )

    class Meta:
        model = Book
        fields = ['category', 'library', 'author']