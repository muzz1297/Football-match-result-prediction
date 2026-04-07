import os
# Create templates and static directories
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Create index.html
index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Match Result Predictor</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>⚽ Football Match Result Predictor</h1>
            <div class="accuracy-badge">
                Model Accuracy: {{ "%.1f"|format(overall_accuracy) }}%
            </div>
        </header>

        <section class="filters">
            <form method="GET" action="/">
                <div class="filter-group">
                    <label for="season">Season:</label>
                    <select name="season" id="season" onchange="this.form.submit()">
                        <option value="">All Seasons</option>
                        {% for season in seasons %}
                        <option value="{{ season }}" {% if season == selected_season %}selected{% endif %}>
                            {{ season }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="filter-group">
                    <label for="league">League:</label>
                    <select name="league" id="league" onchange="this.form.submit()">
                        <option value="">All Leagues</option>
                        {% for league in leagues %}
                        <option value="{{ league }}" {% if league == selected_league %}selected{% endif %}>
                            {{ league }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <button type="submit" class="btn-filter">Apply Filters</button>
                <a href="/" class="btn-reset">Reset</a>
            </form>
        </section>

        <section class="stats-bar">
            <div class="stat">
                <span class="stat-value">{{ total_matches }}</span>
                <span class="stat-label">Total Matches</span>
            </div>
            <div class="stat">
                <span class="stat-value">{{ correct_count }}</span>
                <span class="stat-label">Correct Predictions</span>
            </div>
            <div class="stat">
                <span class="stat-value">{{ "%.1f"|format(filtered_accuracy) }}%</span>
                <span class="stat-label">Filtered Accuracy</span>
            </div>
        </section>

        <section class="predictions-table">
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Season</th>
                        <th>League</th>
                        <th>Home Team</th>
                        <th>Away Team</th>
                        <th>Actual Result</th>
                        <th>Predicted Result</th>
                        <th>Correct</th>
                    </tr>
                </thead>
                <tbody>
                    {% for pred in predictions %}
                    <tr class="{{ 'correct-row' if pred.correct else 'wrong-row' }}">
                        <td>{{ loop.index }}</td>
                        <td>{{ pred.season }}</td>
                        <td>{{ pred.league_name }}</td>
                        <td>{{ pred.home_team_name }}</td>
                        <td>{{ pred.away_team_name }}</td>
                        <td class="result">{{ pred.actual_result }}</td>
                        <td class="result">{{ pred.predicted_result }}</td>
                        <td class="status">
                            {% if pred.correct %}
                            <span class="correct">✅</span>
                            {% else %}
                            <span class="wrong">❌</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </section>

        <footer>
            <p>Football Match Result Predictor | Powered by XGBoost Machine Learning</p>
        </footer>
    </div>
</body>
</html>'''

style_css = '''/* Football Match Result Predictor - Dark Theme */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    min-height: 100vh;
    color: #e4e4e4;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

/* Header */
header {
    text-align: center;
    padding: 30px 0;
    border-bottom: 2px solid #3a4f7a;
    margin-bottom: 30px;
}

header h1 {
    font-size: 2.5rem;
    color: #00ff88;
    text-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    margin-bottom: 20px;
}

.accuracy-badge {
    display: inline-block;
    background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
    color: #1a1a2e;
    font-size: 1.5rem;
    font-weight: bold;
    padding: 15px 40px;
    border-radius: 50px;
    box-shadow: 0 4px 15px rgba(0, 255, 136, 0.4);
}

/* Filters Section */
.filters {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 25px;
    margin-bottom: 25px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.filters form {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    align-items: flex-end;
    justify-content: center;
}

.filter-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.filter-group label {
    font-size: 0.9rem;
    color: #aaa;
    font-weight: 500;
}

.filter-group select {
    padding: 12px 20px;
    font-size: 1rem;
    border: 2px solid #3a4f7a;
    border-radius: 8px;
    background: #1a1a2e;
    color: #e4e4e4;
    cursor: pointer;
    min-width: 200px;
    transition: all 0.3s ease;
}

.filter-group select:hover,
.filter-group select:focus {
    border-color: #00ff88;
    outline: none;
    box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
}

.btn-filter {
    padding: 12px 30px;
    font-size: 1rem;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    background: linear-gradient(135deg, #00ff88 0%, #00cc6a 100%);
    color: #1a1a2e;
    cursor: pointer;
    transition: all 0.3s ease;
}

.btn-filter:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0, 255, 136, 0.4);
}

.btn-reset {
    padding: 12px 30px;
    font-size: 1rem;
    font-weight: 600;
    border: 2px solid #ff6b6b;
    border-radius: 8px;
    background: transparent;
    color: #ff6b6b;
    text-decoration: none;
    transition: all 0.3s ease;
}

.btn-reset:hover {
    background: #ff6b6b;
    color: #1a1a2e;
}

/* Stats Bar */
.stats-bar {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-bottom: 30px;
    flex-wrap: wrap;
}

.stat {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px 40px;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.1);
    min-width: 180px;
}

.stat-value {
    display: block;
    font-size: 2rem;
    font-weight: bold;
    color: #00ff88;
}

.stat-label {
    display: block;
    font-size: 0.9rem;
    color: #aaa;
    margin-top: 5px;
}

/* Predictions Table */
.predictions-table {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

table {
    width: 100%;
    border-collapse: collapse;
}

thead {
    background: linear-gradient(135deg, #3a4f7a 0%, #2d3e5f 100%);
}

th {
    padding: 18px 15px;
    text-align: left;
    font-weight: 600;
    font-size: 0.95rem;
    color: #fff;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

td {
    padding: 15px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

tbody tr {
    transition: all 0.3s ease;
}

tbody tr:hover {
    background: rgba(255, 255, 255, 0.08);
}

/* Row Colors */
.correct-row {
    background: rgba(0, 255, 136, 0.08);
}

.correct-row:hover {
    background: rgba(0, 255, 136, 0.15);
}

.wrong-row {
    background: rgba(255, 107, 107, 0.08);
}

.wrong-row:hover {
    background: rgba(255, 107, 107, 0.15);
}

/* Result badges */
.result {
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    display: inline-block;
}

.correct-row .result {
    background: rgba(0, 255, 136, 0.2);
    color: #00ff88;
}

.wrong-row .result {
    background: rgba(255, 107, 107, 0.2);
    color: #ff6b6b;
}

.status {
    font-size: 1.2rem;
    text-align: center;
}

.correct {
    color: #00ff88;
}

.wrong {
    color: #ff6b6b;
}

/* Footer */
footer {
    text-align: center;
    padding: 30px;
    margin-top: 30px;
    color: #666;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* Responsive Design */
@media (max-width: 1200px) {
    table {
        font-size: 0.9rem;
    }
    
    th, td {
        padding: 12px 10px;
    }
}

@media (max-width: 768px) {
    header h1 {
        font-size: 1.8rem;
    }
    
    .accuracy-badge {
        font-size: 1.2rem;
        padding: 12px 25px;
    }
    
    .filters form {
        flex-direction: column;
        align-items: stretch;
    }
    
    .filter-group select {
        width: 100%;
    }
    
    .stats-bar {
        gap: 15px;
    }
    
    .stat {
        padding: 15px 20px;
        min-width: 140px;
    }
    
    .predictions-table {
        overflow-x: auto;
    }
    
    table {
        min-width: 900px;
    }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: #1a1a2e;
}

::-webkit-scrollbar-thumb {
    background: #3a4f7a;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: #4a5f8a;
}'''

# Write the files
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(index_html)

with open('static/style.css', 'w', encoding='utf-8') as f:
    f.write(style_css)

print("Created templates/index.html and static/style.css successfully!")
