# SparkPost Traffic Generator

A simple app, which can easily be deployed to Heroku, to generate random traffic through your SparkPost
account towards the "bouncy sink".  Note that all sent messages count towards your account usage.

Environment variables (which are configured via Heroku's start dialog):

```txt
SPARKPOST_HOST (optional)
    The URL of the SparkPost API service you're using. Defaults to https://api.sparkpost.com.

SPARKPOST_API_KEY
    API key on your SparkPost account, with transmission rights.

MESSAGES_PER_MINUTE_LOW
    Lowest number of messages to be sent per minute, from 0 to 10000

MESSAGES_PER_MINUTE_HIGH
    Highest number of messages to be sent per minute, from 0 to 10000

FROM_EMAIL
    FROM address belonging to a valid sending domain on your account.  e.g. fred@example.com
```

## Deploying to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

- Enter values for the above environment variables
- After a short time Heroku should report `Build finished`

### Running periodically with the Heroku Scheduler

This app formerly used `time.sleep()` for built-in scheduling, but that doesn't play nicely with
Heroku's [free dyno hours](https://devcenter.heroku.com/articles/free-dyno-hours#consuming-hours) allowance.
The worker-thread gets killed by Heroku after 30 minutes.

Instead, use the built-in Heroku Scheduler:

- Go to Manage App / Add Ons.  Search for scheduler, choose Heroku Scheduler.  Provision / Free.
- Click next to clock icon.  Add New Job.  In command box, type `./sparkpost-traffic-gen.py`
- Choose Schedule Every 10 Minutes.  Next due time is displayed.
- To monitor, go to App Settings / More / View Log file