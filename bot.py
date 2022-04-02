from requests import Session, auth
from threading import Thread
import jwt
import time
import json

with open('config.json', 'r') as f:
    config = json.load(f)

with open('dev_accounts.txt', 'r') as f:
    dev_accounts = f.read().split('\n')


def _payload(coordinates, color):
    x, y = coordinates
    return {'operationName': 'setPixel',
            'query': "mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
            'variables': {
                'input': {
                    'PixelMessageData': {'coordinate': {'x': x, 'y': y}, 'colorIndex': color, 'canvasIndex': 0},
                    'actionName': "r/replace:set_pixel"
                }
            }
            }


def _add_developer_account(name):
    def _write_file():
        dev_accounts.append(name)
        with open('dev_accounts.txt', 'w+') as f:
            for d in dev_accounts:
                f.write(d)
    Thread(target=_write_file).start()
    s = Session()
    text = s.get('https://www.reddit.com/login').text
    csrf = text[text.find('csrf_token') + 19:text.find('csrf_token') + 59]
    r = s.post('https://www.reddit.com/login',
               data={
                   'username': config['main-dev-account']['username'],
                   'password': config['main-dev-account']['password'],
                   'csrf_token': csrf,
                   'otp': '',
                   'dest': 'https://www.reddit.com'
               }, headers={'content-type': 'application/x-www-form-urlencoded',
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}
               )
    time.sleep(1)
    text = s.get('https://reddit.com/prefs/apps', headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}).text
    uh = text[text.find('<input type="hidden" name="uh" value=') + 38:text.find('<input type="hidden" name="uh" value=') + 88]
    print(uh)
    time.sleep(1)
    r = s.post('https://www.reddit.com/api/adddeveloper',
               data={
                   'uh': uh,
                   'client_id': config['app-client-id'],
                   'name': name,
                   'id': f'#app-developer-{config["app-client-id"]}',
                   'renderstyle': 'html'
               }, headers={'content-type': 'application/x-www-form-urlencoded',
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}
               )
    print(r.text)


class account:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = Session()
        self.auth_token = None
        self.auth_token_expiry = 0

    def get_auth_token(self):
        if self.username not in dev_accounts:
            _add_developer_account(self.username)
        j = json.loads(self.session.post('https://ssl.reddit.com/api/v1/access_token', data={'grant_type': 'password',
                                                                                             'username': self.username,
                                                                                             'password': self.password},
                                         auth=auth.HTTPBasicAuth(config['app-client-id'], config['app-secret']),
                                         headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}).text)
        self.auth_token = 'Bearer ' + j['access_token']
        self.auth_token_expiry = time.time() + j['expires_in']

    def add_pixel(self, coordinates, color):
        r = self.session.get(f'https://www.reddit.com/r/place?cx={coordinates[0]}&cy={coordinates[1]}&px=18', headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0', })
        if not self.auth_token or (time.time() - self.auth_token_expiry >= 3550):
            self.get_auth_token()
        r = self.session.post('https://gql-realtime-2.reddit.com/query', headers={'content-type': 'application/json',
                                                                                  'origin': 'https://hot-potato.reddit.com',
                                                                                  'referer': 'https://hot-potato.reddit.com/',
                                                                                  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                                                                                  'apollographql-client-name': 'mona-lisa',
                                                                                  'apollographql-client-version': '0.0.1',
                                                                                  'authorization': self.auth_token}, json=_payload(coordinates, color))
        return r.text


if __name__ == '__main__':
    a = account('OEawoobNgXFQGfpwTDlS', '#z|6D~LICM}7tZYo')  # this is the burner account i am using for testing. feel free to use it.
    print(a.add_pixel((3, 0), 3))
