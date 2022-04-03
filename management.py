import bot
import parse_image
import json
import numpy as np
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
        self.queue = Queue()
        self.threads = []
        self.state = 'idle'
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
                    'state': 'IDLE'
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
        img.save('board.png')  # save image to see success of the bot
        return parse_image.parse_image(img, self.image_location)

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
                account['state'] = 'IN USE'
                return account
        return None

    def event_queuer(self, thread_event):
        def sorted_key(x):
            return len(x[1])
        next_update = 0
        while thread_event.is_set():
            if time.time() >= next_update:
                with self.queue.mutex:
                    self.queue.queue.clear()
                events = sorted(list(self.stage_events().items()), key=sorted_key)
                next_update = time.time() + _config.config['event-update-interval']
                for color, c in events:
                    for coords in c:
                        self.queue.put((coords, color))
                Logger.log(f'Updated events. Next update at {next_update}, which is {_config.config["event-update-interval"]} seconds from now.', severity=Logger.Verbose)

    def execute_events(self, thread_event):
        while thread_event.is_set():
            try:
                time.sleep(random.randint(1, 1 + int(_config.config['worker-count'] / 2)))  # random sleep for less worker conflict
                if self.queue.empty():
                    continue
                coords, color = self.queue.get()
                Logger.log(f'{current_thread().name} - Setting pixel {coords} with color {color}', severity=Logger.Verbose)
                account = self.choose_account()
                if not account:
                    Logger.log(f'{current_thread().name} - No accounts available! Waiting 30 seconds.', severity=Logger.Error)
                    time.sleep(30)
                r = json.loads(account['class'].set_pixel(coords, color))
                if 'errors' in r.keys():
                    if (r['errors'][0]['extensions']['nextAvailablePixelTs'] / 100) - time.time() > 1000:
                        account['state'] = 'BANNED'
                        Logger.log(f'{current_thread().name} - Account {account["username"]} is banned!', severity=Logger.Warn)
                        Logger.log(f'{current_thread().name} - Failed last action due to ban.', severity=Logger.Error)
                    else:
                        account['next_available'] = r['errors'][1]['next available']
                else:
                    account['state'] = 'IDLE'
                    account['next_available'] = r['data']['act']['data'][0]['data']['nextAvailablePixelTimestamp']
            except Exception as e:
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
        self.state = 'running'

    def stop(self):
        self.thread_event.clear()
        Logger.log('Stopping...', severity=Logger.Moderate)
        for thread in self.threads:
            if thread != current_thread():
                thread.join()
            Logger.log(f'Stopped {thread.name}', severity=Logger.Verbose)
        self.state = 'stopped'
