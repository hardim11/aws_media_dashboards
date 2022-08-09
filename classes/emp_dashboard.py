"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental Media Package metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""


from datetime import datetime
import json
import boto3

TAG_KEY="Product"


class EmpDashboard:
    """
    a class to create Elemental Media Connect dashboard
    """
    _logger = None
    _mp_client = None

    def __init__(self, region, profile, logger=None):
        """
        constructor
        """
        self._logger = logger

        if profile is None:
            session = boto3.Session()
        else:
            session = boto3.Session(profile_name=profile)

        # create a client
        self._mp_client = session.client(
          "mediapackage",
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



