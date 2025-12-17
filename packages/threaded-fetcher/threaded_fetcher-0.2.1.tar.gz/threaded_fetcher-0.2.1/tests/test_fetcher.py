import time
from threaded_fetcher.fetcher import Fetcher


def test_basic_fetch():
    class DummyResp:
        def __init__(self, code, body=b"ok"):
            self.status_code = code
            self.content = body

    class DummySession:
        def get(self, url, timeout=None):
            time.sleep(0.01)
            return DummyResp(200, b"hello")

    fetcher = Fetcher(max_workers=4, retries=0, session_factory=DummySession)
    urls = ["http://a", "http://b", "http://c"]

    results = fetcher.fetch(urls)

    assert len(results) == 3
    for r in results:
        assert r["status"] == 200
