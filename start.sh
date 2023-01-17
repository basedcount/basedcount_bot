#!/usr/bin/env bash
source venv/bin/activate
pm2 start basedcount_bot.py --name basedcount_bot
