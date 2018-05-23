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

## Amazon EC2 Linux

`python3` (which also installs `pip`), git.  Upgrade pip to latest version
```
sudo su -
yum install -y python36 git
pip install --upgrade pip
```

Set path to `pip` by editing .profile and adding
```
export PATH=/usr/local/bin:$PATH
```

Web application server and redis-py library, SparkPost library:
```
pip install gunicorn redis sparkpost flask
```

Install redis https://redis.io/topics/quickstart
```
yum install -y gcc
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable/deps
make hiredis jemalloc linenoise lua geohash-int
cd ..
make install
yum install -y tcl
make test
```
Follow the latter stages of this guide:
https://medium.com/@andrewcbass/install-redis-v3-2-on-aws-ec2-instance-93259d40a3ce

Check you've started the `redis` service using this command. It should say PONG back.

```
redis-cli ping
```

You can now leave sudo privilege.  Get the traffic generator, and check it runs
```
git clone https://github.com/tuck1s/sparkpost-traffic-gen.git
cd sparkpost-traffic-gen
./sparkpost-traffic-gen.py
Invalid MESSAGES_PER_MINUTE_LOW setting - must be number 1 to 10000
```

Expect an error message as we don't have env vars set up yet.  Now set these up in a shell script:

vim tg.sh
```
#!/bin/bash
# export SPARKPOST_HOST=https://api.sparkpost.com
export SPARKPOST_API_KEY=<YOUR API KEY>
export MESSAGES_PER_MINUTE_LOW=0
export MESSAGES_PER_MINUTE_HIGH=10
export FROM_EMAIL=test.ec2@email-eu.thetucks.com
export RESULTS_KEY=abcd
```

Load the variables into your environment
```
chmod +x tg.sh 
. tg.sh 
```

Check the generator runs OK interactively:
```
./sparkpost-traffic-gen.py
Opened connection to https://api.sparkpost.com
Sending to 38 recipients
  To    38 recipients | campaign "sparkpost-traffic-gen Todays_Sales" | OK - in 0.659 seconds
Done in 0.7s.
Results written to redis
```

TODO:
- periodic running via cron
- web service

## AWS Lambda

Coming soon

## Serverless.com

Coming soon