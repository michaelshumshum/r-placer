# r-placer
bot for ~2022~ 2023 r/place

unarchived if anybody wants to help work on this. i am not sure if it works. my main developer account was banned, so you must provide your own API key.

## ~place has ended.~ thanks to everyone who participated and to those who used my bot!
![place.png](/place.jpg)

## what
(maybe) working r/place bot that takes an input image, location, and account login to draw to the r/place canvas. relatively neat compared to [this one](https://github.com/rdeepak2002/reddit-place-script-2022) as coding style is more OOP. though, could still need some touching up.

supports multiple accounts.
automatically determines which canvas to add to. just use coordinates.
## contributing
please

## requirements
`pip install -r requirements.txt`

## setup
create a new file called `accounts.csv` which contains the data for the accounts you want to use. each row should formatted like `email username password`, where spaces are delimiters. email is optional, so you can put filler information there if needed.

adjust configuration in `config.json`. i have included the information for my apps and the developer account for it. feel free to use it as well or change it to your own apps. the apps are necessary for the accounts to receive their access token. more apps = more accounts. you must also adjust the `main-dev-account` to the information of the account you used to create the app.

### tor
included is a `torrc` file that is required. you must also have the `tor` binary installed on your machine. on linux and mac, you can use homebrew: `brew install tor`. once installed, go to `/usr/local/etc/tor/` and put the `torrc` file in there. making a sym-link is also valid. finally, run `brew services start tor`. windows installation is more complicated and i don't have a windows machine to try it out.


## usage
run `python main.py <image path> <x-coord> <y-coord>`, where the image path is the image you want to draw, and x-coord/y-coord represent the location you want the image to be drawn.
### account maker
simple selenium script that automatically creates a reddit account. 90% can solve the captcha, though some human intervention might be needed occasionally. sends account data to a specified google sheet using gspread. makes one account at a time as reddit limits you to 1 account per ip every 10 minutes. to make more, use a vpn for every iteration. my focus wasn't on the account maker that much, so it isn't as refined. if you want to adjust anything, look into the `sheets.py` and `account_maker.py` files. for anybody else, refer to [the gspread page](https://docs.gspread.org/en/latest/) to see how to setup gspread. there is a paramter in the config that identifies the email for the accounts.

## notes
make sure to verify all the emails for all your accounts and interact with it a little. for me, i join a random subreddit, which has really made the accounts immune so far. that seems to be primary factor in getting accounts banned. though, still not guaranteed it doesn't get banned.  
