import os
import yaml
import datetime
currentpath=os.path.dirname(os.path.abspath(__file__))
superiorpath=os.path.dirname(currentpath)
dt_now=datetime.datetime.now().strftime('%y%m%d%H%M%S')
with open('%s/settings/settings.yaml' % superiorpath) as yamlfile:
    yml = yaml.load(yamlfile,Loader=yaml.SafeLoader)
figuredirectory=yml["figuredirectory"]
def check_figuredirectory():
    if not os.path.exists(figuredirectory):
        os.mkdir(figuredirectory)