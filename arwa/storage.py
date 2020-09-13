import os
import sqlite3
from typing import List

from arwa.types import SlackMessage


class SqliteDB:
    def __init__(self, path: str):
        if not os.path.exists(path):
            raise RuntimeError(f"arwa db path {path} not found")
        self.conn = sqlite3.connect(path)

        self.slack_table = "slack_rtm"

    def save_message(self, msg: SlackMessage):
        cur = self.conn.cursor()
        cur.execute(
            f"""INSERT INTO {self.slack_table} (message, channel, thread_ts) VALUES (?, ?, ?)""",
            (msg.message, msg.channel, msg.thread_ts)
        )
        self.conn.commit()

    def load_messages(self) -> List[SlackMessage]:
        cur = self.conn.cursor()
        cur.execute(f"""SELECT message, channel, thread_ts FROM {self.slack_table}""")

        return [SlackMessage(*it) for it in cur.fetchall()]
