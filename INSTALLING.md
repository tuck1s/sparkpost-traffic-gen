# Installing & internal documentation

The worker thread code `sparkpost-traffic-gen.py`is a simple Python script that could be hosted on any platform.

The `webReporter.py` app depends on the Flask framework (and Gunicorn, or other suitable app server). You could consider this
part optional if you are self-hosting.

# Heroku command-line deployment

This is done for you if you use the "deploy" button. You can also manually install from a repo fork using the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli):

```
brew install heroku/brew/heroku         # only if you don't already have the CLI
heroku login

git clone https://github.com/tuck1s/sparkpost-traffic-gen.git       # this project
cd sparkpost-traffic-gen
heroku apps:create my-traffic-gen
heroku git:remote -a my-traffic-gen
git push heroku master

heroku addons:create scheduler
heroku addons:create heroku-redis
```
Now set the remote environment variables for the Heroku app, for example in a bash script.
You can skip setting SPARKPOST_HOST when using the standard US service.
```
#!/bin/bash
heroku config:set SPARKPOST_API_KEY=<<< YOUR API KEY HERE >>>\
MESSAGES_PER_MINUTE_LOW=0 \
MESSAGES_PER_MINUTE_HIGH=1 \
FROM_EMAIL=test@yourdomain.com \
SPARKPOST_HOST=api.eu.sparkpost.com/api/v1/ \
RESULTS_KEY=$RANDOM$RANDOM$RANDOM$RANDOM
```
Run your script. then you'll need to open and configure the scheduler as usual
```
heroku addons:open SCHEDULER
```

### Why redis is used for worker/web communication

Heroku runs the worker thread and web thread in identical-looking, but separate, non-communicating filesystem spaces.
Temp files therefore don't work to communicate metrics from worker to web thread.
Instead, [Redis](https://redis.io/topics/quickstart) is used to communicate metrics to the `webReporter.py` app.

Your Heroku account provides you with a single Redis namespace. Because you might want to run more than one traffic
generator (e.g. to generate traffic from different subaccounts), the app relies on a randomised `RESULTS_KEY` environment var.

# Other platforms

## Amazon EC2 Linux

Start an instance (t2.micro size is fine). Allow ssh and http in the instance's security group.

**Caveats**:
- These instructions set up a plain (http) server for your results page, which will be visible to the world
- Check your firewall settings!
- These instructions serve port 80 directly via the `Gunicorn` app server. Long-term setups should follow the advice to use a proxy - see http://docs.gunicorn.org/en/stable/deploy.html?highlight=nginx

Get an up-to-date Python interpreter (and `pip`) and git.  
```
sudo su -
yum install -y python36 python36-pip git
```

Set path for `pip` by editing .profile and adding
```
export PATH=/usr/local/bin:$PATH
```

Upgrade pip to latest version
```
pip install --upgrade pip
```

Get web application server and redis-py library, SparkPost library:
```
pip install gunicorn redis sparkpost flask
```

Get redis - see https://redis.io/topics/quickstart and https://unix.stackexchange.com/a/108311
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
If using EC2 Linux,[this guide](https://medium.com/@andrewcbass/install-redis-v3-2-on-aws-ec2-instance-93259d40a3ce)
will help - start from the "Make directories & copy files" stage onwards.

Check you've started the `redis` service using this command. It should say PONG back.
```
redis-cli ping
```

You can now leave root privilege.  Get the traffic generator, and check it runs:
```
git clone https://github.com/tuck1s/sparkpost-traffic-gen.git
cd sparkpost-traffic-gen
./sparkpost-traffic-gen.py
Invalid MESSAGES_PER_MINUTE_LOW setting - must be number 1 to 10000
```

Expect **an error message** as this stage as we don't have env vars set up yet.<br>Now set these up in a shell script, e.g. 
`vim tg.sh`
```
#!/bin/bash
# export SPARKPOST_HOST=https://api.sparkpost.com
export SPARKPOST_API_KEY=<YOUR API KEY>
export MESSAGES_PER_MINUTE_LOW=0
export MESSAGES_PER_MINUTE_HIGH=1
export FROM_EMAIL=test.ec2@email-eu.thetucks.com
export RESULTS_KEY=$RANDOM$RANDOM$RANDOM$RANDOM
```
then
```
chmod +x tg.sh 
```

Start the `gunicorn` web application server to run in the background with thes env vars (will survive logout, but not a reboot).
Bind onto all interfaces, port 80. The web app depends on the `RESULTS_KEY` env var being set, as you start the server, otherwise
traffic won't show on the status page!

```
. tg.sh; sudo -E /usr/local/bin/gunicorn webReporter:app --bind=0.0.0.0:80 --access-logfile gunicorn.log --daemon
```

Open results page in a browser (using http). You should see a page appear. If not, then
check your EC2 security group (firewall) settings and `iptables` settings.

Check the generator runs interactively:
```
./sparkpost-traffic-gen.py
Opened connection to https://api.sparkpost.com
Sending to 38 recipients
  To    38 recipients | campaign "sparkpost-traffic-gen Todays_Sales" | OK - in 0.659 seconds
Done in 0.7s.
Results written to redis
```

Add the following line to the end of your `tg.sh`:
```
./sparkpost-traffic-gen.py >>sparkpost-traffic-gen.log 2>&1
```

Run `crontab -e` and add the following:
```
#
# The paths below assume you have a copy of the project installed in the shown directory, adjust if this is not the case
#
# This executes the script at every 10th minute

*/10 * * * * cd sparkpost-traffic-gen; bash tg.sh
```

Monitor your web page, and the logfile. If SparkPost returns errors, these are displayed.  For example, you might see the following, if your account
limit is reached:
```
Opened connection to https://api.eu.sparkpost.com
Sending to 6 recipients
  To     6 recipients | campaign "sparkpost-traffic-gen Newsletter" | error code 420 : ['Exceed Sending Limit (daily) Code: 2102 Description: none \n']
Done in 0.6s.
Results written to redis
```

Gunicorn access logfile looks like:
```
82.10.62.100 - - [24/May/2018:21:20:58 +0000] "GET / HTTP/1.1" 200 1864 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
82.10.62.100 - - [24/May/2018:21:20:59 +0000] "GET /favicon.ico HTTP/1.1" 200 - "http://54.202.195.231/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
```

## AWS Lambda

Coming soon

## Serverless.com

Coming soon

## Azure Functions

Coming soon
