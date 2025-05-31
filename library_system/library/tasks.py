from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Borrow


@shared_task
def send_confirmation_email(borrow_id):

    borrow = Borrow.objects.select_related("book", "user").filter(id=borrow_id).first()

    if not borrow:
        return f"Borrow with ID {borrow_id} not found"

    user = borrow.user
    book = borrow.book
    subject = 'Library Borrow Confirmation'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@library.com')

    message = f"""
        Dear {user.first_name or user.username},

        You have successfully borrowed "{book.title}".

        Borrow Details:
        - Book: {book.title}
        - Author: {getattr(book, 'author', 'Unknown')}
        - Borrow Date: {borrow.borrow_date}
        - Return Date: {borrow.return_date}

        Please return the book by the due date.

        Thank you!
        Library Management System
        """

    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[user.email],
        fail_silently=False,
    )


@shared_task
def update_borrows():
    today = timezone.now().date()
    updated_count = Borrow.objects.filter(
        return_date__lt=today,
        status=Borrow.BorrowStatus.BORROWED
    ).update(status=Borrow.BorrowStatus.OVERDUE)
    return f"Updated {updated_count} borrows as overdue."



@shared_task
def send_daily_borrow_reminders():
    today = timezone.now().date()
    reminder_threshold = today + timedelta(days=3)

    # Find borrows due within the next 3 days with status BORROWED
    borrows = Borrow.objects.filter(
        return_date__lte=reminder_threshold,
        return_date__gte=today,
        status=Borrow.BorrowStatus.BORROWED
    ).select_related("book", "user")

    for borrow in borrows:
        days_remaining = (borrow.return_date - today).days
        subject = "Reminder"
        message = f'Reminder: Return {borrow.book.title} in {days_remaining} Day{"s" if days_remaining != 1 else ""}'
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL')
        to_email = borrow.user.email
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=True,
        )


@shared_task
def test_celery_beat():
    return "Celert Beat is working!"