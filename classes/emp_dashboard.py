"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental Media Package metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""


import copy
from datetime import datetime
import boto3


TAG_KEY="Product"
EMP_IngressResponseTime_widget_d = {
            "height": 6,
            "width": 18,
            "y": 0,
            "x": 0,
            "type": "metric",
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaPackage",
                        "IngressResponseTime",
                        "Channel",
                        "ChannelName"
                    ]
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-west-2",
                "stat": "Average",
                "period": 60,
                "title": "Ingress Response Times - All Channels",
                "legend": {
                    "position": "right"
                },
                "yAxis": {
                    "left": {
                        "min": 0,
                        "label": "msec",
                        "showUnits": False
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
}
EMP_IngressBytes_widget_d = {
            "height": 6,
            "width": 18,
            "y": 6,
            "x": 0,
            "type": "metric",
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaPackage",
                        "IngressBytes",
                        "Channel",
                        "ChannelName"
                    ]
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-west-2",
                "stat": "Average",
                "period": 60,
                "title": "Ingress Rate (Bytes) - All Channels",
                "legend": {
                    "position": "right"
                },
                "yAxis": {
                    "left": {
                        "min": 0,
                        "label": "Bytes",
                        "showUnits": False
                    },
                    "right": {
                        "min": 0
                    }
                }
            }
}
EMP_EgressResponseTime_widget_d = {
            "height": 6,
            "width": 18,
            "y": 12,
            "x": 0,
            "type": "metric",
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaPackage",
                        "EgressResponseTime",
                        "Channel",
                        "ChannelName"
                    ]
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-west-2",
                "stat": "Average",
                "period": 60,
                "title": "Egress Response Times - All Channels",
                "yAxis": {
                    "left": {
                        "min": 0,
                        "label": "msec",
                        "showUnits": False
                    },
                    "right": {
                        "min": 0
                    }
                },
                "legend": {
                    "position": "right"
                }
            }
        }
EMP_EgressRequestCount_widget_d = {
            "height": 6,
            "width": 9,
            "y": 18,
            "x": 0,
            "type": "metric",
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaPackage",
                        "EgressRequestCount",
                        "Channel",
                        "ChannelName",
                        "StatusCodeRange",
                        "2xx",
                        { "label": "2xx Successful" }
                    ],
                    [
                        "...",
                        "4xx",
                        { "label": "4xx Errors" }
                    ],
                    [
                        "...",
                        "5xx",
                        { "label": "5xx Errors" }
                    ]
                ],
                "view": "timeSeries",
                "stacked": True,
                "region": "us-west-2",
                "stat": "Average",
                "period": 60,
                "title": "Egress Request Counts for Channel ",
                "yAxis": {
                    "left": {
                        "min": 0,
                        "label": "Status Codes",
                        "showUnits": False
                    },
                    "right": {
                        "min": 0
                    }
                },
                "setPeriodToTimeRange": True,
                "legend": {
                    "position": "bottom"
                }
            }
 }


class EmpDashboard:
    """
    a class to create Elemental Media Connect dashboard
    """
    _logger = None
    _mp_client = None
    _total_channels_processed = -1
    _per_channel_widgets=[]

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


    def get_channels(self):
        """
        get a list of channels in this region
        """
        # Create a reusable Paginator
        paginator = self._mp_client.get_paginator('list_channels')

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


    def add_channel_dashboard(self, channel, widgets_list):
        """
        build the dashboard
        """
        self._total_channels_processed = self._total_channels_processed + 1
        # metric_template_line = [
        #     "...",
        #     "SecondChannelName"
        # ]
        channel_id = channel["Id"]
        # channel_desc = channel["Description"]
        # channel_name = channel_id.ljust(32, ' ')
        # this_label = "CH:" + channel_name
        this_flowarn = channel["Arn"]

        arn_split = this_flowarn.split(":")
        region = arn_split[3]

        tmp=copy.deepcopy(EMP_EgressRequestCount_widget_d)
        tmp['properties']['metrics'][0][3] = channel_id
        tmp['properties']['title'] = \
            EMP_EgressRequestCount_widget_d['properties']['title'] + channel_id
        self._per_channel_widgets.append(tmp)

        if self._total_channels_processed == 0:
            for a_widget in widgets_list:
                a_widget['properties']['metrics'][0][3] = channel_id
                #AllChannelsWidgetsList[counter]['properties']['metrics'][0][6]['label'] = thislabel
                a_widget['properties']['region'] = region
        else:
            for a_widget in widgets_list:
                next_line = [
                    "...",
                    channel_id
                ]
                a_widget['properties']['metrics'].append(next_line)


    def get_dashboards(self, tag_selection = ""):
        """
        build the dashboards
        tag_selection - if empty then all, else uses tag matching TAG_KEY
        """
        channels = self.get_channels()

        if tag_selection != "":
            # apply a filter
            channels = self.filter_channels(channels, tag_selection)

        self.logit("EmpDashboard - processing {0} channels".format(len(channels)))
        if len(channels) < 1:
            raise Exception("No matching channels found")


        #print(json.dumps(channels))

        ## Aggregate all the metrics dictionaries into a list of dictionaries
        widgets_list = [
            EMP_IngressBytes_widget_d,
            EMP_IngressResponseTime_widget_d,
            EMP_EgressResponseTime_widget_d
        ]

        res = { "widgets" : [] }
        for channel in channels:
            self.add_channel_dashboard(channel, widgets_list)

        # build output
        for a_widget in widgets_list:
            res["widgets"].append(a_widget)
        for a_widget in self._per_channel_widgets:
            res["widgets"].append(a_widget)

        return res
