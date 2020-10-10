import praw
import time
import traceback
import urllib.parse
from datetime import datetime, timedelta
from os import environ, getcwd, mkdir, path

import link_modifier_methods as lmm

LOGS_FILEPATH = getcwd() + "/logs/WikiHowBot.log"


def log_message(message):
    with open(LOGS_FILEPATH, 'a', errors="ignore") as output_file:
        output_file.writelines(message)


def create_log_file():
    """Creates directory and file for logs if it doesn't exist yet."""

    # Creates directory.
    mkdir(LOGS_FILEPATH.rsplit('/', 1)[0] + '/')

    # Creates a file at specified location.
    with open(LOGS_FILEPATH, 'w'):
        pass


def minutes_posted(submission):
    """Gets the time that passed (in minutes) from when the post was made. All time is converted to UTC."""

    time_created = submission.created_utc
    current_time = datetime.utcnow()
    time_posted = datetime.utcfromtimestamp(time_created)
    time_difference_in_minutes = (current_time - time_posted) / timedelta(minutes=1)
    return time_difference_in_minutes


def connect_to_reddit():
    """Connects the bot to the Reddit client."""

    return praw.Reddit(client_id=environ["WIKIHOWLINKBOT_CLIENT_ID"],
                       client_secret=environ["WIKIHOWLINKBOT_CLIENT_SECRET"],
                       user_agent=environ["WIKIHOWLINKBOT_USER_AGENT"],
                       username=environ["WIKIHOWLINKBOT_USERNAME"],
                       password=environ["WIKIHOWLINKBOT_PASSWORD"])


def send_error_message(stack_trace):
    """If a runtime error has occurred, PM a mod with the error details."""
    reddit = connect_to_reddit()

    reddit.redditor('Improbably_wrong').message('ERROR - r/disneyvacation', stack_trace)
    reddit.redditor('Xalaxis').message('ERROR - r/disneyvacation', stack_trace)


def source_added_check():
    """
    Checks if source was added by searching through all unread inbox replies for a wikiHow link.
    If the wikiHow link was provided, remove parent comment and user comment, and approve the post while adding the
    users provided comment as a top-level comment to the post.
    """

    reddit = connect_to_reddit()

    bot_inbox = reddit.inbox.unread(limit=None)
    unread_messages = []

    for message in bot_inbox:

        message_provided = urllib.parse.unquote(message.body)
        if message.was_comment and message.submission.banned_by == "WikiHowLinkBot" and lmm.is_wikihow_url_in_comment(message_provided):

            try:
                message.parent().mod.remove()  # Deletes the bots comment
                message.mod.remove()  # Deletes user comment
            except AttributeError:
                reddit.inbox.mark_read([message])
                continue

            # Replies to post with wikiHow source link provided by OP.
            message.submission.reply(lmm.link_formatter(message_provided, post_reapproval=True)).mod.distinguish(how='yes')

            message.submission.mod.approve()  # Approves the post
            log_message("Post RE-APPROVED - " + message.submission.title + " (www.reddit.com" + message.submission.permalink + ")\n")

        unread_messages.append(message)

    reddit.inbox.mark_read(unread_messages)


def moderate_post(link, title, reminder):
    """
    If post was made over 5 minutes ago, ensure a wikiHow link was posted as a top-level comment reply.
    If the wikiHow link was provided in plain-text desktop format, post is skipped.
    If the wikiHow link was provided in mobile, AMP or hyperlink format, bot replies to comment with the correctly formatted wikiHow link.
    If the wikiHow link was not provided, post is deleted and the bot replies with a reminder to post the link to the source article.
    """

    reddit = connect_to_reddit()

    submission = reddit.submission(url='https://www.reddit.com' + link)
    wikihow_link = False

    # Skips if post was made by a mod or if post author was deleted.
    if not submission.author or submission.author.name in environ["WIKIHOWLINKBOT_DISNEYVACATION_MODS"].split(','):
        return

    if not wikihow_link:
        submission.comments.replace_more(limit=0)
        # Searches through top-level comments and checks if there is a wikiHow link in them.
        for top_level_comment in submission.comments:
            if not top_level_comment.author:
                continue
            comment_to_check = urllib.parse.unquote(top_level_comment.body)
            # Checks if any wikiHow domains are linked in the comments by the author or if mods already replied to post.
            if top_level_comment.author.name == submission.author.name and lmm.is_wikihow_url_in_comment(comment_to_check):

                wikihow_link = True
                for comment in top_level_comment.replies:  # Checks if bot already replied with a desktop link.
                    if not comment.author:
                        continue
                    if comment.author.name == 'WikiHowLinkBot':
                        return

                # Replies with plain-text desktop link if comment containing link isn't formatted correctly.
                link_to_reply = lmm.link_formatter(comment_to_check)
                if link_to_reply:
                    top_level_comment.reply(link_to_reply)
                break

    # Replies to post and stickies the reply + distinguish.
    if not wikihow_link:
        submission.reply(f"Hey /u/{submission.author.name}\n\n{reminder}").mod.distinguish(how='yes', sticky=True)
        log_message("Post FAILED - " + title + " (www.reddit.com" + link + ")\n")
        time.sleep(3)  # Prevents Reddit from detecting spam.
        submission.mod.remove()  # Deletes the post.
    else:
        log_message("Post PASSED - " + title + " (wikiHow link)" + "\n")


def moderate_posts():
    subreddit_name = 'disneyvacation'
    post_link_reminder_text = "The mod team at /r/disneyvacation thanks you for your submission, however it has been " \
                              "automatically removed since the link to the wikiHow source article was not provided." \
                              "\n\nPlease reply to THIS COMMENT with the source article and your post " \
                              "will be approved within at most 5 minutes."

    reddit = connect_to_reddit()

    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.new(limit=50)

    # Creates log directory and file if it doesn't exist.
    if not path.isdir(LOGS_FILEPATH.rsplit('/', 1)[0] + '/'):
        create_log_file()

    for post in posts:
        if minutes_posted(post) < 5:
            continue
        if minutes_posted(post) > 12:
            break

        moderate_post(post.permalink, post.title, post_link_reminder_text)

    source_added_check()  # Checks bots inbox for comment replies with wikiHow link.


if __name__ == "__main__":

    try:
        while True:
            print("WikiHowLinkBot is starting @ " + str(datetime.now()))
            moderate_posts()
            print("Sweep finished @ " + str(datetime.now()))
            time.sleep(5 * 60)  # Wait for 5 minutes before running again.
    except Exception as error:
        print(f"An error has occurred: {error}")
        send_error_message(traceback.format_exc())
        time.sleep(5 * 60 * 60)  # Stop for 5 hours if an exception occurred.
