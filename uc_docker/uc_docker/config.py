class Config:

    CONFIG = {
        "GIT":
        {
            # GitLab's host and port, make sure open-edx can access
            "HOST" : "192.168.122.5",
            "PORT" : 80,

            # GitLab admin account's token
            "ADMIN_TOKEN": "NqTT2HZSs7-gJqp1RSR7",

            # Teacher account information, be used to create repo/project
            "TEACHER":
            {
                "TOKEN": "X1Ua_uPpyijshQX-gPDs"
            }
        },

        "DOCKER":
        {
            # Default docker image's namespace, for example, "mynamespace/mydocker1"
            "NAMESPACE": "uclassroom",

            # memory for each container
            "MEM_LIMIT": "256m",

            # Container's host, may be same as docker server's host,
            # could be visited by students' browsers
            "HOST"   : "mooc.enight.me",

            # URL and TLS information of remote docker server
            "REMOTE_API":
            {
                "URL"    : "2376",  # url of docker host
                "PORT"   : 2376,                       # port of docker daemon
                "CA"     : "/home/moocedx/.docker/ca.pem",  # ca file at local
                "CERT"   : "/home/moocedx/.docker/cert.pem",  # cert file at local
                "KEY"    : "/home/moocedx/.docker/key.pem",  # key file at local
                "VERSION": "1.17"  # docker remote api version
            }
        }
    }
