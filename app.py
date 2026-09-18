from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from gtts import gTTS
import requests
import os
import uuid
from langdetect import detect


app = Flask(__name__)

app.secret_key = "multilingual_translator_secret_key"


MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "multilingual_translator"


AUDIO_FOLDER = "audio"

os.makedirs(AUDIO_FOLDER, exist_ok=True)


def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )


LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Italian": "it",
    "Portuguese": "pt",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-CN",
    "Arabic": "ar",
    "Russian": "ru"
}


@app.route("/")
def index():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        languages=LANGUAGES
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:

            flash(
                "Please fill all fields.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                cursor.close()
                connection.close()

                flash(
                    "Email already registered.",
                    "error"
                )

                return redirect(
                    url_for("register")
                )

            hashed_password = generate_password_hash(
                password
            )

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password)
                VALUES (%s, %s, %s)
                """,
                (
                    name,
                    email,
                    hashed_password
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except Exception as e:

            print("Registration error:", e)

            flash(
                "Database error during registration.",
                "error"
            )

            return redirect(
                url_for("register")
            )

    return render_template(
        "register.html"
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        try:

            connection = get_db_connection()

            cursor = connection.cursor(
                dictionary=True
            )

            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (email,)
            )

            user = cursor.fetchone()

            cursor.close()
            connection.close()

            if user and check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]

                return redirect(
                    url_for("index")
                )

            flash(
                "Invalid email or password.",
                "error"
            )

        except Exception as e:

            print("Login error:", e)

            flash(
                "Database connection error.",
                "error"
            )

    return render_template(
        "login.html"
    )


@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


def translate_using_mymemory(
    text,
    source_language,
    target_language
):

    if source_language == target_language:

        return text

    if source_language == "auto":

        try:

            detected_language = detect(text)

        except Exception:

            detected_language = "en"

        source_language = detected_language

    response = requests.get(
        "https://api.mymemory.translated.net/get",
        params={
            "q": text,
            "langpair":
                f"{source_language}|{target_language}"
        },
        timeout=15
    )

    if response.status_code != 200:

        raise Exception(
            "Translation service is unavailable."
        )

    result = response.json()

    response_data = result.get(
        "responseData",
        {}
    )

    translated_text = response_data.get(
        "translatedText"
    )

    if not translated_text:

        raise Exception(
            "Translation could not be completed."
        )

    return translated_text


@app.route("/translate", methods=["POST"])
def translate():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    original_text = data.get(
        "text",
        ""
    ).strip()

    source_language = data.get(
        "source_language",
        "auto"
    )

    target_language = data.get(
        "target_language",
        "en"
    )

    if not original_text:

        return jsonify({
            "success": False,
            "message": "Please provide some text."
        }), 400

    if len(original_text) > 5000:

        return jsonify({
            "success": False,
            "message":
                "Please enter less than 5000 characters."
        }), 400

    try:

        translated_text = translate_using_mymemory(
            original_text,
            source_language,
            target_language
        )

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO translation_history
                (
                    user_id,
                    original_text,
                    translated_text,
                    source_language,
                    target_language
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    session["user_id"],
                    original_text,
                    translated_text,
                    source_language,
                    target_language
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

        except Exception as database_error:

            print(
                "History database error:",
                database_error
            )

        return jsonify({
            "success": True,
            "translated_text":
                translated_text
        })

    except Exception as e:

        print(
            "Translation error:",
            e
        )

        return jsonify({
            "success": False,
            "message":
                "Translation failed. Please try again."
        }), 500


@app.route("/speech", methods=["POST"])
def speech():

    if "user_id" not in session:

        return jsonify({
            "success": False,
            "message": "Please login first."
        }), 401

    data = request.get_json(
        silent=True
    ) or {}

    text = data.get(
        "text",
        ""
    ).strip()

    language = data.get(
        "language",
        "en"
    )

    if not text:

        return jsonify({
            "success": False,
            "message": "No text provided."
        }), 400

    try:

        filename = (
            str(uuid.uuid4())
            + ".mp3"
        )

        filepath = os.path.join(
            AUDIO_FOLDER,
            filename
        )

        tts = gTTS(
            text=text,
            lang=language,
            slow=False
        )

        tts.save(filepath)

        return jsonify({
            "success": True,
            "audio_url": url_for(
                "audio_file",
                filename=filename
            )
        })

    except Exception as e:

        print(
            "Speech error:",
            e
        )

        return jsonify({
            "success": False,
            "message":
                "Unable to create speech."
        }), 500


@app.route("/audio/<filename>")
def audio_file(filename):

    return send_from_directory(
        AUDIO_FOLDER,
        filename
    )


@app.route("/history")
def history():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        cursor.execute(
            """
            SELECT *
            FROM translation_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (
                session["user_id"],
            )
        )

        records = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template(
            "history.html",
            records=records
        )

    except Exception as e:

        print(
            "History error:",
            e
        )

        return render_template(
            "history.html",
            records=[]
        )


@app.route(
    "/delete-history/<int:history_id>",
    methods=["POST"]
)
def delete_history(history_id):

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM translation_history
            WHERE id = %s
            AND user_id = %s
            """,
            (
                history_id,
                session["user_id"]
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

    except Exception as e:

        print(
            "Delete history error:",
            e
        )

    return redirect(
        url_for("history")
    )


if __name__ == "__main__":

    app.run(
        debug=True
    )