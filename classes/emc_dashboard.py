"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental Media Convert metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""


from datetime import datetime
import boto3
from .jinga_render import JinjaRender

TAG_KEY="Product"
TEMPLATE_FILE="emc.j2"

class EmcDashboard:
    """
    a class to create Elemental Media Connect dashboard
    """
    _logger = None
    _mc_client = None
    _mc_client_endpoint = None
    _region = ""
    _endpoints = []

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
          "mediaconvert",
          region_name = region
        )

        # get the regional end point
        self.get_regional_endpoints()

        # create a client to use the endpoint
        self._mc_client_endpoint = session.client(
          "mediaconvert",
          region_name = region,
          endpoint_url=self._endpoints[0]["Url"]
        )


    def logit(self, message):
        """
        logs to the supplied logger or prints if none
        """
        if self._logger is None:
            print(datetime.utcnow().strftime("%Y%m%d-%H%M%S") + " : " + message)
        else:
            self._logger(message)


    def get_regional_endpoints(self):
        """
        hmmm as Media Convert is "odd", you need a specific
        endpoint for your account - don't you love Elemental's
        not quite right fitting into AWS!
        """
        # get the regional endpoint
        self._endpoints = self._mc_client.describe_endpoints()["Endpoints"]

        if len(self._endpoints) < 1:
            raise Exception("Unable to get regional endpoints for Media Convert")

        return self._endpoints


    def get_queues(self):
        """
        get all the mediaconvert queues
        """
        # Create a reusable Paginator
        paginator = self._mc_client_endpoint.get_paginator('list_queues')

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate()

        queues = []
        for page in page_iterator:
            queues.extend(page["Queues"])

        return queues


    def get_flow_grab_bag(self, queues):
        """
        construct a grab bag for the template to use
        """
        grab_bag = {
            "items": [],
            "region": self._region
        }

        # collect the data into a dictionary
        for queue in queues:
            #
            arn = queue["Arn"]
            arn_split = arn.split(":")
            region = arn_split[3]
            a_queue = {
                "name": queue["Name"],
                "arn": arn,
                "region": region
            }
            grab_bag["items"].append(a_queue)

        return grab_bag


    def get_dashboards(self):
        """
        build the dashboards
        tag_selection - if empty then all, else uses tag matching TAG_KEY
        """
        queues = self.get_queues()

        self.logit("EmcDashboard - processing {0} channels".format(len(queues)))
        if len(queues) < 1:
            self.logit("No matching channels found")
            return None

        grab_bag = self.get_flow_grab_bag(queues)

        rendered = JinjaRender.render_template(
            TEMPLATE_FILE,
            grab_bag
        )

        return rendered
