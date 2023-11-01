import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
app.debug = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    if user_id is None:
        return redirect("/login")

    # query users table for cash
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    print(user)
    if len(user) == 0:
        return redirect("/login")

    # query trades table for all symbols and shares for user
    trades = db.execute(
        "SELECT *,SUM(shares) sum_shares FROM trades WHERE user_id = ? "
        "group by symbol HAVING SUM(shares) > 0",
        user_id,
    )

    # calculate total value of each stock
    stock_value = 0
    for stock in trades:
        stock["current_price"] = usd(lookup(stock["symbol"])["price"])
        stock["total"] = stock["sum_shares"] * usd(stock["current_price"])
        stock_value += stock["total"]

    return render_template(
        "index.html", trades=trades, user=user, stock_value=stock_value
    )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)
        shares = request.form.get("shares")
        if not shares:
            return apology("must provide number of shares", 400)
        if not shares.isdigit():
            return apology("must provide positive number of shares", 400)
        if shares < 1:
            return apology("must provide positive number of shares", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 400)

        cost = stock["price"] * shares
        user_id = session["user_id"]
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        current_cash = user[0]["cash"]
        if current_cash < cost:
            return apology("can't afford", 400)
        db.execute(
            "INSERT INTO trades (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id,
            symbol,
            shares,
            stock["price"],
        )
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?", current_cash - cost, user_id
        )
        flash("Bought!")
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]
    trades = db.execute(
        "SELECT * FROM trades WHERE user_id = ? ORDER BY created_at DESC", user_id
    )
    return render_template("history.html", trades=trades)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide symbol", 400)
        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 400)
        return render_template("quoted.html", symbol=stock)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("must provide username", 400)
        if not password:
            return apology("must provide password", 400)
        if not confirmation:
            return apology("must provide confirmation", 400)
        if password != confirmation:
            return apology("passwords don't match", 400)

        # check if username already exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return apology("username already exists", 400)
        hashed = generate_password_hash(password)
        result = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed
        )
        if not result:
            return apology("registration failed", 400)
        flash("Registered!")
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        if not symbol:
            return apology("must provide symbol", 400)
        if shares < 1:
            return apology("must provide positive number of shares", 400)

        stock = lookup(symbol)
        if not stock:
            return apology("invalid symbol", 400)

        trades = db.execute(
            "SELECT *,SUM(shares) sum_shares FROM trades WHERE user_id = ? AND symbol = ? "
            "group by symbol HAVING SUM(shares) > 0",
            user_id,
            symbol,
        )
        if len(trades) != 1:
            return apology("invalid symbol", 400)
        if shares > trades[0]["sum_shares"]:
            return apology("too many shares", 400)

        cost = stock["price"] * shares
        user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
        current_cash = user[0]["cash"]
        db.execute(
            "INSERT INTO trades (user_id, symbol, shares, price) VALUES (?, ?, ?, ?)",
            user_id,
            symbol,
            -shares,
            stock["price"],
        )
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?", current_cash + cost, user_id
        )
        flash("Sold!")
        return redirect("/")
    else:
        trades = db.execute(
            "SELECT *,SUM(shares) sum_shares FROM trades WHERE user_id = ? "
            "group by symbol HAVING SUM(shares) > 0",
            user_id,
        )
        return render_template("sell.html", trades=trades)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run()
