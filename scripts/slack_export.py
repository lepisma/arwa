"""
Export messages from slack to a jsonl file.

Needs SLACK_USER_TOKEN with *:history scopes set. Mostly I am using
channels:history and im:history for now.

Usage:
  slack_export.py <c-id> --output-jsonl=<output-jsonl>

Arguments:
  <c-id>       Conversations id. This can be channel id, dm id or anything
               that behaves like a conversation in slack terminology.
"""

import os

from docopt import docopt
from tqdm import tqdm

import jsonlines
import slack


def get_message_batches(client, c_id: str):
    """
    Get messages in batches of requests.
    """

    response = client.conversations_history(channel=c_id)
    message_batch = response["messages"]

    if not message_batch:
        return

    yield message_batch

    while response["has_more"]:
        next_cursor = response["response_metadata"]["next_cursor"]
        response = client.conversations_history(channel=c_id, cursor=next_cursor)
        yield response["messages"]


if __name__ == "__main__":
    args = docopt(__doc__)

    client = slack.WebClient(os.environ["SLACK_USER_TOKEN"])

    with jsonlines.open(args["--output-jsonl"], mode="w") as fp:
        bar = tqdm()
        for batch in get_message_batches(client, args["<c-id>"]):
            fp.write_all(batch)
            bar.update(len(batch))
