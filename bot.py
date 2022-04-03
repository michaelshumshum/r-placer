from requests import Session, auth
from threading import Thread
from json import loads
import jwt
import time
import _config

with open('dev_accounts.txt', 'r') as f:
    dev_accounts = f.read().split('\n')


def _setpixel_payload(coordinates, color):
    x, y = coordinates
    canvas = 0
    if (x > 1000):  # support for the new canvases
        x -= 1000
        if (y > 1000):
            y -= 1000
            canvas = 4
        else:
            canvas = 2
    else:
        if (y > 1000):
            y -= 1000
            canvas = 3
        else:
            canvas = 1
    return {'operationName': 'setPixel',
            'query': "mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            'variables': {
                'input': {
                    'PixelMessageData': {'coordinate': {'x': x, 'y': y}, 'colorIndex': color, 'canvasIndex': canvas},
                    'actionName': "r/replace:set_pixel"
                }
            }
            }


def _pixelhistory_payload(coordinates):
    x, y = coordinates
    if (x > 1000):
        x -= 1000
        if (y > 1000):
            y -= 1000
            canvas = 4
        else:
            canvas = 2
    else:
        if (y > 1000):
            y -= 1000
            canvas = 3
        else:
            canvas = 1
    return {"operationName": "pixelHistory",
            "variables": {
                "input": {
                    "actionName": "r/replace:get_tile_history", "PixelMessageData": {
                        "coordinate": {"x": x, "y": y}, "colorIndex": 0, "canvasIndex": canvas}}},
            "query": "mutation pixelHistory($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetTileHistoryResponseMessageData {\n            lastModifiedTimestamp\n            userInfo {\n              userID\n              username\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}


def _add_developer_account(name):
    def _write_file():
        dev_accounts.append(name)
        with open('dev_accounts.txt', 'a') as f:
            f.write('\n' + name)
    Thread(target=_write_file).start()
    s = Session()
    text = s.get('https://www.reddit.com/login').text
    csrf = text[text.find('csrf_token') + 19:text.find('csrf_token') + 59]
    r = s.post('https://www.reddit.com/login',
               data={
                   'username': _config.config['main-dev-account']['username'],
                   'password': _config.config['main-dev-account']['password'],
                   'csrf_token': csrf,
                   'otp': '',
                   'dest': 'https://www.reddit.com'
               }, headers={'content-type': 'application/x-www-form-urlencoded',
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}
               )
    time.sleep(1)
    text = s.get('https://reddit.com/prefs/apps', headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}).text
    uh = text[text.find('<input type="hidden" name="uh" value=') + 38:text.find('<input type="hidden" name="uh" value=') + 88]
    time.sleep(1)
    r = s.post('https://www.reddit.com/api/adddeveloper',
               data={
                   'uh': uh,
                   'client_id': _config.config['app-client-id'],
                   'name': name,
                   'id': f'#app-developer-{_config.config["app-client-id"]}',
                   'renderstyle': 'html'
               }, headers={'content-type': 'application/x-www-form-urlencoded',
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}
               )


class account:
    def __init__(self, username, password, auth_token=None):
        self.username = username
        self.password = password

        self.session = Session()
        self.auth_token = auth_token
        self.auth_token_expiry = 0

    def get_auth_token(self):
        if self.username not in dev_accounts:
            _add_developer_account(self.username)
        j = loads(self.session.post('https://ssl.reddit.com/api/v1/access_token', data={'grant_type': 'password',
                                                                                        'username': self.username,
                                                                                        'password': self.password},
                                    auth=auth.HTTPBasicAuth(_config.config['app-client-id'], _config.config['app-secret']),
                                    headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}).text)
        while True:  # might hit rate limit. retry later to obtain access token.
            try:
                self.auth_token = 'Bearer ' + j['access_token']
                break
            except Exception:
                time.sleep(5)
        self.auth_token_expiry = time.time() + j['expires_in']

    def check_pixel(self, coordinates):
        if not self.auth_token or (time.time() - self.auth_token_expiry >= 3550):
            self.get_auth_token()
        r = self.session.post('https://gql-realtime-2.reddit.com/query', headers={'content-type': 'application/json',
                                                                                  'origin': 'https://hot-potato.reddit.com',
                                                                                  'referer': 'https://hot-potato.reddit.com/',
                                                                                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                                                                                  'apollographql-client-name': 'mona-lisa',
                                                                                  'apollographql-client-version': '0.0.1',
                                                                                  'authorization': self.auth_token}, json=_pixelhistory_payload(coordinates))
        return r.text

    def set_pixel(self, coordinates, color):
        if not self.auth_token or (time.time() - self.auth_token_expiry >= 3550):
            self.get_auth_token()
        r = self.session.post('https://gql-realtime-2.reddit.com/query', headers={'content-type': 'application/json',
                                                                                  'origin': 'https://hot-potato.reddit.com',
                                                                                  'referer': 'https://hot-potato.reddit.com/',
                                                                                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                                                                                  'apollographql-client-name': 'mona-lisa',
                                                                                  'apollographql-client-version': '0.0.1',
                                                                                  'authorization': self.auth_token}, json=_setpixel_payload(coordinates, color))
        return r.text
