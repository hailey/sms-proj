# sms-proj
This is a project to handle sending and receiving stuff for flowroute

# Requirements
Install the requirements by running
> pip3 install -r requirements.txt

This requires a flowroute account. It uses google to authenticate. But I might add twillo support later.

# App Server
App runs via the following command.
> gunicorn3 smsproj:app

This will run and listen on a port, probably port 8000 as its default as a daemon.
