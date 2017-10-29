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

def sticky_and_delete(link):
	""" Post where wikihow bot made a comment in is called and the comment is stickied and the post is deleted"""
	reddit = praw.Reddit(client_id='',
		client_secret= '',
		user_agent='',
		username='',
		password='')
		
	submission = reddit.submission(url = 'https://www.reddit.com' + link)
	submission.comments.replace_more(limit=0)
	
	#Searched for wikihowbots post and pins it to top
	for top_level_comment in submission.comments:
		if top_level_comment.author == 'WikiHowLinkBot':
			top_level_comment.mod.distinguish(how='yes', sticky=True)
		break
		
	submission.mod.remove() #deletes the post
	
def comment_on_post(link, title, reminder):
	"""If post was made longer than 10 minutes ago, module checks if wikihow link is a top-level comment
If true, post is skipped. If false, comment is made on post, then another definition is called to sticky and delete post"""
	reddit = praw.Reddit(client_id='',
					client_secret= '',
					user_agent='',
					username='',
					password='')
					
	
	wikihow_domains = [ 'wikihow.com/','wikihow.mom/','wikihow.life/','wikihow.pet/']	# Different possible wikihow domains
	submission = reddit.submission(url = 'https://www.reddit.com' + link)
	wikihowlink = False

	# Prevents exception (AttributeError: 'MoreComments' object has no attribute 'body')
	# For more info, go to (http://praw.readthedocs.io/en/latest/tutorials/comments.html) 
	submission.comments.replace_more(limit=0)
	
	#searches through top-level comments and checks if there is a wikihow link in them
	for top_level_comment in submission.comments:
		if any(urls in top_level_comment.body for urls in wikihow_domains): # Checks if any wikihow domains are linked in the comments
			wikihowlink = True
			
	if wikihowlink == False:
		print(title)
		print('https://www.reddit.com' + link)
		webbrowser.open_new_tab('https://www.reddit.com' + link)
		submission.reply(reminder) #replys to post
		print("Reply done")
		time.sleep(7) # Prevents praw from detecting spam and also gives enough time for reply to register before calling sticky_and_delete
		sticky_and_delete(link)	
		print("Sticky done")
		#time.sleep(60) # Gives Xalaxis time to check the bot is working	
		
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
		comment_on_post(submission.permalink, submission.title, post_link_reminder_text)
