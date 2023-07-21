import bot
import parse_image
import json
import numpy as np
from websocket import WebSocketConnectionClosedException, create_connection
import random
import time
import _config
import sys
from threading import Thread, Event, current_thread
from queue import Queue
from PIL import Image
from io import BytesIO
from csv import reader
from requests import get


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
    def log(cls, text, severity):
        output = ''
        if not severity:
            raise ValueError('Severity is required')
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
        self.queue = Queue()
        self.threads = []
        self.state = 'idle'
        self.image_location = [location[0], location[1]]
        if (self.image_location[0] > 1000):
            self.image_location[0] -= 1000
            if (self.image_location[1] > 1000):
                self.image_location[1] -= 1000
                self.canvas = 4
            else:
                self.canvas = 2
        else:
            if (self.image_location[1] > 1000):
                self.image_location[1] -= 1000
                self.canvas = 3
            else:
                self.canvas = 1
        self.accounts = []
        self.image_data = parse_image.parse_image(image_dir, self.image_location)
        self.image_size = parse_image.get_image_size(image_dir)
        with open('accounts.csv', 'r') as f:
            for row in reader(f, delimiter=' '):
                email, username, password = row
                self.accounts.append({
                    'email': email,
                    'username': username,
                    'password': password,
                    'class': bot.account(username, password),
                    'next_available': 0,
                    'state': 'IDLE'
                })

    def get_board(self):
        self.accounts[0]['class'].get_auth_token()
        while True:
            try:
                ws = create_connection(
                    "wss://gql-realtime-2.reddit.com/query",
                    origin="https://garlic-bread.reddit.com",
                )
                ws.send(
                json.dumps(
                    {
                        "type": "connection_init",
                        "payload": {"Authorization": self.accounts[0]['class'].auth_token},
                    }
                )
                )
                while True:
                    try:
                        msg = ws.recv()
                    except WebSocketConnectionClosedException as e:
                        continue
                    if msg is None:
                        Logger.log(text='Websocket failure', severity=Logger.Error)
                        sys.exit()
                    if msg.startswith('{"type":"connection_ack"}'):
                        break
                ws.send(json.dumps(
                                {
                                    "id": "1",
                                    "type": "start",
                                    "payload": {
                                        "variables": {
                                            "input": {
                                                "channel": {
                                                    "teamOwner": "GARLICBREAD",
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
                while True:
                    canvas_payload = json.loads(ws.recv())
                    if canvas_payload["type"] == "data":
                        canvas_details = canvas_payload["payload"]["data"]["subscribe"]["data"]
                        break
                canvas_sockets = []

                canvas_count = len(canvas_details["canvasConfigurations"])

                for i in range(0, canvas_count):
                    canvas_sockets.append(i)
                    ws.send(
                        json.dumps(
                            {
                                "id": str(i),
                                "type": "start",
                                "payload": {
                                    "variables": {
                                        "input": {
                                            "channel": {
                                                "teamOwner": "GARLICBREAD",
                                                "category": "CANVAS",
                                                "tag": str(i),
                                            }
                                        }
                                    },
                                    "extensions": {},
                                    "operationName": "replace",
                                    "query": """subscription replace($input: SubscribeInput!) {subscribe(input: $input) {id... on BasicMessage { data {
                    __typename
                    ... on FullFrameMessageData {
                    __typename
                    name
                    timestamp
                    }
                    ... on DiffFrameMessageData {
                    __typename
                    name
                    currentTimestamp
                    previousTimestamp
                    }
                }
                }
            }
            }""",
                                },
                            }
                        )
                    )
                imgs = []

                while len(canvas_sockets) > 0:
                    temp = json.loads(ws.recv())
                    if temp["type"] == "data":
                        msg = temp["payload"]["data"]["subscribe"]
                        if msg["data"]["__typename"] == "FullFrameMessageData":
                            img_id = int(temp["id"])
                            if img_id in canvas_sockets:
                                try:
                                    imgs.append(
                                        [
                                            img_id,
                                            Image.open(BytesIO(get(msg["data"]["name"],stream=True,).content)),
                                        ]
                                    )
                                except Exception as e:
                                    pass

                                canvas_sockets.remove(img_id)


                for i in range(0, canvas_count - 1):
                    ws.send(json.dumps({"id": str(2 + i), "type": "stop"}))

                ws.close()

                new_img_width = (
                    max(map(lambda x: x["dx"], canvas_details["canvasConfigurations"])) +
                    canvas_details["canvasWidth"]
                )

                new_img_height = (
                    max(map(lambda x: x["dy"], canvas_details["canvasConfigurations"])) +
                    canvas_details["canvasHeight"]
                )
                new_img = Image.new("RGB", (new_img_width, new_img_height))

                for idx, img in enumerate(sorted(imgs, key=lambda x: x[0])):
                    dx_offset = int(canvas_details["canvasConfigurations"][idx]["dx"])
                    dy_offset = int(canvas_details["canvasConfigurations"][idx]["dy"])
                    new_img.paste(img[1], (dx_offset, dy_offset))

                new_img = new_img.crop((0,500,1500,1500)
                        ).crop(
                                    (self.image_location[0],
                                     self.image_location[1] ,
                                     self.image_location[0] + self.image_size[1] ,
                                     self.image_location[1] + self.image_size[0] )
                                )
                new_img.save('board.png')
                return parse_image.parse_image(new_img, self.image_location)
            except Exception as e:
                print(e)
                time.sleep(30)

    def stage_events(self):  # get all unset pixels from get_image_state. create a queue of events that can that the accounts can execute.
        events = {i: [] for i in range(1, 33)}
        for (x, y), color in self.get_board().items():
            if self.image_data[(x, y)] != color:
                events[self.image_data[(x, y)]].append((x, y))
        deletes = []
        for event in events:
            if len(events[event]) == 0:
                deletes.append(event)
        for d in deletes:
            del events[d]
        return events

    def choose_account(self):
        for i in range(len(self.accounts)):
            account = random.choice(self.accounts)
            if (account['state'] == 'BANNED') or (account['next_available'] > time.time()) or (account['state'] == 'IN USE'):
                continue
            else:
                return account
        return None

    def check_ban_status(self):
        bans = 1
        for account in self.accounts:
            if account['state'] == 'BANNED':
                bans += 1
        if bans == len(self.accounts):
            Logger.log('All accounts banned!', severity=Logger.Error)
            self.stop()

    def event_queuer(self, thread_event):
        def sorted_key(x):
            return len(x[1])
        next_update = 0
        while thread_event.is_set():
            if time.time() >= next_update:
                events = sorted(list(self.stage_events().items()), key=sorted_key)
                next_update = time.time() + _config.config['event-update-interval']
                for color, c in events:
                    for coords in c:
                        random.shuffle(c)
                        self.queue.put((coords, color))
                Logger.log(f'Updated events. Next update at {next_update}, which is {_config.config["event-update-interval"]} seconds from now.', severity=Logger.Verbose)
                for account in self.accounts:
                    if len(account['username']) < 16:
                        print(f"{account['username']}\t\t{account['next_available']}\t{account['state']}")
                    else:
                        print(f"{account['username']}\t{account['next_available']}\t{account['state']}")

    def execute_events(self, thread_event):
        while thread_event.is_set():
            try:
                time.sleep(random.randint(1, 1 + int(_config.config['worker-count'] / 2)))  # random sleep for less worker conflict
                if self.queue.empty():
                    continue
                else:
                    account = self.choose_account()
                    if not account:
                        Logger.log(f'{current_thread().name} - No accounts available! Waiting 30 seconds.', severity=Logger.Error)
                        time.sleep(30)
                        continue
                account['state'] = 'IN USE'
                coords, color = self.queue.get()
                coords = [coords[0], coords[1] + 500]
                Logger.log(f'{current_thread().name} - Setting pixel {coords} on canvas {self.canvas} to color {color}', severity=Logger.Verbose)
                r = json.loads(account['class'].set_pixel(coords, color, self.canvas))
                if 'errors' in r.keys():
                    self.queue.put((coords, color))  # retry the last action
                    if (r['errors'][0]['extensions']['nextAvailablePixelTs'] / 1000) - time.time() > 1000:
                        account['state'] = 'BANNED'
                        Logger.log(f'{current_thread().name} - Account {account["username"]} is banned!', severity=Logger.Warn)
                        Logger.log(f'{current_thread().name} - Failed last action due to ban.', severity=Logger.Error)
                        account['next_available'] = r['errors'][0]['extensions']['nextAvailablePixelTs'] / 1000
                        self.check_ban_status()
                    else:
                        account['state'] = 'IDLE'
                        Logger.log(f'{current_thread().name} - Failed last action due to unknown next availability.', severity=Logger.Warn)
                        account['next_available'] = r['errors'][0]['extensions']['nextAvailablePixelTs'] / 1000
                else:
                    account['state'] = 'IDLE'
                    account['next_available'] = r['data']['act']['data'][0]['data']['nextAvailablePixelTimestamp'] / 1000
            except Exception as e:
                account['state'] = 'IDLE'
                Logger.log(f'{current_thread().name} - Failed last action due to exception "{e}".', severity=Logger.Error)

    def run(self):
        self.thread_event = Event()
        self.thread_event.set()
        self.threads.append(Thread(target=self.event_queuer, name='event-queuer', args=(self.thread_event,)))
        for i in range(_config.config['worker-count']):
            self.threads.append(Thread(target=self.execute_events, name=f'worker{i}', args=(self.thread_event,)))
        for thread in self.threads:
            thread.start()
            Logger.log(f'Started {thread.name}', severity=Logger.Verbose)
            time.sleep(0.1)
        self.state = 'running'

    def stop(self):
        self.thread_event.clear()
        Logger.log('Stopping...', severity=Logger.Moderate)
        for thread in self.threads:
            if thread != current_thread():
                thread.join()
            Logger.log(f'Stopped {thread.name}', severity=Logger.Verbose)
        self.state = 'stopped'
