#!/bin/bash

# Infinite loop to monitor resources every 15 seconds
while true; do
  # Disk usage percentage (root filesystem)
  DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
  
  # Memory usage percentage
  MEM_TOTAL=$(free -m | awk 'NR==2 {print $2}')
  MEM_USED=$(free -m | awk 'NR==2 {print $3}')
  MEM_USAGE=$((MEM_USED * 100 / MEM_TOTAL))
  
  # CPU usage percentage (average over all cores)
  CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | cut -d'.' -f1)
  
  # Echo the percentages with a timestamp
  echo "$(date '+%Y-%m-%d %H:%M:%S') - Disk: ${DISK_USAGE}% | Memory: ${MEM_USAGE}% | CPU: ${CPU_USAGE}%"
  
  # Wait 5 seconds
  sleep 5
done
