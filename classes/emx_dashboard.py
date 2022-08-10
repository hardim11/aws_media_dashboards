"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental MediaConnect metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""

from datetime import datetime
import boto3
from .jinga_render import JinjaRender


TAG_KEY="Product"
TEMPLATE_FILE="emx.j2"


class EmxDashboard:
    """
    a class to create Elemental Media Connect dashboard
    """
    _logger = None
    _mc_client = None
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
        self._mc_client = session.client(
          "mediaconnect",
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


    def get_flows(self):
        """
        get a list of flows in this region
        """
        # Create a reusable Paginator
        paginator = self._mc_client.get_paginator('list_flows')

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate()

        flows = []
        for page in page_iterator:
            flows.extend(page["Flows"])

        return flows


    def get_tags_for_flow(self, flow_arn):
        """
        get the tags for the flow
        """
        return self._mc_client.list_tags_for_resource(
            ResourceArn = flow_arn
        )


    def filter_flows(self, flows, tag_selection):
        """
        filter on tags
        """
        output = []
        for flow in flows:
            flow_tags = self.get_tags_for_flow(flow["FlowArn"])
            if TAG_KEY in flow_tags["Tags"]:
                if flow_tags["Tags"][TAG_KEY] == tag_selection:
                    output.append(flow)

        return output


    def get_flow_grab_bag(self, flows):
        """
        construct a grab bag for the template to use
        """
        grab_bag = {
            "items": [],
            "region": self._region
        }

        # collect the data into a dictionary
        for flow in flows:
            #
            arn = flow["FlowArn"]
            arn_split = arn.split(":")
            region = arn_split[3]
            a_flow = {
                "name": flow["Name"],
                "arn": arn,
                "region": region
            }
            grab_bag["items"].append(a_flow)

        return grab_bag


    def get_dashboards(self, tag_selection = ""):
        """
        build the dashboards
        tag_selection - if empty then all, else uses tag matching TAG_KEY
        """
        flows = self.get_flows()

        if tag_selection != "":
            # apply a filter
            flows = self.filter_flows(flows, tag_selection)

        self.logit("EmxDashboard - processing {0} channels".format(len(flows)))
        if len(flows) < 1:
            self.logit("No matching channels found")
            return None

        grab_bag = self.get_flow_grab_bag(flows)

        rendered = JinjaRender.render_template(
            TEMPLATE_FILE,
            grab_bag
        )

        return rendered
