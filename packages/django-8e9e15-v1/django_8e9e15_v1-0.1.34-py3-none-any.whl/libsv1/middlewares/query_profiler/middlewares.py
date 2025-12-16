import logging
from django.conf import settings
from django.db import connection

logger = logging.getLogger(__name__)

class QueryProfilerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not settings.DEBUG:
            return self.get_response(request)

        response = self.get_response(request)

        self._log_queries()

        return response

    def _log_queries(self):
        ignore_patterns = getattr(settings, 'QUERY_PROFILER_IGNORE_PATTERNS', [])

        queries = connection.queries
        if not queries:
            return

        query_count = len(queries)
        total_time = sum(float(q['time']) for q in queries)

        logger.debug(
            "SQL Query Profiler: %d queries executed in %.2fms",
            query_count, total_time * 1000
        )

        for query in queries:
            sql = query['sql'].lower()

            if any(pattern in sql for pattern in ignore_patterns):
                continue

            logger.debug("-> (%.2fms) %s", float(query['time']) * 1000, query['sql'])