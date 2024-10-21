# 44-Control Firewatch Automated Monitoring And Alert Bot
This is a Python-powered automated fire alert monitoring bot that tracks the 44-control.net website for fire alerts and sends telegram alerts upon new incidents identified

# How does it work?
This checks the website https://firewatch.44-control.net/ and keeps a log file named incidents.log that helps to track which incident is found as new and alerts as soon as a new incident is recorded.

# Requirements
Install Python with add to path enabled and then open the terminal to install the library using the command below:
<pre>pip install requests</pre>
Then run the script and it will monitor the website. Before running it, configure the telegram bot API key and chat ID on top of the Python script.
