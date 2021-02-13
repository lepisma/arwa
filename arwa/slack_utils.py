from typing import Dict, Iterator, List

import slack
from pydash import py_
from tqdm import trange

from arwa.types import SlackUser


def last_user_access(client: slack.WebClient, n_pages=10) -> Dict[SlackUser, Dict]:
    """
    Return latest user slack access information.

    HACK: This is an approximation and since we are only going to use this for
          geolocation, it's alright.
    """

    access = {}

    for page_number in trange(1, n_pages + 1):
        response = client.team_accessLogs(count=100, page=page_number)

        # We probably don't need sorting
        for login in sorted(response["logins"], key=lambda it: it["date_last"], reverse=True):
            # Note that this name does not align with names from other sources
            user = SlackUser(login["user_id"], login["username"])
            if user not in access:
                access[user] = login

    return access


def list_users(client: slack.WebClient, all_users=False) -> List[SlackUser]:
    """
    List workspace users. If `all_users` is True, return bots and deactivated
    users also.

    Notice that reading email needs `users:read.email` slack scope.
    """

    response = client.users_list()
    members = response["members"]

    users = []
    for member in members:
        users.append(SlackUser(
            member["id"], member["profile"]["real_name"],
            is_bot=member["is_bot"],
            is_deleted=member["deleted"],
            email=member["profile"].get("email")
        ))

    if all_users:
        return users
    else:
        return [
            u for u in users
            if not (u.is_bot or u.is_deleted or u.id == "USLACKBOT")
        ]


def list_usergroups(client: slack.WebClient) -> List[str]:
    """
    Return usergroups represented via handles.
    """

    usergroups = client.usergroups_list()["usergroups"]
    return [u["handle"] for u in usergroups]


def list_users_from_usergroup(client: slack.WebClient, usergroup: str) -> List[SlackUser]:
    """
    List users in a given usergroup handle.
    """

    usergroups = client.usergroups_list(include_users=True)["usergroups"]
    group = py_.find(usergroups, lambda it: it["handle"] == usergroup)
    user_ids = group["users"]

    users = []
    for i in user_ids:
        u = client.users_info(user=i)["user"]
        users.append(SlackUser(u["id"], u["profile"]["real_name"], email=u["profile"].get("email")))

    return users


def channel_name_to_id(name: str, client: slack.WebClient) -> str:
    """
    Return slack id for given channel name. This only works for the channel the
    slack client is part of.
    """

    response = client.users_conversations(types="public_channel,private_channel,mpim,im", exclude_archived=True)
    channels = response["channels"]

    result = py_.find(channels, lambda ch: ch.get("name", "") == name)

    if result:
        return result["id"]
    else:
        raise ValueError(f"Channel {name} not found")


def get_message_batches(conversation_id: str, client: slack.WebClient) -> Iterator[List[Dict]]:
    """
    Get messages in batches of requests.
    """

    response = client.conversations_history(channel=conversation_id)
    message_batch = response["messages"]

    if not message_batch:
        return

    yield message_batch

    while response["has_more"]:
        next_cursor = response["response_metadata"]["next_cursor"]
        response = client.conversations_history(channel=conversation_id, cursor=next_cursor)
        yield response["messages"]
