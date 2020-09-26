"""
Slack sentinel

Usage:
  slack_sentinel.py --db-path=<db-path>
"""

import os
import time

from docopt import docopt

import aiohttp.client_exceptions
import slack
from arwa.storage import SqliteDB
from arwa.types import SlackMessage


class Sentinel:
    def __init__(self, db: SqliteDB):
        self.db = db

    def on_message(self, **kwargs):
        data = kwargs["data"]

        text = data.get("text")
        if not text:
            return

        if not text.startswith(":follow-up"):
            return

        msg = SlackMessage(text, data["channel"], data["ts"])
        print(f":  Saving {msg}")
        self.db.save_message(msg)


if __name__ == "__main__":
    args = docopt(__doc__)

    db = SqliteDB(args["--db-path"])
    sentinel = Sentinel(db)
    sentinel.on_message = slack.RTMClient.run_on(event="message")(sentinel.on_message)

    slack_token = os.environ["SLACK_CLASSIC_BOT_USER_TOKEN"]
    rtm_client = slack.RTMClient(token=slack_token)

    retry_time = 5

    print(":: Starting the watch")
    while True:
        try:
            rtm_client.start()
        except aiohttp.client_exceptions.ClientConnectorError:
            print(f"Connection error, retrying in {retry_time} seconds")
        time.sleep(retry_time)
