"""
Example usage of the RunTracker package
"""

from run_tracker import RunTracker, init_database, register_flow
import time

# Initialize database (run once)
DB_PATH = 'example_tracking.db'
init_database(DB_PATH)

# Register this flow (run once)
register_flow(
    DB_PATH,
    flow_name='Example Script',
    flow_path=__file__,
    description='Example usage of RunTracker'
)

# Use RunTracker in your script
with RunTracker(DB_PATH, trigger_type='manual') as tracker:
    tracker.log("Starting example process")

    # Simulate some work
    for i in range(5):
        tracker.log(f"Processing item {i + 1}/5")
        time.sleep(0.5)

    tracker.log("Example process completed successfully")

print("\nCheck the 'logs' directory for the log file!")
print(f"Check '{DB_PATH}' database for run history")