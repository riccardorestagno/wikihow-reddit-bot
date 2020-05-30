DisneyVacation wikiHow Bot
=========================

Description
===========

Monitors new posts on /r/disneyvacation to ensure all post requirements are met.


Dependencies
=================
Supported Python versions: 3.6.0+ 

- PRAW
- BeautifulSoup4
- Requests


Script Functionality
=====================

This bot searches through all new posts in www.reddit.com/r/disneyvacation. If a post was made and a plain-text desktop link source of the wikiHow image posted by the user was not provided, action is taken to ensure the link is available in the post comments.