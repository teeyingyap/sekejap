import os, csv, random, redis

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
secret_key_value = os.environ.get('SECRET_KEY', None)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# production
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.from_url(os.environ.get("REDIS_URL"))
app.config['SECRET_KEY'] = secret_key_value

# local
# Configure session to use filesystem (instead of signed cookies)
# app.config["SESSION_FILE_DIR"] = mkdtemp()
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"

Session(app)

db = SQL("sqlite:///sekejap.db")

# to run on local:
# set FLASK_APP=application.py
# then flask run


# file system session does not work on heroku
# - therefore use redis for production


def load_kata_csv():
    # only load csv once
    # and also i have to update done to zero
    db.execute("UPDATE words SET done = :done", done=0)

    rows = db.execute("SELECT * FROM words WHERE id = :id", id=61)
    if len(rows) != 1:
        input_file = csv.DictReader(open('kata_list.csv'))
            # with open('kata_list.csv', newline='') as csvfile:
                # got 61 words
                # print(len(csvfile.readlines()) - 1)
                # reader = csv.DictReader(csvfile)
        for row in input_file:
            db.execute("INSERT INTO words (katakana, english) VALUES(:katakana, :english)", katakana=row['katakana'], english=row['english'])



def load_hira_csv():
    # only load csv once
    # and also i have to update done to zero
    db.execute("UPDATE hiravocab SET done = :done", done=0)

    rows = db.execute("SELECT * FROM hiravocab WHERE id = :id", id=23)
    if len(rows) != 1:
        input_file = csv.DictReader(open('hira_list.csv'))
        for row in input_file:
            db.execute("INSERT INTO hiravocab (hiragana, english, kanji) VALUES(:hiragana, :english, :kanji)", hiragana=row['hiragana'], english=row['english'], kanji=row['kanji'])


def calculate_streak():
    # case [1,0,0,1,1,0,1,1,1,0,1]
    # case [0,0,1,1,0,1,1,1,0,1]
    # [0,1,0,1,1,0,1,1,1,0,1]
    # [0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0]
    # convert into string list
    string_list = [str(int) for int in session["streak"]]
    print(string_list)
    streak_string = "". join(string_list)
    return max(map(len, streak_string.split('0')))



def load_kata():
    db.execute("UPDATE kata SET done = :done", done=0)
    kata_list = ['ア','イ','ウ','エ','オ','カ','キ','ク','ケ','コ','ガ','ギ','グ','ゲ','ゴ','サ','シ','ス','セ','ソ',
                    'ザ','ジ','ズ','ゼ','ゾ','タ','チ','ツ','テ','ト','ダ','ヂ','ヅ','デ','ド','ナ','ニ','ヌ','ネ','ノ',
                    'ハ','ヒ','フ','ヘ','ホ','バ','ビ','ブ','ベ','ボ','パ','ピ','プ','ペ','ポ','マ','ミ','ム','メ','モ',
                    'ヤ','ワ','ユ','ン','ヨ','ラ','リ','ル','レ', 'ロ']
    romaji_list = ['a','i','u','e','o','ka','ki','ku','ke','ko','ga','gi','gu','ge','go','sa','shi','su','se','so',
                    'za','ji','zu','ze','zo','ta','chi','tsu','te','to','da','ji','zu','de','do','na','ni','nu','ne','no',
                    'ha','hi','hu','he','ho','ba','bi','bu','be','bo','pa','pi','pu','pe','po','ma','mi','mu','me','mo',
                    'ya','wa','yu','n','yo','ra','ri','ru','re','ro']
    rows = db.execute("SELECT * FROM kata WHERE id = :id", id=10)
    if len(rows) != 1:
        for i in range(len(kata_list)):
            db.execute("INSERT INTO kata (char, romaji) VALUES(:char, :romaji)", char=kata_list[i], romaji=romaji_list[i])




def load_hira():
    db.execute("UPDATE hira SET done = :done", done=0)
    hira_list = ['あ','い','う','え','お','か','き','く','け','こ','が','ぎ','ぐ','げ','ご','さ','し','す','せ','そ',
                'ざ','じ','ず','ぜ','ぞ','た','ち','つ','て','と','だ','ぢ','づ','で','ど','な','に','ぬ','ね','の',
                'は','ひ','ふ','へ','ほ','ば','び','ぶ','べ','ぼ','ぱ','ぴ','ぷ','ぺ','ぽ','ま','み','む','め',
                'も','や','わ','ゆ','ん','よ','ら','り','る','れ','ろ','を']
    romaji_list = ['a','i','u','e','o','ka','ki','ku','ke','ko','ga','gi','gu','ge','go','sa','shi','su','se','so',
                    'za','ji','zu','ze','zo','ta','chi','tsu','te','to','da','ji','zu','de','do','na','ni','nu','ne','no',
                    'ha','hi','hu','he','ho','ba','bi','bu','be','bo','pa','pi','pu','pe','po','ma','mi','mu','me','mo',
                    'ya','wa','yu','n','yo','ra','ri','ru','re','ro','wo']
    
    rows = db.execute("SELECT * FROM hira WHERE id = :id", id=10)
    if len(rows) != 1:
        for i in range(len(hira_list)):
            db.execute("INSERT INTO hira (char, romaji) VALUES(:char, :romaji)", char=hira_list[i], romaji=romaji_list[i])


@app.route("/")
@login_required
def index():
    rows = db.execute("SELECT * FROM users WHERE id = :id",
                          id=session["user_id"])

    load_kata_csv()
    load_hira_csv()
    return render_template("index.html", rows=rows)


@app.route("/vocab", methods=["GET", "POST"])
@login_required
def vocab():
    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE id = :id",
                          id=session["user_id"])
        prev_streak = rows[0]["streak"]
        submitted_answer = request.form.get("answer")
        answer_key = request.form.get("anskey")
        full_answer = request.form.get("fullans")
        romaji = request.form.get("romaji")

        print("ans key:", answer_key)
        print("submit:", submitted_answer)
        if submitted_answer == answer_key:
            print("current streak:")
            flash('You got it! The katakana was ' + full_answer +' (' + romaji + ')', 'info')
            db.execute("UPDATE users SET score = :score WHERE id = :id", score=rows[0]["score"]+1, id=session["user_id"])
            session["streak"].append(1)
            print("correct, and streak list", session["streak"])
            current_streak = calculate_streak()
            print("current_streak is", current_streak)
            if current_streak > prev_streak:
                db.execute("UPDATE users SET streak = :streak WHERE id = :id", streak=current_streak, id=session["user_id"])
        else:
            # update streak only when i answer wrong
            flash('Good try! The katakana was ' + full_answer +' (' + romaji + ')', 'warning')
            session["streak"].append(0)
            print("wrong, and streak list", session["streak"])
            current_streak = calculate_streak()
            print("current_streak is", current_streak)
            if current_streak > prev_streak:
                db.execute("UPDATE users SET streak = :streak WHERE id = :id", streak=current_streak, id=session["user_id"])

        return redirect("/vocab")
    else:
        # after post, i render the same page again, with another random number, check whether done is 0 or not
        # if its zero, then we can show the question
        question_id = random.randint(1,84)
        question_rows = db.execute("SELECT * FROM words WHERE id = :id", id=question_id)

        while question_rows[0]['done'] == 1:
            question_id = random.randint(1,84)
            question_rows = db.execute("SELECT * FROM words WHERE id = :id", id=question_id)


        # change done to 1 after selecting
        db.execute("UPDATE words SET done = :done WHERE id = :id", done=1, id=question_id)

        #make answer rows
        answer_list = ['ア','イ','ウ','エ','オ','カ','キ','ク','ケ','コ','ガ','ギ','グ','ゲ','ゴ','サ','シ','ス','セ','ソ',
                        'ザ','ジ','ズ','ゼ','ゾ','タ','チ','ツ','テ','ト','ダ','ヂ','ヅ','デ','ド','ナ','ニ','ヌ','ネ','ノ',
                        'ハ','ヒ','フ','ヘ','ホ','バ','ビ','ブ','ベ','ボ','パ','ピ','プ','ペ','ポ','マ','ミ','ム','メ','モ',
                        'ヤ','ワ','ユ','ン','ヨ','ラ','リ','ル','レ','ロ','ョ','ッ','ー','ャ','ュ']

        print(question_rows[0]['katakana'])
        print(len(question_rows[0]['katakana']))

        answer_index = random.randint(0, len(question_rows[0]['katakana'])-1)
        print(answer_index)
        answer_key = question_rows[0]['katakana'][answer_index]
        print("the answer key is", answer_key)
        # sample must not include answer key
        keys = []
        keys.append(answer_key)
        while len(keys) < 8:
            key = random.choice(answer_list)
            if key != answer_key:
                keys.append(key)

        random.shuffle(keys)

        print(keys)
        return render_template("vocab.html", question_rows=question_rows, keys=keys, answer_key=answer_key)


@app.route("/hiragana_vocab", methods=["GET", "POST"])
@login_required
def hiragana_vocab():
    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE id = :id",
                          id=session["user_id"])
        prev_streak = rows[0]["streak"]
        submitted_answer = request.form.get("answer")
        answer_key = request.form.get("anskey")
        full_answer = request.form.get("fullans")
        romaji = request.form.get("romaji")

        print("ans key:", answer_key)
        print("submit:", submitted_answer)
        if submitted_answer == answer_key:
            print("current streak:")
            flash('You got it! The hiragana was ' + full_answer +' (' + romaji + ')', 'info')
            db.execute("UPDATE users SET score = :score WHERE id = :id", score=rows[0]["score"]+1, id=session["user_id"])
            session["streak"].append(1)
            print("correct, and streak list", session["streak"])
            current_streak = calculate_streak()
            print("current_streak is", current_streak)
            if current_streak > prev_streak:
                db.execute("UPDATE users SET streak = :streak WHERE id = :id", streak=current_streak, id=session["user_id"])
        else:
            # update streak only when i answer wrong
            flash('Good try! The hiragana was ' + full_answer +' (' + romaji + ')', 'warning')
            session["streak"].append(0)
            print("wrong, and streak list", session["streak"])
            current_streak = calculate_streak()
            print("current_streak is", current_streak)
            if current_streak > prev_streak:
                db.execute("UPDATE users SET streak = :streak WHERE id = :id", streak=current_streak, id=session["user_id"])

        return redirect("/hiragana_vocab")
    else:
        # after post, i render the same page again, with another random number, check whether done is 0 or not
        # if its zero, then we can show the question
        question_id = random.randint(1,23)
        question_rows = db.execute("SELECT * FROM hiravocab WHERE id = :id", id=question_id)

        while question_rows[0]['done'] == 1:
            question_id = random.randint(1,23)
            question_rows = db.execute("SELECT * FROM hiravocab WHERE id = :id", id=question_id)


        # change done to 1 after selecting
        db.execute("UPDATE hiravocab SET done = :done WHERE id = :id", done=1, id=question_id)

        #make answer rows
        answer_list = ['あ','い','う','え','お','か','き','く','け','こ','が','ぎ','ぐ','げ','ご','さ','し','す','せ','そ',
                'ざ','じ','ず','ぜ','ぞ','た','ち','つ','て','と','だ','ぢ','づ','で','ど','な','に','ぬ','ね','の',
                'は','ひ','ふ','へ','ほ','ば','び','ぶ','べ','ぼ','ぱ','ぴ','ぷ','ぺ','ぽ','ま','み','む','め',
                'も','や','わ','ゆ','ん','よ','ら','り','る','れ','ろ','を']

        print(question_rows[0]['hiragana'])
        print(len(question_rows[0]['hiragana']))

        answer_index = random.randint(0, len(question_rows[0]['hiragana'])-1)
        print(answer_index)
        answer_key = question_rows[0]['hiragana'][answer_index]
        print("the answer key is", answer_key)
        # sample must not include answer key
        keys = []
        keys.append(answer_key)
        while len(keys) < 8:
            key = random.choice(answer_list)
            if key != answer_key:
                keys.append(key)

        random.shuffle(keys)

        print(keys)
        return render_template("hiragana_vocab.html", question_rows=question_rows, keys=keys, answer_key=answer_key)



@app.route("/memory", methods=["GET", "POST"])
@login_required
def memory():
    if request.method == "POST":
        submitted_answer = request.form.get("answer")
        answer_key = request.form.get("anskey")
        romaji = request.form.get("romaji")
        print("submitted:", submitted_answer)
        print("anskey", answer_key)
        if submitted_answer == answer_key:
            flash('Correct! It was ' + answer_key +' (' + romaji + ')', 'info')
        else:
            flash('Wrong! It was ' + answer_key +' (' + romaji + ')', 'warning')
        return redirect("/memory")
    else:
        load_kata()
        load_hira()

        hira_kata = 0
        # hira = 1, kata = 0

        if random.randint(0, 1) == 0:
            question_id = random.randint(1,70)
            question_rows = db.execute("SELECT * FROM kata WHERE id = :id", id=question_id)

            while question_rows[0]['done'] == 1:
                question_id = random.randint(1,70)
                question_rows = db.execute("SELECT * FROM kata WHERE id = :id", id=question_id)

            answer = question_rows[0]['char']
            romaji_question = question_rows[0]['romaji']
            print(answer, romaji_question)
            options = []
            options.append(answer)
            while len(options) < 6:
                question_rows = db.execute("SELECT * FROM kata WHERE id = :id", id=random.randint(1,70))
                option = question_rows[0]['char']
                if option != answer:
                    options.append(option)

            random.shuffle(options)

            print(options)
        else:
            question_id = random.randint(1,71)
            question_rows = db.execute("SELECT * FROM hira WHERE id = :id", id=question_id)

            while question_rows[0]['done'] == 1:
                question_id = random.randint(1,71)
                question_rows = db.execute("SELECT * FROM hira WHERE id = :id", id=question_id)

            answer = question_rows[0]['char']
            romaji_question = question_rows[0]['romaji']
            print(answer, romaji_question)
            options = []
            options.append(answer)
            while len(options) < 6:
                question_rows = db.execute("SELECT * FROM hira WHERE id = :id", id=random.randint(1,71))
                option = question_rows[0]['char']
                if option != answer:
                    options.append(option)

            random.shuffle(options)

            print(options)


        return render_template("memory.html", question_rows=question_rows, options=options)


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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["streak"] = []

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



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    if request.method == "POST":
        # Ensure username was submitted
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        username = request.form.get("username")

        # check whether the username already exist
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)
        if not username:
            return apology("must provide username", 403)
        elif len(rows) == 1:
            return apology("username already exists", 403)
        elif not password:
            return apology("must provide password", 403)
        elif not confirmation:
            return apology("must confirm password", 403)
        elif password != confirmation:
            return apology("passwords do not match", 403)

        # register account
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)", username=username, hash=generate_password_hash(password))

        # login
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        session["user_id"] = rows[0]["id"]
        session["streak"] = []

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
