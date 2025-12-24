import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

# Laad .env (lokaal) – Azure negeert dit automatisch
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# SMTP instellingen
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

VERZENDER_EMAIL = os.getenv("VERZENDER_EMAIL")
ONTVANGER_EMAIL = os.getenv("ONTVANGER_EMAIL")


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/contact", methods=["POST"])
def contact():

    honeypot = request.form.get('honeypot')
    if honeypot:
        # Als dit veld is ingevuld, is het een bot!
        # We doen net alsof het gelukt is, maar sturen niks.
        print("Bot gevangen! Spam tegengehouden.")
        return redirect(url_for('home'))
    
    name = request.form.get("name")
    klant_email = request.form.get("email")
    message_content = request.form.get("message")

    # === MAIL NAAR JOU ===
    msg_admin = MIMEMultipart()
    msg_admin["From"] = VERZENDER_EMAIL
    msg_admin["To"] = ONTVANGER_EMAIL
    msg_admin["Subject"] = f"Contact via website: {name}"
    msg_admin.add_header("Reply-To", klant_email)

    body_admin = f"""
Naam: {name}
Email: {klant_email}

Bericht:
{message_content}
"""
    msg_admin.attach(MIMEText(body_admin, "plain"))

    # === BEVESTIGING NAAR KLANT ===
    msg_klant = MIMEMultipart()
    msg_klant["From"] = VERZENDER_EMAIL
    msg_klant["To"] = klant_email
    msg_klant["Subject"] = "Bevestiging: bericht ontvangen – The Bhaiwas"

    body_klant = f"""
Hoi {name},

Thanks voor je bericht.
We hebben het goed ontvangen en komen snel bij je terug.

Je bericht:
-----------------
{message_content}
-----------------

Groet,
The Bhaiwas
"""
    msg_klant.attach(MIMEText(body_klant, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)

        server.send_message(msg_admin)
        server.send_message(msg_klant)

        server.quit()

        flash("Je bericht is verzonden. Check je mail voor bevestiging.", "success")

    except Exception as e:
        print("MAIL FOUT:", e)
        flash("Er ging iets mis bij het versturen.", "error")

    return redirect(url_for("home") + "#contact")


if __name__ == "__main__":
    app.run(debug=True)
