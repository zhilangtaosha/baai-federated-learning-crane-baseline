from utils.common_utils import Common


class CustomResult:
    @staticmethod
    def success(**k_args):
        res_data = {
            "status_code": 0,
            "msg": "request succeeded! "
        }

        if "data" in k_args:
            res_data["data"] = k_args["data"]
        else:
            res_data["data"] = None

        if "time" in k_args:
            res_data["time"] = k_args["time"]

        return Common.get_json_by_dict_func(res_data)

    @staticmethod
    def error(**k_args):
        res_data = {
            "status_code": -1,
            "data": None
        }

        if "msg" in k_args:
            res_data["msg"] = k_args["msg"]
        else:
            res_data["msg"] = "request failed! "

        if "time" in k_args:
            res_data["time"] = k_args["time"]

        return Common.get_json_by_dict_func(res_data)
