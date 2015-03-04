class Config:

    CONFIG = {
        "GIT":
        {
            "HOST" : "192.168.0.191",
            "PORT" : 80,
            "ADMIN_TOKEN": "yzH18DzzyEekAVYkroAe",
            # "ADMIN_TOKEN": "dZvpAyzBx--P4GiQ4T6K",
            "TEACHER":
            {
                "NAME": "",
                "TOKEN": "GzHEiRsg1aCSApDDZMFZ"
                # "TOKEN": "MYXs-ghGrsv-5_T_EMyv"
            }
        },
        "DOCKER":
        {
            "NAMESPACE": "uclassroom",
            "HOST"   : "uClassroom",
            "REMOTE_API":
            {
                "URL"    : "https://uClassroom:2376",
                "CA"     : "/home/ggxx/.docker/ca.pem",
                "CERT"   : "/home/ggxx/.docker/cert.pem",
                "KEY"    : "/home/ggxx/.docker/key.pem",
                "VERSION": "1.17"
            }
        }
    }