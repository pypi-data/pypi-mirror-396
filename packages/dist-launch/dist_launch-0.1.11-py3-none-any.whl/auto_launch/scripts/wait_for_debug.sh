#!/bin/bash
# Wait script for debug mode - Run on all nodes to keep them alive
# This should be executed when DLC task starts, before entering debug mode
# Usage: ./wait_for_debug.sh [timeout_seconds]
# Default: wait indefinitely

set -e

TIMEOUT=${1:-0}  # 0 means wait indefinitely
CLUSTER_INFO_FILE="${CLUSTER_INFO_FILE:-/tmp/cluster_info.json}"

# Set NCCL environment variables for GB200 (if not already set)
# Detect network interfaces dynamically if not set
if [ -z "$NCCL_SOCKET_IFNAME" ]; then
    # Try to detect network interfaces using ifconfig or ip command
    if command -v ifconfig >/dev/null 2>&1; then
        # Use ifconfig to get non-loopback interfaces
        DETECTED_IFNAME=$(ifconfig -a | grep -E '^[a-zA-Z0-9]+:' | grep -v '^lo:' | awk -F: '{print $1}' | grep -E 'enP|enp|eth' | head -5 | tr '\n' ',' | sed 's/,$//')
    elif command -v ip >/dev/null 2>&1; then
        # Use ip command to get non-loopback interfaces
        DETECTED_IFNAME=$(ip addr show | grep -E '^[0-9]+:' | grep -v 'lo:' | awk -F: '{print $2}' | tr -d ' ' | grep -E 'enP|enp|eth' | head -5 | tr '\n' ',' | sed 's/,$//')
    fi
    
    if [ -n "$DETECTED_IFNAME" ]; then
        export NCCL_SOCKET_IFNAME="$DETECTED_IFNAME"
        echo "Detected network interfaces: $NCCL_SOCKET_IFNAME"
    else
        # Fallback to default GB200 interfaces
        export NCCL_SOCKET_IFNAME="enP22p3s0f0np0,enP6p3s0f0np0"
        echo "Using fallback NCCL_SOCKET_IFNAME: $NCCL_SOCKET_IFNAME"
    fi
else
    echo "Using existing NCCL_SOCKET_IFNAME: $NCCL_SOCKET_IFNAME"
fi
export NCCL_IB_DISABLE="${NCCL_IB_DISABLE:-1}"

# Cleanup function to handle signals and cleanup
cleanup() {
    echo ""
    echo "Received signal, cleaning up..."
    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null || true
    # Wait for all background jobs to finish
    wait
    echo "Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT SIGQUIT

echo "=== DLC Debug Mode: Cluster Initialization ==="
echo "Cluster info file: $CLUSTER_INFO_FILE"

# Run cluster initialization first (discover hostnames via allgather)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
INIT_SCRIPT="${SCRIPT_DIR}/init_cluster.py"

if [ -f "$INIT_SCRIPT" ]; then
    echo "Initializing cluster and discovering hostnames via PyTorch allgather..."
    python3 "$INIT_SCRIPT"
    if [ $? -eq 0 ]; then
        echo "Cluster initialization completed successfully"
    else
        echo "Warning: Cluster initialization failed, but continuing..."
    fi
else
    echo "Warning: init_cluster.py not found, skipping hostname discovery"
fi

echo ""
echo "=== Entering debug wait mode ==="
echo "All nodes are now waiting. You can:"
echo "1. Login to rank0 node"
echo "2. Prepare your train.sh script"
echo "3. Execute ./run.sh to launch training on all nodes"
echo ""

# Wait mechanism that doesn't create zombie processes
# Use exec to replace current process, avoiding zombie processes
if [ "$TIMEOUT" -gt 0 ]; then
    echo "Waiting for $TIMEOUT seconds..."
    # Use timeout command with sleep
    timeout $TIMEOUT sleep infinity 2>/dev/null || timeout $TIMEOUT tail -f /dev/null || true
else
    echo "Waiting indefinitely (send SIGTERM/SIGINT to exit)..."
    # Use exec to replace current process with tail/sleep
    # This avoids creating child processes that could become zombies
    if command -v sleep >/dev/null 2>&1 && sleep infinity 2>/dev/null; then
        exec sleep infinity
    else
        exec tail -f /dev/null
    fi
fi

echo "Wait script completed"
exit 0

