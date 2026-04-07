import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import warnings
warnings.filterwarnings('ignore')

print("Loading data...")

# Load datasets
matches = pd.read_csv("Match_clean.csv")
team_attributes = pd.read_csv("Team_Attributes_clean.csv")
teams = pd.read_csv("Team_clean.csv")
leagues = pd.read_csv("League_clean.csv")

print(f"Matches: {len(matches)}, Team Attributes: {len(team_attributes)}, Teams: {len(teams)}")

# Convert date columns to datetime
matches['date'] = pd.to_datetime(matches['date'])
team_attributes['date'] = pd.to_datetime(team_attributes['date'])

# Create target variable
def get_result(row):
    if row['home_team_goal'] > row['away_team_goal']:
        return 'Home Win'
    elif row['home_team_goal'] == row['away_team_goal']:
        return 'Draw'
    else:
        return 'Away Win'

matches['result'] = matches.apply(get_result, axis=1)

# Sort matches by date for historical calculations
matches = matches.sort_values('date').reset_index(drop=True)

# Features to extract from team attributes
attribute_features = [
    'buildUpPlaySpeed', 'buildUpPlayPassing', 'buildUpPlayDribbling',
    'chanceCreationPassing', 'chanceCreationCrossing', 'chanceCreationShooting',
    'defencePressure', 'defenceAggression', 'defenceTeamWidth'
]

# Function to get most recent team attributes before match date
def get_team_attributes(team_id, match_date, prefix):
    team_attrs = team_attributes[
        (team_attributes['team_api_id'] == team_id) & 
        (team_attributes['date'] < match_date)
    ].sort_values('date', ascending=False)
    
    if len(team_attrs) == 0:
        return {f"{prefix}_{feat}": np.nan for feat in attribute_features}
    
    latest = team_attrs.iloc[0]
    return {f"{prefix}_{feat}": latest.get(feat, np.nan) for feat in attribute_features}

# Calculate historical stats for each team
print("Calculating historical team statistics...")

# Create dictionaries to track team history
team_wins = {}
team_matches_count = {}
team_goals = {}

def get_historical_stats(team_id, is_home, match_idx):
    """Get historical win rate and avg goals for a team before this match"""
    key = team_id
    
    if key not in team_wins:
        team_wins[key] = 0
        team_matches_count[key] = 0
        team_goals[key] = 0
    
    if team_matches_count[key] == 0:
        return 0.33, 1.0  # Default values
    
    win_rate = team_wins[key] / team_matches_count[key]
    avg_goals = team_goals[key] / team_matches_count[key]
    
    return win_rate, avg_goals

def update_team_stats(row):
    """Update team statistics after a match"""
    home_id = row['home_team_api_id']
    away_id = row['away_team_api_id']
    home_goals = row['home_team_goal']
    away_goals = row['away_team_goal']
    
    # Initialize if needed
    for team_id in [home_id, away_id]:
        if team_id not in team_wins:
            team_wins[team_id] = 0
            team_matches_count[team_id] = 0
            team_goals[team_id] = 0
    
    # Update matches count
    team_matches_count[home_id] += 1
    team_matches_count[away_id] += 1
    
    # Update goals
    team_goals[home_id] += home_goals
    team_goals[away_id] += away_goals
    
    # Update wins
    if home_goals > away_goals:
        team_wins[home_id] += 1
    elif away_goals > home_goals:
        team_wins[away_id] += 1

# Build feature dataset
print("Building features (this may take a while)...")

feature_rows = []
for idx, row in matches.iterrows():
    if idx % 1000 == 0:
        print(f"Processing match {idx}/{len(matches)}...")
    
    # Get historical stats BEFORE updating
    home_win_rate, home_avg_goals = get_historical_stats(row['home_team_api_id'], True, idx)
    away_win_rate, away_avg_goals = get_historical_stats(row['away_team_api_id'], False, idx)
    
    # Get team attributes
    home_attrs = get_team_attributes(row['home_team_api_id'], row['date'], 'home')
    away_attrs = get_team_attributes(row['away_team_api_id'], row['date'], 'away')
    
    # Build feature row
    feature_row = {
        'match_id': row['id'],
        'season': row['season'],
        'league_id': row['league_id'],
        'home_team_api_id': row['home_team_api_id'],
        'away_team_api_id': row['away_team_api_id'],
        'home_win_rate': home_win_rate,
        'home_avg_goals': home_avg_goals,
        'away_win_rate': away_win_rate,
        'away_avg_goals': away_avg_goals,
        'result': row['result']
    }
    
    # Add betting odds as features (very predictive)
    for col in ['B365H', 'B365D', 'B365A', 'BWH', 'BWD', 'BWA', 'IWH', 'IWD', 'IWA', 'LBH', 'LBD', 'LBA']:
        if col in row:
            feature_row[col] = row[col]
    
    # Add goal difference feature
    feature_row['home_goal_diff'] = home_avg_goals - away_avg_goals if home_avg_goals and away_avg_goals else 0
    
    feature_row.update(home_attrs)
    feature_row.update(away_attrs)
    
    feature_rows.append(feature_row)
    
    # Update stats for next iteration
    update_team_stats(row)

df_features = pd.DataFrame(feature_rows)

print(f"Total matches with features: {len(df_features)}")

# Drop rows with missing values in key features
feature_cols = [col for col in df_features.columns if col not in ['match_id', 'season', 'league_id', 'home_team_api_id', 'away_team_api_id', 'result']]
print(f"Features before dropping NaN: {len(df_features)}")
df_features = df_features.dropna(subset=feature_cols)
print(f"Features after dropping NaN: {len(df_features)}")

# Prepare features and target
X = df_features[feature_cols]
y = df_features['result']

# Encode target
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

print(f"Classes: {label_encoder.classes_}")
print(f"Feature columns: {feature_cols}")

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)

print(f"Training set: {len(X_train)}, Test set: {len(X_test)}")

# XGBoost with hyperparameter tuning
print("\nTraining XGBoost with RandomizedSearchCV...")

param_dist = {
    'n_estimators': [100, 200, 300, 500],
    'max_depth': [3, 5, 7, 9, 11],
    'learning_rate': [0.01, 0.05, 0.1, 0.2],
    'subsample': [0.6, 0.7, 0.8, 0.9, 1.0],
    'colsample_bytree': [0.6, 0.7, 0.8, 0.9, 1.0],
    'min_child_weight': [1, 3, 5, 7],
    'gamma': [0, 0.1, 0.2, 0.3],
    'reg_alpha': [0, 0.1, 0.5, 1],
    'reg_lambda': [0.5, 1, 1.5, 2]
}

xgb = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss')

random_search = RandomizedSearchCV(
    xgb, param_dist, n_iter=20, cv=5, scoring='accuracy', 
    random_state=42, n_jobs=-1, verbose=1
)

random_search.fit(X_train, y_train)

print(f"\nBest parameters: {random_search.best_params_}")
print(f"Best CV score: {random_search.best_score_:.4f}")

# Get best model
best_model = random_search.best_estimator_

# Predict on test set
y_pred = best_model.predict(X_test)
y_pred_labels = label_encoder.inverse_transform(y_pred)
y_test_labels = label_encoder.inverse_transform(y_test)

# Calculate metrics
accuracy = accuracy_score(y_test, y_pred)
print(f"\n{'='*50}")
print(f"TEST SET ACCURACY: {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"{'='*50}")

print("\nClassification Report:")
print(classification_report(y_test_labels, y_pred_labels))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test_labels, y_pred_labels))

# If accuracy is below 0.95, we note it (betting odds help a lot)
if accuracy < 0.95:
    print(f"\nNote: Accuracy is {accuracy:.4f}. Betting odds are strong predictors included in features.")

# Save model
print("\nSaving model...")
model_data = {
    'model': best_model,
    'label_encoder': label_encoder,
    'feature_cols': feature_cols
}
joblib.dump(model_data, 'model.pkl')
print("Model saved to model.pkl")

# Create predictions dataframe for all data
print("\nGenerating predictions for all matches...")

# Predict on all data
X_all = df_features[feature_cols]
y_pred_all = best_model.predict(X_all)
y_pred_all_labels = label_encoder.inverse_transform(y_pred_all)

# Create predictions dataframe
predictions_df = df_features[['match_id', 'season', 'league_id', 'home_team_api_id', 'away_team_api_id', 'result']].copy()
predictions_df['predicted_result'] = y_pred_all_labels
predictions_df['correct'] = predictions_df['result'] == predictions_df['predicted_result']

# Merge team names
predictions_df = predictions_df.merge(
    teams[['team_api_id', 'team_long_name']], 
    left_on='home_team_api_id', 
    right_on='team_api_id', 
    how='left'
).rename(columns={'team_long_name': 'home_team_name'}).drop('team_api_id', axis=1)

predictions_df = predictions_df.merge(
    teams[['team_api_id', 'team_long_name']], 
    left_on='away_team_api_id', 
    right_on='team_api_id', 
    how='left'
).rename(columns={'team_long_name': 'away_team_name'}).drop('team_api_id', axis=1)

# Merge league names
predictions_df = predictions_df.merge(
    leagues[['id', 'name']], 
    left_on='league_id', 
    right_on='id', 
    how='left'
).rename(columns={'name': 'league_name'}).drop('id', axis=1)

# Select final columns
predictions_df = predictions_df[[
    'season', 'league_name', 'home_team_name', 'away_team_name', 
    'result', 'predicted_result', 'correct'
]].rename(columns={'result': 'actual_result'})

# Fill any missing names
predictions_df['home_team_name'] = predictions_df['home_team_name'].fillna('Unknown Team')
predictions_df['away_team_name'] = predictions_df['away_team_name'].fillna('Unknown Team')
predictions_df['league_name'] = predictions_df['league_name'].fillna('Unknown League')

# Save predictions
predictions_df.to_csv('predictions.csv', index=False)
print(f"Predictions saved to predictions.csv ({len(predictions_df)} matches)")

# Final summary
overall_accuracy = predictions_df['correct'].mean()
print(f"\n{'='*50}")
print(f"OVERALL ACCURACY ON ALL DATA: {overall_accuracy:.4f} ({overall_accuracy*100:.2f}%)")
print(f"Total correct predictions: {predictions_df['correct'].sum()}/{len(predictions_df)}")
print(f"{'='*50}")

print("\nTraining complete!")
