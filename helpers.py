import os
import requests
import urllib.parse, urllib.request, urllib.error
from bs4 import BeautifulSoup
import re
import json
import datetime
from datetime import datetime

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def get_rates() -> dict:
    """
    Return rates from online or server, depending on age of last update.
    """
    path = "/dyn/rates"

    # Non existing -> fetch online
    if not os.path.isfile(path):
        return update_rates()

    # Needs to be updated -> fetch online
    last_mod_time = datetime.datetime.utcfromtimestamp(
                    os.path.getmtime(path))
    if (datetime.datetime.now() - last_mod_time).days > 0:
        return update_rates()

    # Get file from server
    return load_rates()


def load_rates() -> dict:
    """
    Load HMRC rates from server.
    """
    with open("/dyn/rates", "r") as f:
        rates = json.load(f)
    return rates


def update_rates() -> dict:
    """
    Return latest HMRC international scale rates dictionary and save it on the server.
    """

    # Get html page
    url = "https://www.gov.uk/guidance/expenses-rates-for-employees-travelling-outside-the-uk"
    response = urllib.request.urlopen(url)
    page_content = response.read()

    # Soupify html page
    soup = BeautifulSoup(page_content, features="html.parser")
    page_content = page_content.decode("utf-8")

    # Get scale rates for each city
    ROWS = {
        "Over 5 hours",
        "Over 10 hours",
        "24 hour rate",
        "Room rate",
        "Breakfast",
        "Lunch",
        "Dinner",
        "Other",
        "Drinks",
        "Hotel to office",
        "Total residual"}

    cities = {}
    tmp_cities = soup.find_all("h4")
    tmp_cities.append("Canberra, Australia")
    for city in tmp_cities:
        try:
            city = city.string
        except AttributeError:
            pass
        cities[city] = {}
        for row in ROWS:
            pattern = rf"{re.escape(city)}[.\s\S]+?(?<={row}</td>)[\s\S.]+?<td>([\d\.]*)"
            match = re.search(pattern, page_content)
            if match:
                cities[city][row] = float(match[1])
            else:
                print(f"No match for {city}: {row}")

    # Create rates dict structure
    rates = {}
    # Insert countries & currencies
    for country in soup.find_all("h3"):
        try:
            # Find currency of each country
            pattern = rf"{re.escape(country.string)}</h3>[\s]*<p>All rate(?:s)?(?: are)?(?: in)?([\w\s]*)(?:\(unless)?"
            ccy = re.search(pattern, page_content)

            # Discard letters & special case Canberra, Australia
            if ccy is None:
                continue
            # Special case-ccy: Laos
            elif country.string == "Laos":
                ccy = "Laotian kip"
            # Special case-ccy: Latvia
            elif country.string == "Latvia":
                ccy = "euros"
            else:
                ccy = ccy[1].strip()

            # Special case-ctry: Honduras
            if "Honduras" in country.string:
                rates["Honduras"] = {"currency":ccy}
            # Add country, its ccy to rates
            else:
                rates[country.string] = {"currency":ccy}

        except KeyError as e:
            print(e)
            print(country)

        except Exception as e:
            print(e)

    # Insert cities to countries in rates
    for country in rates:

        # Handle country and city names inconsistencies
        country_tmp = country
        if "(" in country:
            country_tmp = country[:country.find("(")-1]

        elif "Republic" in country and "," in country:
            country_tmp = country[country.find(",")+2:]
            country_tmp += " of "
            country_tmp += country[:country.find(",")]

        elif "Islands" in country:
            country_tmp = country.replace("Islands", "Island")

        elif country == "Occupied Territories":
            rates[country]["Jerusalem"] = cities["Jerusalem"]

        # Join city with country key
        for city in cities:
            if country_tmp in city:
                city_name = re.search(rf"([\w ]*)", city)[1]
                if city_name:
                    rates[country][city_name] = cities[city]
                else:
                    print(f"No match for {city}")

    # Special case (2 Koreas)
    del rates["Korea, Republic"]["Pyongyang"]

    # Save rates to server
    with open("dyn/rates", "w") as f:
        json.dump(rates, f)

    # Return rates
    return rates


def compute_rates(rates: dict, dt_in: datetime, dt_out: datetime) -> tuple:
    '''Return a trip's scale rate.'''

    delta = dt_out - dt_in
    exp = ""
    res = delta.days * (rates["24 hour rate"] + rates["Room rate"])
    exp += f"{delta.days} x 24 hour rate (incl. room rate)"

    if delta.seconds / 3600 > 10:
        res += rates["Over 10 hours"]
        exp += " + over 10 hours"

    elif delta.seconds / 3600 > 5:
        res += rates["Over 5 hours"]
        exp += " + Over 5 hours"

    if (delta.days == 0 and dt_out.date() != dt_in.date()) \
        or dt_out.date() - dt_in.date() > delta:
        res += rates["Room rate"]
        exp += " + Room rate"

    exp += "."

    return res, exp