from typing import List

import slack
from arwa.types import SlackUser


def list_users(client: slack.WebClient) -> List[SlackUser]:
    """
    List workspace users except bots and deactivated accounts.
    """

    response = client.users_list()
    members = response["members"]

    users = []
    for member in members:
        if member["is_bot"]:
            continue
        if member["deleted"]:
            continue
        if member["id"] == "USLACKBOT":
            continue
        users.append(SlackUser(member["id"], member["real_name"]))
    return users


def channel_name_to_id(name: str, client: slack.WebClient) -> str:
    """
    Return slack id for given channel name.
    """

    response = client.users_conversations(types="public_channel,private_channel,mpim,im", exclude_archived=True)
    channels = response["channels"]

    result = py_.find(channels, lambda ch: ch["name"] == name)

    if result:
        return result["id"]
    else:
        raise ValueError(f"Channel {name} not found")
