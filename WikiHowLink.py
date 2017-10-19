import praw
import time

def reddit_bot(link, title, reminder):
	
	reddit = praw.Reddit(client_id='',
					client_secret= '',
					user_agent='',
					username='',
					password='')
					
					
	submission = reddit.submission(url = link)
	wikihowlink = False

	# Prevents exception (AttributeError: 'MoreComments' object has no attribute 'body')
	# For more info, go to (http://praw.readthedocs.io/en/latest/tutorials/comments.html) 
	submission.comments.replace_more(limit=0)
	
	for top_level_comment in submission.comments:
		if 'wikihow.com/' in top_level_comment.body:
			wikihowlink = True
			
	if wikihowlink == False:
		print(title)
		submission.reply(reminder) #replys to post
		time.sleep(5) # Prevents praw from detecting spam

if __name__ == "__main__":
	post_link_reminder_text = 'A friendly reminder to comment on this post the wikihow link from where this picture is from' 

	reddit = praw.Reddit(client_id='',
					client_secret= '',
					user_agent='')

	subreddit = reddit.subreddit('reddit_bot_tester')
	submissions = subreddit.new(limit=40)

	#gets url of newest posts on disneyvacations
	for submission in submissions:
		reddit_bot(submission.url, submission.title, post_link_reminder_text)
