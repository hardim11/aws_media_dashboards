# aws_media_dashboards
a python only rewrite of the AWS media dashboard scripts

https://aws.amazon.com/blogs/media/cs-quick-and-easy-media-services-dashboards/

# Implemented Classes
* CloudwatchDashboard - just used to post the created JSON to AWS
* JinjaRender - wrapper for the Jinja2 template renderer
* EmxDashboard - Elemental Media Connect Dashboard builder
* EmlDashboard - Elemental Media Live Dashboard builder
* EmpDashboard - Elemental Media Package Dashboard builder
* EmcDashboard - Elemental Media convert Dashboard builder
* S3Dashboard - S3 Bucket summary

I haven't done the other dashboards, yet, as I don't need them!

# Requirements
* python3
* pip to install the required libraries, namely
* * boto3 - the AWS library
* * Jinja2 - the template renderer library
* You will need the AWS profile setup, this is done via installing the AWS CLI and running aws configure.


# Installing
* Download and unzip
* Install Python dependancies by changing to the folder with the requirements.txt and running

    pip install -r requirements.txt

* configure the script by editing main.py - the two constants to change are
* * AWS_PROFILE - the name of a profile you have created on your system (e.g. via "aws configure")
* * AWS_REGION - the AWS region to look for resources in and also to create the dashboard in, e.g. eu-west-1
* run the script (python maybe python3 on some systems)

    python main.py

Edit the main.py to pick and choose which dashboards / the AWS profile you use and the region

# Change To Jinga2
I've changed the code to use Jinja2 templates to make the code a little easier to read. Need to
fully test but it should allow the templates to be quickly changed and edited.

# TODO
* make more generic
* test!
* build a command line interface
* support better filtering by name and tags
* support deleting "empty" dashboards
* Make the region and profile more flexible (rather than coded)

