from utils.http_request_utils import HttpRequest


class RequestApi:
    @staticmethod
    def request(method: str, url: str, **k_args):
        """ check if the request is GET or POST """
        req = HttpRequest()
        res_data = None

        if method == "GET":
            res_data = req.get_func(url=url, **k_args)

        if method == "POST":
            res_data = req.post_func(url=url, **k_args)

        return res_data


if __name__ == '__main__':
    RequestApi.request(method="GET", url="http://localhost:5002/test/getName", params={"name": "Tom"})
