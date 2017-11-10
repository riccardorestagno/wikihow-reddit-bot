import smtplib
from datetime import date, timedelta

def send_email(body, date):

	email_server = smtplib.SMTP('smtp.gmail.com', 587)
	email_server.ehlo()

	email_server.starttls()

	email_server.login('', '')

	email_server.sendmail('From: ', 'To: ',\
	'Subject: WikiHowLink Bot Log for Week of ' + date + '\n' + body)

	email_server.quit()

def clear_textfile(filepath):
	i=0
	file = open(filepath,"r")
	lines = file.readlines()
	file.close()

	with open(filepath, 'w') as clearfile:
		for line in lines:
			clearfile.write(line)
			i+=1
			if i == 2:
				break
			
if __name__ == '__main__':
	filepath = r"C:\Users\....\WikiHowBotLog.txt"
	
	last_week = date.today() - timedelta(7)
	date_formatted = last_week.strftime("%Y-%m-%d")

	with open(filepath, 'r') as output:
		email_body = output.read()
		
	send_email(email_body, date_formatted)
	clear_textfile(filepath)
