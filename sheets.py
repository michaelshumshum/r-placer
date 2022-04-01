import gspread

gc = gspread.service_account()
sheet = gc.open('reddit accounts').get_worksheet(0)


def add(data: list):
    sheet.append_row(data)
    print(data)
