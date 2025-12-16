import logging
import time
import sys
from gke_pod_snapshots_tools import maybe_snapshot_on_gke

# Setup logging to stdout
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    logging.info(">>> APP START: Simulating heavy initialization...")
    time.sleep(5) 
    logging.info(">>> APP INIT DONE.")

    logging.info(">>> TRIGGER: Calling maybe_snapshot_on_gke()...")
    maybe_snapshot_on_gke()
    
    logging.info(">>> RESUMED: I have been restored from snapshot! Starting main loop...")
    
    count = 0
    while True:
        count += 1
        logging.info(f"App is running... tick {count}")
        time.sleep(10)

if __name__ == "__main__":
    main()
