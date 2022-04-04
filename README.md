# r-placer
bot for 2022 r/place

## what
working r/place bot that takes an input image, location, and account login to draw to the r/place canvas. relatively neat compared to [this one](https://github.com/rdeepak2002/reddit-place-script-2022) as coding style is more OOP. though, could still need some touching up.

supports multiple accounts.
automatically determines which canvas to add to. just use coordinates.
## contributing
please

## requirements
`pip install -r requirements.txt`

## setup
create a new file called `accounts.csv` which contains the data for the accounts you want to use. each row should formatted like `email username password`, where spaces are delimiters. email is optional, so you can put filler information there if needed.

adjust configuration in `config.json`. i have included the information for my app and the developer account for it. feel free to use it as well or change it to your own app. the app is necessary for the accounts to receive their access token. you must also adjust the `main-dev-account` to the information of the account you used to create the app.

run `python main.py <image path> <x-coord> <y-coord>`, where the image path is the image you want to draw, and x-coord/y-coord represent the location you want the image to be drawn.

### tor
included is a `torrc` file that is required. you must also have the `tor` binary installed on your machine. on linux and mac, you can use homebrew: `brew install tor`. once installed, go to `/usr/local/etc/tor/` and put the `torrc` file in there. making a sym-link is also valid. finally, run `brew services start tor`. windows installation is more complicated and i don't have a windows machine to try it out.

## notes
make sure to verify all the emails for all your accounts. that seems to be primary factor in getting accounts banned. though, still not guaranteed it doesn't get banned. some people have success. all my accounts get banned.

account maker is quite dysfunctional.
