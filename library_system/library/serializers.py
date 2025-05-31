from datetime import timedelta, date

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Library, Book, Author, Category, Borrow


class LibrarySerializer(serializers.ModelSerializer):
    distance = serializers.SerializerMethodField(allow_null=True, read_only=True)

    class Meta:
        model = Library
        fields = ['uuid', 'name', 'address', 'location', "distance"]

    def get_distance(self, obj):
        # return the distance in km
        return obj.distance.km if hasattr(obj, 'distance') else None



class ListAuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['uuid', 'name', 'book_count']

    def get_book_count(self, obj):
        print(obj.books_count)
        return obj.books_count

class ListBookSerializer(serializers.ModelSerializer):
    author_names = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = ['uuid', 'title', 'is_available', 'author_names', 'category_name']

    def get_author_names(self, obj):
        return [author.name for author in obj.authors.all()]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['uuid', 'name']


class BookWithCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['uuid', 'title', 'is_available', 'category']


class ListLoadedAuthorSerializer(serializers.ModelSerializer):
    books = BookWithCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['uuid', 'name', 'books']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'uuid']


class BorrowBookSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    return_date = serializers.DateField(required=True)

    class Meta:
        model = Borrow
        fields = ['return_date', "book", "uuid"]
        read_only_fields = ['borrow_date', "book", "uuid"]

    def validate_return_date(self, value):
        today = date.today()
        max_return_date = today + timedelta(days=30)

        if value > max_return_date:
            raise ValidationError("Return date cannot be more than 1 month from now.")
        if value <= today:
            raise ValidationError("Return date cannot be in the today or in the past.")

        return value

    def validate(self, data):
        user = self.context['request'].user
        book = self.context['book']

        if user.active_borrows >= 3:
            raise ValidationError("Cannot borrow more than 3 books. Return a book to borrow another.")

        if not book.is_available:
            raise ValidationError("This book is currently unavailable.")

        return data


class BookReturnSerializer(serializers.ModelSerializer):
    penalty = serializers.FloatField(read_only=True)
    borrow_date = serializers.SerializerMethodField()
    actual_return_date = serializers.SerializerMethodField()

    class Meta:
        model = Borrow
        fields = ["penalty", 'borrow_date', 'actual_return_date']
        read_only_fields = ['borrow_date', 'actual_return_date', "penalty"]


    def get_borrow_date(self, obj):
        return obj.borrow_date if isinstance(obj.borrow_date, date) else obj.borrow_date.date()

    def get_actual_return_date(self, obj):
        return obj.actual_return_date if isinstance(obj.actual_return_date, date) else obj.actual_return_date.date()