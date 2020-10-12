import time
import traceback
import urllib.parse
from datetime import datetime
from os import environ, path

import helpers.link_modifier_methods as lmm
from helpers.logging import create_log_file, log_message, LOGS_FILEPATH
from helpers.reddit import connect_to_reddit, minutes_posted, send_error_message


SUBREDDIT_NAME = 'disneyvacation'
POST_LINK_REMINDER_TEXT = "The mod team at /r/disneyvacation thanks you for your submission, however it has been " \
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


def moderate_post(link, title):
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

    submission.comments.replace_more(limit=0)
    # Searches through top-level comments and checks if there is a wikiHow link in them.
    for top_level_comment in submission.comments:

        if not top_level_comment.author:  # User was deleted.
            continue

        if top_level_comment.author.name == 'WikiHowLinkBot':  # Bot already replied with the source.
            return

        comment_to_check = urllib.parse.unquote(top_level_comment.body)

        # Checks if any wikiHow domains are linked in the comments by the author or if mods already replied to post.
        if top_level_comment.author.name == submission.author.name and lmm.is_wikihow_url_in_comment(comment_to_check):

            wikihow_link = True
            for comment in top_level_comment.replies:  # Checks if bot already replied with a desktop link.
                if comment.author and comment.author.name == 'WikiHowLinkBot':
                    return

            # Replies with plain-text desktop link if comment containing link isn't formatted correctly.
            link_to_reply = lmm.link_formatter(comment_to_check)
            if link_to_reply:
                top_level_comment.reply(link_to_reply)
            break

    # Replies to post and stickies the reply + distinguish.
    if not wikihow_link:
        submission.reply(f"Hey /u/{submission.author.name}\n\n{POST_LINK_REMINDER_TEXT}").mod.distinguish(how='yes', sticky=True)
        log_message(f"Post FAILED - {title} (https://www.reddit.com{link})\n")
        time.sleep(3)  # Prevents Reddit from detecting spam.
        submission.mod.remove()  # Deletes the post.
    else:
        log_message(f"Post PASSED - {title} (https://www.reddit.com{link})\n")


def moderate_posts():
    """
    Iterates through all new submissions on r/disneyvacation that were posted between 5-12 minutes ago to ensure
    they meet all posting requirements.
    """

    reddit = connect_to_reddit()

    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    posts = subreddit.new(limit=50)

    # Creates log directory and file if it doesn't exist.
    if not path.isdir(LOGS_FILEPATH.rsplit('/', 1)[0] + '/'):
        create_log_file()

    for post in posts:
        if minutes_posted(post) < 5:
            continue
        if minutes_posted(post) > 12:
            break

        moderate_post(post.permalink, post.title)

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
        time.sleep(1 * 60 * 60)  # Stop for 1 hour if an exception occurred.
