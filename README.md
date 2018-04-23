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

- Messages are sent every minute (no longer using Heroku 10-minute scheduler)
- To monitor, go to App Settings / More / View Log file
