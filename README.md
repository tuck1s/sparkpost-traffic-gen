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

Instead, this project installs the addon [Heroku Scheduler](https://devcenter.heroku.com/articles/scheduler), but you
need to manually configure it:

- Click next to clock icon.  Add New Job.  In command box, type `./sparkpost-traffic-gen.py`
- Choose Schedule Every 10 Minutes.  Next due time is displayed.

### Monitoring

- Click Open App. Results appear once scheduler has run at least once.  Does _not_ display your API key as it's a public page.
- For detailed logs, go to App Settings / More / View Log file.
- A JSON-format reporting endpoint is also available (URL ending in `/json`).

### Changing settings

- While running, you can change values in the Settings / Reveal Config Vars page.  Changes are displayed on Open App screen immediately and affect traffic on the next scheduled run. No need to restart dynos.
