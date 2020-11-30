from flask import Blueprint

my_api = Blueprint("my_api", __name__)

from .my_api import *
