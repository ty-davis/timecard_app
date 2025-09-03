#!/bin/bash

sqlite3 ../instance/timecard.db .dump > recent_backup.sql
cp recent_backup.sql "$(date +%Y-%m-%d).sql"
