from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector


app = Flask(__name__)
app.secret_key = "secret123"

db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="soundify",
    port=8889
)

# ---------------- HOME ----------------
@app.route("/")
def home():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM songs")
    songs = cursor.fetchall()
    return render_template("index.html", songs=songs)

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users(email,password) VALUES(%s,%s)",
            (email,password)
        )
        db.commit()

        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email,password)
        )

        user = cursor.fetchone()

        if user:
            session['user'] = user['id']
            return redirect("/")

    return render_template("login.html")


# ---------------- SEARCH ----------------
@app.route("/search")
def search():
    q = request.args.get("q")

    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM songs
        WHERE title LIKE %s OR artist LIKE %s
    """,(f"%{q}%",f"%{q}%"))

    return jsonify(cursor.fetchall())

# ---------------- FAVOURITE ----------------
@app.route("/fav/<int:song_id>")
def fav(song_id):
    if "user" not in session:
        return "Login first"

    cursor = db.cursor()
    cursor.execute("INSERT INTO favourites(user_id,song_id) VALUES(%s,%s)",
                   (session['user'],song_id))
    db.commit()

    return "Added"

if __name__ == "__main__":
    app.run(debug=True)
