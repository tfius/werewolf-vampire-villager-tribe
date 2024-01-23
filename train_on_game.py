import json
import pandas as pd

## Parse the logs

# Assuming the logs are stored in a file named 'game_logs.txt'
with open('game_logs.txt', 'r') as file:
    log_lines = file.readlines()

# Parse each line of the log file
parsed_logs = [json.loads(line) for line in log_lines]

# Flatten the nested structure into a DataFrame
df = pd.json_normalize(parsed_logs, record_path=['game', 'p'], 
                       meta=[['game', 'v']], 
                       record_prefix='player_')

# Example of how the DataFrame might look
print(df.head())

# Adding a feature for the night/day cycle
df['is_night'] = df['game.v'].apply(lambda x: x[0]['night'])


from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Let's say you want to predict if a player is a werewolf based on their actions and game state
X = df.drop(['player_i', 'player_r'], axis=1)  # Features
y = df['player_r']  # Target variable (role of the player)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest Classifier
clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Evaluate the model
accuracy = clf.score(X_test, y_test)
print(f"Model Accuracy: {accuracy}")
