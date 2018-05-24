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

Start an instance (t2.micro size is fine). Allow ssh and http in the instance's security group.
**Caveat**: these instructions set up a plain (http) server for your results page, which will be visible to the world.

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
If using EC2 Linux, the later stages of [this guide](https://medium.com/@andrewcbass/install-redis-v3-2-on-aws-ec2-instance-93259d40a3ce)
will help.

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

Expect an error message as we don't have env vars set up yet.  Now set these up in a shell script, e.g. 
`vim tg.sh`
```
#!/bin/bash
# export SPARKPOST_HOST=https://api.sparkpost.com
export SPARKPOST_API_KEY=<YOUR API KEY>
export MESSAGES_PER_MINUTE_LOW=0
export MESSAGES_PER_MINUTE_HIGH=1
export FROM_EMAIL=test.ec2@email-eu.thetucks.com
export RESULTS_KEY=abcd
```

Load the variables into your environment:
```
chmod +x tg.sh 
. tg.sh 
```

Start the `gunicorn` web application server to run in the background (will survive logout, but not a reboot).
Bind onto all interfaces, port 80
```
sudo -E /usr/local/bin/gunicorn webReporter:app --bind=0.0.0.0:80 &
```

Open your results page in a browser (using http, not https at this stage). You should see a page appear. If not, then
check your firewall settings and `iptables` settings.

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

#
# The paths below assume you have a copy of the project installed via git in your home directory, adjust if this is not the case
#
# This executes the script at every 10th minute

*/10 * * * * cd sparkpost-traffic-gen; bash tg.sh
```

Monitor your web page, and optionally monitor the logfile. If SparkPost returns errors, these are displayed.  For example, you might see
```
Opened connection to https://api.eu.sparkpost.com
Sending to 6 recipients
  To     6 recipients | campaign "sparkpost-traffic-gen Newsletter" | error code 420 : ['Exceed Sending Limit (daily) Code: 2102 Description: none \n']
Done in 0.6s.
Results written to redis
```

TODO:

## AWS Lambda

Coming soon

## Serverless.com

Coming soon