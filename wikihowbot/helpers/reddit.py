import praw
from datetime import datetime, timedelta
from os import environ


def connect_to_reddit():
    """Connects the bot to the Reddit client."""

    return praw.Reddit(client_id=environ["WIKIHOWLINKBOT_CLIENT_ID"],
                       client_secret=environ["WIKIHOWLINKBOT_CLIENT_SECRET"],
                       user_agent=environ["WIKIHOWLINKBOT_USER_AGENT"],
                       username=environ["WIKIHOWLINKBOT_USERNAME"],
                       password=environ["WIKIHOWLINKBOT_PASSWORD"])


def minutes_posted(submission):
    """Gets the time that passed (in minutes) from when the post was made. All time is converted to UTC."""

    time_created = submission.created_utc
    current_time = datetime.utcnow()
    time_posted = datetime.utcfromtimestamp(time_created)
    time_difference_in_minutes = (current_time - time_posted) / timedelta(minutes=1)
    return time_difference_in_minutes


def send_error_message(stack_trace):
    """If a runtime error has occurred, PM a mod with the error details."""
    reddit = connect_to_reddit()

    reddit.redditor('Improbably_wrong').message('ERROR - r/disneyvacation', stack_trace)
    reddit.redditor('Xalaxis').message('ERROR - r/disneyvacation', stack_trace)
