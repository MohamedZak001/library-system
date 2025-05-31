import uuid
from datetime import date

from django.db import models
from django.contrib.gis.db import models as gis_models

from users.models import User


class Library(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    location = gis_models.PointField(geography=True)


    def __str__(self):
        return self.name


class Author(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Category(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    library = models.ManyToManyField(Library, related_name='books')
    authors = models.ManyToManyField(Author, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    available_copies = models.PositiveIntegerField(default=1)

    @property
    def is_available(self) -> bool:
        return bool(self.available_copies > 0)

    def __str__(self):
        return self.title


class Borrow(models.Model):
    class BorrowStatus(models.TextChoices):
        BORROWED = 'BORROWED', 'Borrowed'
        RETURNED = 'RETURNED', 'Returned'
        OVERDUE = 'OVERDUE', 'Overdue'

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='borrows')
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name='borrows')
    return_date = models.DateField(editable=False)
    actual_return_date = models.DateField(null=True, default=None, blank=True)
    borrow_date = models.DateField(editable=False)
    status = models.CharField(
        max_length=20,
        choices=BorrowStatus.choices,
        default=BorrowStatus.BORROWED
    )


    @property
    def penalty(self):
        today = date.today()
        overdue_days = (today - self.return_date).days
        return int(overdue_days) if overdue_days > 0 else 0.0


    def __str__(self):
        return f"{self.user} borrowed {self.book.title}"
