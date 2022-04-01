# r-placer
a stupid bot for r/place

## what
in development attempt at making fully automated bot for r/place. currently working on pixel drawing. i am having trouble with getting GQL token as the one stored in cookies is somehow different than the one you need to send. the entire API was overhauled as they now use graphql, which is more difficult.

included is a reddit account creator that uses disposable emails. it can automatically add them to a google sheet (which is what i am doing). you will need to set up a google service account for google sheets and install/setup `gspread`. you will also need `selenium` and `chromedriver` if you want to make accounts.

right now, code is really messy. hopefully this time it lasts longer so this can at least be used a little bit.

to use it/test right now, run `make_request.py`. most of the future work will be done in there.
## contributing
please

## requirements
for bot:
`pip install requests`

for account creation:
`pip install selenium gspread webdriver-manager`

or use requirements.txt file
`pip install -r requirements.txt`
