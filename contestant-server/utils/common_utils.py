import json
import pickle

from loguru import logger


class Common:
    @staticmethod
    def print_msg_func(msg):
        logger.info(" ======> {} ".format(msg))

    @staticmethod
    def get_dict_by_json_file_func(file_path):
        """ get the dict by the json file (key-value) """
        file = open(file_path, "r", encoding="utf8")
        data_dict = json.loads(file.read())
        file.close()
        return data_dict

    @staticmethod
    def merge_dict_func(dict_1, dict_2):
        """ merge two dicts into one dict """
        return dict_2.update(dict_1)

    @staticmethod
    def get_json_by_dict_func(target: object):
        """ get the json file by the dict or list (set ensure_ascii=False for preventing Chinese error codes """
        return json.dumps(target, ensure_ascii=False)

    @staticmethod
    def get_dict_by_json_str_func(string: str):
        """ get the json file by the string """
        return json.loads(string)

    @staticmethod
    def get_bytes_by_pickle_object_func(target: object):
        """ get binary file by the object """
        return pickle.dumps(target)

    @staticmethod
    def get_object_by_pickle_bytes_func(byte_str: bytes):
        """ get the object by the binary file """
        return pickle.loads(byte_str)
