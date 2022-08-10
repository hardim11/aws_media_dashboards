"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental Media Live  metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""

from datetime import datetime
import boto3
from .jinga_render import JinjaRender


TAG_KEY="Product"
TEMPLATE_FILE="eml.j2"


class EmlDashboard:
    """
    a class to create Elemental Media Live dashboard
    """
    _logger = None
    _ml_client = None
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
        self._ml_client = session.client(
          "medialive",
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
        get a list of channels in this region
        """
        # Create a reusable Paginator
        paginator = self._ml_client.get_paginator('list_channels')

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate()

        channels = []
        for page in page_iterator:
            channels.extend(page["Channels"])

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


    def get_channel_grab_bag(self, channels):
        """
        construct a grab bag for the template to use
            channel.channel_id
            channel.pipeline
            channel.name

            rtp_inputs.channel_id
            rtp_inputs.pipeline
            rtp_inputs.name
        """
        grab_bag = {
            "channels": [],
            "rtp_inputs": [],
            "region": self._region
        }

        for channel in channels:
            # extract details for pipeline 0
            arn = channel["Arn"]
            id = channel["Id"]
            name = "CH:" + channel["Name"] + "_PL:0"
            arn_split = arn.split(":")
            region = arn_split[3]

            a_channel = {
                "name": name,
                "arn": arn,
                "channel_id": id,
                "pipeline": "0",
                "region": region
            }
            grab_bag["channels"].append(a_channel)

            # if a standard channel pipeline 1
            if channel['ChannelClass'] == 'STANDARD':
                # add pipeline 1
                name = "CH:" + channel["Name"] + "_PL:1"
                b_channel = {
                    "name": name,
                    "arn": arn,
                    "channel_id": id,
                    "pipeline": "1",
                    "region": region
                }
                grab_bag["channels"].append(b_channel)

            # finally do RTP inputs
            for input_attachment in channel['InputAttachments']:
                # check if RTP
                input_attachment_desc = self._ml_client.describe_input(
                    InputId=input_attachment["InputId"]
                )

                if input_attachment_desc['Type']  == "RTP_PUSH":
                    # add it
                    a_input = {
                        "channel_id": id,
                        "pipeline": "0",
                        "name": channel["Name"] + "_PL:0"
                    }
                    grab_bag["rtp_inputs"].append(a_channel)
                    #TODO is there a pipeline 1 input?

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

        self.logit("EmlDashboard - processing {0} channels".format(len(channels)))
        if len(channels) < 1:
            self.logit("No matching channels found")
            return None

        grab_bag = self.get_channel_grab_bag(channels)

        rendered = JinjaRender.render_template(
            TEMPLATE_FILE,
            grab_bag
        )

        return rendered
