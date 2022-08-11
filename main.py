"""
main entry point
"""


from classes.cloudwatch_dashboard import CloudwatchDashboard
from classes.emx_dashboard import EmxDashboard
from classes.eml_dashboard import EmlDashboard
from classes.emp_dashboard import EmpDashboard
from classes.emc_dashboard import EmcDashboard
from classes.s3_dashboard import S3Dashboard



# this should match the name of the local AWS cli profile
AWS_PROFILE="matt-root"
# the region to scan for media services  and the dashboard is saved to
AWS_REGION="eu-west-1"

def logger(message):
    """
    log to console
    """
    print(message)

# object used to do the upload of the dashboard to AWS
cw = CloudwatchDashboard(AWS_REGION, AWS_PROFILE)

# create and upload the Elemental Media Connect Dashboard
emx = EmxDashboard(AWS_REGION, AWS_PROFILE, logger)
emx_widgets = emx.get_dashboards("")
cw.publish_dashboard("MediaConnect_Flows-Python-Jinja", emx_widgets)

# create and upload the Elemental Media Live Dashboard
eml = EmlDashboard(AWS_REGION, AWS_PROFILE, logger)
eml_widgets = eml.get_dashboards("")
cw.publish_dashboard("MediaLive-Python-Jinja", eml_widgets)

# create and upload the Elemental Media Package Dashboard
emp = EmpDashboard(AWS_REGION, AWS_PROFILE, logger)
emp_widgets = emp.get_dashboards("")
cw.publish_dashboard("MediaPackage_Channels-Python-Jinja", emp_widgets)

# create and upload the Elemental Media Convert Dashboard
emc = EmcDashboard(AWS_REGION, AWS_PROFILE, logger)
emc_widgets = emc.get_dashboards()
cw.publish_dashboard("MediaConvert_Channels-Python-Jinja", emc_widgets)

# create and upload the Elemental Media Convert Dashboard
s3 = S3Dashboard(AWS_REGION, AWS_PROFILE, logger)
s3_widgets = s3.get_dashboards()
cw.publish_dashboard("S3_Buckets-Python-Jinja", s3_widgets)
