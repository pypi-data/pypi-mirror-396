#!/bin/bash

secs=150                          # Set interval (duration) in seconds.
endTime=$(( $(date +%s) + secs )) # Calculate end time.

check_health() {
    curl -s localhost:8000/-/health > /dev/null
}

while [ $(date +%s) -lt $endTime ]; do  # Loop until interval has elapsed.
     if check_health; then
      echo "Health endpoint is responding correctly."
      exit 0
    else
      echo "Health endpoint is not responding. Retrying in 10 seconds ..."
      sleep 10
    fi
done

echo "Timeout reached. Health endpoint did not respond within $secs seconds."
exit 1
