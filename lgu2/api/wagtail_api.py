import requests

base_url = "http://lgu2-cms.eu-west-2.elasticbeanstalk.com/api/v2/"

def get_wagtail_content(url):
    url = base_url + url
    headers = {'Accept': "application/json"}
    api_data = requests.get(url, headers=headers)
    return api_data.json()
