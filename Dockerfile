# Based on Python
FROM python:alpine

LABEL Name=wikihow_reddit_bot Version=0.0.1

# Copy all files in wikihowbot as well as requirements.txt to the working directory of the container filesystem.
WORKDIR /wikihowbot
COPY wikihowbot .
COPY requirements.txt .

# Using pip:
RUN python3 -m pip install -r requirements.txt

# Start bot
CMD ["python3", "-u", "./wikihowbot.py"]