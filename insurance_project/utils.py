# #TODO: add to celery periodic task
# def expired_time_validation():
#         """2.2
#     Если текущая дата > end_date, статус полиса автоматически становится expired."""
#     InsurancePolicy.objects.filter(
#         end_date=timezone.now(),
#         status="AE"
#     ).update(status="ED")
from django.core.exceptions import ValidationError

from core.models import InsurancePolicy, Car


def cancel_active_police(customer):
    """Пользователь может отменить активный полис (status → cancelled)."""
    # TODO: переделать на 1 машина нужная = ее полис отменяется а не на все машины

    customer_cars = Car.objects.filter(customer=customer)
    active_polices = InsurancePolicy.objects.filter(
        car__in=customer_cars,
        status="AE"
    )

    if active_polices.exists():
        # all car's polices status = canceled
        active_polices.update(status="CD")
    else:
        raise ValidationError("Active police didn't found")