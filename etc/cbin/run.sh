#!/usr/bin/env bash

# This script is used to start async-aloha container

# Create cron job to clean old events
cp /async-aloha/etc/crontab /etc/cron.d/cleanup-cron
chmod 0644 /etc/cron.d/cleanup-cron
cron && touch /async-aloha/logs/cron.log


# Wait until postgre is loading
while ! pg_isready -h "postgresdb" -p "5432" > /dev/null 2> /dev/null; do
   echo "Connecting to postgres Failed"
   sleep 1
 done

python3 /async-aloha/server/db.py
python3 /async-aloha/server/server.py
