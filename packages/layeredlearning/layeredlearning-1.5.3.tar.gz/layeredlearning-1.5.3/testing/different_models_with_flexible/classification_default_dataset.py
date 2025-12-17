# Import necessary libraries
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, StackingClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from layerlearn import FlexibleStackedClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
import xgboost as XGBoost
import catboost as CatBoost
import lightgbm as LightGBM 
import warnings

# --- 1. Generate a Synthetic Dataset ---
# This creates a sample dataset for classification tasks.
X, y = make_classification(
    n_samples=10000,
    n_features=20,
    n_informative=10,
    n_redundant=5,
    n_classes=2,
    random_state=42
)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)


# --- 2. Define Base and Meta Models for Stacking ---
estimators = [
    ('lr', LogisticRegression(random_state=42))
]

base_model = LogisticRegression()
meta_model = RandomForestClassifier()

# --- 3. Initialize All Models ---
# Create a dictionary to hold all the models you want to compare.
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Support Vector Classifier": SVC(kernel='rbf', C=1, gamma='auto', random_state=42),
    "Random Forest Classifier": RandomForestClassifier(n_estimators=100, random_state=42),
    "Decision Tree Classifier": DecisionTreeClassifier(random_state=42),
    "KNeighbors Classifier": KNeighborsClassifier(n_neighbors=5),
    "FlexibleStackedClassifier": FlexibleStackedClassifier(base_model, meta_model),
    "StackingClassifier": StackingClassifier(estimators=estimators, final_estimator=meta_model),
    "XGBoost Classifier": XGBoost.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42),
    "Gradient Boosting Classifier": GradientBoostingClassifier(n_estimators=100, random_state=42),
    "AdaBoost Classifier": AdaBoostClassifier(n_estimators=100, random_state=42),
    "XGBoost Classifier": XGBoost.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42),
    "CatBoost Classifier": CatBoost.CatBoostClassifier(verbose=0, random_state=42),
    "LightGBM Classifier": LightGBM.LGBMClassifier(random_state=42)
}

# --- 4. Train Models and Evaluate ---
# This dictionary will store the performance scores.
results = {}
confusion_matrices = {}
classification_reports = {}
warnings.filterwarnings("ignore")
print("Training and evaluating models...")
for name, model in models.items():
    # Train the model on the training data
    model.fit(X_train, y_train)

    # Make predictions on the test data
    y_pred = model.predict(X_test)

    # Calculate the accuracy score and store it
    score = accuracy_score(y_test, y_pred)
    results[name] = score
    confusion_matrices[name] = confusion_matrix(y_test, y_pred)
    classification_reports[name] = classification_report(y_test, y_pred)
    print(f"- {name}: Accuracy score = {score:.4f}")
    print(f"Confusion Matrix:\n{confusion_matrices[name]}")
    print(f"Classification Report:\n{classification_reports[name]}\n")

# --- 5. Create Comparison Graph ---
# Prepare data for plotting
model_names = list(results.keys())
accuracy_scores = list(results.values())

# Create the bar chart
plt.style.use('seaborn-v0_8-darkgrid')
fig, ax = plt.subplots(figsize=(10, 7))

# Create bars with different colors
colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B2', '#CCB974', '#64B5CD', '#8C8C8C']
bars = ax.barh(model_names, accuracy_scores, color=colors)

# Add title and labels
ax.set_title('Comparison of ML Classifier Performance', fontsize=18, fontweight='bold')
ax.set_xlabel('Accuracy Score', fontsize=12)
ax.set_ylabel('Algorithm', fontsize=12)
ax.set_xlim(0, 1.0) # Accuracy score ranges from 0 to 1

# Add the score value on each bar
for bar in bars:
    width = bar.get_width()
    # Position text slightly outside the bar
    label_x_pos = width + 0.01
    ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:.3f}',
            va='center', ha='left', fontsize=11, color='black')

# Invert y-axis to have the best-performing model on top
ax.invert_yaxis()

# Show the plot
plt.show()