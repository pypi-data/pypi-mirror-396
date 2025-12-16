import seldom


class TestRequest(seldom.TestCase):

    def start(self):
        self.url = "http://httpbin.org/post"

    def test_case(self):
        headers = {"User-Agent": "python-requests/2.25.0", "Accept-Encoding": "gzip, deflate", "Accept": "application/json", "Connection": "keep-alive", "Host": "httpbin.org", "Content-Length": "36", "Origin": "http://httpbin.org", "Content-Type": "application/json", "Cookie": "lang=zh"}
        cookies = {"lang": "zh"}
        self.post(self.url, json={"key1": "value1", "key2": "value2"}, headers=headers, cookies=cookies)
        self.assertStatusCode(200)


if __name__ == '__main__':
    seldom.main()
