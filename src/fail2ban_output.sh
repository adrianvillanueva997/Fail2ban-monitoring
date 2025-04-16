#!/usr/bin/env bash
grep "Ban " /var/log/fail2ban.log | grep $(date +%Y-%m-%d) | awk '{print $NF}' | sort -u >$(pwd)/f2b.txt
