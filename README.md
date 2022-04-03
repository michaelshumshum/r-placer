# r-placer
bot for 2022 r/place

## what
almost working r/place bot that takes an input image, location, and account logins to draw to the r/place canvas. relatively neat compared to [this one](https://github.com/Zequez/reddit-placebot) as coding style is more OOP. though, could still need some touching up.

supports multiple accounts.
## contributing
please

## requirements
`pip install -r requirements.txt`

## setup
create a new file called `accounts.csv` which contains the data for the accounts you want to use. each row should formatted like `email, username, password`. email is optional, so you can put filler information there if needed.

adjust configuration in `config.json`. i have included the information for my app and the developer account for it. feel free to use it as well or change it to your own app. the app is necessary for the accounts to receive their access token. you must also adjust the `main-dev-account` to the information of the account you used to create the app.

run `python main.py <image path> <x-coord> <y-coord>`, where the image path is the image you want to draw, and x-coord/y-coord represent the location you want the image to be drawn.
