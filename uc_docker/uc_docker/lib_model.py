import datetime


class Docker(object):

    def __init__(self):
        self._name = ""
        self._lab = Lab()
        self._creation_time = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S")
        self._last_start_time = ""
        self._status = ""
        self._container_id = ""
        self._host = ""
        self._port = 0
        self._vnc = 0

    def object_to_dict(self):
        dic = dict(
            name=self._name,
            lab=self._lab.object_to_dict(),
            creation_time=self._creation_time,
            last_start_time=self._last_start_time,
            status=self._status,
            container_id=self._container_id,
            host=self._host,
            port=self._port,
            vnc=self._vnc)
        return dic

    @staticmethod
    def dict_to_object(dic):
        obj = Docker()
        obj.name = dic["name"]
        obj.lab = Lab.dict_to_object(dic["lab"])
        obj.creation_time = dic["creation_time"]
        obj.last_start_time = dic["last_start_time"]
        obj.status = dic["status"]
        obj.container_id = dic["container_id"]
        obj.host = dic["host"]
        obj.port = dic["port"]
        obj.vnc = dic["vnc"]
        return obj

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def get_lab(self):
        return self._lab

    def set_lab(self, lab):
        self._lab = lab

    def get_creation_time(self):
        return self._creation_time

    def set_creation_time(self, time):
        self._creation_time = time

    def get_last_start_time(self):
        return self._last_start_time

    def set_last_start_time(self, value):
        self._last_start_time = value

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._status = value

    def get_container_id(self):
        return self._container_id

    def set_container_id(self, value):
        self._container_id = value

    def get_host(self):
        return self._host

    def set_host(self, value):
        self._host = value

    def get_port(self):
        return self._port

    def set_port(self, value):
        self._port = value

    def get_vnc(self):
        return self._vnc

    def set_vnc(self, value):
        self._vnc = value

    name = property(get_name, set_name)
    lab = property(get_lab, set_lab)
    creation_time = property(get_creation_time, set_creation_time)
    last_start_time = property(get_last_start_time, set_last_start_time)
    status = property(get_status, set_status)
    container_id = property(get_container_id, set_container_id)
    host = property(get_host, set_host)
    port = property(get_port, set_port)
    vnc = property(get_vnc, set_vnc)


class Lab(object):
    def __init__(self):
        self._name = ""
        self._desc = ""
        self._docker_file = ""
        self._teacher = Teacher()
        self._project = ""
        self._creation_time = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S")
        self._make_scripts = ""
        self._status = ""

    def object_to_dict(self):
        dic = dict(
            name=self._name,
            desc=self._desc,
            docker_file=self._docker_file,
            teacher=self._teacher.object_to_dict(),
            project=self._project,
            creation_time=self._creation_time,
            make_scripts=self._make_scripts,
            status=self._status)
        return dic

    @staticmethod
    def dict_to_object(dic):
        obj = Lab()
        obj.name = dic["name"]
        obj.desc = dic["desc"]
        obj.docker_file = dic["docker_file"]
        obj.teacher = Teacher.dict_to_object(dic["teacher"])
        obj.project = dic["project"]
        obj.creation_time = dic["creation_time"]
        obj.make_scripts = dic["make_scripts"]
        obj.status = dic["status"]
        return obj

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    def get_desc(self):
        return self._desc

    def set_desc(self, value):
        self._desc = value

    def get_docker_file(self):
        return self._docker_file

    def set_docker_file(self, value):
        self._docker_file = value

    def get_teacher(self):
        return self._teacher

    def set_teacher(self, value):
        self._teacher = value

    def get_project(self):
        return self._project

    def set_project(self, value):
        self._project = value

    def get_creation_time(self):
        return self._creation_time

    def set_creation_time(self, value):
        self._creation_time = value

    def get_make_scripts(self):
        return self._make_scripts

    def set_make_scripts(self, value):
        self._make_scripts = value

    def get_status(self):
        return self._status

    def set_status(self, value):
        self._status = value

    name = property(get_name, set_name)
    desc = property(get_desc, set_desc)
    docker_file = property(get_docker_file, set_docker_file)
    teacher = property(get_teacher, set_teacher)
    project = property(get_project, set_project)
    creating_time = property(get_creation_time, set_creation_time)
    make_scripts = property(get_make_scripts, set_make_scripts)
    status = property(get_status, set_status)


class User(object):
    def __init__(self):
        self._name = ""
        self._git_id = 0

    def get_name(self):
        return self._name

    def set_name(self, value):
        self._name = value

    def get_git_id(self):
        return self._git_id

    def set_git_id(self, value):
        self._git_id = value

    name = property(get_name, set_name)
    git_id = property(get_git_id, set_git_id)

    def object_to_dict(self):
        dic = dict(
            name=self._name,
            git_id=self._git_id)
        return dic

    @staticmethod
    def dict_to_object(dic):
        obj = User()
        obj.name = dic["name"]
        obj.git_id = dic["git_id"]
        return obj


class Teacher(User):
    def __init__(self):
        User.__init__(self)

    @staticmethod
    def dict_to_object(dic):
        obj = Teacher()
        obj.name = dic["name"]
        obj.git_id = dic["git_id"]
        return obj