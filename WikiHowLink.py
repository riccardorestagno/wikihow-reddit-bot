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

def connect_to_reddit():
	""" Connects the bot to the Reddit client"""
	
	reddit = praw.Reddit(client_id='',
			client_secret= '',
			user_agent='',
			username='',
			password='')
	return reddit

def mobile_to_desktop_link(mobile_link, post_reapproval):
	""" Converts moble link to desktop link"""
	
	desktop_link = mobile_link
	if '[' in desktop_link: #removes end bracket in hyperlink if user added any as well as any following text
		desktop_link = desktop_link.rsplit(')', 1)[0]
	desktop_link = desktop_link.rsplit('m.wikihow.', 1)[1] #removes hyperlinks
	desktop_link = 'https://www.wikihow.' + desktop_link.rsplit('?', 1)[0] #removes redirects
	desktop_link = desktop_link.rsplit('amp=', 1)[0] # removes 'amp' mobile tag
	desktop_link = desktop_link.split('%3F', 1)[0]
	desktop_link = desktop_link.split('%3f', 1)[0]
		
	if post_reapproval == True:	
		return 'Source: ' + desktop_link
	else:
		return 'Desktop Link: ' + desktop_link
	
def plaintext_link_maker(comment, post_reapproval=False):
	"""Converts wikihow hyperlink comment to plain text"""
	link_to_reply = comment.split('(', 1)[1]
	link_to_reply = link_to_reply.rsplit(')', 1)[0]
	if post_reapproval == True:	
		return 'Source: ' + desktop_link
	else:
		return 'Desktop Link: ' + desktop_link

def source_added_check(filepath):
	""" Checks if source was added by searching theorugh all unread inbox replies for a wikihow link
	If wikihow link was provided, remove parent comment and user comment, and approve the post while adding the users comment as a top-level comment to the post"""

	wikihow_domains = [ 'wikihow.com/', 'wikihow.mom/', 'wikihow.life/', 'wikihow.pet/', 'wikihow.fitness/'] # Different possible wikihow domains
	
	reddit = connect_to_reddit()
						
	bot_inbox = reddit.inbox.unread(limit=None) #only checks unread messages
	unread_messages = []
	
	for message in bot_inbox:
		if any(urls in message.body for urls in wikihow_domains) and message.submission.banned_by == "WikiHowLinkBot": #checks if reply contains a wikihow url
			
			try:
				message.parent().mod.remove() #deletes the bots comment
				message.mod.remove() #deletes user comment
			except AttributeError: #Error when checking DMs
				reddit.inbox.mark_read([message])
				continue
				
			if 'm.wikihow.' in message.body: #If mobile link is given, convert mobile to desktop link
				message.submission.reply(mobile_to_desktop_link(message.body, post_reapproval = True)) #replies to post with wikihow source link provided (adjusted for mobile links)
				with open(filepath, 'a') as outputfile:
						outputfile.writelines("Desktop link added - " + message.submission.title + " (www.reddit.com" + message.submission.permalink + ")\n")
			elif '](' in message.body:
				message.submission.reply(plaintext_link_maker(message.body, post_reapproval=True))
			else:
				message.submission.reply('Source: ' + message.body) #replies to post with wikihow source link provided
			message.submission.mod.approve() #approves the post
			with open(filepath, 'a') as outputfile:
				outputfile.writelines("Post RE-APPROVED - " + message.submission.title + " (www.reddit.com" + message.submission.permalink + ")\n")
			
		unread_messages.append(message) #creates a list of all unread messages
		
	reddit.inbox.mark_read(unread_messages)	#marks all checked messages as read
	
def comment_on_post(link, title, reminder, filepath):
	"""If post was made longer than 10 minutes ago, module checks if wikihow link is a top-level comment
If true, post is skipped. If false, comment is made on post, then another definition is called to sticky and delete post"""
	
	reddit = connect_to_reddit()
				
	wikihow_domains = [ 'wikihow.com/', 'wikihow.mom/', 'wikihow.life/', 'wikihow.pet/', 'wikihow.fitness/'] # Different possible wikihow domains
	disneyvacation_mods = ['DaemonXI', 'Xalaxis', 'sloth_on_meth', 'Improbably_wrong', 'WikiHowLinkBot']
	submission = reddit.submission(url = 'https://www.reddit.com' + link)
	wikihowlink = False

	#Checks if post has meta tag
	try:
		if (submission.link_flair_text.lower() == 'meta' and submission.domain.startswith('self.')) or submission.author.name in disneyvacation_mods::
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
			if any(urls in top_level_comment.body for urls in wikihow_domains) or any(mods == top_level_comment.author.name for mods in disneyvacation_mods):
				wikihowlink = True
				for comment in top_level_comment.replies:# Checks if bot already replied with a desktop link
					if comment.author.name == 'WikiHowLinkBot':
						return
				if 'm.wikihow.' in top_level_comment.body: #If mobile link is given, convert mobile to desktop link					
					top_level_comment.reply(mobile_to_desktop_link(top_level_comment.body, post_reapproval = False)) #replys with desktop link
						
				elif '](' in top_level_comment.body:
					top_level_comment.reply(plaintext_link_maker(top_level_comment.body))
				break
			
	if wikihowlink == False:
		submission.reply('Hey /u/' + submission.author.name + " ." + reminder).mod.distinguish(how='yes', sticky=True) #replys to post and stickies the reply + distinguish
		with open(filepath, 'a') as outputfile:
			outputfile.writelines("Post FAILED - " + title + " (www.reddit.com" + link + ")\n")
		time.sleep(3) # Prevents praw from detecting spam
		submission.mod.remove() #deletes the post	
	else:
		with open(filepath, 'a') as outputfile:
			outputfile.writelines("Post PASSED - " + title + " (WikiHow link)" + "\n")
if __name__ == "__main__":
	filepath = r"C:\Users\......\WikiHowBotLog.txt"
	post_link_reminder_text = """ The mod team at /r/disneyvacation thanks you for your submission, however it has been removed for the following reason:  

Rule 2: All posts must provide the source WikiHow article as a link in the comments.

Please reply to THIS COMMENT with the RAW source article (no hyperlink or any other text), and your post will be approved within at most 10 minutes.

If your post was related to internal discussion, please flair your post with the 'Meta' tag (Rule 6)"""

	reddit = connect_to_reddit()

	subreddit = reddit.subreddit('disneyvacation')
	submissions = subreddit.new(limit=50)

	#gets url of newest posts on disneyvacation
	for submission in submissions:
		#Goes to next loop iteration if post was made less than 10 minutes ago
		if minutes_posted(submission) < 10:
			continue
			
		#Loop ends if post was made longer than 21 minutes ago
		if minutes_posted(submission) > 21:
			break	
			
		comment_on_post(submission.permalink, submission.title, post_link_reminder_text, filepath)

	source_added_check(filepath)
