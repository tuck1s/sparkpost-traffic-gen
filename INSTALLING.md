# Installing & internal documentation

The worker thread code `sparkpost-traffic-gen.py`is a simple Python script that could be hosted on any platform.

The `webReporter.py` app depends on the Flask framework (and Gunicorn, or other suitable app server). You could consider this
part optional if you are self-hosting.

# Heroku

This is done for you if you use the "deploy" button. You can also manually install from a repo fork using the Heroku CLI.

Heroku runs the worker thread and web thread in identical-looking, but separate, non-communicating filesystem spaces.
Temp files therefore don't work to communicate metrics from worker to web thread.
Instead, [Redis](https://redis.io/topics/quickstart) is used to communicate metrics to the `webReporter.py` app.

Your Heroku account provides you with a single Redis namespace. Because you might want to run more than one traffic
generator (e.g. to generate traffic from different subaccounts), the app uses a randomised `RESULTS_KEY` environment var.

# Other platforms

## Linux

Coming soon

## AWS Lambda

Coming soon

## Serverless.com

Coming soon