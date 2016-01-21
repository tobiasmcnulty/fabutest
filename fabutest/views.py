import logging

from django.db import connections
from django.http import HttpResponse, HttpResponseServerError


def health_check(request):
    """
    Health check for the load balancer.
    """
    logger = logging.getLogger('fabutest.views.health_check')
    db_errors = []
    for conn_name in connections:
        conn = connections[conn_name]
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            row = cursor.fetchone()
            assert row[0] == 1
        except Exception, e:
            # note that there doesn't seem to be a way to pass a timeout to
            # psycopg2 through Django, so this will likely not raise a timeout
            # exception
            logger.warning('Caught error checking database connection "{0}"'
                           ''.format(conn_name), exc_info=True)
            db_errors.append(e)
    if not db_errors:
        return HttpResponse('OK')
    else:
        return HttpResponseServerError('Configuration Error')
