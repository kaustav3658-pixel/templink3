#!/bin/bash
gunicorn app:app &
python bot.py
