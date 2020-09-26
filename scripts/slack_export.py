"""
Export messages from slack.

Usage:
  slack_export.py channel <channel-id> --output-jsonl=<output-jsonl>
  slack_export.py dm <user-id> --output-jsonl=<output-jsonl>
"""

import os

from docopt import docopt

import jsonlines
import slack

if __name__ == "__main__":
    args = docopt(__doc__)

    client = slack.WebClient(os.environ["SLACK_USER_TOKEN"])
