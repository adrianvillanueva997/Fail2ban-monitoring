#!/bin/bash
grep "Ban " /var/log/fail2ban.log | grep `date +%Y-%m-%d` | awk '{print $NF}' | sort | uniq > $(pwd)/f2b.txt
# awk '{print $12}' /var/log/messages |uniq > /home/jvgm/grafana/csf.txt
source $(pwd)/venv/bin/activate
cd ip_monitor
python3 ./xiao_server.py
