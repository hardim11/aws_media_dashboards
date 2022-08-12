"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Cloudfront metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""


from datetime import datetime
import boto3
from .jinga_render import JinjaRender


TAG_KEY="Product"
TEMPLATE_FILE="cloudfront.j2"

class CloudFrontDashboard:
    """
    a class to create Coudfront
    """
    _logger = None
    _cf_client = None
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
        self._cf_client = session.client(
          "cloudfront",
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


    def get_distributions(self):
        """
        get list of distributions
        """
        # Create a reusable Paginator
        paginator = self._cf_client.get_paginator('list_distributions')

        # Create a PageIterator from the Paginator
        page_iterator = paginator.paginate()

        distributions = []
        for page in page_iterator:
            if "Items" in page["DistributionList"]:
                print("*********************")
                distributions.extend(page["DistributionList"]["Items"])

        return distributions


    def get_tags_for_distribution(self, distribution_arn):
        """
        get the tags for the distribution
        """
        return self._cf_client.list_tags_for_resource(
            Resource = distribution_arn
        )


    def filter_distributions(self, distributions, tag_selection):
        """
        filter on tags
        """
        #TODO is this right? Cloudfront is different
        output = []
        for distribution in distributions:
            distribution_tags = self.get_tags_for_distribution(distribution["ARN"])
            if TAG_KEY in distribution_tags["Tags"]["Items"]:
                if distribution_tags["Tags"]["Items"][TAG_KEY] == tag_selection:
                    output.append(distribution)

        return output


    def get_grab_bag(self, distributions):
        """
        construct a grab bag for the template to use
        """
        grab_bag = {
            "items": [],
            "region": self._region
        }

        # collect the data into a dictionary
        for distribution in distributions:
            #
            arn = distribution["ARN"]
            arn_split = arn.split(":")
            region = arn_split[3]
            a_distribution = {
                "name": distribution["Id"],
                "arn": arn,
                "region": region,
                "description": distribution["Comment"]
            }
            grab_bag["items"].append(a_distribution)

        return grab_bag


    def get_dashboards(self, tag_selection = ""):
        """
        build the dashboards
        tag_selection - if empty then all, else uses tag matching TAG_KEY
        """
        distributions = self.get_distributions()

        if tag_selection != "":
            # apply a filter
            distributions = self.filter_distributions(distributions, tag_selection)

        self.logit("CloudFront - processing {0} channels".format(len(distributions)))
        if len(distributions) < 1:
            self.logit("No matching distributions found")
            return None

        grab_bag = self.get_grab_bag(distributions)

        rendered = JinjaRender.render_template(
            TEMPLATE_FILE,
            grab_bag
        )

        return rendered
