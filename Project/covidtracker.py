import requests
import urllib.parse
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

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

db = SQL("sqlite:///covidtracker.db")

#coviduk main api start line
main_api = 'https://api.coronavirus.data.gov.uk/v2/data?'
rest_of_url = [
    "&areaType=region&metric=cumCasesByPublishDate&metric=cumDeathsByPublishDate&metric=newDeathsByPublishDate&metric=newCasesByPublishDate&format=json",
    "&areaType=nation&metric=cumCasesByPublishDate&metric=cumDeathsByPublishDate&metric=newDeaths28DaysByPublishDate&metric=newCasesByPublishDate&format=json"
        ]




@app.route("/", methods=["GET", "POST"])
@login_required
def getregion():
#Ensure request method is post
    if request.method == "POST":

#store area name
        val = str(request.form.get("region"))

        areaCode = val
#Ensure user enters valid area name
        if not areaCode:
            return apology("Please enter area code")


#save end of url to a var to be added on end of full url
        url_region = rest_of_url[0]

#concatinate variables to form full url
        url = main_api + urllib.parse.urlencode({'areaCode': areaCode}) + url_region
#store the result of requesting data from the api in json format in a var
        json_data = requests.get(url).json()
#store the values in vars
        date = json_data['body'][0]['date']
        cumCasesByPublishDate = json_data['body'][0]['cumCasesByPublishDate']
        cumDeathsByPublishDate = json_data['body'][0]['cumDeathsByPublishDate']
        newCasesByPublishDate = json_data['body'][0]['newCasesByPublishDate']
        newDeathsByPublishDate = json_data['body'][0]['newDeathsByPublishDate']
        return render_template("searched.html", date=date, totalCases=cumCasesByPublishDate, totalDeaths=cumDeathsByPublishDate, newCases=newCasesByPublishDate, newDeaths=newDeathsByPublishDate)


    else:
        return render_template("search.html")

@app.route("/uk", methods=["GET", "POST"])
@login_required
def getnation():
#Ensure request method is post
    if request.method == "POST":

#store area name
        val = str(request.form.get("nation"))

        areaCode = val
#Ensure user enters valid area name
        if not areaCode:
            return apology("Please enter area code")

#coviduk main api start line

#save end of url to a var to be added on end of full url
        url_nation = rest_of_url[1]

#concatinate variables to form full url
        url = main_api + urllib.parse.urlencode({'areaCode': areaCode}) + url_nation
#store the result of requesting data from the api in json format in a var
        json_data = requests.get(url).json()
#store the values in vars
        date = json_data['body'][0]['date']
        cumCasesByPublishDate = json_data['body'][0]['cumCasesByPublishDate']
        cumDeathsByPublishDate = json_data['body'][0]['cumDeathsByPublishDate']
        newCasesByPublishDate = json_data['body'][0]['newCasesByPublishDate']
        newDeaths28DaysByPublishDate = json_data['body'][0]['newDeaths28DaysByPublishDate']
        return render_template("searched-nation.html", date=date, totalCases=cumCasesByPublishDate, totalDeaths=cumDeathsByPublishDate, newCases=newCasesByPublishDate, newDeaths=newDeaths28DaysByPublishDate)


    else:
        return render_template("searchnation.html")




@app.route("/news",methods=["GET", "POST"])
@login_required
def getnews():
        url = ('http://newsapi.org/v2/top-headlines?q=covid&country=gb&category=health&apiKey=11878960dfcf4f289cc492eb31c87900')
        response = requests.get(url)
        data = response.json()
#store params
        articles = data['articles']

#initialise empty lists
        news = []
        desc = []
        img = []
#iterate through each article in the articles var
        for i in range(len(articles)):
            myArticles = articles[i]

#append values to lists
            news.append(myArticles['title'])
            desc.append(myArticles['description'])
            img.append(myArticles['urlToImage'])

        myList = zip(news, desc, img)
        return render_template("news.html", context=myList)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Ensure that user is reached via post
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)


        # check that the input in confirmation matches the password field
        elif not password == confirmation:
            return apology("passwords must match")


        # request password from from and create hash
        hash = generate_password_hash(password)
        #insert a new user to the database

        rows = db.execute("SELECT username FROM users WHERE username = :username", username = request.form.get("username"))


       #Ensure that this is a unique username
        if len(rows) > 0:
            return apology("username already exists", 403)

       #insert new user into database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username = request.form.get("username"), hash = hash)

        return redirect("/")

    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Please enter username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Please enter password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/uk")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/register")