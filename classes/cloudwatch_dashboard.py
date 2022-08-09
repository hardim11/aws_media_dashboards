"""
helper function for cloudwatch dashboard
"""

from datetime import datetime
import json
import boto3


class CloudwatchDashboard:
    """
    helper class really, could be static
    """
    _logger = None
    _cw_client = None
    _region = ""

    def __init__(self, region, profile, logger=None):
        """
        constructor
        """
        self._logger = logger
        self._region = region

        if profile is None:
            session = boto3.Session()
        else:
            session = boto3.Session(profile_name=profile)

        # create a client
        self._cw_client = session.client(
          "cloudwatch",
          region_name = region
        )


    def logit(self, message):
        """
        logs to the supplied logger or prints if none
        """
        if self._logger is None:
            print(datetime.utcnow().strftime("%Y%m%d-%H%M%S") + " : " + message)
        else:
            self._logger(message)


    def publish_dashboard(self, dashboard_name, widgets):
        """
        publish to Cloudwatch dashboards
        """
        self.logit("CloudwatchDashboard uploading dashboard {0} ({1})".format(
                dashboard_name,
                self._region
            )
        )
        self._cw_client.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=json.dumps(widgets, indent=4)
        )
