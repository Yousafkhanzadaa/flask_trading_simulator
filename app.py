################################################################################
################################################################################
########                                                                ########
########   Python - Firebase - Flask Login/Register App                 ########
########   Author: Hemkesh Agrawal                                      ########
########   Website: http://hemkesh.com                                  ########
########   Last updated on: 11/27/2019                                  ########
########                                                                ########
########   P.S. This is my first ever github project, so I              ########
########   would love to hear your feedback : agrawalh@msu.edu          ########
########                                                                ########
################################################################################
################################################################################

import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for, jsonify
import pandas as pd
import yfinance as yf
import json
import numpy as np
from datetime import datetime
import openai
import plotly
import plotly.graph_objects as go
import charts.balance_chat as bc
import charts.candle_chart as cc
import trading_logics.mean_reversion as mr_strategy

app = Flask(__name__)       #Initialze flask constructor

#Add your own details
config = {
  "apiKey": "AIzaSyCCrooeD3hkU1f-BRDqy2PVIOje65gRn1M",
  "authDomain": "tradingautonow.firebaseapp.com",
  "databaseURL": "PASTE_HERE",
  "storageBucket": "tradingautonow.appspot.com"
}

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

#Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

#Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("welcome.html", email = person["email"], name = person["name"])
    else:
        return redirect(url_for('login'))

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            #Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            #Redirect to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            #Append data to the firebase realtime database
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            #Go to welcome page
            return redirect(url_for('welcome'))
        except:
            #If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))

# Define the root route with a form for input
@app.route('/trade')
def index():
    return render_template('trading.html')  # Assuming you have an index.html file with the form


# Endpoint to handle form submission and simulate trading
@app.route('/simulate_trading', methods=['POST'])
def simulate_trading():
    # Fetch and process data (add your own data processing function)
    data = yf.download(tickers="BTC-USD", period='1y', interval='1d')
    
    # Simulate trading (add your own trading simulation function)
    asset_df, trade_actions, final_balance = mr_strategy.simulate_mean_reversion_trading(data, 10000, 0.025, 0.025, lookback_window=20)
    balance_df = pd.DataFrame(asset_df)
    
    # Create charts using Plotly (adapt your plotting functions)
    balance_chart = bc.plot_balance_chart(balance_df, trade_actions)
    candlestick_chart = cc.plot_candlestick_chart(data, trade_actions)
    
    # Convert charts to JSON for web rendering
    balance_chart_json = json.dumps(balance_chart, cls=plotly.utils.PlotlyJSONEncoder)
    candlestick_chart_json = json.dumps(candlestick_chart, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Render results template with charts and final balance information
    return jsonify({
        'balance_chart': balance_chart_json,
        'candlestick_chart': candlestick_chart_json,
        'final_balance': final_balance
    })

if __name__ == "__main__":
    app.run()
