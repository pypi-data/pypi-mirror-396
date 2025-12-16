"""
Core functionality for GKE Pod Snapshots integration.
"""

import logging
import os
import random

# Configure standard logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def maybe_snapshot_on_gke():
    """
    If running on GKE (gVisor), create or resume from a GKE Snapshot.
    
    This function detects if the environment supports application-driven checkpointing.
    If available, it triggers a snapshot. When the container is restored, execution 
    resumes immediately after the snapshot trigger.
    """
    
    # 1. Check if the checkpoint interface exists
    checkpoint_path = '/proc/gvisor/checkpoint'
    try:
        os.stat(checkpoint_path)
    except FileNotFoundError:
        # Application-driven checkpointing is not enabled or not on gVisor.
        return

    # 2. Trigger the Snapshot
    # This uses the standard blocking read method.
    # The process will suspend here inside the f.read() call.
    with open(checkpoint_path, "rb+") as f:
        logging.info("Taking a GKE Snapshot. This may take a few minutes.")
        f.write(b"1")
        f.read() 

    # 3. Post-Restore actions
    logging.info("Resumed from GKE Snapshot.")
    
    # Reset random seed to ensure randomness differs between restored instances
    random.seed()
