import urllib.parse
import praw
import kdapi.kdapi as kd
import time
from datetime import datetime, timedelta

wikihow_domains = ['wikihow.com/', 'wikihow.mom/', 'wikihow.life/', 'wikihow.pet/', 'wikihow.fitness/', 'wikihow.it/']
disneyvacation_mods = ['DaemonXI', 'Xalaxis', 'sloth_on_meth', 'Improbably_wrong', 'Quimpers', 'siouxsie_siouxv2',
                       'WikiHowLinkBot']


def repost_check(link, title, subreddit):
  """Returns true if a repost occured"""

    reddit = connect_to_reddit()

    for repost in kd.check(link, subreddit):
        submission = reddit.submission(url=repost.link)

        # Repost
        if repost.similarity is not None and repost.similarity > 95:

            # Image Repost
            if minutes_posted(submission) < 60 * 24 and submission.score > 500:
                submission.reply('Hey /u/' + submission.author.name + ". The mod team at /r/disneyvacation thanks you for your submission, however it has been automatically removed since"
                                 + " the wikihow image provided is an image repost of the following post: " + repost.link
                                 + "\nPlease refrain from using Wikihow images that were used within the past 24 hours on this sub."
                                 + "\nNOTE: This feature is currently in BETA so if you believe this post was removed incorrectly, please contact us through modmail.").mod.distinguish(how='yes', sticky=True)
                time.sleep(3)  # Prevents PRAW from detecting spam
                submission.mod.remove()  # Deletes the post
                return True

            # Blatant Repost
            same_words = set.intersection(set(repost.title.split()), set(title.lower().split()))
            if submission.score > 5000 and same_words >= 6:
                submission.reply(
                    'Hey /u/' + submission.author.name + ". The mod team at /r/disneyvacation thanks you for your submission, however it has been automatically removed since"
                    + " the wikihow image provided is a blatant of the following post: " + repost.link
                    + "\nPlease refrain from using Wikihow images that were used within the past 24 hours on this sub."
                    + "\nNOTE: This feature is currently in BETA so if you believe this post was removed incorrectly, please contact us through modmail.").mod.distinguish(how='yes', sticky=True)
                time.sleep(3)  # Prevents PRAW from detecting spam
                submission.mod.remove()  # Deletes the post
                return True
              
    return False


def minutes_posted(submission):
    """Gets the time that passed (in minutes) from when the post was made. (All time is converted to UTC)"""
    time_created = submission.created_utc
    current_time = datetime.utcnow()
    time_posted = datetime.utcfromtimestamp(time_created)
    time_difference_in_minutes = (current_time - time_posted)/timedelta(minutes=1)
    return time_difference_in_minutes


def connect_to_reddit():
    """ Connects the bot to the Reddit client"""

    reddit = praw.Reddit(client_id='',
                         client_secret='',
                         user_agent='',
                         username='',
                         password='')
    return reddit


def mobile_to_desktop_link(mobile_link, post_reapproval):
    """ Converts moble link to desktop link"""
    desktop_link = mobile_link
    if '[' in desktop_link:  # removes end bracket in hyperlink if user added any as well as any following text
        desktop_link = desktop_link.rsplit(')', 1)[0]
    desktop_link = desktop_link.rsplit('m.wikihow.', 1)[1]  # removes mobile hyperlinks
    desktop_link = 'https://www.wikihow.' + desktop_link.split('?', 1)[0]  # removes additional parameters
    desktop_link = desktop_link.rsplit('amp=', 1)[0]  # removes 'amp' mobile tag

    if post_reapproval:
        return 'User-provided source: ' + desktop_link
    else:
        return 'Desktop Link: ' + desktop_link


def plaintext_link_maker(comment, post_reapproval=False):
    """Converts wikihow hyperlink comment to plain text"""
    link_to_reply = comment.split('](', 1)[1]
    link_to_reply = link_to_reply.rsplit(')', 1)[0]

    if not post_reapproval:
        return 'Plain Text Link: ' + link_to_reply
    else:
        return 'User-provided source: ' + link_to_reply


def source_added_check(filepath):
    """ Checks if source was added by searching thorough all unread inbox replies for a wikihow link
    If Wikihow link was provided, remove parent comment and user comment, and approve the post while adding the users comment as a top-level comment to the post
    POTENTIAL GLITCH: If the user replies a wikihow link to a non-removal comment, both comments can be deleted and an incorrect source can be added."""

    reddit = connect_to_reddit()

    bot_inbox = reddit.inbox.unread(limit=None)
    unread_messages = []

    for message in bot_inbox:

        message_provided = urllib.parse.unquote(message.body)
        if any(urls in message_provided for urls in wikihow_domains) and message.submission.banned_by == "WikiHowLinkBot": #checks if reply contains a wikihow url

            try:
                message.parent().mod.remove()  # deletes the bots comment
                message.mod.remove()  # deletes user comment
            except AttributeError:
                reddit.inbox.mark_read([message])
                continue

            if 'm.wikihow.' in message_provided:  # If mobile link is given, convert mobile to desktop link
                message.submission.reply(mobile_to_desktop_link(message_provided, post_reapproval = True)).mod.distinguish(how='yes')
                with open(filepath, 'a') as outputfile:
                        outputfile.writelines("Desktop link added - " + message.submission.title + " (www.reddit.com" + message.submission.permalink + ")\n")
            elif '](' in message_provided and message_provided.lower().count(".wikihow.") == 1:
                message.submission.reply(plaintext_link_maker(message_provided, post_reapproval=True)).mod.distinguish(how='yes')
            else:
                message.submission.reply('User-provided source: https://www.wikihow.' + message_provided.split('.wikihow.', 1)[1].split('](')[0]).mod.distinguish(how='yes') #replies to post with wikihow source link provided

            message.submission.mod.approve()  # approves the post
            with open(filepath, 'a') as outputfile:
                outputfile.writelines("Post RE-APPROVED - " + message.submission.title + " (www.reddit.com" + message.submission.permalink + ")\n")

        unread_messages.append(message)

    reddit.inbox.mark_read(unread_messages)


def comment_on_post(link, title, reminder, filepath):
    """If post was made longer than 5 minutes ago, module checks if wikihow link is a top-level comment
If true, post is skipped. If false, comment is made on post, then another definition is called to sticky and delete post"""

    reddit = connect_to_reddit()

    submission = reddit.submission(url = 'https://www.reddit.com' + link)
    wikihowlink = False

    # Skips if post was made by a mod
    if submission.author.name in disneyvacation_mods:
        return

    if not wikihowlink:
        submission.comments.replace_more(limit=0)
        # searches through top-level comments and checks if there is a wikihow link in them
        for top_level_comment in submission.comments:
            comment_to_check = urllib.parse.unquote(top_level_comment.body)
            # Checks if any wikihow domains are linked in the comments by the author or if mods already replied to post
            if (top_level_comment.author.name == submission.author.name and any(urls in comment_to_check for urls in wikihow_domains)) \
            or any(mods == top_level_comment.author.name for mods in disneyvacation_mods):

                wikihowlink = True
                for comment in top_level_comment.replies:  # Checks if bot already replied with a desktop link
                    if comment.author.name == 'WikiHowLinkBot':
                        return

                if 'm.wikihow.' in comment_to_check:  # If mobile link is given, convert mobile to desktop link
                    top_level_comment.reply(mobile_to_desktop_link(comment_to_check, post_reapproval = False))  # replies with desktop link

                elif '](' in comment_to_check and comment_to_check.lower().count(".wikihow.") == 1:
                    top_level_comment.reply(plaintext_link_maker(comment_to_check))
                break

    if not wikihowlink:
        submission.reply('Hey /u/' + submission.author.name + reminder).mod.distinguish(how='yes', sticky=True)  # replies to post and stickies the reply + distinguish
        with open(filepath, 'a') as outputfile:
            outputfile.writelines("Post FAILED - " + title + " (www.reddit.com" + link + ")\n")
        time.sleep(3)  # Prevents PRAW from detecting spam
        submission.mod.remove()  # deletes the post
    else:
        with open(filepath, 'a') as outputfile:
            outputfile.writelines("Post PASSED - " + title + " (WikiHow link)" + "\n")


if __name__ == "__main__":

    subreddit_name = 'disneyvacation'
    filepath = r"C:\Users\Riccardo\Desktop\Python_Scripts\WikiHow Reddit Bot\WikiHowBotLog.txt"
    post_link_reminder_text = """. The mod team at /r/disneyvacation thanks you for your submission, however it has been automatically removed since the link to the Wikihow source article was not provided.

Please reply to THIS COMMENT with the source article and your post will be approved within at most 10 minutes."""

    reddit = connect_to_reddit()

    subreddit = reddit.subreddit(subreddit_name)
    posts = subreddit.new(limit=50)

    for post in posts:
        if minutes_posted(post) < 5:
            continue

        if minutes_posted(post) > 12:
            break

        # If its not a repost, then check for source
        if not repost_check(post.url, post.title, subreddit_name):  # Checks for reposts (BETA)
            comment_on_post(post.permalink, post.title, post_link_reminder_text, filepath)

    source_added_check(filepath)  # Checks bots inbox for comment replies with wikihow link
