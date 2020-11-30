# -*- coding: utf-8 -*-
import gevent
import os
import pickle
import torch

from gevent import monkey
from loguru import logger
from service.federated.models.models import Darknet
from service.federated.utils.options import args_parser
from service.federated.utils.utils import set_random_seed, timer, weights_init_normal
from utils.request_api import RequestApi
from utils.common_utils import Common


monkey.patch_all()

# arguments parsing
args = args_parser()


class Server(object):
    """ the server class is responsible for scheduling each client to participate in federated training, testing and detecting """
    # set random seed for list, numpy, CPU, current GPU and all the GPUs
    set_random_seed(args)

    # create folders for saving model and log information
    args.model_folder_path = os.path.join('./save')
    args.log_folder_path = os.path.join('./log')

    if not os.path.exists(args.model_folder_path):
        os.makedirs(args.model_folder_path)
    if not os.path.exists(args.log_folder_path):
        os.makedirs(args.log_folder_path)

    # add device, model and log file path arguments
    args.device = torch.device('cpu')

    args.model_file_path = os.path.join(args.model_folder_path,
                                        'D_{}_M_{}_SE_{}_CE_{}.pkl'.format(args.dataset, args.model,
                                                                                 args.server_epoch, args.client_epoch))
    args.log_file_path = os.path.join(args.log_folder_path,
                                        'D_{}_M_{}_SE_{}_CE_{}.log'.format(args.dataset, args.model,
                                                                                 args.server_epoch, args.client_epoch))

    # initialize log output configuration
    logger.add(args.log_file_path)

    # initiate model and load pretrained model weights
    model = Darknet(config_path=args.model_def, image_size=args.image_size).to(args.device)
    model.apply(weights_init_normal)

    if args.pretrained_weights:
        if args.pretrained_weights.endswith(".pth"):
            model.load_state_dict(torch.load(args.pretrained_weights))
        else:
            model.load_darknet_weights(args.pretrained_weights)

    ip_lst = [ip for ip in args.client_ips.split(",")]
    port_lst = [port for port in args.client_ports.split(",")]
    federated_train_size_urls = ["http://{}:{}/federated_train_size".format(ip, port) for (ip, port) in
                                 zip(ip_lst, port_lst)]
    federated_train_urls = ["http://{}:{}/federated_train".format(ip, port) for (ip, port) in zip(ip_lst, port_lst)]
    federated_test_urls = ["http://{}:{}/federated_test".format(ip, port) for (ip, port) in zip(ip_lst, port_lst)]
    federated_detect_urls = ["http://{}:{}/federated_detect".format(ip, port) for (ip, port) in zip(ip_lst, port_lst)]

    server_model_params = model.state_dict()
    best_model_params = None
    client_ratio_lst = []

    @classmethod
    def call_federated_train_size(cls):
        """ get the training data ratio of each client """
        with timer("call federated train size", logger):
            train_jobs = [gevent.spawn(RequestApi.request, method="GET", url=federated_train_size_url,
                                       custom_headers={"Content-Type": "application/json"}) for federated_train_size_url
                          in cls.federated_train_size_urls]
            gevent.joinall(train_jobs, timeout=args.timeout)

            for train_job in train_jobs:
                federated_train_size = Common.get_dict_by_json_str_func(train_job.value['data'])["federated_train_size"]
                cls.client_ratio_lst.append(federated_train_size)

            logger.info("before normalization: client_ratio_lst: {}".format(cls.client_ratio_lst))
            client_ratio_sum = sum(cls.client_ratio_lst)
            cls.client_ratio_lst = [ratio / client_ratio_sum for ratio in cls.client_ratio_lst]
            logger.info("after normalization: client_ratio_lst: {}".format(cls.client_ratio_lst))

    @classmethod
    def call_federated_train(cls):
        """ call the model of each client for federated training """
        with timer("call federated train", logger):
            train_loss = []
            best_epoch = None
            best_loss = float('inf')

            for epoch in range(1, args.server_epoch + 1):
                with timer('train for epoch {}/{}'.format(epoch, args.server_epoch), logger):

                    pickled_epoch = Common.get_bytes_by_pickle_object_func(epoch)
                    pickled_server_model_params = Common.get_bytes_by_pickle_object_func(cls.server_model_params)

                    train_jobs = [gevent.spawn(RequestApi.request, method="POST", url=federated_train_url,
                                               params={"server_epoch": pickled_epoch,
                                                       "server_model_params": pickled_server_model_params},
                                               custom_headers={"Content-Type": "multipart/form-data"}) for
                                  federated_train_url in cls.federated_train_urls]
                    gevent.joinall(train_jobs, timeout=args.timeout)

                    avg_loss = 0.0
                    client_weight_lst = []

                    for idx, train_job in enumerate(train_jobs):
                        returned_client_model_params = Common.get_object_by_pickle_bytes_func(train_job.value['data'])[
                            "client_model_params"]
                        returned_epo_avg_loss = Common.get_object_by_pickle_bytes_func(train_job.value['data'])[
                            "epo_avg_loss"]

                        # update the average training loss of all clients for the epoch
                        avg_loss += (returned_epo_avg_loss - avg_loss) / (idx + 1)

                        client_weight_lst.append(returned_client_model_params)

                    for key in client_weight_lst[-1].keys():
                        client_weight_lst[-1][key] = cls.client_ratio_lst[-1] * client_weight_lst[-1][key]
                        for idx in range(0, len(client_weight_lst) - 1):
                            client_weight_lst[-1][key] += cls.client_ratio_lst[idx] * client_weight_lst[idx][key]

                    cls.server_model_params = client_weight_lst[-1]

                    logger.info('epoch {:3d}, average loss {:.3f}'.format(epoch, avg_loss))
                    train_loss.append(avg_loss)

                    # save the model, loss and epoch with the smallest training average loss for all the epochs
                    if avg_loss < best_loss:
                        best_loss = avg_loss
                        best_epoch = epoch
                        cls.best_model_params = cls.server_model_params

            logger.info("best train loss: {}".format(best_loss))
            logger.info("best epoch: {}".format(best_epoch))
            pickle.dump(cls.best_model_params, open(args.model_file_path, "wb"))

    @classmethod
    def call_federated_test(cls):
        """ send the best model to all the clients for testing after the federated training """
        pickled_best_model_params = Common.get_bytes_by_pickle_object_func(cls.best_model_params)
        with timer("call federated test", logger):
            test_jobs = [gevent.spawn(RequestApi.request, method="POST", url=federated_test_url,
                                      params={"best_model_params": pickled_best_model_params},
                                      custom_headers={"Content-Type": "multipart/form-data"}) for federated_test_url in
                         cls.federated_test_urls]
            gevent.joinall(test_jobs, timeout=args.timeout)

    @classmethod
    def call_federated_detect(cls):
        """ send the best model to all the clients for detecting after the federated training """
        pickled_best_model_params = Common.get_bytes_by_pickle_object_func(cls.best_model_params)
        with timer("call federated detect", logger):
            detect_jobs = [gevent.spawn(RequestApi.request, method="POST", url=federated_detect_url,
                                        params={"best_model_params": pickled_best_model_params},
                                        custom_headers={"Content-Type": "multipart/form-data"}) for federated_detect_url in
                         cls.federated_detect_urls]
            gevent.joinall(detect_jobs, timeout=args.timeout)


if __name__ == "__main__":
    Server.call_federated_train_size()
    Server.call_federated_train()
    Server.call_federated_test()
    Server.call_federated_detect()
