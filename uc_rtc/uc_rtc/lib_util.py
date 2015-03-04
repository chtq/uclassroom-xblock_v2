__author__ = 'ggxx'

import logging
import pkg_resources

from django.template import Context, Template


class Util(object):

    @staticmethod
    def load_resource(resource_path):
        resource_content = pkg_resources.resource_string(__name__, resource_path)
        return unicode(resource_content)

    @staticmethod
    def render_template(template_path, context={}):
        template_str = Util.load_resource(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    _log_file = "/tmp/uc_rtc_xblock.log"
    _fh = logging.FileHandler(_log_file, encoding="utf-8")
    _fmt = logging.Formatter("%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s")
    _fh.setFormatter(_fmt)
    _logger = logging.getLogger("uc_xblock")
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(_fh)

    @staticmethod
    def uc_logger():
        return Util._logger