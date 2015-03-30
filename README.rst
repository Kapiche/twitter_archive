Twitter Archive
===============
This tool archives tweets from twitter using a users' twitter credentials.

How it Works
------------
It's a Python web application that uses Django, Foundation, Knockout and Celery. It's deployed using Docker. Users
login using their twitter account and register searches with the tool. They are allowed a maximum of 3 searches and 
each search will collect a maximum of 100,000 tweets before stopping.

The twitter search API is hit every minute using a Celery task.
