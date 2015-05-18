__author__ = 'ggxx'

import datetime
import docker
import json

from io import BytesIO
from lib_git import GitLabUtil
from lib_util import Util


class DockerHelper(object):

    logger = Util.uc_logger()

    def __init__(self, host, url, ca, cert, key, version):
        self.logger.info("__init__")
        self._host = host
        tls_config = docker.tls.TLSConfig(
            client_cert=(cert, key),
            ca_cert=ca,
            verify = True
        )
        self._client = docker.Client(base_url=url, tls=tls_config, version=version)

    def build_lab_docker(self, image_name, docker_file_text):
        self.logger.info("DockerHelper.build_lab_docker")
        f = BytesIO(docker_file_text.encode('utf-8'))
        response = [line for line in self._client.build(tag=image_name, rm=True, fileobj=f)]
        self.logger.info("docker.build:")
        for line in response:
            self.logger.info(line)
        self.logger.info("DockerHelper.build_lab_docker.complete")

    def build_student_docker(self, image_name, docker_obj, private_key, public_key, user_name, user_psw, user_email, user_token, git_host, git_port, teacher_token, docker_namespace):
        self.logger.info("DockerHelper.build_student_docker")
        result, message = GitLabUtil.get_user(git_host, git_port, teacher_token)
        if not result:
            self.logger.info(message)
            return
        teacher_id = json.loads(message)["id"]
        teacher_name = json.loads(message)["username"]

        project_name = docker_obj.name
        docker_file_text = self._create_ucore_docker_file(docker_obj, private_key, public_key, user_name, user_psw, user_email, git_host, git_port, docker_namespace, teacher_name)
        docker_file = BytesIO(docker_file_text.encode('utf-8'))

        result, message = GitLabUtil.create_private_project(git_host, git_port, user_token, project_name)
        if not result:
            self.logger.info(message)
            return

        result, message = GitLabUtil.add_project_developer(git_host, git_port, user_token, user_name, project_name, teacher_id)
        if not result:
            self.logger.info(message)
            return

        response = [line for line in self._client.build(tag=image_name, rm=True, fileobj=docker_file)]
        self.logger.info("build docker result:")
        for line in response:
            self.logger.info(line)

        container = self._client.create_container(image=image_name, ports=[8080])
        self.logger.info("docker.create_container:")
        self.logger.info(container)
        docker_obj.container_id = container["Id"]
        self.logger.info("DockerHelper.build_student_docker.complete")

    def start_student_docker(self, docker_obj):
        print "DockerHelper.start_student_docker"
        self._client.start(docker_obj.container_id, port_bindings={6080: ("0.0.0.0", ), 8080: ("0.0.0.0",)})
        port = self._client.port(docker_obj.container_id, 8080)
        vnc = self._client.port(docker_obj.container_id, 6080)
        docker_obj.host = self._host
        docker_obj.port = port[0]["HostPort"]
        docker_obj.vnc = vnc[0]["HostPort"]
        docker_obj.last_start_time = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S")
        self.logger.info("DockerHelper.start_student_docker.complete")

    def stop_student_docker(self, docker_obj):
        print "DockerHelper.stop_student_docker"
        self._client.stop(docker_obj.container_id)
        print "DockerHelper.stop_student_docker.complete"

    def _create_ucore_docker_file(self, docker_obj, private_key, public_key, user_name, user_pwd, user_email, git_host, git_port, docker_namespace, teacher_name):
        text = (
            'FROM ' + docker_namespace + '/' + docker_obj.lab.name +
            '\nMAINTAINER ggxx<ggxx120@gmail.com>' +
            '\n' +
            '\nRUN echo -ne "' + private_key.replace("\n", "\\n") + '" > /root/.ssh/id_rsa;\\' +
            '\n  echo "' + public_key + '" > /root/.ssh/id_rsa.pub;\\' +
            '\n  chmod 0600 /root/.ssh/id_rsa ;\\' +
            '\n  echo -ne "' + self.startup_shell + '" > /startup.sh;\\' +
            '\n  chmod +x /startup.sh;\\' +
            '\n  echo -ne "' + self.tty_config.format(user_name, user_pwd).replace("\n", "\\n") + '" > /opt/ttyjs/ttyjs-config.json;\\' +
            '\n  echo ' + user_pwd + ' | echo $(vncpasswd -f) > /root/.vnc/passwd;\\' +
            '\n  chmod 0600 /root/.vnc/passwd;\\' +
            '\n  git config --global user.name "' + user_name + '" ;\\' +
            '\n  git config --global user.email "' + user_email + '" ;\\' +
            '\n  echo -ne "StrictHostKeyChecking no\\nUserKnownHostsFile /dev/null\\n" >> /etc/ssh/ssh_config ;\\' +
            '\n  cd /my_lab/ ;\\' +
            '\n  git remote remove origin; \\' +
            '\n  git remote add origin git@' + git_host + ':' + user_name + '/' + docker_obj.name + '.git; \\'
            '\n  git push -u origin master' +
            '\n' +
            '\nEXPOSE 6080' +
            '\nEXPOSE 8080' +
            '\nENTRYPOINT ["/startup.sh"]',)
        self.logger.info(text[0])
        return text[0]

    startup_shell = """#!/usr/bin/env bash
(vncserver && /opt/noVNC/utils/launch.sh --vnc localhost:5901) & tty.js --config /opt/ttyjs/ttyjs-config.json"""

    tty_config = """{{
  \\"users\\": {{ \\"{0}\\": \\"{1}\\" }},
  \\"port\\": 8080,
  \\"hostname\\": \\"0.0.0.0\\",
  \\"shell\\": \\"bash\\",
  \\"limitGlobal\\": 10000,
  \\"limitPerUser\\": 1000,
  \\"localOnly\\": false,
  \\"cwd\\": \\"/\\",
  \\"syncSession\\": false,
  \\"sessionTimeout\\": 600000,
  \\"log\\": true,
  \\"io\\": {{ \\"log\\": false }},
  \\"debug\\": false,
  \\"term\\": {{
    \\"termName\\": \\"xterm\\",
    \\"geometry\\": [80, 24],
    \\"scrollback\\": 1000,
    \\"visualBell\\": false,
    \\"popOnBell\\": false,
    \\"cursorBlink\\": false,
    \\"screenKeys\\": false,
    \\"colors\\": [
      \\"#2e3436\\",
      \\"#cc0000\\",
      \\"#4e9a06\\",
      \\"#c4a000\\",
      \\"#3465a4\\",
      \\"#75507b\\",
      \\"#06989a\\",
      \\"#d3d7cf\\",
      \\"#555753\\",
      \\"#ef2929\\",
      \\"#8ae234\\",
      \\"#fce94f\\",
      \\"#729fcf\\",
      \\"#ad7fa8\\",
      \\"#34e2e2\\",
      \\"#eeeeec\\"
    ]
  }}
}}"""