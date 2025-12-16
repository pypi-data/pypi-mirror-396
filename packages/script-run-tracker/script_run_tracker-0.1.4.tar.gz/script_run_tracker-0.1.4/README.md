# Script Run Tracker

A lightweight SQLite-based run tracker for Python scripts with automatic logging capabilities. 

This library is a companion tool for the **Python Automation Project**, designed to track execution history, monitor scheduled jobs, data pipelines, and automation scripts with detailed logging.

## Features

- 📊 **SQLite-based tracking** - No external dependencies
- 📝 **Automatic logging** - Creates timestamped log files for each run
- 🔄 **Log rotation** - Automatically manages old log files
- ⚡ **Context manager support** - Clean and simple API
- 🎯 **Trigger tracking** - Distinguishes between manual and scheduled runs
- ✅ **Status tracking** - Automatically tracks success/failure states
- 📁 **Project organization** - Logs stored alongside your scripts

## Installation

```bash
pip install script-run-tracker
```

## Related Projects

This library is part of the **Python Automation Project** ecosystem, designed to provide robust tracking and monitoring capabilities for automated workflows.

## Quick Start

### 1. Initialize the database

First, create the database schema (run once):

```python
from run_tracker import init_database

init_database('tracking.db')
```

### 2. Register your flow

```python
from run_tracker import register_flow

register_flow(
    db_path='tracking.db',
    flow_name='Daily Data Processing',
    flow_path='/path/to/your/script.py',
    description='Processes daily sales data'
)
```

### 3. Use in your script

```python
from run_tracker import RunTracker

with RunTracker('tracking.db', trigger_type='scheduler') as tracker:
    tracker.log("Starting data processing")
    
    # Your code here
    data = load_data()
    tracker.log(f"Loaded {len(data)} records")
    
    process_data(data)
    tracker.log("Processing complete")
```

## Usage

### Basic Usage

```python
from run_tracker import RunTracker

with RunTracker('tracking.db') as tracker:
    tracker.log("Process started")
    # Your code here
    tracker.log("Process completed")
```

### Custom Project Name

```python
with RunTracker('tracking.db', project_name='my_etl_job') as tracker:
    tracker.log("ETL job started")
    # Your code here
```

### Trigger Types

Automatically detect whether the script was run manually or by a scheduler:

```python
import sys
from run_tracker import RunTracker

# Detect trigger type from command line argument
trigger_type = sys.argv[1] if len(sys.argv) > 1 else "scheduler"

with RunTracker('tracking.db', trigger_type=trigger_type, max_log_files=10) as tracker:
    tracker.log("Process started")
    # Your code here
```

**Usage:**
```bash
# Run manually (defaults to 'scheduler' if no argument)
python your_script.py

# Explicitly set trigger type
python your_script.py manual
python your_script.py scheduler
```

Alternatively, you can explicitly set the trigger type:

```python
# For scheduled runs
with RunTracker('tracking.db', trigger_type='scheduler') as tracker:
    tracker.log("Automated run started")

# For manual runs
with RunTracker('tracking.db', trigger_type='manual') as tracker:
    tracker.log("Manual run started")
```

### Log Levels

```python
with RunTracker('tracking.db') as tracker:
    tracker.log("Informational message", level='INFO')
    tracker.log("Debug information", level='DEBUG')
    tracker.log("Warning message", level='WARNING')
    tracker.log("Error occurred", level='ERROR')
    tracker.log("Critical issue", level='CRITICAL')
```

### Configure Log Retention

```python
# Keep only the last 5 log files
with RunTracker('tracking.db', max_log_files=5) as tracker:
    tracker.log("Starting with custom retention")
```

## Database Schema

The package automatically creates two tables:

**flows** - Stores information about your scripts
- flow_id (PRIMARY KEY)
- flow_name
- flow_path
- description
- is_active
- created_at

**runs** - Stores execution history
- run_id (PRIMARY KEY)
- flow_id (FOREIGN KEY)
- status ('running', 'success', 'fail')
- trigger_type ('scheduler', 'manual')
- start_time
- finish_time
- error_message
- log_file_path

## Log Files

Log files are automatically created in a `logs/` directory next to your script:

```
your_project/
├── your_script.py
└── logs/
    ├── your_script_run_1.log
    ├── your_script_run_2.log
    └── your_script_run_3.log
```

## Error Handling

RunTracker automatically captures and logs exceptions:

```python
with RunTracker('tracking.db') as tracker:
    tracker.log("Starting risky operation")
    
    # If this raises an exception, it will be:
    # 1. Logged to the log file
    # 2. Stored in the database
    # 3. Re-raised for your handling
    risky_operation()
```

## Utility Functions

### Initialize Database

```python
from run_tracker import init_database

init_database('tracking.db')
```

### Register a Flow

```python
from run_tracker import register_flow

register_flow(
    db_path='tracking.db',
    flow_name='Data Sync Job',
    flow_path='/opt/scripts/data_sync.py',
    description='Syncs data from external API'
)
```

### Deactivate a Flow

```python
from run_tracker import deactivate_flow

deactivate_flow('tracking.db', 'Data Sync Job')
```

## Requirements

- Python 3.7+
- No external dependencies (uses only Python standard library)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository.