from xblock.core import XBlock
from xblock.fragment import Fragment
from lib_util import Util


class UcRtcXBlock(XBlock):

    def student_view(self, context=None):
        # preview in studio
        if self.runtime.anonymous_student_id == "student":
            return self.message_view(title="This a real-time communication XBlock base-on WebRTC!",
                                     message="There is nothing to edit in studio view.")
        fragment = Fragment()
        fragment.add_content(Util.render_template('static/html/uc_rtc.html'))
        fragment.add_css(Util.load_resource("static/css/uc_rtc.css"))
        fragment.add_javascript(Util.load_resource("static/js/src/socket.io-1.3.2.js"))
        fragment.add_javascript(Util.load_resource("static/js/src/adapter.js"))
        fragment.add_javascript(Util.load_resource("static/js/src/static.js"))
        fragment.add_javascript(Util.load_resource("static/js/src/uc_rtc.js"))
        fragment.initialize_js("UcRtcXBlock")
        return fragment

    def studio_view(self, context=None):
        fragment = Fragment()
        fragment.add_content(Util.render_template('static/html/uc_rtc_studio.html'))
        fragment.add_css(Util.load_resource("static/css/uc_rtc.css"))
        fragment.add_javascript(Util.load_resource("static/js/src/uc_rtc_edit.js"))
        fragment.initialize_js("UcRtcXBlock")
        return fragment

    def message_view(self, title, message, context=None):
        context_dict = {
            "title": title,
            "message": message
        }
        fragment = Fragment()
        fragment.add_content(Util.render_template('static/html/uc_message.html', context_dict))
        fragment.add_css(Util.load_resource("static/css/uc_rtc.css"))
        fragment.add_javascript(Util.load_resource("static/js/src/uc_null.js"))
        fragment.initialize_js("UcRtcXBlock")
        return fragment

    @XBlock.json_handler
    def get_name(self, data, suffix=''):
        user = self.runtime.get_real_user(self.runtime.anonymous_student_id)
        username = user.username
        return {"username": username}

    @staticmethod
    def workbench_scenarios():
        return [
            ("UcRtcXBlock", """<vertical_demo><uc_rtc/></vertical_demo>"""),
        ]