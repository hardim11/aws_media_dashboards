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
TEMPLATE_FILE="emt_vod.j2"

class EmtVodDashboard:
    """
    a class to create Elemental Media Tailor VOD dashboard
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


    def get_channels(self):
        """
        get list of campaigns in this region
        """
        # Create a reusable Paginator
        paginator = self._mt_client.get_paginator('list_channels')

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate()

        channels = []
        for page in page_iterator:
            channels.extend(page["Items"])

        return channels


    def filter_channels(self, channels, tag_selection):
        """
        filter on tags
        """
        output = []
        for channel in channels:
            if TAG_KEY in channel["Tags"]:
                if channel["Tags"][TAG_KEY] == tag_selection:
                    output.append(channel)

        return output


    def get_grab_bag(self, channels):
        """
        construct a grab bag for the template to use
        """
        grab_bag = {
            "items": [],
            "region": self._region
        }

        # collect the data into a dictionary
        for channel in channels:
            #
            arn = channel["Arn"]
            arn_split = arn.split(":")
            region = arn_split[3]
            a_channel = {
                "name": channel["ChannelName"],
                "arn": arn,
                "region": region
            }
            grab_bag["items"].append(a_channel)

        return grab_bag


    def get_dashboards(self, tag_selection = ""):
        """
        build the dashboards
        tag_selection - if empty then all, else uses tag matching TAG_KEY
        """
        channels = self.get_channels()

        if tag_selection != "":
            # apply a filter
            channels = self.filter_channels(channels, tag_selection)

        self.logit("EMT VOD - processing {0} channels".format(len(channels)))
        if len(channels) < 1:
            self.logit("No matching channels found")
            return None

        grab_bag = self.get_grab_bag(channels)

        rendered = JinjaRender.render_template(
            TEMPLATE_FILE,
            grab_bag
        )

        return rendered
