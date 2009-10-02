#!/usr/bin/python
from __future__ import with_statement
import os
import twitter
import simplejson

config_file = os.path.expanduser('~/.tadtwit.json')
state_file = os.path.expanduser('~/.tadtwit.state')

with open(config_file) as f:
    config = simplejson.load(f)

allowed_users = config.get('users', [])
if not allowed_users:
    print >> sys.stderr, 'No allowed users listed in %s!' % config_file
    sys.exit(1)

username = config['username']
api = twitter.Api(username=username, password=config['password'])

if not os.path.exists(state_file):
    state = []
else:
    with open(state_file) as f:
        state = simplejson.load(f)

username_prefix = len('@%s ' % username)

try:
    for reply in api.GetReplies():
        if (reply.id in state or
            reply.user.screen_name == username or
            reply.user.screen_name not in config['users'] or
            not reply.text.startswith('@%s' % username) and
            not reply.text.endswith('@%s' % username)):

            if reply.id not in state:
                state.append(reply.id)
            continue

        suffix = ' from @%s' % reply.user.screen_name

        if reply.text.endswith('@%s' % username):
            msg = reply.text[:-username_prefix]
        else:
            msg = reply.text[username_prefix:]

        if len(msg + suffix) > 140:
            msg = msg[:140-len(suffix)] + '...'

        state.append(reply.id)

        msg = msg + suffix
        api.PostUpdate(msg)
except:
    raise
finally:
    with open(state_file, 'w') as f:
        simplejson.dump(state, f)
