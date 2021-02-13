"""
arwa

Usage:
  arwa slack bulk-invite <channel-name>
  arwa slack export conversations --conversation-id=<conversation-id> --output-jsonl=<output-jsonl>
  arwa slack export users --output-json=output-json
  arwa slack export usergroup-emails <user-group-name>
  arwa slack post image <image-path> --channel-name=<channel-name> [--text=<text>]
  arwa slack post --text-file=<text-file> --channel-name=<channel-name>
  arwa slack post bulk --template-file=<template-file> --bulk-post-config=<bulk-post-config>
  arwa calendar hours <email-id>

Options:
  --bulk-post-config=<bulk-post-config>       Yaml config for bulk text.
"""

import dataclasses
import datetime
import json
import os

import jinja2
import jsonlines
import slack
import yaml
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
                    users = list_users(client)
                    json.dump([dataclasses.asdict(u) for u in users], fp)

        elif args["post"]:
            client = slack.WebClient(os.environ["SLACK_BOT_USER_TOKEN"])

            if args["image"]:
                client.files_upload(
                    channels=args["--channel-name"],
                    file=args["<image-path>"],
                    initial_comment=(args["--text"] or "")
                )

            if args["--text-file"]:
                with open(args["--text-file"]) as fp:
                    text = fp.read()

                channel_id = channel_name_to_id(args["--channel-name"], client)
                client.chat_postMessage(
                    channel=channel_id,
                    text="",
                    blocks=[{
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": text
                        }
                    }]
                )

            if args["bulk"]:
                with open(args["--template-file"]) as fp:
                    template = jinja2.Template(fp.read())

                with open(args["--bulk-post-config"]) as fp:
                    bulk_items = yaml.safe_load(fp)

                for item in tqdm(bulk_items):
                    variables = item.get("variables", {})
                    response = client.conversations_open(users=item["user-ids"])
                    client.chat_postMessage(channel=response["channel"]["id"], text=template.render(**variables))

    if args["calendar"]:
        email_id = args["<email-id>"]
        n_prev = n_next = 5

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
