"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental MediaConnect metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""

from datetime import datetime
import boto3


TAG_KEY="Product"
EMX_SourceBitRate_widget_d = {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 18,
            "height": 6,
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaConnect",
                        "SourceBitRate",
                        "FlowARN",
                        "{flow_arn}",
                        { "label": "{flow_name}" }
                    ],
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-west-2",
                "title": "Source Bitrates",
                "period": 60,
                "stat": "Average"
            }
}
EMX_SourceRecoveredPackets_widget_d = {
            "type": "metric",
            "x": 0,
            "y": 6,
            "width": 9,
            "height": 6,
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaConnect",
                        "SourceRecoveredPackets",
                        "FlowARN",
                        "{flow_arn}",
                        { "label": "{flow_name}" }
                    ],
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-west-2",
                "title": "Source Recovered Packets",
                "period": 60,
                "stat": "Average",
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
}
EMX_SourceNotRecoveredPackets_widget_d =  {
            "type": "metric",
            "x": 9,
            "y": 6,
            "width": 9,
            "height": 6,
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaConnect",
                        "SourceNotRecoveredPackets",
                        "FlowARN",
                        "{flow_arn}",
                        { "label": "{flow_name}" }
                    ],
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-west-2",
                "title": "Source Not Recovered Packets",
                "period": 60,
                "stat": "Average"
            }
}
EMX_SourceFECRecovered_widget_d = {
            "type": "metric",
            "x": 0,
            "y": 12,
            "width": 9,
            "height": 6,
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaConnect",
                        "SourceFECRecovered",
                        "FlowARN",
                        "{flow_arn}",
                        { "label": "{flow_name}" }
                    ],
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-west-2",
                "title": "Source FEC Recovered Packets",
                "period": 60,
                "stat": "Average",
                "yAxis": {
                    "left": {
                        "min": 0
                    }
                }
            }
        }
EMX_SourceContinuityCounter_widget_d = {
            "type": "metric",
            "x": 9,
            "y": 12,
            "width": 9,
            "height": 6,
            "properties": {
                "metrics": [
                    [
                        "AWS/MediaConnect",
                        "SourceContinuityCounter",
                        "FlowARN",
                        "{flow_arn}",
                        { "label": "{flow_name}" }
                    ],
                ],
                "view": "timeSeries",
                "stacked": False,
                "region": "us-west-2",
                "title": "Source Continuity Error Counter",
                "period": 60,
                "yAxis": {
                    "left": {
                        "label": "Incorrectly Ordered or Lost Pkts",
                        "min": 0
                    }
                },
                "stat": "Average"
            }
}


class EmxDashboard:
    """
    a class to create Elemental Media Connect dashboard
    """
    _logger = None
    _mc_client = None

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


    def add_flow_dashboard(self, flow, flow_row, widgets_list):
        """
        build dashboard for 1 flow
        """
        metric_template_line = [ "...", "nextarn", { "label": "labelvalue" } ]
        this_flowname = (flow['Name'])
        this_flowarn = (flow['FlowArn'])
        arn_split = this_flowarn.split(":")
        region = arn_split[3]

        if flow_row == 0:
            # we are in the first line of each metric - special case due formatting needed
            for a_widget in widgets_list:
                a_widget['properties']['metrics'][0][3] = this_flowarn
                a_widget['properties']['metrics'][0][4]['label'] = this_flowname
                a_widget['properties']['region']= region
        else:
            ## we are in rows 2-N, so add a line to each metric:
            for a_widget in widgets_list:
                a_widget['properties']['metrics'].append(metric_template_line)
                a_widget['properties']['metrics'][flow_row][1] = this_flowarn
                a_widget['properties']['metrics'][flow_row][2]['label'] = this_flowname

        return widgets_list


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

        flow_row = -1

        ## Aggregate all the metrics dictionaries into a list of dictionaries
        widgets_list = [
            EMX_SourceBitRate_widget_d,
            EMX_SourceRecoveredPackets_widget_d,
            EMX_SourceNotRecoveredPackets_widget_d,
            EMX_SourceFECRecovered_widget_d,
            EMX_SourceContinuityCounter_widget_d
        ]

        for flow in flows:
            flow_row=flow_row + 1
            self.add_flow_dashboard(flow, flow_row, widgets_list)

        res = { "widgets" : [] }
        res["widgets"] = widgets_list
        return res
