# SparkPost Traffic Generator

A simple app, which can easily be deployed to Heroku.

Environment variables (which are configured easily via Heroku's start dialog):

```txt
SPARKPOST_HOST (optional)
    The URL of the SparkPost API service you're using. Defaults to https://api.sparkpost.com.

SPARKPOST_API_KEY
    API key on your SparkPost account, with transmission rights.

MESSAGES_PER_MINUTE
    Messages to be sent per minute, from 1 to 10000

FROM_EMAIL
    FROM address belonging to a valid sending domain on your account.  e.g. fred@example.com
```

## Deploying to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
