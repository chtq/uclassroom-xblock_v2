# coding=utf-8
__author__ = 'ggxx'

import urllib
import httplib
import json


class GitLabUtil(object):

    @staticmethod
    def create_http_client(host, port, req, url, params):
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        http_client = httplib.HTTPConnection(host, port, timeout=30)
        http_client.request(req, url, params, headers)
        return http_client

    @staticmethod
    def handle_response(response):
        status = response.status
        if status == 200 or status == 201:
            return True, response.read()
        elif status == 400:
            output = ""
            message = json.loads(response.read())
            for key, value in message["message"].items():
                output = output + key + ": "
                for msg in value:
                    output = output + msg + ", "
                output = output + ";"
            return False, output
        elif status == 403:
            return False, "403 Forbidden - The request is not allowed."
        elif status == 404:
            return False, "404 Not Found - The resource you asked could not be accessed or found."
        elif status == 409:
            return False, "409 Conflict - A conflicting resource already exists."
        elif status == 500:
            return False, "500 Server Error."
        else:
            return False, response.reason

    @staticmethod
    def create_account(host, port, admin_token, name, user_name, email, password):
        print "git.create_account"
        http_client = None
        try:
            url = "/api/v3/users?private_token={0}".format(admin_token)
            params = urllib.urlencode({'name': name, 'email': email, "username": user_name, "password": password})
            http_client = GitLabUtil.create_http_client(host, port, "POST", url, params)
            result, message = GitLabUtil.handle_response(http_client.getresponse())
        except Exception, e:
            print e
            result = False
            message = "Error in create_account function"
        finally:
            if http_client:
                http_client.close()
        return result, message

    @staticmethod
    def get_user_projects(host, port, user_token):
        print "git.get_user_projects"
        http_client = None
        try:
            url = "/api/v3/projects/owned?private_token={0}".format(user_token)
            params = urllib.urlencode({})
            http_client = GitLabUtil.create_http_client(host, port, "GET", url, params)
            result, message = GitLabUtil.handle_response(http_client.getresponse())
        except Exception, e:
            print e
            result = False
            message = "Error in get_user_projects function"
        finally:
            if http_client:
                http_client.close()
        return result, message

    @staticmethod
    def login(host, port, name, password):
        print "git.login"
        http_client = None
        try:
            url = "/api/v3/session"
            params = urllib.urlencode({'login': name, 'password': password})
            http_client = GitLabUtil.create_http_client(host, port, "POST", url, params)
            result, message = GitLabUtil.handle_response(http_client.getresponse())
        except Exception, e:
            print e
            result = False
            message = "Error in login function"
        finally:
            if http_client:
                http_client.close()
        return result, message

    @staticmethod
    def add_ssh_key(host, port, user_token, title, key):
        print "git.add_ssh_key"
        http_client = None
        try:
            url = "/api/v3/user/keys?private_token={0}".format(user_token)
            params = urllib.urlencode({'title': title, 'key': key})
            http_client = GitLabUtil.create_http_client(host, port, "POST", url, params)
            result, message = GitLabUtil.handle_response(http_client.getresponse())
        except Exception, e:
            print e
            result = False
            message = "Error in add_ssh_key function"
        finally:
            if http_client:
                http_client.close()
        return result, message

    @staticmethod
    def create_private_project(host, port, user_token, project_name):
        print "git.create_private_project"
        http_client = None
        try:
            url = "/api/v3/projects?private_token={0}".format(user_token)
            params = urllib.urlencode({'name': project_name, 'visibility_level': 0})
            http_client = GitLabUtil.create_http_client(host, port, "POST", url, params)
            result, message = GitLabUtil.handle_response(http_client.getresponse())
        except Exception, e:
            print e
            result = False
            message = "Error in create_private_project function"
        finally:
            if http_client:
                http_client.close()
        return result, message

    @staticmethod
    def add_project_developer(host, port, user_token, git_owner, git_project, git_developer_id):
        print "git.add_project_developer"
        http_client = None
        try:
            url = "/api/v3/projects/{0}%2F{1}/members?private_token={2}".format(git_owner, git_project, user_token)
            params = urllib.urlencode({'user_id': git_developer_id, 'access_level': 30})
            http_client = GitLabUtil.create_http_client(host, port, "POST", url, params)
            result, message = GitLabUtil.handle_response(http_client.getresponse())
        except Exception, e:
            print e
            result = False
            message = "Error in add_project_developer function"
        finally:
            if http_client:
                http_client.close()
        return result, message

    @staticmethod
    def get_user(host, port, user_token):
        print "git.get_user"
        http_client = None
        try:
            url = "/api/v3/user?private_token={0}".format(user_token)
            params = urllib.urlencode({})
            http_client = GitLabUtil.create_http_client(host, port, "GET", url, params)
            result, message = GitLabUtil.handle_response(http_client.getresponse())
        except Exception, e:
            print e
            result = False
            message = "Error in get_user function"
        finally:
            if http_client:
                http_client.close()
        return result, message

    @staticmethod
    def update_file(host, port, user_token, project_id):
        http_client = None
        try:
            url = "/api/v3/projects/{0}/repository/files?private_token={1}".format(project_id, user_token)
            params = urllib.urlencode({"file_path":"hello.c", "branch_name":"master", "content": "it is a test\nnewline汉字", "commit_message":"test commit3"})
            http_client = GitLabUtil.create_http_client(host, port, "PUT", url, params)
            result, message = GitLabUtil.handle_response(http_client.getresponse())
        except Exception, e:
            print e
            result = False
            message = "Error in update_file function"
        finally:
            if http_client:
                http_client.close()
        return result, message


if __name__ == '__main__':
    user_token = 'xNxCBik71qQBB-K5gBW6'
    project_id = '6'
    result, msg= GitLabUtil.update_file('166.111.131.12', 10880, user_token, project_id)
    print result
    print msg