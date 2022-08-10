"""
Performs a Jinja2 Template render - very basic
"""

import os
import json
from jinja2 import Template

class JinjaRender:
    """
    Performs a Jinja2 Template render - very basic
    """

    @staticmethod
    def render_template(template_file, grab_bag):
        """
        renders the specified template, returns a string
        """
        template_file_path = os.path.join(
            os.path.dirname(__file__),
            "templates",
            template_file
        )
        with open(template_file_path) as file_:
            template = Template(file_.read())

        tmp = template.render(grab_bag)
        return json.dumps(json.loads(tmp), indent=4)
