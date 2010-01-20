#!/usr/bin/python
# This code is public domain and can be freely used.
#
# This script echoes all replies it has received that are either
# prefixed or suffixed with @username
#
# Requirements:
# Python 2.5+
# python-twitter: http://code.google.com/p/python-twitter/
# simplejson: http://www.undefined.org/python/
#
# Short documentation:
#
# By default, tadtwit searches configuration files in directory
# ~/.tadtwit. The program uses two configuration files, a file named
# *state*, that remembers the tweets already tweeted and config, which
# contains the essential configuration of the program. The
# configuration directory can be overridden by environmental variable
# TADTWIT_DIR.
#
# State file TADTWIT_DIR/state is created by tadtwit. Config file is a
# JSON file in TADTWIT_DIR/config that contains following JSON:
#
# {
#   "username": "username",
#   "password": "mypassword",
#   "users": ["alloweduser1", "alloweduser2"]
# }
#
# "users" is a list of users whose tweets are allowed to be echoed
#
# To run just start the tadtwit.py.
#
# Protip: You might want to put this program to cron

from __future__ import with_statement
import os
import twitter
try:
    import json
except ImportError:
    import simplejson as json


if 'TADTWIT_DIR' not in os.environ:
    tadtwit_dir = os.path.expanduser('~/.tadtwit/')
else:
    tadtwit_dir = os.environ['TADTWIT_DIR']

config_file = os.path.join(tadtwit_dir, 'config')
state_file = os.path.join(tadtwit_dir, 'state')

with open(config_file) as f:
    config = simplejson.load(f)

allowed_users = config.get('users', [])
if not allowed_users:
    print >> sys.stderr, 'No allowed users listed in %s!' % config_file
    sys.exit(1)

username = config['username']
api = twitter.Api(username=username, password=config['password'])

if not os.path.exists(state_file):
    state = set()
else:
    with open(state_file) as f:
        state = set(json.load(f))

username_prefix = len('@%s ' % username)

try:
    for reply in api.GetReplies():
        if (reply.id in state or
            reply.user.screen_name == username or
            reply.user.screen_name not in config['users'] or
            not reply.text.startswith('@%s' % username) and
            not reply.text.endswith('@%s' % username)):

            state.add(reply.id)
            continue

        suffix = ' from @%s' % reply.user.screen_name

        if reply.text.endswith('@%s' % username):
            msg = reply.text[:-username_prefix]
        else:
            msg = reply.text[username_prefix:]

        if len(msg + suffix) > 140:
            msg = msg[:140-len(suffix)] + '...'

        state.add(reply.id)

        msg = msg + suffix
        api.PostUpdate(msg)
finally:
    with open(state_file, 'w') as f:
        json.dump(list(state), f)
