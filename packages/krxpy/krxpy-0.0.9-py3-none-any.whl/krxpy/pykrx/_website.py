from .base import *


class Post:

    def __init__(self, headers=None):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36" # FakeAgent.random
        }
        if headers is not None:
            self.headers.update(headers)

    def read(self, **params):
        # print(f"Headers : {self.headers}")
        # print(f"Params : {params}")
        resp = requests.post(self.url, headers=self.headers, data=params)
        return resp

    @property
    @abstractmethod
    def url(self):
        return NotImplementedError
