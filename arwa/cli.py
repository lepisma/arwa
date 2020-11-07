"""
arwa

Usage:
  arwa slack bulk-invite <channel-name>
  arwa slack export conversations --conversation-id=<conversation-id> --output-jsonl=<output-jsonl>
  arwa slack export users --output-json=output-json
  arwa slack export usergroup-emails <user-group-name>
  arwa slack post image <image-path> --channel-name=<channel-name> [--text=<text>]
  arwa calendar hours <email-id>
"""

import datetime
import json
import os

import jsonlines
import slack
from docopt import docopt
from tabulate import tabulate
from tqdm import tqdm

from arwa import __version__
from arwa.calendar_utils import (calculate_time_spent, get_last_sunday,
                                 parse_google_calendar)
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

            if args["conversations"]:
                conversation_id = args["--conversation-id"]
                with jsonlines.open(args["--output-jsonl"], mode="w") as fp:
                    bar = tqdm()
                    for batch in get_message_batches(conversation_id, client):
                        fp.write_all(batch)
                        bar.update(len(batch))

            elif args["users"]:
                with open(args["--output-json"], "w") as fp:
                    json.dump(client.users_list()["members"], fp)

        elif args["post"]:
            client = slack.WebClient(os.environ["SLACK_BOT_USER_TOKEN"])

            if args["image"]:
                client.files_upload(
                    channels=args["--channel-name"],
                    file=args["<image-path>"],
                    initial_comment=(args["--text"] or "")
                )

    if args["calendar"]:
        email_id = args["<email-id>"]
        n_prev = 5
        n_next = 3

        anchor_dt = get_last_sunday()
        delta = datetime.timedelta(days=7)

        start_dts = [anchor_dt - (delta * i) for i in range(n_prev, -(n_next + 1), -1)]

        table = []
        for start_time in start_dts:
            end_time = start_time + delta
            evs = parse_google_calendar(email_id, start_time, end_time)
            hours = calculate_time_spent(evs) / 60
            table.append((start_time.date(), end_time.date(), hours))

        print(tabulate(
            table,
            headers=["Start", "End", "Number of hours"],
            tablefmt="fancy_grid"
        ))
