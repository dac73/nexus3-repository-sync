#!/usr/bin/env python3

from os import getenv
from config import FROM_COOKIE, FROM_HOST_URL, FROM_REPO_NAME, TO_COOKIE, TO_HOST_URL, TO_REPO_NAME
import requests

TEMP_FILE = 'tmp_nexus_asset'


def get_assets(next_token=None):
    headers = {
        'Cookie': FROM_COOKIE,
        'accept': 'application/json'
    }
    cnt_token_string = ''
    if next_token is not None:
        cnt_token_string = 'continuationToken=%s&' % next_token

    req_url = '%s/service/rest/v1/assets?%srepository=%s' % (
        FROM_HOST_URL, cnt_token_string, FROM_REPO_NAME)
    res = requests.get(req_url, headers=headers)
    return res.json()


def download_asset(download_url):
    print('Downloading: %s' % download_url)
    headers = {
        'Cookie': FROM_COOKIE
    }
    with open(TEMP_FILE, 'wb') as file:
        res = requests.get(download_url, headers=headers)
        file.write(res.content)


def upload_asset(path):
    directory = path.split('/')[0]
    filename = path.split('/')[1]
    headers = {
        'Cookie': TO_COOKIE,
        'accept': 'application/json'
    }
    files = {
        'raw.directory': (None, directory),
        'raw.asset1': (filename, open(TEMP_FILE, 'rb')),
        'raw.asset1.filename': (None, filename)
    }
    post_url = '%s/service/rest/v1/components?repository=%s' % (
        TO_HOST_URL, TO_REPO_NAME)
    resp = requests.post(post_url, headers=headers, files=files)
    print(resp)


items = []
assets = get_assets()
items.append(assets['items'])
while assets['continuationToken']:
    assets = get_assets(assets['continuationToken'])
    items.append(assets['items'])
    print('Processed token: %s' % assets['continuationToken'])

for assets in items:
    for asset in assets:
        download_asset(asset['downloadUrl'])
        upload_asset(asset['path'])

print('Done')
