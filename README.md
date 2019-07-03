# SudoLogic
A listener to SumoLogic that propagates alerts to Slack.

### Sumosv
This is a Flask application that accepts connections directly from SumoLogic. It uses RedisQueue to propagate the message, passing tasks to 'fire-and-forget' workers that send Slack alerts using Canary.

It must be run to ensure functionality.

### Canary
This file is both a 'library' for the workers to interface with the Slack API with, and its own script. When run, it listens to all Slack channels the bot is in and responds to commands.

It is not necessary to run this for critical functionality, but it is recommended if you do not wish to manually alter the config file to set authorised channels for alert propagation.

## **Installation and Use**

### Flask Application
Use your preferred deployment method for the Flask application. It must be run on port 80, and SumoLogic must direct log outputs to its IP address, port 80, with the url extension '/alert'.

### Canary
Get the token for your desired bot from Slack's application interface. Set it as an environmental variable called 'SLACK_BOT_TOKEN' in Canary's environment. If you so wish, run canary.py as a test; to get a list of commands, PM it or mention it in a channel with the keyword 'help'.

### Redis and RQ
Have a terminal running redis-server to keep the queue intact. To activate the first worker, in a terminal type ```rq worker default```.

### Testing
To run the full unit test battery, run ```python3 -m unittest``` in a terminal from the project directory. Check test_script.py for details on the unit tests present.