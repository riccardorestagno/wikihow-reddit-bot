# import kdapi.kdapi as kd
# import time
# import wikihowlink as wk
#
# def repost_check(link, title, subreddit):
#     """Returns true if a repost occured"""
#
#     reddit = wk.connect_to_reddit()
#
#     for repost in kd.check(link, subreddit):
#         submission = reddit.submission(url=repost.link)
#
#         # Repost
#         if repost.similarity is not None and repost.similarity > 95:
#
#             # Image Repost
#             if wk.minutes_posted(submission) < 60 * 24 and submission.score > 500:
#                 submission.reply('Hey /u/' + submission.author.name + ". The mod team at /r/disneyvacation thanks you for your submission, however it has been automatically removed since"
#                                  + " the wikihow image provided is an image repost of the following post: " + repost.link
#                                  + "\nPlease refrain from using Wikihow images that were used within the past 24 hours on this sub."
#                                  + "\nNOTE: This feature is currently in BETA so if you believe this post was removed incorrectly, please contact us through modmail.").mod.distinguish(how='yes', sticky=True)
#                 time.sleep(3)  # Prevents PRAW from detecting spam
#                 submission.mod.remove()  # Deletes the post
#                 return True
#
#             # Blatant Repost
#             same_words = set.intersection(set(repost.title.lower().split()), set(title.lower().split()))
#             if submission.score > 5000 and same_words >= 6:
#                 submission.reply(
#                     'Hey /u/' + submission.author.name + ". The mod team at /r/disneyvacation thanks you for your submission, however it has been automatically removed since"
#                     + " the wikihow image provided is a blatant of the following post: " + repost.link
#                     + "\nPlease refrain from using Wikihow images that were used within the past 24 hours on this sub."
#                     + "\nNOTE: This feature is currently in BETA so if you believe this post was removed incorrectly, please contact us through modmail.").mod.distinguish(how='yes', sticky=True)
#                 time.sleep(3)  # Prevents PRAW from detecting spam
#                 submission.mod.remove()  # Deletes the post
#                 return True
#
#     return False
