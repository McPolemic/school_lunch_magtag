from adafruit_magtag.magtag import MagTag
from adafruit_progressbar.progressbar import ProgressBar
from adafruit_datetime import datetime, date, timedelta
import adafruit_requests
import wifi
import socketpool
import ssl
import alarm
import time

# Set up where we'll be fetching data from
DATA_SOURCE = (
    "https://api.mealviewer.com/api/v4/school/Klondikeelementary/{0}/{0}"
)
DATE_SOURCE = "https://worldtimeapi.org/api/timezone/America/New_York"

magtag = MagTag()
magtag.network.connect()

magtag.add_text(
    text_font="/fonts/ncenR14.pcf",
    text_position=((magtag.graphics.display.width // 2) - 1, 8),
    text_anchor_point=(0.5, 0.5),
    is_data=False,
)  # Title

magtag.add_text(
    text_font="/fonts/ncenR14.pcf",
    text_position=((magtag.graphics.display.width // 2) - 1, 23),
    text_anchor_point=(0.5, 0.5),
    is_data=False,
)  # Day

magtag.add_text(
    text_font="/fonts/ncenR14.pcf",
    text_position=(10, 40),
    text_anchor_point=(0, 0.5),
    is_data=False,
)  # item 1

magtag.add_text(
    text_font="/fonts/ncenR14.pcf",
    text_position=(10, 55),
    text_anchor_point=(0, 0.5),
    is_data=False,
)  # itemLabelNumber 2

magtag.add_text(
    text_font="/fonts/ncenR14.pcf",
    text_position=(10, 70),
    text_anchor_point=(0, 0.5),
    is_data=False,
)  # itemLabelNumber 3

magtag.add_text(
    text_font="/fonts/ncenR14.pcf",
    text_position=(10, 85),
    text_anchor_point=(0, 0.5),
    is_data=False,
)  # itemLabelNumber 4

magtag.add_text(
    text_font="/fonts/ncenR14.pcf",
    text_position=(10, 100),
    text_anchor_point=(0, 0.5),
    is_data=False,
)  # itemLabelNumber 5

voltage_text = magtag.add_text(
    text_font="/fonts/ncenR14.pcf",
    text_position=(50, 130),
    text_anchor_point=(0, 0.5),
    is_data=False,
)

# magtag.graphics.set_background("/bmps/background.bmp")

def write_menu(todayMenu, date_string):
    itemLabelNumber = 2
    itemLabelMax = 5
    lunchMenuBlock = 1

    menuDate = "{0} ({1})".format(todayMenu["dateInformation"]["weekDayName"], date_string)

    menuBlocks = todayMenu["menuBlocks"]
    if not menuBlocks:
        magtag.set_text(menuDate + " " + "Closed!", 1, False)
        return
    lunchMenu = menuBlocks[lunchMenuBlock]
    blockName = lunchMenu["blockName"]
    magtag.set_text(menuDate + " " + blockName, 1, False)

    foodItems = lunchMenu["cafeteriaLineList"]["data"][0]["foodItemList"]["data"]
    entrees = []
    sides = []
    veggies = []

    for foodItem in foodItems:
        itemType = foodItem["item_Type"]

        if itemType == "ENTREES":
            entrees.append(foodItem["item_Name"])

        if itemType == "SIDES":
            sides.append(foodItem["item_Name"])

        if itemType == "VEGETABLES":
            sides.append(foodItem["item_Name"])

    for entree in entrees:
        if itemLabelNumber > itemLabelMax:
            continue
        magtag.set_text(entree, itemLabelNumber, False)
        itemLabelNumber += 1
    for side in sides:
        if itemLabelNumber > itemLabelMax:
            continue
        magtag.set_text(side, itemLabelNumber, False)
        itemLabelNumber += 1
    for veggie in veggies:
        if itemLabelNumber > itemLabelMax:
            continue
        magtag.set_text(veggie, itemLabelNumber, False)
        itemLabelNumber += 1


try:
    # data = magtag.fetch()
    # date = data['menuSchedules'][0]['dateInformation']['weekDayName']
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    response = requests.get(DATE_SOURCE)
    dateObject = response.json()
    dayToUse = datetime.fromtimestamp(dateObject["unixtime"])
    if dayToUse.hour > 12:
        dayToUse = dayToUse + timedelta(days=1)

    date_as_string = dayToUse.date().isoformat()
    # print("Getting Data from: ", DATA_SOURCE)
    response = requests.get(DATA_SOURCE.format(date_as_string))
    # print("Data Retrieved. Parsing from json  ... ")
    data = response.json()
    # print(data)
    # print("Done Parsing.")
    schoolName = data["physicalLocation"]["name"]
    # print("Response is ", schoolName)
    magtag.set_text(schoolName, 0, False)

    todayMenu = data["menuSchedules"][0]
    write_menu(todayMenu, date_as_string)

    voltage = magtag.peripherals.battery
    magtag.set_text(f'Battery: {voltage:2f} V', 6, False)

    magtag.refresh()

    seconds_to_sleep = 60 * 60 * 2 # Sleep for two hours
    # print(f"Sleeping for {seconds_to_sleep} seconds")
    al = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + seconds_to_sleep)
    alarm.exit_and_deep_sleep_until_alarms(al)

except (ValueError, RuntimeError) as e:
    print("Some error occured, retrying! -", e)

