from flask import Flask, request
from datetime import datetime


HEADERS = ('X-Forwarded-For', 'Accept-Language', 'User-Agent')
BROWSER_DEPENDENT = ('Sec-Ch-Ua', 'Sec-Ch-Ua-Mobile', 'Sec-Ch-Ua-Platform')
HEADERS = HEADERS + BROWSER_DEPENDENT
REQUEST = ('url',)
LOG_FILE = 'requests.log'


class Log:
    def __init__(self, app: Flask):
        self.app = app
        # self._init_log()

    def log(self):
        if '/static/' in request.url:
            return

        def get_header(name: str):
            return request.headers.get(name)
        print(request.headers)
        headers = {}
        for i in HEADERS:
            headers[i] = get_header(i)
        for i in REQUEST:
            headers[i.title()] = getattr(request, i, None)
        print(headers)
        # self.log_to_file(headers)

    def log_to_file(self, headers: dict):
        date = datetime.utcnow()
        msg = ', '.join([f'{k}:{v}' for k, v in headers.items()])
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f'{msg}\n')

    def _init_log(self):
        self.log = self.app.before_request(self.log)
