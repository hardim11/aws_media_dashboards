"""
helper function for cloudwatch dashboard
"""

import json
import boto3

class CloudwatchDashboard:
    """
    helper class really, could be static
    """

    _cw_client = None

    def __init__(self, region, profile):
        """
        constructor
        """
        if profile is None:
            session = boto3.Session()
        else:
            session = boto3.Session(profile_name=profile)

        # create a client
        self._cw_client = session.client(
          "cloudwatch",
          region_name = region
        )


    def publish_dashboard(self, dashboard_name, widgets):
        """
        publish to Cloudwatch dashboards
        """
        self._cw_client.put_dashboard(
            DashboardName=dashboard_name,
            DashboardBody=json.dumps(widgets, indent=4)
        )
