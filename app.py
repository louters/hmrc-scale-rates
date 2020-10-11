import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, get_rates, compute_rates

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    '''Returns home page.'''
    return render_template("index.html")


@app.route("/lookup", methods=["GET", "POST"])
def lookup():
    '''Allows a user to lookup rates for a destination'''
    # Get rates
    rates = get_rates()

    # GET Method
    if request.method == "GET":
        return render_template("lookup.html", rates=rates)

    # POST Method
    else:
        city = request.form.get("city")
        country = request.form.get("country")
        return render_template(
            "lookedup.html",
            city=city,
            country=country,
            rates=rates[country][city],
            ccy=rates[country]["currency"])


@app.route("/compute", methods=["GET", "POST"])
def compute():
    '''Allows a user to compute his/her trip's rate'''
    # Get rates
    rates = get_rates()

    # GET Method
    if request.method == "GET":
        return render_template("compute.html", rates=rates)

    # POST Method
    else:
        country = request.form.get("country")
        city = request.form.get("city")
        dt_in = datetime.strptime(
                    request.form.get("date_in") + " "
                    + request.form.get("time_in"),
                    "%Y-%m-%d %H:%M")

        dt_out = datetime.strptime(
                    request.form.get("date_out") + " "
                    + request.form.get("time_out"),
                    "%Y-%m-%d %H:%M")

        res = compute_rates(rates[country][city], dt_in, dt_out)

        return render_template("computed.html", res=res,
                                location=country + ", " + city,
                                dt=(dt_in, dt_out),
                                ccy=rates[country]["currency"])