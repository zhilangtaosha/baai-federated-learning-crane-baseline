class ProjectConf:
    # development environment
    dev = {
        "host": "0.0.0.0",
        "port": 5016,
        "config": {
            "ENV": "dev",
            "DEBUG": True
        }
    }

    # product environment
    pro = {
        "config": {
            "ENV": "pro",
            "DEBUG": False
        }
    }
