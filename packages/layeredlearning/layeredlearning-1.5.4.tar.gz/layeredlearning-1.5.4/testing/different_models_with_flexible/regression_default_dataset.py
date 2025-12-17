# Import necessary libraries
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, StackingRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.svm import SVR
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from layerlearn import FlexibleStackedRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
import xgboost as XGBoost
import catboost as CatBoost
import lightgbm as LightGBM
import warnings

warnings.filterwarnings("ignore")

# --- 1. Generate or Load Dataset ---
# This creates a sample dataset for regression tasks.
X, y = make_regression(n_samples=10000, n_features=10, n_informative=5, noise=15, random_state=42)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# --- 2. Define Base and Meta Models for Stacking ---
# Define base and meta models for the FlexibleStackedRegressor
base_model1 = LinearRegression()
meta_model1 = RandomForestRegressor(random_state=42)

# --- 3. Initialize All Models ---
# Create a dictionary to hold all the models you want to compare.
models = {
    "Linear Regression": LinearRegression(),
    "Support Vector Regressor": SVR(kernel='rbf', C=100, gamma=0.1, epsilon=.1),
    "Random Forest Regressor": RandomForestRegressor(n_estimators=100, random_state=42),
    "Decision Tree Regressor": DecisionTreeRegressor(random_state=42),
    "KNeighbors Regressor": KNeighborsRegressor(n_neighbors=5),
    "FlexibleStackedRegressor": FlexibleStackedRegressor(base_model1, meta_model1),
    "StackingRegressor": StackingRegressor(estimators=[('base', base_model1)], final_estimator=meta_model1),
    "GradientBoostingRegressor": GradientBoostingRegressor(n_estimators=100, random_state=42),
    "AdaBoostRegressor": AdaBoostRegressor(n_estimators=100, random_state=42),
    "XGBoost Regressor": XGBoost.XGBRegressor(objective ='reg:squarederror', n_estimators=100, random_state=42),
    "CatBoost Regressor": CatBoost.CatBoostRegressor(verbose=0, random_state=42),
    "LightGBM Regressor": LightGBM.LGBMRegressor(random_state=42)
}

# --- 4. Train Models and Evaluate ---
results = {}
errors = {}

print("Training and evaluating models...")
for name, model in models.items():
    try:
        # Train the model on the training data
        model.fit(X_train, y_train)

        # Make predictions on the test data
        y_pred = model.predict(X_test)

        # Calculate the R-squared score and store it
        score = r2_score(y_test, y_pred)
        results[name] = score
        mean_absolute_error_val = mean_absolute_error(y_test, y_pred)
        mean_squared_error_val = mean_squared_error(y_test, y_pred)
        print(f"- {name}: R2 score = {score:.4f}")
        print(f"  Mean Absolute Error: {mean_absolute_error_val:.4f}")
        print(f"  Mean Squared Error: {mean_squared_error_val:.4f}\n")
    except Exception as e:
        errors[name] = str(e)
        print(f"- {name}: ERROR -> {e}")

if not results:
    raise RuntimeError("No model produced a valid result. Check errors: " + str(errors))

# --- 5. Create Comparison Graph ---
# Prepare data for plotting
model_names = list(results.keys())
r2_scores = list(results.values())

# Create the bar chart
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(10, 7))

# Generate colors to match number of models
colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD', '#8C8C8C']
bars = ax.barh(model_names, r2_scores, color=colors)

# Add title and labels
ax.set_title('Comparison of ML Regressor Performance', fontsize=18, fontweight='bold')
ax.set_xlabel('R-squared Score', fontsize=12)
ax.set_ylabel('Algorithm', fontsize=12)

# Adjust x-limits to include negative R² if present
min_score = min(r2_scores)
max_score = max(r2_scores)
margin = max(0.05, (max_score - min_score) * 0.05)
ax.set_xlim(min_score - margin, max_score + margin)

# Add the score value on each bar
for bar in bars:
    width = bar.get_width()
    label_x_pos = width + (margin * 0.5)
    ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.3f}',
            va='center', ha='left', fontsize=11)

# Invert y-axis to have the best model on top (optional)
ax.invert_yaxis()

plt.tight_layout()
# Show the plot
plt.show()

# If there were errors, print them after plotting
if errors:
    print("\nModels that failed:")
    for name, err in errors.items():
        print(f"- {name}: {err}")