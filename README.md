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

### Traffic handling
The `bouncy-sink` recipient domain responds to traffic according to a statistical model:

<img src="doc-img/bouncy-sink-statistical-model.svg"/>


### Monitoring

- Click Open App. Results appear once scheduler has run at least once.  Does _not_ display your API key as it's a public page.
- For detailed logs, go to App Settings / More / View Log file.
- A JSON-format reporting endpoint is also available (URL ending in `/json`).

### Changing settings

- While running, you can change values in the Settings / Reveal Config Vars page.  Changes are displayed on Open App screen immediately and affect traffic on the next scheduled run. No need to restart dynos.

### Hosting options

The worker thread code `sparkpost-traffic-gen.py`is a simple Python script that could be hosted on any platform.

Heroku runs the worker thread and web thread in identical-looking, but separate, non-communicating filesystem spaces.
Temp files therefore don't work to communicate metrics from worker to web thread.
Instead, [Redis](https://redis.io/topics/quickstart) is used to communicate metrics to the `webReporter.py` app.

Your Heroku account provides you with a single Redis namespace. Because you might want to run more than one traffic
generator (e.g. to generate traffic from different subaccounts), the app uses a randomised `RESULTS_KEY` environment var.

The `webReporter.py` app depends on the Flask framework (and Gunicorn, or other suitable app server). You could consider this
part optional if you are self-hosting.

### Changing settings in the code

If you wish to generate traffic going to some place other than the `bouncy-sink`, the code can easily be changed
[here](https://github.com/tuck1s/sparkpost-traffic-gen/blob/8b5761e0e52e94fe2ca76de654aef87c1d21050d/sparkpost-traffic-gen.py#L19).
Note that sending traffic to real ISP domains with fake addresses is likely to harm your [reputation](https://www.sparkpost.com/blog/email-reputation-matters/) - use with care.

You can also easily customise
- the metadata included with each recipient (Cities, Genders)
- The target link that will be clicked by the sink
- Campaign names
- Subject lines
- Link names (that appear in the SparkPost Engagement report, for example)
- `To` address prefix and name
- Default send interval that your scheduler is running to (used to translate the per-minute env var settings into numbers)
- API call batch size (chosen for efficiency)