"""
arwa

Usage:
  arwa slack bulk-invite <channel-name>
  arwa slack export <conversation-id> --output-jsonl=<output-jsonl>

Arguments:
  <conversation-id>       Conversation id. This can be channel id, dm id or anything
                          that behaves like a conversation in slack terminology.
"""

import os

import jsonlines
from docopt import docopt
from tqdm import tqdm

import slack
from arwa import __version__
from arwa.slack_utils import (channel_name_to_id, get_message_batches,
                              list_users)


def main():
    args = docopt(__doc__, version=__version__)

    if args["slack"]:
        if args["bulk-invite"]:
            client = slack.WebClient(os.environ["SLACK_BOT_USER_TOKEN"])
            channel_id = channel_name_to_id(args["<channel-name>"], client)
            users = list_users(client)

            print(f"Inviting {len(users)} to {args['<channel-name>']}")

            client.conversations_invite(channel=channel_id, users=[u.id for u in users])
        elif args["export"]:
            client = slack.WebClient(os.environ["SLACK_USER_TOKEN"])

            with jsonlines.open(args["--output-jsonl"], mode="w") as fp:
                bar = tqdm()
                for batch in get_message_batches(args["<conversation-id>"], client):
                    fp.write_all(batch)
                    bar.update(len(batch))
        else:
            raise NotImplementedError()
    else:
        raise NotImplementedError()
