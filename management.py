import bot
import parse_image
import json
import numpy as np
import random
import time
import _config
import sys
from threading import Thread, Event
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
        self.canvas = 0
        x = self.image_size[0]
        while self.canvas > 1000:  # adjust x-coordinate for other canvases
            x -= 1000
            self.canvas += 1

        self.image_location = location
        self.accounts = []
        with open('accounts.csv', 'r') as f:
            for row in reader(f, delimiter=' '):
                email, username, password = row
                self.accounts.append({
                    'email': email,
                    'username': username,
                    'password': password,
                    'class': bot.account(username, password),
                    'next_available': 0,
                    'state': 'OK'
                })

    def get_board(self):  # from https://github.com/Zequez/reddit-placebot/issues/46#issuecomment-1086736236
        self.accounts[0]['class'].get_auth_token()
        r = json.loads(get('https://canvas.codes/canvas').text)
        if self.canvas == 0:
            img = Image.open(BytesIO(get(r['canvas_left']).content))
        else:
            img = Image.open(BytesIO(get(r['canvas_right']).content))
        img = img.convert('RGB').crop(
            (self.image_location[0],
             self.image_location[1],
             self.image_location[0] + self.image_size[1],
             self.image_location[1] + self.image_size[0])
        )
        img.save('board.png')
        return parse_image.parse_image(img, self.image_location)

    def stage_events(self):  # get all unset pixels from get_image_state. create a queue of events that can that the accounts can execute.
        events = {i: [] for i in range(1, 33)}
        change_count = 0
        for (x, y), color in self.get_board().items():
            if self.image_data[(x, y)] != color:
                events[self.image_data[(x, y)]].append((x, y))
                change_count += 1
        deletes = []
        for event in events:
            if len(events[event]) == 0:
                deletes.append(event)
        for d in deletes:
            del events[d]
        return events, change_count

    def choose_account(self):
        for i in range(len(self.accounts)):
            account = random.choice(self.accounts)
            if (account['state'] == 'BANNED') or (account['next_available'] > time.time()):
                continue
            else:
                return account
        return None

    def execute_events(self, events):
        def f(x):
            return len(x[1])
        events = sorted(list(events.items()), key=f)
        for color, c in events:
            Logger.log(f'Starting events for color {color}', severity=Logger.Moderate)
            for coords in c:
                Logger.log(f'Setting pixel {coords} with color {color}', severity=Logger.Moderate)
                account = self.choose_account()
                if not account:
                    Logger.log('All accounts banned!', severity=Logger.Error)
                    sys.exit()
                r = json.loads(account['class'].set_pixel(coords, color))
                if 'errors' in r.keys():
                    if r['errors'][0]['extensions']['nextAvailablePixelTs'] > 1000:
                        account['state'] = 'BANNED'
                        Logger.log(f'Account {account["username"]} is banned!', severity=Logger.Warn)
                    else:
                        account['next_available'] = r['errors'][1]['next available']
                    Logger.log('Failed last action due to error.', severity=Logger.Error)
                else:
                    account['next_available'] = r['data']['act']['data'][0]['data']['nextAvailablePixelTimestamp']
                time.sleep(1)

    def run(self):
        def f(event):
            while event.is_set():
                events, changes = self.stage_events()
                Logger.log(f'Making {changes} changes to existing board.', severity=Logger.Moderate)
                Logger.log(f'Using colors {tuple(events.keys())}.', severity=Logger.Moderate)
                self.execute_events(events)
        self.thread_event = Event()
        self.thread_event.set()
        self.thread = Thread(target=f, args=(self.thread_event,))
        self.thread.run()

    def stop(self):
        self.thead_event.clear()
