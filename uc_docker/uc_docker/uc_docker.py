import json
import thread
import datetime
import re

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String, List, Boolean
from xblock.fragment import Fragment

from config import Config
from lib_docker_raw import DockerRawHelper
from lib_git import GitLabUtil
from lib_model import Lab, Docker
from lib_util import Util


class UcDockerXBlock(XBlock):

    logger = Util.uc_logger()

    is_new = Boolean(default=True, scope=Scope.user_state, help="is new")
    private_key = String(default="", scope=Scope.user_state, help="SHH Private Key")
    public_key = String(default="", scope=Scope.user_state, help="SHH Public Key")
    git_password = String(default="", scope=Scope.user_state, help="Git password")
    git_id = Integer(default="", scope=Scope.user_state, help="Git id")
    git_user_token = String(default="", scope=Scope.user_state, help="Git private token")
    dockers = List(default=[], scope=Scope.user_state, help="dockers")

    labs = List(default=[], scope=Scope.content, help="labs")

    # config
    CONFIG = Config.CONFIG
    git_host = CONFIG["GIT"]["HOST"]
    git_port = CONFIG["GIT"]["PORT"]
    git_admin_token = CONFIG["GIT"]["ADMIN_TOKEN"]
    docker_host = CONFIG["DOCKER"]["HOST"]
    docker_url = CONFIG["DOCKER"]["REMOTE_API"]["URL"]
    docker_namespace = CONFIG["DOCKER"]["NAMESPACE"]
    docker_mem = CONFIG["DOCKER"]["MEM_LIMIT"]
    ca = CONFIG["DOCKER"]["REMOTE_API"]["CA"]
    cert = CONFIG["DOCKER"]["REMOTE_API"]["CERT"]
    key = CONFIG["DOCKER"]["REMOTE_API"]["KEY"]
    version = CONFIG["DOCKER"]["REMOTE_API"]["VERSION"]
    git_teacher_token = CONFIG["GIT"]["TEACHER"]["TOKEN"]

    docker_helper = DockerRawHelper(docker_host, docker_url, ca, cert, key)

    def student_view(self, context=None):

        # runtime error
        if not hasattr(self.runtime, "anonymous_student_id"):
            return self.message_view("Error in uc_docker (get anonymous student id)", "Cannot get anonymous_student_id in runtime", context)

        # preview in studio
        if self.runtime.anonymous_student_id == "student":

            result, message = GitLabUtil.get_user_projects(self.git_host, self.git_port, self.git_teacher_token)
            if not result:
                return self.message_view("Error in uc_docker (get git projects)", "Cannot get user's projects in git", context)

            context_dict = {
                "labs": self.labs,
                "message": ""
            }
            fragment = Fragment()
            fragment.add_content(Util.render_template('static/html/uc_lab.html', context_dict))
            fragment.add_css(Util.load_resource("static/css/uc_docker.css"))
            fragment.add_javascript(Util.load_resource("static/js/src/uc_lab.js"))
            fragment.initialize_js("UcDockerXBlock")
            return fragment

        # student view in open-edx
        if self.is_new:
            # create git account when first visiting
            student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
            email = student.email
            name = student.first_name + " " + student.last_name
            username = student.username
            self.git_password = Util.create_random_password()
            # first_name, last_name are empty
            if name == " ":
                name = username
            self.logger.info("password is " + self.git_password)

            self.logger.info(self.git_host + "," + str(self.git_port) + "," + self.git_admin_token + "," + name + "," + username + "," + email + "," + self.git_password)
            result, message = GitLabUtil.create_account(self.git_host, self.git_port, self.git_admin_token, name, username, email, self.git_password)
            self.logger.info("create_account result:")
            self.logger.info(result)
            self.logger.info(message)
            if not result:
                return self.message_view("Error in uc_docker (create git account)", message, context)

            result, message = GitLabUtil.login(self.git_host, self.git_port, username, self.git_password)
            self.logger.info("login result:")
            self.logger.info(result)
            self.logger.info(message)
            if not result:
                return self.message_view("Error in uc_docker (login git account)", message, context)

            try:
                message = json.loads(message)
                self.git_id = message["id"]
                self.git_user_token = message["private_token"]
            except Exception, ex:
                return self.message_view("Error in uc_docker (load json string)", message, context)

            try:
                self.private_key, self.public_key = Util.gen_ssh_keys(email)
            except Exception, ex:
                return self.message_view("Error in uc_docker (gen ssh key)", ex, context)

            result, message = GitLabUtil.add_ssh_key(self.git_host, self.git_port, self.git_user_token, "uClassroom default", self.public_key)
            self.logger.info("add_ssh_key result:")
            self.logger.info(result)
            self.logger.info(message)
            if not result:
                return self.message_view("Error in uc_docker (add git ssh key)", message, context)

            self.is_new = False
        else:
            # TODO update git account
            student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
            username = student.username
            print 'OK'

        context_dict = {
            "labs": self._get_available_labs(),
            "dockers": self.dockers,
            "password": self.git_password,
            "username": username,
            "message": "",
            "report":""
        }
        fragment = Fragment()
        fragment.add_content(Util.render_template('static/html/uc_docker.html', context_dict))
        fragment.add_css(Util.load_resource("static/css/uc_docker.css"))
        fragment.add_javascript(Util.load_resource("static/js/src/uc_docker.js"))
        fragment.initialize_js("UcDockerXBlock")
        return fragment

    def studio_view(self, context=None):
        # to add new lab
        context_dict = {
            "labs": self.labs,
            "docker_file": """FROM uclassroom/ucore-vnc-base
MAINTAINER ggxx<ggxx120@gmail.com>

RUN cd / && git clone https://github.com/chyyuu/ucore_lab.git my_lab && cd /my_lab/ && git remote remove origin
ENTRYPOINT ["bash"]
""",
            "message": ""
        }
        fragment = Fragment()
        fragment.add_content(Util.render_template('static/html/uc_lab_new.html', context_dict))
        fragment.add_css(Util.load_resource("static/css/uc_docker.css"))
        fragment.add_javascript(Util.load_resource("static/js/src/uc_lab.js"))
        fragment.initialize_js("UcDockerXBlock")
        return fragment

    def message_view(self, title, message, context=None):
        context_dict = {
            "title": title,
            "message": message
        }
        fragment = Fragment()
        fragment.add_content(Util.render_template('static/html/uc_message.html', context_dict))
        fragment.add_css(Util.load_resource("static/css/uc_docker.css"))
        fragment.add_javascript(Util.load_resource("static/js/src/uc_null.js"))
        fragment.initialize_js("UcDockerXBlock")
        return fragment

    @XBlock.json_handler
    def create_lab(self, data, suffix=""):
        if not self.check_obj_name(data["name"]):
            return {"result": False, "message": "Invalid lab name"}

        if self._get_lab(data["name"]) is not None:
            return {"result": False, "message": "Lab name exists"}

        lab = Lab()
        lab.name = data["name"]
        lab.desc = data["desc"]
        lab.project = data["project"]
        lab.docker_file = data["dockerfile"]
        lab.make_scripts = data["makescripts"]
        lab.creation_time = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S")
        lab.status = "building"
        self.labs.append(lab.object_to_dict())
        self.save()
        build_lab_docker_worker(self, lab)
        # I don't know why self.labs cannot be saved/updated in new thread
        # thread.start_new_thread(build_lab_docker_worker, (self, lab))
        return {"result": True}

    @XBlock.json_handler
    def get_lab(self, data, suffix=""):
        print "get_lab"
        for l in self.labs:
            if l["name"] == data["name"]:
                return {
                    "result": True,
                    "name": l["name"],
                    "desc": l["desc"],
                    "project": l["project"],
                    "dockerfile": l["docker_file"],
                    "makescripts": l["make_scripts"]}
        return {"result": False}

    @XBlock.json_handler
    def view_result(self, data, suffix=""):
        student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        user_name = student.username
        
        dockername=data["name"]
        conn = pymongo.Connection('192.168.122.115', 27017)
        db = conn.test
        user = db.user
        result = user.find_one({"username":user_name, "dockername":dockername})
        conn.disconnect()
        return {"message": result["result"]}
    @XBlock.json_handler
    def create_docker(self, data, suffix=""):
        if not self.check_obj_name(data["name"]):
            return {"result": False, "message": "Invalid docker name"}

        if self._get_docker(data["name"]) is not None:
            return {"result": False, "message": "Docker name exists"}

        docker = Docker()
        docker.name = data["name"]
        docker.lab = Lab.dict_to_object(self._get_lab(data["lab"]))
        docker.status = "building"
        self.dockers.append(docker.object_to_dict())
        self.save()

        student = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        user_email = student.email
        user_name = student.username
        thread.start_new_thread(build_student_docker_worker, (self, docker, user_name, user_email))
        return {"result": True}

    @XBlock.json_handler
    def run_docker(self, data, suffix=""):
        print "run_docker"
        docker = Docker.dict_to_object(self._get_docker(data["name"]))
        docker.status = "starting"
        self._update_docker(docker)
        self.save()
        thread.start_new_thread(start_student_docker_worker, (self, docker))
        return {"result": True}

    @XBlock.json_handler
    def stop_docker(self, data, suffix=""):
        print "stop_docker"
        docker = Docker.dict_to_object(self._get_docker(data["name"]))
        docker.status = "stopping"
        self._update_docker(docker)
        self.save()
        thread.start_new_thread(stop_student_docker_worker, (self, docker))
        return {"result": True}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("UcDockerXBlock", """<vertical_demo><uc_docker/></vertical_demo>"""),
        ]

    def check_obj_name(self, obj_name):
        exp_name = "[a-z]+[a-z0-9_\-]*$"
        if re.match(exp_name, obj_name) is None:
            return False
        return True

    def _get_lab(self, name):
        for lab in self.labs:
            if lab["name"] == name:
                return lab
        return None

    def _get_available_labs(self):
        labs = []
        for lab in self.labs:
            if lab["status"] == "ready":
                labs.append(lab)
        return labs

    def _get_docker(self, name):
        for docker in self.dockers:
            if docker["name"] == name:
                return docker
        return None

    def _update_docker(self, docker):
        for d in self.dockers:
            if d["name"] == docker.name:
                self.dockers.remove(d)
                self.dockers.append(docker.object_to_dict())
                break

    def _update_lab(self, lab):
        for l in self.labs:
            if l["name"] == lab.name:
                self.labs.remove(l)
                self.labs.append(lab.object_to_dict())
                break

    def lab_changed_callback(self, lab):
        self.logger.info("lab_changed_callback, status:" + lab.status)
        self._update_lab(lab)
        self.save()

    def docker_changed_callback(self, docker):
        self.logger.info("docker_changed_callback, status:" + docker.status)
        self._update_docker(docker)
        self.save()


def build_lab_docker_worker(xb, lab):
    xb.logger.info("build_lab_docker_worker.start")
    xb.docker_helper.build_lab_docker("{0}/{1}".format(xb.docker_namespace, lab.name), lab.docker_file)
    lab.status = "ready"
    xb.lab_changed_callback(lab)


def build_student_docker_worker(xb, docker, user_name, user_email):
    xb.logger.info("build_student_docker_worker.start")
    xb.docker_helper.build_student_docker("{0}/{1}".format(user_name, docker.name), docker, xb.private_key, xb.public_key, user_name, xb.git_password, user_email, xb.git_user_token, xb.git_host, xb.git_port, xb.git_teacher_token, xb.docker_namespace, xb.docker_mem)
    docker.status = "ready"
    xb.docker_changed_callback(docker)


def start_student_docker_worker(xb, docker):
    xb.logger.info("start_student_docker_worker.start")
    xb.docker_helper.start_student_docker(docker)
    docker.status = "running"
    xb.docker_changed_callback(docker)


def stop_student_docker_worker(xb, docker):
    xb.logger.info("stop_student_docker_worker.start")
    xb.docker_helper.stop_student_docker(docker)
    docker.status = "ready"
    xb.docker_changed_callback(docker)
