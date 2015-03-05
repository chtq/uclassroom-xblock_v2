class Config:

    CONFIG = {
        "GIT":
        {
            # GitLab's host and port, make sure open-edx can access
            "HOST" : "192.168.0.191",
            "PORT" : 80,

            # GitLab admin account's token
            "ADMIN_TOKEN": "yzH18DzzyEekAVYkroAe",

            # Teacher account information, be used to create repo/project
            "TEACHER":
            {
                "TOKEN": "GzHEiRsg1aCSApDDZMFZ"
            }
        },

        "DOCKER":
        {
            # Default docker image's namespace, for example, "mynamespace/mydocker1"
            "NAMESPACE": "uclassroom",

            # Container's host, may be same as docker server's host,
            # could be visited by students' browsers
            "HOST"   : "uClassroom",

            # URL and TLS information of remote docker server
            "REMOTE_API":
            {
                "URL"    : "https://uClassroom:2376",  # url of docker host
                "CA"     : "/home/ggxx/.docker/ca.pem",  # ca file at local
                "CERT"   : "/home/ggxx/.docker/cert.pem",  # cert file at local
                "KEY"    : "/home/ggxx/.docker/key.pem",  # key file at local
                "VERSION": "1.17"  # docker remote api version
            }
        }
    }