"""
arwa

Usage:
  arwa slack bulk-invite <channel-name>
"""

import os

from docopt import docopt

import slack
from arwa import __version__
from arwa.slack_utils import channel_name_to_id, list_users


def main():
    args = docopt(__doc__, version=__version__)

    if args["slack"]:
        if args["bulk-invite"]:
            client = slack.WebClient(os.environ["SLACK_BOT_USER_TOKEN"])
            channel_id = channel_name_to_id(args["<channel-name>"], client)
            users = list_users(client)

            print(f"Inviting {len(users)} to {args['<channel-name>']}")

            client.conversations_invite(channel=channel_id, users=[u.id for u in users])
        else:
            raise NotImplementedError()
    else:
        raise NotImplementedError()
