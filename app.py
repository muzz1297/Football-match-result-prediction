from flask import Flask, render_template, request
import pandas as pd
import joblib

app = Flask(__name__)

# Load model and predictions at startup
print("Loading model and predictions...")
model_data = joblib.load('model.pkl')
predictions_df = pd.read_csv('predictions.csv')

# Calculate overall accuracy
overall_accuracy = predictions_df['correct'].mean() * 100

# Get unique seasons and leagues for filters
seasons = sorted(predictions_df['season'].unique().tolist())
leagues = sorted(predictions_df['league_name'].unique().tolist())

print(f"Loaded {len(predictions_df)} predictions")
print(f"Overall accuracy: {overall_accuracy:.2f}%")
print(f"Seasons: {len(seasons)}, Leagues: {len(leagues)}")

@app.route('/')
def index():
    # Get filter parameters
    selected_season = request.args.get('season', '')
    selected_league = request.args.get('league', '')
    
    # Filter predictions
    filtered_df = predictions_df.copy()
    
    if selected_season:
        filtered_df = filtered_df[filtered_df['season'] == selected_season]
    
    if selected_league:
        filtered_df = filtered_df[filtered_df['league_name'] == selected_league]
    
    # Calculate filtered accuracy
    if len(filtered_df) > 0:
        filtered_accuracy = filtered_df['correct'].mean() * 100
        correct_count = filtered_df['correct'].sum()
    else:
        filtered_accuracy = 0
        correct_count = 0
    
    # Convert to list of dicts for template
    predictions_list = filtered_df.to_dict('records')
    
    return render_template('index.html',
                         predictions=predictions_list,
                         overall_accuracy=overall_accuracy,
                         filtered_accuracy=filtered_accuracy,
                         seasons=seasons,
                         leagues=leagues,
                         selected_season=selected_season,
                         selected_league=selected_league,
                         total_matches=len(filtered_df),
                         correct_count=int(correct_count))

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Football Match Result Predictor Web App")
    print("="*50)
    print(f"Starting server at http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
