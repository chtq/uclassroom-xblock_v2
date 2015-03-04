__author__ = 'ggxx'

import random
import string
import paramiko
import logging
import pkg_resources

from Crypto.Random import atfork

from django.template import Context, Template


class Util(object):

    @staticmethod
    def get_chars():
        return 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890-_'

    @staticmethod
    def random_string(length):
        return string.join(random.sample(Util.get_chars(), length)).replace(' ', '')

    @staticmethod
    def create_random_password():
        return Util.random_string(12)

    @staticmethod
    def gen_ssh_keys(email):
        atfork()
        tmp_file = '/tmp/id_rsa_{0}.tmp'.format(Util.random_string(12))
        key = paramiko.RSAKey.generate(bits=2048)
        key.write_private_key_file(tmp_file)
        key_text = open(tmp_file).read()
        pub = "{0} {1} {2}".format(key.get_name(), key.get_base64(), email)
        return key_text, pub

    @staticmethod
    def load_resource(resource_path):
        resource_content = pkg_resources.resource_string(__name__, resource_path)
        return unicode(resource_content)

    @staticmethod
    def render_template(template_path, context={}):
        template_str = Util.load_resource(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    _log_file = "/tmp/uc_docker_xblock.log"
    _fh = logging.FileHandler(_log_file, encoding="utf-8")
    _fmt = logging.Formatter("%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s")
    _fh.setFormatter(_fmt)
    _logger = logging.getLogger("uc_xblock")
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(_fh)

    @staticmethod
    def uc_logger():
        return Util._logger
