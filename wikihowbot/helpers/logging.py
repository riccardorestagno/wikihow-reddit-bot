import os
import smtplib
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from os import getcwd, makedirs


LOGS_FILEPATH = getcwd() + "/logs/WikiHowBot.log"


def log_message(message):
    with open(LOGS_FILEPATH, 'a', errors="ignore") as output_file:
        output_file.writelines(message)


def create_log_file():
    """Creates directory and file for logs if it doesn't exist yet."""

    # Creates directory.
    makedirs(LOGS_FILEPATH.rsplit('/', 1)[0] + '/', exist_ok=True)

    # Creates a file at specified location.
    with open(LOGS_FILEPATH, 'w'):
        pass


def send_email(sender, recipients, attachment):
    email_server = smtplib.SMTP('smtp.gmail.com', 587)
    email_server.ehlo()

    email_server.starttls()

    email_server.login('', '')

    email_server.sendmail(sender, recipients, attachment)

    email_server.quit()


def attachment(sender, recipients, date):
    """Creates attachment using MIMEMultipart (see: https://gist.github.com/rdempsey/22afd43f8d777b78ef22)."""
    msg = MIMEMultipart()
    msg['Subject'] = "WikiHowLink Bot Log for Week of " + date
    msg['From'] = sender
    msg['To'] = recipients

    part = MIMEBase('application', "octet-stream")
    part.set_payload(open(filepath, "rb").read())
    encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(filepath))

    msg.attach(part)
    composed = msg.as_string()

    return composed


def clear_textfile(filepath):
    i = 0
    file = open(filepath, "r")
    lines = file.readlines()
    file.close()

    with open(filepath, 'w') as file:
        for line in lines:
            file.write(line)
            i += 1
            if i == 4:
                break


if __name__ == '__main__':
    filepath = r""

    sender = ''
    recipients = ['']
    recipients = ', '.join(recipients)

    last_week = datetime.today() - timedelta(7)
    date_formatted = last_week.strftime("%Y-%m-%d")

    send_email(sender, recipients, attachment(sender, recipients, date_formatted))
    clear_textfile(filepath)
