CREATE TABLE IF NOT EXISTS slack_rtm (
  id INTEGER PRIMARY KEY,
  message TEXT NOT NULL,
  channel TEXT NOT NULL,
  thread_ts TEXT
);
