import json
import pandas as pd

## Parse the logs

# Read the log file
with open('action_logs.txt', 'r') as file:
    lines = file.readlines()

# Convert each line from JSON to a dictionary
log_entries = [json.loads(line) for line in lines]

# Create a DataFrame from the log entries
df = pd.DataFrame(log_entries)

# Assuming df is your DataFrame

# You can create new columns based on existing data to better capture the relationships
# can be n = 0, v = 1, w = 2
df['role'] = df['player'].apply(lambda x: 0 if x['r'] == 'n' elif x['w'] else 0)
df['is_werewolf'] = df['player'].apply(lambda x: 0 if x['r'] == 'n' elif x['w'] else 0)
df['action_type'] = df['action'].apply(lambda x: list(x.keys())[0] if isinstance(x, dict) else x)
