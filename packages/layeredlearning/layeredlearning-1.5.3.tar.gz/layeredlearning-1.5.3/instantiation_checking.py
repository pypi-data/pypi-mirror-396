# Import the classes from your newly installed package
from layerlearn import FlexibleStackedClassifier, FlexibleStackedRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

print("[SUCCESS] Successfully imported from the layerlearn package!")

# You can even instantiate the classes to make sure they work
try:
    # We need to pass dummy models to test instantiation
    base_model1 = LogisticRegression()
    meta_model1 = RandomForestClassifier()
    
    base_model2 = LinearRegression()
    meta_model2 = RandomForestRegressor()

    classifier = FlexibleStackedClassifier(base_model1, meta_model1)
    regressor = FlexibleStackedRegressor(base_model2, meta_model2)
    print("[SUCCESS] Successfully created a FlexibleStackedClassifier instance.")
    print("[SUCCESS] Successfully created a FlexibleStackedRegressor instance.")
except Exception as e:
    print(f"[ERROR] Failed to instantiate classes. Error: {e}")