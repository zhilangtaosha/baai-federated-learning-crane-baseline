from api import my_api


@my_api.route('/')
def index():
    return '<h1>Hello, this is Server!</h1>'

