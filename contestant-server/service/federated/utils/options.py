# -*- coding: utf-8 -*-
import argparse


def args_parser():
    """ argument parser """
    parser = argparse.ArgumentParser()

    # federated parameters
    parser.add_argument('--server_epoch', type=int, default=20, help="number of server epochs: SE")
    parser.add_argument('--client_epoch', type=int, default=5, help="number of client epochs: CE")
    parser.add_argument('--user_num', type=int, default=2, help="number of users: K")
    parser.add_argument('--timeout', type=float, default=3600, help="the maximum number of seconds to wait: T")

    # model parameters
    parser.add_argument('--model', type=str, default='yolov3', help='model name: M')
    parser.add_argument("--model_def", type=str, default="service/federated/config/preliminary_contest_crane_federal/yolov3_preliminary_contest_crane_federal.cfg",
                        help="path to model definition file")
    parser.add_argument("--pretrained_weights", type=str, default="your/weights/path/weights/darknet53.conv.74",
                        help="if specified starts from checkpoint model")

    # other parameters
    parser.add_argument('--dataset', type=str, default='preliminary_contest_crane_federal', help="name of dataset: D")
    parser.add_argument('--image_size', type=int, default=832, help='width and height of images')
    parser.add_argument('--server_ip', type=str, default="127.0.0.1", help="internet protocol of server")
    parser.add_argument('--server_port', type=int, default=5014, help="port of server")
    parser.add_argument('--client_ips', type=str, default="127.0.0.1,127.0.0.1",
                        help="internet protocols of all the clients")
    parser.add_argument('--client_ports', type=str, default="5015,5016", help="ports of all the clients")
    parser.add_argument('--seed', type=int, default=1, help='random seed (default: 1)')

    args = parser.parse_args()

    return args
