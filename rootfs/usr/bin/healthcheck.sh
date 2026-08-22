#!/bin/sh

# ============================================================================
# Node Health Check Script
# ============================================================================
# Purpose:
#   Verifies that the Node service is running and healthy within the
#   S6 service supervision system.
#
# Exit Codes:
#   0 - Service is running and healthy
#   1 - Service is down or not responding
#
# Dependencies:
#   - S6 overlay must be configured and running
#   - Node service must be registered in S6 service directory
#
# Used By:
#   - Docker HEALTHCHECK instruction
#   - Container orchestration platforms (Kubernetes, Swarm, etc.)
# ============================================================================

# Get the current status of the Node service from S6
# s6-svstat returns service status and timestamps
SERVICE=$(/package/admin/s6/command/s6-svstat /run/s6-rc/servicedirs/node)

# Check if the service is in "down" state
# If service is down, output status and exit with error code
if echo "$SERVICE" | grep -q "down"; then
  echo "$SERVICE"
  exit 1
else
  # Service is running, output status and exit successfully
  echo "$SERVICE"
  exit 0
fi