__author__ = 'ggxx'

import datetime
import json
import subprocess

from os import mkdir
from lib_git import GitLabUtil
from lib_util import Util


class DockerRawHelper(object):

    logger = Util.uc_logger()

    def __init__(self, host, port, ca, cert, key):
        self.logger.info("DockerRawHelper.__init__")
        self._host = host
        self._port = port
        self._ca = ca
        self._cert = cert
        self._key = key

    def build_lab_docker(self, image_name, dockerfile_text):
        dockerfile_path = self._create_tmp_dockerfile(dockerfile_text)
        cmd = "docker --tlsverify --tlscacert={0} --tlscert={1} --tlskey={2} -H={3}:{4} build --rm -t {5} {6}"
        
        cmd = cmd.format(self._ca, self._cert, self._key, self._host, self._port, image_name, dockerfile_path)
        self.logger.info(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_output, err_output) = process.communicate()#timeout=60*10)
        if err_output != '':
            return 1
        return 0

    def build_student_docker(self, image_name, docker, private_key, public_key, user_name, user_psw, user_email, user_token, git_host, git_port, teacher_token, docker_namespace, mem_limit='256m'):
        result, message = GitLabUtil.get_user(git_host, git_port, teacher_token)
        if not result:
            self.logger.info(message)
            return 2
        try:
            teacher_id = json.loads(message)["id"]
            teacher_name = json.loads(message)["username"]
        except Exception:
            return 3
        project_name = docker.name
        dockerfile_text = self._format_ucore_dockerfile_text(docker, private_key, public_key, user_name, user_psw, user_email, git_host, docker_namespace)
        dockerfile_path = self._create_tmp_dockerfile(dockerfile_text)
        result, message = GitLabUtil.create_private_project(git_host, git_port, user_token, project_name)
        if not result:
            self.logger.info(message)
            self.logger.info("hhhhhhhhhhhhh1")
            return 4
        result, message = GitLabUtil.add_project_developer(git_host, git_port, user_token, user_name, project_name, teacher_id)
        if not result:
            self.logger.info(message)
            self.logger.info("hhhhhhhhhhhhhh2")
            return 5
        cmd = "docker --tlsverify --tlscacert={0} --tlscert={1} --tlskey={2} -H={3}:{4} build --rm -t {5} {6}"
        cmd = cmd.format(self._ca, self._cert, self._key, self._host, self._port, image_name, dockerfile_path)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_output, err_output) = process.communicate()#timeout=60*5)
        if err_output != '':
            return 6
        cmd = "docker --tlsverify --tlscacert={0} --tlscert={1} --tlskey={2} -H={3}:{4} create -p :8080 -p :6080 -m {5} {6}"
        cmd = cmd.format(self._ca, self._cert, self._key, self._host, self._port, mem_limit, image_name)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_output, err_output) = process.communicate()#timeout=15)
        docker.container_id = std_output
        if err_output != '':
            return 7
        docker.container_id = std_output
        return 0

    def start_student_docker(self, docker):
        cmd = "docker --tlsverify --tlscacert={0} --tlscert={1} --tlskey={2} -H={3}:{4} start {5}"
        cmd = cmd.format(self._ca, self._cert, self._key, self._host, self._port, docker.container_id)
        self.logger.info(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_output, err_output) = process.communicate()#timeout=15)
        if err_output != '':
            return 1
        cmd = "docker --tlsverify --tlscacert={0} --tlscert={1} --tlskey={2} -H={3}:{4} port {5}"
        cmd = cmd.format(self._ca, self._cert, self._key, self._host, self._port, docker.container_id)
        self.logger.info(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_output, err_output) = process.communicate()#timeout=15)
        if err_output != '':
            return 2
        docker.last_start_time = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%d %H:%M:%S")
        docker.host = self._host
        # std_output is 6080/tcp -> 0.0.0.0:49100\n8080/tcp -> 0.0.0.0:49101
        ports = std_output.split('\n')
        for i in range(0, len(ports)):
            port_docker = ports[i].split("/")[0]
            if port_docker == "6080":
                docker.port = ports[i].split(":")[1]
            elif port_docker == "8080":
                 docker.vnc = ports[i].split(":")[1]
        return 0

    def stop_student_docker(self, docker):
        cmd = "docker --tlsverify --tlscacert={0} --tlscert={1} --tlskey={2} -H={3}:{4} stop {5}"
        cmd = cmd.format(self._ca, self._cert, self._key, self._host, self._port, docker.container_id)
        self.logger.info(cmd)
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (std_output, err_output) = process.communicate()#timeout=15)
        if err_output != '':
            return 1
        return 0

    def _create_tmp_dockerfile(self, docker_file_text):
        tmp_path = "/tmp/uc_docker/" + Util.random_string(12)
        tmp_file = tmp_path + "/Dockerfile"
        mkdir(tmp_path)
        f=open(tmp_file, 'w')
        f.write(docker_file_text)
        f.flush()
        f.close()
        return tmp_path

    def _format_ucore_dockerfile_text(self, docker, private_key, public_key, user_name, user_pwd, user_email, git_host, docker_namespace):
        text = (
            'FROM ' + docker_namespace + '/' + docker.lab.name +
            '\nMAINTAINER ggxx<ggxx120@gmail.com>' +
            '\n' +
            '\nRUN echo -ne "' + private_key.replace("\n", "\\n") + '" > /root/.ssh/id_rsa;\\' +
            '\n  echo "' + public_key + '" > /root/.ssh/id_rsa.pub;\\' +
            '\n  chmod 0600 /root/.ssh/id_rsa ;\\' +
            '\n  echo -ne "' + self._startup_shell.replace("\n", "\\n") + '" > /startup.sh;\\' +
            '\n  chmod +x /startup.sh;\\' +
            '\n  echo -ne "' + self._tty_config.format(user_name, user_pwd).replace("\n", "\\n") + '" > /opt/ttyjs/ttyjs-config.json;\\' +
            '\n  echo ' + user_pwd + ' | echo $(vncpasswd -f) > /root/.vnc/passwd;\\' +
            '\n  chmod 0600 /root/.vnc/passwd;\\' +
            '\n  git config --global user.name "' + user_name + '" ;\\' +
            '\n  git config --global user.email "' + user_email + '" ;\\' +
            '\n  echo -ne "StrictHostKeyChecking no\\nUserKnownHostsFile /dev/null\\n" >> /etc/ssh/ssh_config ;\\' +
            '\n  cd /my_lab/ ;\\' +
            '\n  git remote add origin git@' + git_host + ':' + user_name + '/' + docker.name + '.git; \\'
            '\n  git push -u origin master' +
            '\n' +
            '\nEXPOSE 6080' +
            '\nEXPOSE 8080' +
            '\nENTRYPOINT ["/startup.sh"]',)
        self.logger.info(text[0])
        return text[0]

    _startup_shell = """#!/usr/bin/env bash
vncserver -kill :1
(vncserver && /opt/noVNC/utils/launch.sh --vnc localhost:5901) & tty.js --config /opt/ttyjs/ttyjs-config.json"""

    _tty_config = """{{
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


'''
if __name__ == "__main__":
    docker = DockerRawHelper("uclassroom", 2376,
                             "/home/ggxx/Documents/uclassroom-node/scripts/certs/ca.pem",
                             "/home/ggxx/Documents/uclassroom-node/scripts/certs/cert.pem",
                             "/home/ggxx/Documents/uclassroom-node/scripts/certs/key.pem")
    if docker.build_lab_docker("testns/testimg2", "FROM docker.io/fedora:21\nENTRYPOINT [\"bash\"]") == 0:
        print "OK"
    else:
        print "ERROR"

'''
