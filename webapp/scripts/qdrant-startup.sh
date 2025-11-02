#!/bin/sh
# Qdrant Startup Script
# Only restores snapshots if collections don't already exist in storage

# Check if collections already exist in storage
COLLECTIONS_DIR="/qdrant/storage/collections"
if [ -d "$COLLECTIONS_DIR" ] && [ "$(ls -A $COLLECTIONS_DIR 2>/dev/null)" ]; then
  echo "Collections already exist in storage. Starting Qdrant normally..."
  exec /qdrant/qdrant
fi

# Build snapshot arguments if collections don't exist
echo "No collections found. Checking for snapshots to restore..."
SNAPSHOT_ARGS=""
for snapshot in /qdrant/snapshots/*.snapshot; do
  if [ -f "$snapshot" ]; then
    collection_name=$(basename "$snapshot" .snapshot)
    SNAPSHOT_ARGS="$SNAPSHOT_ARGS --snapshot $snapshot:$collection_name"
  fi
done

# Start Qdrant with or without snapshots
if [ -n "$SNAPSHOT_ARGS" ]; then
  echo "Restoring snapshots: $SNAPSHOT_ARGS"
  exec /qdrant/qdrant $SNAPSHOT_ARGS
else
  echo "No snapshots found. Starting Qdrant normally..."
  exec /qdrant/qdrant
fi

