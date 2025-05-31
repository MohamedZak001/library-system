from rest_framework.throttling import ScopedRateThrottle



class BookBorrowRateThrottle(ScopedRateThrottle):
    scope = 'borrow_book'



class BookReturnRateThrottle(ScopedRateThrottle):
    scope = 'return_book'