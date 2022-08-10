# aws_media_dashboards
a python only rewrite of the AWS media dashboard scripts

https://aws.amazon.com/blogs/media/cs-quick-and-easy-media-services-dashboards/

# Implemented Classes
* CloudwatchDashboard - just used to post the created JSON to AWS
* EmxDashboard - Elemental Media Connect Dashboard builder
* EmlDashboard - Elemental Media Live Dashboard builder
* EmpDashboard - Elemental Media Package Dashboard builder

I haven't done the other dashboards, yet, as I don't need them!

# Change To Jinga
I've chnaged the code to use Jinja2 templates to make the code a little easier to read. Need to
fully test but it should allow the templates to be quickly changed and edited.

