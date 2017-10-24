import praw
import time
from datetime import datetime, timedelta


def minutes_posted(submission):
	"""Gets the time that passed (in minutes) from when the post was made. (All time is converted to UTC)"""
	time_created = submission.created_utc
	current_time = datetime.utcnow()
	time_posted = datetime.utcfromtimestamp(time_created)
	time_difference_in_minutes = (current_time - time_posted)/timedelta(minutes=1)
	return time_difference_in_minutes

def reddit_bot(link, title, reminder):
	"""If post was made longer than 10 minutes ago, module checks if wikihow link is a top-level comment
If true, post is skipped. If false, comment is made on post, then it is deleted"""
	reddit = praw.Reddit(client_id='',
					client_secret= '',
					user_agent='',
					username='',
					password='')
					
					
	submission = reddit.submission(url = 'https://www.reddit.com' + link)
	wikihowlink = False

	# Prevents exception (AttributeError: 'MoreComments' object has no attribute 'body')
	# For more info, go to (http://praw.readthedocs.io/en/latest/tutorials/comments.html) 
	submission.comments.replace_more(limit=0)
	
	#searches through top-level comments and checks if there is a wikihow link in them
	for top_level_comment in submission.comments:
		if 'wikihow.com/' in top_level_comment.body:
			wikihowlink = True
			
	if wikihowlink == False:
		print(title)
		submission.reply(reminder) #replys to post
		submission.mod.remove() #deletes the post
		time.sleep(5) # Prevents praw from detecting spam

if __name__ == "__main__":
	post_link_reminder_text = """Hello user. Thank you for your submission. However, it has been removed for the following reason(s):  

Rule 2: All posts must provide the source WikiHow article as a link in the comments.


Please add a comment linking to the source article, then [message the mods](http://www.reddit.com/message/compose?to=%2Fr%2FDisneyVacation) and provide us with the link to the comment's section of your post."""

	reddit = praw.Reddit(client_id='',
					client_secret= '',
					user_agent='')

	subreddit = reddit.subreddit('disneyvacation')
	submissions = subreddit.new(limit=50)

	#gets url of newest posts on disneyvacation
	for submission in submissions:
		#Goes to next loop iteration if post was made less than 10 minutes ago
		if minutes_posted(submission) < 10:
			continue
		reddit_bot(submission.permalink, submission.title, post_link_reminder_text)
