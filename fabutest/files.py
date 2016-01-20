import pytz
from django.conf import settings
from django.utils import timezone
from storages.backends.s3boto import S3BotoStorage

__all__ = ['DefaultStorage']


class TimezoneFixMixin(object):
    """
    As of 1.1.8, the S3BotoStorage backend returns modified_time in UTC rather
    than the local timezone, like other storage backends. See the following bug:
    https://bitbucket.org/david/django-storages/issues/167/collectstatic-is-not-overwriting-changed
    """

    def modified_time(self, name):
        time = super(TimezoneFixMixin, self).modified_time(name)
        # make timezone-aware (S3 returns UTC)
        time = pytz.utc.localize(time)
        # convert to Django's timezone
        time = time.astimezone(timezone.get_current_timezone())
        # convert back to a naive datetime (what Django is expecting, at least
        # so long as USE_TZ remains False)
        return time.replace(tzinfo=None)


class DefaultStorage(TimezoneFixMixin, S3BotoStorage):
    """
    S3 file storage class with public access and no authentication.  It uses
    the bucket name specified in the SAM_PUBLIC_BUCKET_NAME setting.
    """
    def __init__(self):
        config = {
            'encryption': False,
            'bucket': settings.STATICFILES_BUCKET_NAME,
            'bucket_acl': 'public-read',
            'acl': 'public-read',
            'secure_urls': True,
            'querystring_auth': False,
        }
        time = super(DefaultStorage, self).__init__(**config)

