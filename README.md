# Multilingual Speech Translator

A web-based multilingual speech translator built using Python and Flask. The application allows users to enter text, translate it into different languages, convert translated text into speech, and maintain their translation history.

## Features

* User registration and login
* Secure password hashing
* Text translation between multiple languages
* Automatic source language detection
* Text-to-speech conversion
* Translation history
* Delete translation history
* MySQL database integration
* Simple and interactive web interface
* Support for multiple Indian and international languages

## Technologies Used

* Python
* Flask
* HTML
* CSS
* JavaScript
* MySQL
* MySQL Connector
* gTTS
* MyMemory Translation API
* LangDetect
* python-dotenv

## Project Structure

```text
Multilingual-Speech-Translator/
│
├── app.py
├── requirements.txt
├── .gitignore
├── .env
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── history.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── audio/
```

## How It Works

1. Users register and create an account.
2. Users log in to access the translator.
3. Users enter the text they want to translate.
4. The application translates the text using the MyMemory Translation API.
5. The translated text can be converted into speech using gTTS.
6. Translation details are stored in the MySQL database.
7. Users can view and delete their previous translation history.

## Database

The application uses MySQL to store:

* User information
* Encrypted/hashed passwords
* Translation history
* Source and target languages
* Original and translated text

Create a database named:

```sql
CREATE DATABASE multilingual_translator;
```

The required tables should be created before running the application.

## Environment Variables

Sensitive information such as the MySQL password and Flask secret key is stored in a `.env` file.

Example:

```env
SECRET_KEY=your_secret_key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=multilingual_translator
```

**Do not upload the `.env` file to GitHub.**

The `.gitignore` file should contain:

```gitignore
.env
__pycache__/
*.pyc
audio/
venv/
.venv/
```

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Open the project folder:

```bash
cd Multilingual-Speech-Translator
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Create the `.env` file and add your MySQL configuration.

## Run the Application

Start the Flask application:

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

## Security

* Passwords are stored using password hashing.
* Database credentials are stored in environment variables.
* The `.env` file is excluded from GitHub using `.gitignore`.
* User translation history is associated with the logged-in user.

## Future Enhancements

* Voice input using speech recognition
* More language support
* Improved translation accuracy
* Download translated audio
* Responsive UI improvements
* Deployment to a cloud platform

## Author

Charanya

B.Tech – Computer Science and Engineering
Specialization: Artificial Intelligence and Data Science
