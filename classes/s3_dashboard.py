"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for S3 metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""


from datetime import datetime
import boto3
from .jinga_render import JinjaRender

TAG_KEY="Product"
TEMPLATE_FILE="s3.j2"

class S3Dashboard:
    """
    a class to create S3 dashboard
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
          "s3",
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


    def get_buckets(self):
        """
        list the buckets
        """
        # apparently no paginator!
        buckets = self._mc_client.list_buckets()
        return buckets["Buckets"]


    def get_grab_bag(self, buckets):
        """
        construct a grab bag for the template to use
        """
        grab_bag = {
            "items": [],
            "region": self._region
        }

        # collect the data into a dictionary
        for bucket in buckets:
            a_bucket = {
                "name": bucket["Name"],
                "region": self._region
            }
            grab_bag["items"].append(a_bucket)

        return grab_bag


    def get_dashboards(self, tag_selection = ""):
        """
        build the dashboards
        tag_selection - if empty then all, else uses tag matching TAG_KEY
        """
        buckets = self.get_buckets()

        #TODO do I want to filter for tags?
        # if tag_selection != "":
        #     # apply a filter
        #     flows = self.filter_flows(flows, tag_selection)

        self.logit("S3Dashboard - processing {0} buckets".format(len(buckets)))
        if len(buckets) < 1:
            self.logit("No matching buckets found")
            return None

        grab_bag = self.get_grab_bag(buckets)

        rendered = JinjaRender.render_template(
            TEMPLATE_FILE,
            grab_bag
        )

        return rendered
