# ⚽ Football Match Result Predictor

A Machine Learning web application that predicts football match results using XGBoost classifier. Built with Flask, featuring a professional dark-themed UI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![XGBoost](https://img.shields.io/badge/XGBoost-ML-orange.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [How It Works](#-how-it-works)
- [Screenshots](#-screenshots)
- [Tech Stack](#-tech-stack)

---

## ✨ Features

- 🤖 **XGBoost ML Model** - Trained with RandomizedSearchCV hyperparameter tuning
- 📊 **Multiple Features** - Uses betting odds, team attributes, and historical statistics
- 🎯 **High Accuracy** - Optimized for best prediction performance
- 🌐 **Web Interface** - Clean Flask web app to view predictions
- 🔍 **Filtering** - Filter results by Season and League
- 🎨 **Dark Theme** - Professional football-style UI design
- ✅❌ **Visual Indicators** - Color-coded correct/incorrect predictions

---

## 📁 Project Structure

```
Muzz/
├── Country_clean.csv          # Country data
├── League_clean.csv           # League data
├── Match_clean.csv            # Match results data
├── Player_clean.csv           # Player data
├── Team_Attributes_clean.csv  # Team attributes data
├── Team_clean.csv             # Team names data
├── requirements.txt           # Python dependencies
├── setup_files.py             # Creates templates & static folders
├── train_model.py             # ML model training script
├── app.py                     # Flask web application
├── model.pkl                  # Trained model (generated)
├── predictions.csv            # Predictions output (generated)
├── templates/
│   └── index.html             # Web page template
└── static/
    └── style.css              # CSS styling
```

---

## 📌 Prerequisites

- **Python 3.8 or higher** installed on your system
- **pip** (Python package manager)
- Terminal/Command Prompt access

To check if Python is installed:
```bash
python --version
```

---

## 🚀 Installation & Setup

Follow these steps **in order**:

### Step 1: Navigate to Project Folder

Open terminal/command prompt and navigate to the Muzz folder:
```bash
cd path/to/Muzz
```

### Step 2: Install Dependencies

Install all required Python packages:
```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- Pandas (data manipulation)
- NumPy (numerical computing)
- Scikit-learn (ML utilities)
- XGBoost (ML algorithm)
- Joblib (model serialization)

### Step 3: Create Templates & Static Folders

Run the setup script to create HTML and CSS files:
```bash
python setup_files.py
```

You should see:
```
Created templates/index.html and static/style.css successfully!
```

### Step 4: Train the Model

Run the training script:
```bash
python train_model.py
```

**⏱️ This takes approximately 5-10 minutes.**

The script will:
1. Load all CSV data files
2. Create target variable (Home Win / Draw / Away Win)
3. Engineer features from team attributes
4. Calculate historical win rates and average goals
5. Train XGBoost with hyperparameter tuning (20 iterations, 5-fold CV)
6. Print accuracy metrics and confusion matrix
7. Save `model.pkl` and `predictions.csv`

### Step 5: Start the Web Application

Launch the Flask server:
```bash
python app.py
```

You should see:
```
==================================================
Football Match Result Predictor Web App
==================================================
Starting server at http://localhost:5000
Press Ctrl+C to stop
```

### Step 6: Open in Browser

Open your web browser and go to:
```
http://localhost:5000
```

🎉 **You should now see the Football Match Result Predictor web app!**

---

## 🔧 How It Works

### Data Flow

1. **Match_clean.csv** → Contains match results (home/away goals, teams, dates)
2. **Team_Attributes_clean.csv** → Contains team playing styles (speed, passing, defense, etc.)
3. **Team_clean.csv** → Contains team names
4. **League_clean.csv** → Contains league names

### Feature Engineering

The model uses these features:
- **Team Attributes**: buildUpPlaySpeed, buildUpPlayPassing, chanceCreationShooting, defencePressure, etc.
- **Historical Stats**: Each team's win rate and average goals from past matches
- **Betting Odds**: B365, BW, IW, LB odds (strong predictors)

### Model Training

- **Algorithm**: XGBoost Classifier
- **Tuning**: RandomizedSearchCV with 20 iterations
- **Validation**: 5-fold cross-validation
- **Target**: Home Win / Draw / Away Win

---

## 🖥️ Screenshots

The web app features:
- Large accuracy badge at the top
- Dropdown filters for Season and League
- Statistics bar showing total matches and correct predictions
- Color-coded table (green = correct, red = wrong)
- Responsive dark-themed design

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.8+ | Programming language |
| Flask | Web framework |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Scikit-learn | ML utilities |
| XGBoost | Classification algorithm |
| Joblib | Model serialization |
| HTML/CSS | Frontend UI |

---

## ❓ Troubleshooting

### "ModuleNotFoundError: No module named 'xyz'"
Run: `pip install -r requirements.txt`

### "FileNotFoundError: model.pkl"
Run: `python train_model.py` first before `python app.py`

### "TemplateNotFound: index.html"
Run: `python setup_files.py` to create template files

### Port 5000 already in use
Either stop the other process or change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## 📄 License

This project is for educational purposes.

---

## 👤 Author

Football Match Result Predictor - ML Web Application

---

**Happy Predicting! ⚽🏆**
