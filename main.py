"""
main entry point
"""

from classes.cloudwatch_dashboard import CloudwatchDashboard
from classes.emx_dashboard import EmxDashboard
from classes.eml_dashboard import EmlDashboard
from classes.emp_dashboard import EmpDashboard


AWS_PROFILE="matt-root"
AWS_REGION="eu-west-1"

def logger(message):
    """
    log to console
    """
    print(message)


cw = CloudwatchDashboard(AWS_REGION, AWS_PROFILE)

emx = EmxDashboard(AWS_REGION, AWS_PROFILE, logger)
emx_widgets = emx.get_dashboards("")
cw.publish_dashboard("MediaConnect_Flows-Python", emx_widgets)

eml = EmlDashboard(AWS_REGION, AWS_PROFILE, logger)
eml_widgets = eml.get_dashboards("")
cw.publish_dashboard("MediaLive-Python", eml_widgets)

emp = EmpDashboard(AWS_REGION, AWS_PROFILE, logger)
emp_widgets = emp.get_dashboards("")
cw.publish_dashboard("MediaPackage_Channels-Python", emp_widgets)
