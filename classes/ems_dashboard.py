"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental Media Package metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""


from datetime import datetime
import boto3
from .jinga_render import JinjaRender

TAG_KEY="Product"
TEMPLATE_FILE="ems.j2"

class EmsDashboard:
    """
    a class to create Elemental Media Store dashboard
    """
    _logger = None
    _ms_client = None
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
        self._ms_client = session.client(
          "mediastore",
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


    def get_store_containers(self):
        """
        get all the mediastores in this region
        """
        # Create a reusable Paginator
        paginator = self._ms_client.get_paginator('list_containers')

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate()

        containers = []
        for page in page_iterator:
            containers.extend(page["Containers"])

        return containers


    def get_tags_for_container(self, container_arn):
        """
        get the tags for the container
        """
        return self._ms_client.list_tags_for_resource(
            Resource = container_arn
        )


    def filter_containers(self, containers, tag_selection):
        """
        filter on tags
        """
        output = []
        for container in containers:
            container_tags = self.get_tags_for_container(container["ARN"])
            if TAG_KEY in container_tags["Tags"]:
                if container_tags["Tags"][TAG_KEY] == tag_selection:
                    output.append(container)

        return output


    def get_grab_bag(self, containers):
        """
        construct a grab bag for the template to use
        """
        grab_bag = {
            "items": [],
            "region": self._region
        }

        # collect the data into a dictionary
        for container in containers:
            #
            arn = container["ARN"]
            arn_split = arn.split(":")
            region = arn_split[3]
            a_flow = {
                "name": container["Name"],
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
        containers = self.get_store_containers()

        if tag_selection != "":
            # apply a filter
            containers = self.filter_containers(containers, tag_selection)

        self.logit("EmsDashboard - processing {0} containers".format(len(containers)))
        if len(containers) < 1:
            self.logit("No matching containers found")
            return None

        grab_bag = self.get_grab_bag(containers)

        rendered = JinjaRender.render_template(
            TEMPLATE_FILE,
            grab_bag
        )

        return rendered
    