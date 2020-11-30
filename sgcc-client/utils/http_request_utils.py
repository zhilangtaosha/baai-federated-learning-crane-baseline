import requests

from utils.common_utils import Common as common_utils


class HttpRequest:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
            # "Content-Type": "multipart/form-data"
        }
        self.params = None

    def get_func(self, url: str, **k_args):
        common_utils.print_msg_func("request url: %s" % url)

        if "params" in k_args:
            self.params = k_args["params"]

        if "custom_headers" in k_args:
            self.headers = common_utils.merge_dict_func(k_args["custom_headers"], self.headers)

        res_data = requests.get(url=url, params=self.params, headers=self.headers)
        res_data.encoding = "UTF8"
        # common_utils.print_msg_func("return value: %s" % res_data.text)

        if res_data.status_code == 200:
            return {
                "data": res_data.text,
                "time": res_data.elapsed.microseconds / 1000
            }
        else:
            return None

    def post_func(self, url: str, **k_args):
        common_utils.print_msg_func("request url: %s" % url)

        if "params" in k_args:
            self.params = k_args["params"]

        if "custom_headers" in k_args:
            self.headers = common_utils.merge_dict_func(k_args["custom_headers"], self.headers)

        res_data = requests.post(url=url, files=self.params, headers=self.headers)
        res_data.encoding = "UTF8"
        # common_utils.print_msg_func("return value: %s" % res_data.text)

        if res_data.status_code == 200:
            return {
                "data": res_data.content,
                "time": res_data.elapsed.microseconds / 1000
            }
        else:
            return None
