from datetime import datetime, timedelta
import pytz
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from mailing.models import Mail, Logs


def my_job():
    day = timedelta(days=1, hours=0, minutes=0)
    week = timedelta(days=7, hours=0, minutes=0)
    month = timedelta(days=30, hours=0, minutes=0)

    mailing = Mail.objects.all().filter(status='created') \
        .filter(is_active=True) \
        .filter(next_date__lte=datetime.now(pytz.timezone('Europe/Moscow'))) \
        .filter(end_date__gte=datetime.now(pytz.timezone('Europe/Moscow')))

    for mail in mailing:
        mail.status = 'start'
        mail.save()
        emails_list = [client.email for client in mail.mail_to.all()]

        result = send_mail(
            subject=mail.message.title,
            message=mail.message.content,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=emails_list,
            fail_silently=False,
        )

        if result == 1:
            status = 'Отправлено'
        else:
            status = 'Ошибка отправки'

        log = Logs(mailing=mail, status=status)
        log.save()

        mail.last_mailing_time = timezone.now()

        if mail.interval == 'once_a_day':
            mail.next_date = mail.last_mailing_time + day
        elif mail.interval == 'once_a_week':
            mail.next_date = mail.last_mailing_time + week
        elif mail.interval == 'once_a_month':
            mail.next_date = mail.last_mailing_time + month

        if mail.next_date < mail.end_date:
            mail.status = 'created'
        else:
            mail.status = 'finish'
        mail.save()


def get_cache_for_mail():
    if settings.CACHE_ENABLED:
        key = 'mail_count'
        mail_count = cache.get(key)
        if mail_count is None:
            mail_count = Mail.objects.all().count()
            cache.set(key, mail_count)
    else:
        mail_count = Mail.objects.all().count()
    return mail_count


def get_cache_for_active_mail():
    if settings.CACHE_ENABLED:
        key = 'active_mailings_count'
        active_mail_count = cache.get(key)
        if active_mail_count is None:
            active_mail_count = Mail.objects.filter(is_active=True).count()
            cache.set(key, active_mail_count)
    else:
        active_mail_count = Mail.objects.filter(is_active=True).count()
    return active_mail_count
