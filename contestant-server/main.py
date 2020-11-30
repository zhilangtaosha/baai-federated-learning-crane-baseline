from config import init_app
from api import *

app, server_info_dict = init_app("dev")
app.register_blueprint(my_api)

if __name__ == "__main__":
    app.run(host=server_info_dict["host"], port=server_info_dict["port"], use_reloader=False)
