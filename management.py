import bot
import parse_image
import json
import numpy as np
import random
import time
import _config
from threading import Thread, Event
from queue import Queue
from PIL import Image
from io import BytesIO
from csv import reader
from requests import get
from websocket import create_connection


class Logger:

    class Severity:
        pass

    class Moderate(Severity):
        pass

    class Error(Severity):
        pass

    class Success(Severity):
        pass

    class Warn(Severity):
        pass

    class Verbose(Severity):
        pass

    verbose = False  # change this to true for inclusion verbose logging

    @classmethod
    def log(cls, text, severity=Moderate):
        output = ''
        if not isinstance(severity(), cls.Severity):
            raise TypeError(f'must be Logger.Severity, not {severity.__name__}')
        if isinstance(severity(), cls.Verbose) and not cls.verbose:
            return
        if isinstance(severity(), cls.Moderate) or (isinstance(severity(), cls.Verbose) and cls.verbose):
            output += '[INFO]'
        elif isinstance(severity(), cls.Error):
            output += '[31m[ERROR][0m'  # invisible character is actuall backslash033
        elif isinstance(severity(), cls.Success):
            output += '[32m[SUCCESS][0m'
        elif isinstance(severity(), cls.Warn):
            output += '[33m[WARN][0m'

        print(output + ' ' + text)


Logger.verbose = _config.config['verbose']


class manager:
    def __init__(self, image_dir, location):
        self.image_data = parse_image.parse_image(image_dir, location)
        self.image_size = parse_image.get_image_size(image_dir)
        self.image_location = location
        self.accounts = []
        with open('accounts.csv', 'r') as f:
            for row in reader(f):
                email, username, password = row
                self.accounts.append({
                    'email': email,
                    'username': username,
                    'password': password,
                    'class': bot.account(username, password),
                    'next_available': 0,
                    'state': 'OK'
                })

    def get_board(self):  # from https://github.com/rdeepak2002/reddit-place-script-2022/blob/main/main.py
        self.accounts[0]['class'].get_auth_token()
        ws = create_connection(
            "wss://gql-realtime-2.reddit.com/query",
            origin="https://hot-potato.reddit.com",
        )
        ws.send(
            json.dumps(
                {
                    "type": "connection_init",
                    "payload": {"Authorization": self.accounts[0]['class'].auth_token},
                }
            )
        )
        ws.recv()
        ws.send(
            json.dumps(
                {
                    "id": "1",
                    "type": "start",
                    "payload": {
                        "variables": {
                            "input": {
                                "channel": {
                                    "teamOwner": "AFD2022",
                                    "category": "CONFIG",
                                }
                            }
                        },
                        "extensions": {},
                        "operationName": "configuration",
                        "query": "subscription configuration($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on ConfigurationMessageData {\n          colorPalette {\n            colors {\n              hex\n              index\n              __typename\n            }\n            __typename\n          }\n          canvasConfigurations {\n            index\n            dx\n            dy\n            __typename\n          }\n          canvasWidth\n          canvasHeight\n          __typename\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                    },
                }
            )
        )
        ws.recv()
        ws.send(
            json.dumps(
                {
                    "id": "2",
                    "type": "start",
                    "payload": {
                        "variables": {
                            "input": {
                                "channel": {
                                    "teamOwner": "AFD2022",
                                    "category": "CANVAS",
                                    "tag": "0",
                                }
                            }
                        },
                        "extensions": {},
                        "operationName": "replace",
                        "query": "subscription replace($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on FullFrameMessageData {\n          __typename\n          name\n          timestamp\n        }\n        ... on DiffFrameMessageData {\n          __typename\n          name\n          currentTimestamp\n          previousTimestamp\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                    },
                }
            )
        )

        file = ""
        while True:
            temp = json.loads(ws.recv())
            if temp["type"] == "data":
                msg = temp["payload"]["data"]["subscribe"]
                if msg["data"]["__typename"] == "FullFrameMessageData":
                    file = msg["data"]["name"]
                    break

        ws.close()
        img = Image.open(BytesIO(get(file, stream=True).content))
        img = img.crop(
            (self.image_location[0],
             self.image_location[1],
             self.image_location[0] + self.image_size[1],
             self.image_location[1] + self.image_size[0])
        )
        return np.array(img)

    def stage_events(self):  # get all unset pixels from get_image_state. create a queue of events that can that the accounts can execute.
        events = {i: [] for i in range(1, 33)}
        board = self.get_board()
        change_count = 0
        for (x, y), color in parse_image.parse_board_array(board, self.image_location).items():
            if self.image_data[(x, y)] != color:
                events[color].append((x, y))
                change_count += 1
        return events, change_count

    def choose_account(self):
        while True:
            account = random.choice(self.accounts)
            if (account['state'] == 'BANNED') or (account['next_draw'] > time.time()):
                continue
            else:
                return account
        return None

    def execute_events(self, events):
        for color, c in events:
            for coords in c:
                account = self.choose_account()
                if not account:
                    raise Exception('All accounts banned!')
                r = json.loads(account['class'].set_pixel(coords, color))
                if 'error' in r.keys:
                    account['state'] = 'BANNED'
                else:
                    account['next_available'] = r['data']['act']['data'][0]['data']['nextAvailablePixelTimestamp']
                time.sleep(1)

    def run(self):
        def f(event):
            while event.is_set():
                self.execute_events(self.stage_events())
        self.thread_event = Event()
        self.thread_event.set()
        self.thread = Thread(target=f, args=(self.thread_event))
        self.thread.run()

    def stop(self):
        self.thead_event.clear()


if __name__ == '__main__':
    m = manager('/Users/shum/Desktop/Screenshot 2022-04-03 at 3.16.13 AM.png', (100, 50))
