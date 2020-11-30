from api import my_api
from service.federated.client import Client
from utils.common_utils import Common
from flask import request


@my_api.route('/')
def index():
    return '<h1>Hello, this is client!</h1>'


@my_api.route("/federated_train_size", methods=["GET", "POST"])
def federated_train_size():
    return Client.get_federated_train_size()


@my_api.route("/federated_train", methods=["GET", "POST"])
def federated_train():
    # receive the server training epoch and initial or federated averaging model
    pickled_server_epoch = request.files["server_epoch"].read()
    pickled_server_model_params = request.files["server_model_params"].read()

    server_epoch = Common.get_object_by_pickle_bytes_func(pickled_server_epoch)
    server_model_params = Common.get_object_by_pickle_bytes_func(pickled_server_model_params)

    # return the local model after training of current client to server
    return Client.train(server_model_params=server_model_params, epoch=server_epoch)


@my_api.route("/federated_test", methods=["GET", "POST"])
def federated_test():
    # receive the final best model from server and do the evaluating
    pickled_best_model_params = request.files["best_model_params"].read()

    best_model_params = Common.get_object_by_pickle_bytes_func(pickled_best_model_params)

    return Client.test(test_model_params=best_model_params, mode="test")

@my_api.route("/federated_detect", methods=["GET", "POST"])
def federated_detect():
    # receive the final best model from server and do the evaluating
    pickled_best_model_params = request.files["best_model_params"].read()

    best_model_params = Common.get_object_by_pickle_bytes_func(pickled_best_model_params)

    return Client.detect(detect_model_params=best_model_params)

