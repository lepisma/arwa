"""
arwa

Usage:
  arwa slack bulk-invite <channel-name>
  arwa slack export conversations --conversation-id=<conversation-id> --output-jsonl=<output-jsonl>
  arwa slack export users --output-json=output-json
  arwa slack post --text-file=<text-file> --channel-name=<channel-name>
  arwa slack post bulk --template-file=<template-file> --bulk-post-config=<bulk-post-config>
  arwa calendar report <email-id> [--n-next=<n-next] [--n-prev=<n-prev>]
  arwa calendar export --users-json=<users-json> --output-pickle=<output-pickle> [--n-next=<n-next] [--n-prev=<n-prev>]

Options:
  --bulk-post-config=<bulk-post-config>       Yaml config for bulk text.
  --n-next=<n-next>                           Number of future weeks to look in [default: 2].
  --n-prev=<n-prev>                           Number of past weeks to look in [default: 2].
"""

import dataclasses
import datetime
import json
import os
import pickle

import jinja2
import jsonlines
import slack
import yaml
from docopt import docopt
from pydash import py_
from tabulate import tabulate
from tqdm import tqdm

from arwa import __version__
from arwa.calendar_utils import (get_last_day_of_month, get_last_sunday,
                                 parse_google_calendar, report_events_summary)
from arwa.slack_utils import (channel_name_to_id, get_message_batches,
                              list_users)
from arwa.types import SlackUser


def main():
    args = docopt(__doc__, version=__version__)

    if args["slack"]:
        if args["bulk-invite"]:
            client = slack.WebClient(os.environ["SLACK_BOT_USER_TOKEN"])
            channel_id = channel_name_to_id(args["<channel-name>"], client)
            users = list_users(client)

            print(f"Inviting {len(users)} to {args['<channel-name>']}")

            for u in tqdm(users):
                try:
                    client.conversations_invite(channel=channel_id, users=[u.id])
                except Exception as e:
                    print(e)

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
        if args["report"]:
            email_id = args["<email-id>"]
            n_prev = int(args["--n-prev"])
            n_next = int(args["--n-next"])

            anchor_dt = get_last_sunday()
            delta = datetime.timedelta(days=7)

            start_dts = [anchor_dt - (delta * i) for i in range(n_prev, -(n_next + 1), -1)]

            headers = ["Start", "End", "Total Hours", "Personal Block", "External", "1:1", "Rest"]

            table = []
            for start_time in start_dts:
                end_time = start_time + delta
                evs = parse_google_calendar(email_id, start_time, end_time)
                summary = report_events_summary(evs)

                table.append((
                    start_time.date(), end_time.date(),
                    summary["total"], summary["personal"], summary["external"], summary["1:1"], summary["rest"]
                ))

            print(tabulate(
                table,
                headers=headers,
                tablefmt="fancy_grid"
            ))

        elif args["export"]:
            with open(args["--users-json"]) as fp:
                users = [SlackUser(**it) for it in json.load(fp)]

            n_prev = int(args["--n-prev"])
            n_next = int(args["--n-next"])

            today = datetime.datetime.today()
            anchor_dt = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # First day of the month

            start_dt = anchor_dt
            for _ in range(n_prev):
                start_dt -= datetime.timedelta(days=1)  # Subtracting a day to go to past month
                start_dt = start_dt.replace(day=1)

            end_dt = get_last_day_of_month(anchor_dt)
            for _ in range(n_next):
                end_dt += datetime.timedelta(days=1)
                end_dt = get_last_day_of_month(end_dt)

            output = {}
            for user in tqdm(users):
                if user.email:
                    events = parse_google_calendar(user.email, start_dt, end_dt)
                    output[user.email] = events

            with open(args["--output-pickle"], "wb") as fp:
                pickle.dump(output, fp)
