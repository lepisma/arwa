"""
Get info about users in the workspace.

Usage:
  slack_user_info.py --output-json=<output-json>
"""

import json
import os

from docopt import docopt

import slack

if __name__ == "__main__":
    args = docopt(__doc__)

    client = slack.WebClient(os.environ["SLACK_USER_TOKEN"])
    with open(args["--output-json"], "w") as fp:
        json.dump(client.users_list()["members"], fp)
