import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone, RegressorMixin

class FlexibleStackedClassifier(BaseEstimator, ClassifierMixin):

    def __init__(self, base_model, meta_model):

        self.base_model = clone(base_model)
        self.meta_model = clone(meta_model)

    def fit(self, X, y):

        # Step 1: Train the base model
        self.base_model.fit(X, y)
        
        # Step 2: Get the predicted probabilities from the base model
        base_predictions = self.base_model.predict_proba(X)
        
        # Step 3: Create the new feature set by combining original features
        # with the base model's predicted probabilities.
        X_meta = np.c_[X, base_predictions]
        
        # Step 4: Train the meta model on the new feature set
        self.meta_model.fit(X_meta, y)
        
        return self

    def predict(self, X):

        # Get probabilities from the base model and create the meta feature set
        base_predictions = self.base_model.predict_proba(X)
        X_meta = np.c_[X, base_predictions]
        
        # Make the final prediction using the meta model's .predict() method
        return self.meta_model.predict(X_meta)

    def predict_proba(self, X):

        # Get probabilities from the base model and create the meta feature set
        base_predictions = self.base_model.predict_proba(X)
        X_meta = np.c_[X, base_predictions]
        
        # Get the final probabilities from the meta model's .predict_proba() method
        return self.meta_model.predict_proba(X_meta)
    
class FlexibleStackedRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, base_model, meta_model):

        # Use clone to ensure that the original models are not modified
        self.base_model = clone(base_model)
        self.meta_model = clone(meta_model)

    def fit(self, X, y):
        # Step 1: Train the base model
        self.base_model.fit(X, y)
        
        # Step 2: Get predictions from the base model
        base_predictions = self.base_model.predict(X)
        
        # Step 3: Create the new feature set by combining original features
        # with the base model's predictions.
        X_meta = np.c_[X, base_predictions]
        
        # Step 4: Train the meta model on the new feature set
        self.meta_model.fit(X_meta, y)
        
        return self

    def predict(self, X):
        # Step 1: Get predictions from the base model
        base_predictions = self.base_model.predict(X)
        
        # Step 2: Create the meta feature set for prediction
        X_meta = np.c_[X, base_predictions]
        
        # Step 3: Make the final prediction using the meta model
        return self.meta_model.predict(X_meta)