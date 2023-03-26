import prawcore
import time
import traceback
import urllib.parse
from datetime import datetime
from os import path

import helpers.link_modifier_methods as lmm
from helpers.logging import create_log_file, log_message, logs_filepath
from helpers.reddit import bot_username, connect_to_reddit, get_minutes_posted, moderated_subreddits, reddit_url, send_error_message


post_link_reminder_text = f"The mod team thanks you for your submission, however it has been " \
                           "automatically removed since the link to the wikiHow source article was not provided." \
                           "\n\nPlease reply to THIS COMMENT with the source article and your post " \
                           "will be approved within at most 5 minutes."


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
        if message.was_comment and message.submission.banned_by == bot_username and lmm.is_wikihow_url_in_comment(message_provided):

            try:
                message.parent().mod.remove()  # Deletes the bots comment.
                message.mod.remove()  # Deletes the users comment.
            except AttributeError:
                reddit.inbox.mark_read([message])
                continue

            # Replies to post with the wikiHow source link provided by OP.
            message.submission.reply(lmm.process_comment(message_provided, post_reapproval=True)).mod.distinguish(how='yes')

            message.submission.mod.approve()  # Approves the post.
            log_message(f"Post RE-APPROVED - {message.submission.title} ({reddit_url}{message.submission.permalink})\n")

        unread_messages.append(message)

    reddit.inbox.mark_read(unread_messages)


def moderate_post(post):
    """
    If post was made over 5 minutes ago, ensure a wikiHow link was posted as a top-level comment reply.
    If the wikiHow link was provided in plain-text desktop format, post is skipped.
    If the wikiHow link was provided in mobile, AMP or hyperlink format, bot replies to comment with the correctly formatted wikiHow link.
    If the wikiHow link was not provided, post is deleted and the bot replies with a reminder to post the link to the source article.
    """

    reddit = connect_to_reddit()
    submission = reddit.submission(url=f"{reddit_url}{post.permalink}")

    # Skips if the post was stickied/distinguished by a mod or if the post author was deleted.
    if submission.stickied or submission.distinguished or not submission.author:
        return

    # Searches through the top-level comments and checks for a wikiHow link provided by OP.
    submission.comments.replace_more(limit=0)
    for top_level_comment in submission.comments:

        if not top_level_comment.author:  # User was deleted.
            continue

        if top_level_comment.author.name == bot_username:  # Bot already replied with the source.
            return

        # Checks if any wikiHow domains are linked in the comments by the author or if the mods already replied to post.
        if top_level_comment.author.name == submission.author.name:

            comment_to_check = urllib.parse.unquote(top_level_comment.body)

            if lmm.is_wikihow_url_in_comment(comment_to_check):

                # Checks if the bot already replied with a correctly formatted link.
                for comment in top_level_comment.replies:
                    if comment.author and comment.author.name == bot_username:
                        return

                # Replies with a plain-text desktop link if a comment containing the wikiHow link isn't formatted correctly.
                link_to_reply = lmm.process_comment(comment_to_check)
                if link_to_reply:
                    top_level_comment.reply(link_to_reply)

                return

    # If no wikiHow link was found, the bot replies to the post with a reminder to provide the source link of the image.
    submission.reply(f"Hey /u/{submission.author.name}\n\n{post_link_reminder_text}").mod.distinguish(how='yes', sticky=True)
    log_message(f"Post FAILED - {post.title} ({reddit_url}{post.permalink})\n")
    time.sleep(3)  # Prevents Reddit from detecting spam.
    submission.mod.remove()  # Deletes the post.


def moderate_posts():
    """Iterates through all new submissions on moderated subreddits to ensure they meet all posting requirements."""

    # Creates log directory and file if it doesn't exist.
    if not path.exists(logs_filepath):
        create_log_file()

    reddit = connect_to_reddit()
    subreddit = reddit.subreddit('+'.join(moderated_subreddits))
    posts = subreddit.new(limit=50)

    for post in posts:
        minutes_posted = get_minutes_posted(post)
        if minutes_posted < 5:
            continue
        if minutes_posted > 30:
            break

        moderate_post(post)

    source_added_check()  # Checks bots inbox for comment replies with wikiHow link.


if __name__ == "__main__":

    while True:
        try:
            print("WikiHowLinkBot is starting @ " + str(datetime.now()))
            moderate_posts()
            print("Sweep finished @ " + str(datetime.now()))
            time.sleep(5 * 60)  # Wait for 5 minutes before running again.
        except prawcore.exceptions.ResponseException as httpError:
            if httpError.response.status_code == 500 or \
                httpError.response.status_code == 502 or \
                httpError.response.status_code == 503:
                log_message(f"Reddit is temporarily down. Waiting 5 minutes.")
                time.sleep(5 * 60)  # Temporary connection error. Wait for 5 minutes before running again.
            else:
                print(f"A HTTP error has occurred. Received {httpError.response.status_code} HTTP response.")
                send_error_message(f"A HTTP error has occurred. Received {httpError.response.status_code} HTTP response.")
                time.sleep(1 * 60 * 60)  # Stop for 1 hour if an unhandled HTTP exception occurred.
        except prawcore.exceptions.RequestException:
            time.sleep(5 * 60)  # Temporary connection error. Wait 5 minutes before running again.
        except Exception as error:
            print(f"An error has occurred: {error}")
            send_error_message(traceback.format_exc())
            time.sleep(1 * 60 * 60)  # Stop for 1 hour if an unknown exception occurred.
