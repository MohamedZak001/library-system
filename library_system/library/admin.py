from django.contrib import admin
from library.models import Book, Library, Borrow, Category, Author

admin.site.register(Book)
admin.site.register(Library)
admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Borrow)
