from requests import Session
import jwt


def payload(coordinates, color):
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


def make(username, password, coordinates, color):
    s = Session()
    text = s.get('https://www.reddit.com/login').text
    csrf = text[text.find('csrf_token') + 19:text.find('csrf_token') + 59]
    r = s.post('https://www.reddit.com/login', data={
        'username': username,
        'password': password,
        'csrf_token': csrf,
        'otp': '',
        'dest': 'https://www.reddit.com'
    }, headers={'content-type': 'application/x-www-form-urlencoded',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'}
    )
    r = s.get(f'https://www.reddit.com/r/place?cx={coordinates[0]}&cy={coordinates[1]}&px=18')
    auth = 'Bearer ' + jwt.decode(s.cookies.get_dict()['token_v2'], options={"verify_signature": False}, algorithms='HS256')['sub']
    r = s.options('https://gql-realtime-2.reddit.com/query', headers={'origin': 'https://hot-potato.reddit.com',
                                                                      'referer': 'https://hot-potato.reddit.com/',
                                                                      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                                                                      'access-control-request-headers': 'authorization,content-type,x-reddit-loid,x-reddit-session',
                                                                      'access-control-request-method': 'POST'})
    r = s.post('https://gql-realtime-2.reddit.com/query', headers={'content-type': 'application/json',
                                                                   'origin': 'https://www.reddit.com',
                                                                   'referer': 'https://www.reddit.com/',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                                                                   'authorization': auth,
                                                                   'x-reddit-loid': s.cookies.get_dict()['loid'],
                                                                   'x-reddit-session': s.cookies.get_dict()['session_tracker']}, data={'id': None,
                                                                                                                                       'operationName': "GetPersonalizedTimer",
                                                                                                                                       'query': "mutation GetPersonalizedTimer{\n  act(\n    input: {actionName: \"r/replace:get_user_cooldown\"}\n  ) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n          }\n        }\n      }\n    }\n  }\n}\n\n\nsubscription SUBSCRIBE_TO_CONFIG_UPDATE {\n  subscribe(input: {channel: {teamOwner: AFD2022, category: CONFIG}}) {\n    id\n    ... on BasicMessage {\n      data {\n        ... on ConfigurationMessageData {\n          __typename\n          colorPalette {\n            colors {\n              hex\n              index\n            }\n          }\n          canvasConfigurations {\n            dx\n            dy\n            index\n          }\n          canvasWidth\n          canvasHeight\n        }\n      }\n    }\n  }\n}\n\n\nsubscription SUBSCRIBE_TO_CANVAS_UPDATE {\n  subscribe(\n    input: {channel: {teamOwner: AFD2022, category: CANVAS, tag: \"0\"}}\n  ) {\n    id\n    ... on BasicMessage {\n      id\n      data {\n        __typename\n        ... on DiffFrameMessageData {\n          currentTimestamp\n          previousTimestamp\n          name\n        }\n        ... on FullFrameMessageData {\n          __typename\n          name\n          timestamp\n        }\n      }\n    }\n  }\n}\n\n\n\n\nmutation SET_PIXEL {\n  act(\n    input: {actionName: \"r/replace:set_pixel\", PixelMessageData: {coordinate: { x: 53, y: 35}, colorIndex: 3, canvasIndex: 0}}\n  ) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on SetPixelResponseMessageData {\n            timestamp\n          }\n        }\n      }\n    }\n  }\n}\n\n\n\n\n# subscription configuration($input: SubscribeInput!) {\n#     subscribe(input: $input) {\n#       id\n#       ... on BasicMessage {\n#         data {\n#           __typename\n#           ... on RReplaceConfigurationMessageData {\n#             colorPalette {\n#               colors {\n#                 hex\n#                 index\n#               }\n#             }\n#             canvasConfigurations {\n#               index\n#               dx\n#               dy\n#             }\n#             canvasWidth\n#             canvasHeight\n#           }\n#         }\n#       }\n#     }\n#   }\n\n# subscription replace($input: SubscribeInput!) {\n#   subscribe(input: $input) {\n#     id\n#     ... on BasicMessage {\n#       data {\n#         __typename\n#         ... on RReplaceFullFrameMessageData {\n#           name\n#           timestamp\n#         }\n#         ... on RReplaceDiffFrameMessageData {\n#           name\n#           currentTimestamp\n#           previousTimestamp\n#         }\n#       }\n#     }\n#   }\n# }\n",
                                                                                                                                       'variables': {'input': {'channel': {'teamOwner': "GROWTH", 'category': "R_REPLACE", 'tag': "canvas:0:frames"}}}})
    r = s.post('https://gql-realtime-2.reddit.com/query', headers={'content-type': 'application/json',
                                                                   'origin': 'https://hot-potato.reddit.com',
                                                                   'referer': 'https://hot-potato.reddit.com/',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
                                                                   'apollographql-client-name': 'mona-lisa',
                                                                   'apollographql-client-version': '0.0.1',
                                                                   'authorization': auth}, data=payload(coordinates, color))
    return r.text


if __name__ == '__main__':
    print(make('OEawoobNgXFQGfpwTDlS', '#z|6D~LICM}7tZYo', (326, 356), 3))  # this is the burner account i am using for testing. feel free to use it.
