"""
Export messages from slack.

Usage:
  slack_export.py channel <channel-id> --output-jsonl=<output-jsonl>
  slack_export.py dm <user-id> --output-jsonl=<output-jsonl>
"""

import os

from docopt import docopt
from tqdm import tqdm

import jsonlines
import slack


def get_message_batches(client, channel_id: str):
    """
    Get messages in batches of requests.
    """

    response = client.conversations_history(channel=channel_id)
    message_batch = response["messages"]

    if not message_batch:
        return

    yield message_batch

    while response["has_more"]:
        next_cursor = response["response_metadata"]["next_cursor"]
        response = client.conversations_history(channel=channel_id, cursor=next_cursor)
        yield response["messages"]


if __name__ == "__main__":
    args = docopt(__doc__)

    client = slack.WebClient(os.environ["SLACK_USER_TOKEN"])

    if args["channel"]:
        channel_id = args["<channel-id>"]
    elif args["user-id"]:
        channel_id = args["<user-id>"]
    else:
        raise NotImplementedError()

    with jsonlines.open(args["--output-jsonl"], mode="w") as fp:
        bar = tqdm()
        for batch in get_message_batches(client, channel_id):
            fp.write_all(batch)
            bar.update(len(batch))
