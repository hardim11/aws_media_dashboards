"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental Media Tailor metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""


from datetime import datetime
import boto3
from .jinga_render import JinjaRender

TAG_KEY="Product"
TEMPLATE_FILE="emt_ssai.j2"

class EmtSsaiDashboard:
    """
    a class to create Elemental Media Tailor SSAI dashboard
    """
    _logger = None
    _mt_client = None
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
        self._mt_client = session.client(
          "mediatailor",
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


    def get_campaigns(self):
        """
        get list of campaigns in this region
        """
        # Create a reusable Paginator
        paginator = self._mt_client.get_paginator('list_playback_configurations')

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate()

        campaigns = []
        for page in page_iterator:
            campaigns.extend(page["Items"])

        return campaigns


    def filter_campaigns(self, campaigns, tag_selection):
        """
        filter on tags
        """
        output = []
        for campaign in campaigns:
            if TAG_KEY in campaign["Tags"]:
                if campaign["Tags"][TAG_KEY] == tag_selection:
                    output.append(campaign)

        return output


    def get_grab_bag(self, campaigns):
        """
        construct a grab bag for the template to use
        """
        grab_bag = {
            "items": [],
            "region": self._region
        }

        # collect the data into a dictionary
        for campaign in campaigns:
            #
            arn = campaign["PlaybackConfigurationArn"]
            arn_split = arn.split(":")
            region = arn_split[3]
            a_capaign = {
                "name": campaign["Name"],
                "arn": arn,
                "region": region
            }
            grab_bag["items"].append(a_capaign)

        return grab_bag


    def get_dashboards(self, tag_selection = ""):
        """
        build the dashboards
        tag_selection - if empty then all, else uses tag matching TAG_KEY
        """
        campaigns = self.get_campaigns()

        if tag_selection != "":
            # apply a filter
            campaigns = self.filter_campaigns(campaigns, tag_selection)

        self.logit("EMT SSAI - processing {0} containers".format(len(campaigns)))
        if len(campaigns) < 1:
            self.logit("No matching campaigns found")
            return None

        grab_bag = self.get_grab_bag(campaigns)

        rendered = JinjaRender.render_template(
            TEMPLATE_FILE,
            grab_bag
        )

        return rendered
