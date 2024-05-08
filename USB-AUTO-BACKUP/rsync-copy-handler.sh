#!/bin/bash
# Usage: ./rsync-copy-handler.sh source destination

SOURCE=$1
DESTINATION=$2

# Ensuring the destination directory exists
mkdir -p "$DESTINATION"

# Using rsync to copy files with progress
rsync -avh --progress $SOURCE/ $DESTINATION/