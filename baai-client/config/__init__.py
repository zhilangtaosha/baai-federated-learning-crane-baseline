from flask import Flask
from config.project_conf import ProjectConf


def init_app(config_name: str):
    """ initialize the project (dev or pro) """
    # read the environment config file
    dev_dict = ProjectConf.dev
    pro_dict = ProjectConf.pro
    server_info_dict = {}

    app = Flask(__name__)

    if config_name == "dev":
        set_flask_config_func(app, dev_dict["config"])
        server_info_dict["host"] = dev_dict["host"]
        server_info_dict["port"] = dev_dict["port"]

    if config_name == "pro":
        set_flask_config_func(app, pro_dict["config"])
        server_info_dict["host"] = pro_dict["host"]
        server_info_dict["port"] = pro_dict["port"]

    return app, server_info_dict


def set_flask_config_func(app, config: dict):
    """ set the flask config file """
    for key, value in config.items():
        app.config[key] = value
