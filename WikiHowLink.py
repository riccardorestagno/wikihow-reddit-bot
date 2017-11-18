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

def source_added_check(filepath):
	wikihow_domains = [ 'wikihow.com/','wikihow.mom/', 'wikihow.life/', 'wikihow.pet/']	# Different possible wikihow domains
	
	reddit = praw.Reddit(client_id='',
			client_secret= '',
			user_agent='',
			username='',
			password='')
						
	bot_inbox = reddit.inbox.unread(limit=None) #only checks unread messages
	unread_messages = []
	
	for message in bot_inbox:
		if any(urls in message.body for urls in wikihow_domains): #checks if reply contains a wikihow url
			message.parent().mod.remove() #deletes the bots comment
			message.mod.remove() #deletes user comment
			message.submission.reply(message.body) #replies to post with wikihow source link
			message.submission.mod.approve() #approves the post
			with open(filepath, 'a') as outputfile:
				outputfile.writelines("Post RE-APPROVED - " + message.submission.title + " (www.reddit.com" + message.submission.permalink + ")\n")
			
		unread_messages.append(message) #creates a list of all unread messages
		
	reddit.inbox.mark_read(unread_messages)	#marks all checked messages as read
	
def comment_on_post(link, title, reminder, filepath):
	"""If post was made longer than 10 minutes ago, module checks if wikihow link is a top-level comment
If true, post is skipped. If false, comment is made on post, then another definition is called to sticky and delete post"""
	reddit = praw.Reddit(client_id='',
					client_secret= '',
					user_agent='',
					username='',
					password='')
				
	wikihow_domains = [ 'wikihow.com/','wikihow.mom/','wikihow.life/','wikihow.pet/']	# Different possible wikihow domains
	disneyvacation_mods = ['DaemonXI', 'Xalaxis', 'UnculturedLout', 'sloth_on_meth', 'AugustusTheWolf', 'Improbably_wrong', 'WikiHowLinkBot']
	submission = reddit.submission(url = 'https://www.reddit.com' + link)
	wikihowlink = False

	#Checks if post has meta tag
	try:
		if submission.link_flair_text.lower() == 'meta':
			wikihowlink = True
			with open(filepath, 'a') as outputfile:
				outputfile.writelines("Post PASSED - " + title + " (Meta Tag)" + "\n")
			return
	except AttributeError:
		pass

	if wikihowlink == False:	
		submission.comments.replace_more(limit=0) #Prevents AttributeError exception
		#searches through top-level comments and checks if there is a wikihow link in them
		for top_level_comment in submission.comments:
			# Checks if any wikihow domains are linked in the comments or if mods already replied to post
			if any(urls in top_level_comment.body for urls in wikihow_domains) or any(mods == top_level_comment.author for mods in disneyvacation_mods):
				wikihowlink = True
				break
			
	if wikihowlink == False:
		print(title)
		print('https://www.reddit.com' + link)
		# webbrowser.open_new_tab('https://www.reddit.com' + link)
		submission.reply('Hey /u/' + submission.author.name + " ." + reminder).mod.distinguish(how='yes', sticky=True) #replys to post and stickies the reply + distinguish
		print("Reply + sticky and distinguish done")
		with open(filepath, 'a') as outputfile:
			outputfile.writelines("Post FAILED - " + title + " (www.reddit.com" + link + ")\n")
		time.sleep(3) # Prevents praw from detecting spam
		submission.mod.remove() #deletes the post	
		print("Delete done")
		# time.sleep(20) # Gives time to check the bot is working
	else:
		with open(filepath, 'a') as outputfile:
			outputfile.writelines("Post PASSED - " + title + " (WikiHow link)" + "\n")
if __name__ == "__main__":
	filepath = r"C:\Users\......\WikiHowBotLog.txt"
	post_link_reminder_text = """ The mod team at /r/disneyvacation thanks you for your submission, however it has been removed for the following reason:  

Rule 2: All posts must provide the source WikiHow article as a link in the comments.

Please reply to THIS COMMENT with the RAW source article (no hyperlink or any other text), and your post will be approved within at most 10 minutes.

If your post was related to internal discussion, please flair your post with the 'Meta' tag (Rule 6)"""

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
			
		#Loop ends if post was made longer than 22 minutes ago
		if minutes_posted(submission) > 22:
			break	
			
		comment_on_post(submission.permalink, submission.title, post_link_reminder_text, filepath)

	source_added_check(filepath)
