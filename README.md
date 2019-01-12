DisneyVacation Wikihow Bot
=========================

Description
===========

Monitors new posts on /r/disneyvacation and takes moderating action if rule violations are found.


Dependencies
=================
Supported Python versions: 3.4.0+ 

PRAW (https://github.com/praw-dev/praw)


Script Functionality
=====================

This bot searches through all new posts in www.reddit.com/r/disneyvacation made within tha past 5-10 minutes. If a post was made and the wikihow link source of the image posted by the user was not provided, then remove the post and wait for the users reply with the source link to re-approve the post.

BETA: Use www.karmadecay.com to check if there are any post duplicates. Note: KarmaDecay is not always reliable at reverse image searching so other means may be needed to solve this issue. 

Credit for KarmaDecay API goes to https://github.com/ethanhjennings/karmadecay-api. Modifications were made to the API by me that are not included in the API as found in the link above (as of January 11, 2019) thus why the API is included in this repository.
