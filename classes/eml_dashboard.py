"""
  a rewrite of the work by R.Clements in pure python

  a simple CW dashboard maker for key Elemental Media Live  metrics
  NOT official AWS product in any way!  Just a helper script.
  R.Clements 03-2021
"""

from datetime import datetime
import boto3


TAG_KEY="Product"
EML_NetworkIn_widget_d = {
    "type": "metric",
    "x": 0,
    "y": 0,
    "width": 21,
    "height": 6,
    "properties": {
        "metrics": [
            [
                "MediaLive",
                "NetworkIn",
                "ChannelId",
                "firstchannelID",
                "Pipeline",
                "0",
                { "label": "firstchannelID p0" }
            ]
        ],
        "view": "timeSeries",
        "stacked": False,
        "title": "MediaLive - AVG NetworkIn Bytes [rolling avg]",
        "region": "us-west-2",
        "period": 60,
        "stat": "Average",
        "yAxis": {
            "left": {
                "min": 0
            }
        },
        "legend": {
            "position": "right"
        }
    }
}
EML_Fillframes_widget_d = {
    "type": "metric",
    "x": 0,
    "y": 6,
    "width": 21,
    "height": 6,
    "properties": {
        "metrics": [
            [
                "MediaLive",
                "FillMsec",
                "ChannelId",
                "firstchannelID",
                "Pipeline",
                "0",
                { "label": "firstchannelID p0" }
            ]
        ],
        "view": "timeSeries",
        "stacked": False,
        "region": "us-west-2",
        "title":
        "Ms of Fill frames inserted on outputs [rolling avg] - indicates possible input issue",
        "stat": "Average",
        "period": 60,
        "legend": {
            "position": "right"
        }
    }
}
EML_SVQ_widget_d = {
    "type": "metric",
    "x": 0,
    "y": 9,
    "width": 21,
    "height": 6,
    "properties": {
        "metrics": [
            [
                "MediaLive",
                "SvqTime",
                "ChannelId",
                "firstchannelID",
                "Pipeline",
                "0",
                { "label": "firstchannelID p0" }
            ]
        ],
        "view": "timeSeries",
        "region": "us-west-2",
        "title": "Quality Reductions to maintain framerate [rolling avg] ",
        "period": 60,
        "liveData": True,
        "stacked": False,
        "yAxis": {
            "left": {
                "min": 0,
                "max": 10,
                "label": "Forced Quality Reductions"
            }
        },
        "stat": "Average",
        "legend": {
            "position": "right"
        }
	}
}
EML_InputFrmRt_widget_d = {
    "type": "metric",
    "x": 0,
    "y": 12,
    "width": 21,
    "height": 6,
    "properties": {
        "metrics": [
            [
                "MediaLive",
                "InputVideoFrameRate",
                "ChannelId",
                "firstchannelID",
                "Pipeline",
                "0",
                { "label": "firstchannelID p0" }
            ]
        ],
        "view": "timeSeries",
        "stacked": False,
        "region": "us-west-2",
        "period": 60,
        "yAxis": {
            "left": {
                "min": 0,
                "max": 75,
                "label": "FPS"
            }
        },
        "stat": "Average",
        "title": "Input Frame Rate [rolling avg]",
        "legend": {
            "position": "right"
        }
    }
}
RTP_widget_d = {
           "type": "metric",
            "x": 0,
            "y": 15,
            "width": 21,
            "height": 6,
            "properties": {
    "metrics": [
        [
            "MediaLive",
            "RtpPacketsReceived",
            "ChannelId",
            "firstchannelID",
            "Pipeline",
            "0",
            { "label": "Pkts-Received_chanID_PL0" }
        ],
        [
            ".",
            "RtpPacketsRecoveredViaFec",
            ".",
            ".",
            ".",
            ".",
            { "label": "Pkts-RecoveredViaFec_chanID_PL0" }
        ],
        [
            ".",
            "RtpPacketsLost",
            ".",
            ".",
            ".",
            ".",
            { "label": "Pkts-Lost_chanID_PL0" }
        ]
    ],
    "view": "singleValue",
    "stacked": False,
    "region": "us-west-2",
    "period": 60,
    "stat": "Sum",
    "title": "RTP Input Metrics"
  },
  "legend": {
                    "position": "right"
                }
}


class EmlDashboard:
    """
    a class to create Elemental Media Live dashboard
    """
    _logger = None
    _ml_client = None
    _needs_rtp_widget = 0
    _rtp_widgets_list=[]
    _total_rtp_widgets = 0
    _total_pipelines = -1

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


    def add_channel_dashboard(self, channel, widgets_list):
        """
        build dashboard for 1 flow
        """
        metric_template_line = [
            "...",
            "nextchannelID",
            "Pipeline",
            "nextpipevalue",
            { "label": "labelvalue" }
        ]
        channel_name = channel['Name']
        this_flowarn = channel['Arn']
        arn_split = this_flowarn.split(":")
        region = arn_split[3]
        channel_id = channel["Id"]

        for inputcounter in range (0,len(channel['InputAttachments'])) :
            this_input_id = channel['InputAttachments'][inputcounter]['InputId']
            this_input_name = channel['InputAttachments'][inputcounter]['InputAttachmentName']

            this_input_description = self._ml_client.describe_input(
                InputId=this_input_id
            )

            if this_input_description['Type']  == "RTP_PUSH" :
                self._needs_rtp_widget = 1

                ## add an empty element to the RTP widget list
                rtp_widget_list = []
                rtp_widget_list[0] = {
                "type": "metric",
                    "x": 0,
                    "y": 15,
                    "width": 9,
                    "height": 3,
                    "properties": {
                        "metrics": [
                            [
                                "MediaLive",
                                "RtpPacketsReceived",
                                "ChannelId",
                                "firstchannelID",
                                "Pipeline",
                                "0",
                                { "label": "." }
                            ],
                            [
                                ".",
                                "RtpPacketsRecoveredViaFec",
                                ".",
                                ".",
                                ".",
                                ".",
                                { "label": "." }
                            ],
                            [
                                ".",
                                "RtpPacketsLost",
                                ".",
                                ".",
                                ".",
                                ".",
                                { "label": "." }
                            ]
                        ],
                        "view": "singleValue",
                        "stacked": "false",
                        "region": "us-west-2",
                        "period": 3600,
                        "stat": "Sum",
                        "title": "RTP Input Metrics [Total for last hr]"
                        }
                    }

                rtp_widget_list[0]['properties']['region'] = region
                # first line of RTP metric
                rtp_widget_list[0]['properties']['metrics'][0][3] = channel_id
                rtp_widget_list[0]['properties']['metrics'][0][5] = "0"
                rtp_widget_list[0]['properties']['metrics'][0][6]['label'] = \
                    "Pkts-Recvd_CH:"+channel_id+"_PL0"
                ## second line of RTP Metric
                rtp_widget_list[0]['properties']['metrics'][1][3] = channel_id
                rtp_widget_list[0]['properties']['metrics'][1][5] = "0"
                rtp_widget_list[0]['properties']['metrics'][1][6]['label'] = \
                    "Pkts-RecoveredViaFec_CH:"+channel_id+"_PL0"
                ## third line of RTP metric
                rtp_widget_list[0]['properties']['metrics'][2][3] = channel_id
                rtp_widget_list[0]['properties']['metrics'][2][5] = "0"
                rtp_widget_list[0]['properties']['metrics'][2][6]['label'] = \
                    "Pkts-Lost_CH:"+channel_id+"_PL0"
                ## title of Metric
                rtp_widget_list[0]['properties']['title'] = \
                    f"RTP Packet Status for Channel:{channel_id}, Input:{this_input_name}"

                self._rtp_widgets_list.append(rtp_widget_list[0])
                self._total_rtp_widgets+=1

        # handle pipeline0 first
        this_label = "CH:" + channel_name + "_PL:0"
        if self._total_pipelines == 0 :
            # special case for first line of each metric due to param counts
            for a_widget in widgets_list:
                a_widget['properties']['metrics'][0][3] = channel_id
                a_widget['properties']['metrics'][0][5] = "0"
                a_widget['properties']['metrics'][0][6]['label'] = this_label
                a_widget['properties']['region']= region

        else:
            ## we are in rows 2-N, so add a line to each metric:
            #print("\n","Adding a row to each widget for channel",chanID)
            for a_widget in widgets_list:
                a_widget['properties']['metrics'].append(metric_template_line)

            ## now set the values
            for a_widget in widgets_list:
                a_widget['properties']['metrics'][self._total_pipelines][1] = channel_id
                a_widget['properties']['metrics'][self._total_pipelines][3] = "0"
                a_widget['properties']['metrics'][self._total_pipelines][4]['label'] = this_label

        if channel['ChannelClass'] == 'STANDARD':
            self._total_pipelines = self._total_pipelines + 1
            metric_template_line = [
                "...",
                "nextchannelID",
                "Pipeline",
                "nextpipevalue",
                { "label": "labelvalue" }
            ]
            thislabel = "CH:"+ channel_name + "_PL:1"
            for a_widget in widgets_list:
                widgets_list[a_widget]['properties']['metrics'].append(metric_template_line)

            for a_widget in widgets_list:
                a_widget['properties']['metrics'][self._total_pipelines][1] = channel_id
                a_widget['properties']['metrics'][self._total_pipelines][3] = "0"
                a_widget['properties']['metrics'][self._total_pipelines][4]['label'] = thislabel

        return widgets_list


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

        # ------------------------------------------------------------------------------------
        ## Iterate through all the discovered channels
        # set a boolean for need RTP widget
        self._needs_rtp_widget = 0

        ## Aggregate all the metrics dictionaries into a list of dictionaries
        widgets_list = [
            EML_NetworkIn_widget_d,
            EML_InputFrmRt_widget_d,
            EML_Fillframes_widget_d,
            EML_SVQ_widget_d
        ]

        for channel in channels:
            # self.logit(flow)
            self._total_pipelines=self._total_pipelines + 1
            self.add_channel_dashboard(channel, widgets_list)

        res = { "widgets" : [] }
        res["widgets"] = widgets_list
        return res
