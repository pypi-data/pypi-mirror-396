import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
import xgboost as XGBoost
import catboost as CatBoost
import lightgbm as LightGBM
from sklearn.model_selection import cross_val_predict

class KNNForestRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)
            
        if self.meta_model is None:
            self.meta_model_ = RandomForestRegressor(random_state=42, n_estimators=100, max_depth=10, min_samples_split=5, min_samples_leaf=2, bootstrap=True, n_jobs=-1)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X, 
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)
        
        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))
        
        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)
        
        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)
        
        return self

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)
        
        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))
        
        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNSupportRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)
            
        if self.meta_model is None:
            self.meta_model_ = SVR(random_state=42, kernel='rbf', gamma='scale', C=1.0, epsilon=0.1, max_iter=-1, tol=1e-3, cache_size=200, verbose=False)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X, 
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)
        
        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))
        
        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)
        
        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)
        
        return self

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)
        
        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))
        
        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNDecisionRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)
            
        if self.meta_model is None:
            self.meta_model_ = DecisionTreeRegressor(random_state=42, max_depth=10, min_samples_split=5, min_samples_leaf=2, max_features='sqrt')
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X, 
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)
        
        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))
        
        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)
        
        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)
        
        return self

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)
        
        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))
        
        # 3. Final prediction
        return self.meta_model_.predict(X_meta)
    
class KNNLinearRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = LinearRegression(n_jobs=-1, random_state=42, positive=True, fit_intercept=True)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions
        
        X_meta = np.hstack((X, base_predictions))
        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)
        # 5. Refit the Base Model on the FULL dataset
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)
        return self
    def predict(self, X):
        # 1. Get predictions from the base model
        base_predictions = self.base_model_.predict(X)

        # 2. Stack features (Original features + Base predictions)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 3. Get predictions from the meta model
        return self.meta_model_.predict(X_meta).reshape(-1, 1)
            
class KNNXGBRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = XGBoost.XGBRegressor(objective ='reg:squarederror', random_state=42, n_estimators=100, max_depth=10, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, reg_alpha=0, reg_lambda=1)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self

    def predict(self, X):
        # 1. Get predictions from the base model
        base_predictions = self.base_model_.predict(X)

        # 2. Stack features (Original features + Base predictions)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 3. Get predictions from the meta model
        return self.meta_model_.predict(X_meta).reshape(-1, 1)
    
    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)
        
        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))
        
        # 3. Final prediction
        return self.meta_model_.predict(X_meta).reshape(-1, 1)
    
class KNNCatRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = CatBoost.CatBoostRegressor(verbose=0, random_state=42, iterations=1000, learning_rate=0.1, depth=10, l2_leaf_reg=3, bagging_temperature=1)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self
    
    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)

        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))

        # 3. Final prediction
        return self.meta_model_.predict(X_meta).reshape(-1, 1)

class KNNGradientRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = GradientBoostingRegressor(n_estimators=100, random_state=42, learning_rate=0.1, max_depth=10, min_samples_split=5, min_samples_leaf=2)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self 

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)

        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))

        # 3. Final prediction
        return self.meta_model_.predict(X_meta).reshape(-1, 1)
    
class KNNAdaRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = AdaBoostRegressor(n_estimators=100, random_state=42, learning_rate=0.1, loss='linear')
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self 

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)

        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))

        # 3. Final prediction
        return self.meta_model_.predict(X_meta).reshape(-1, 1)
    
class KNNLightRegressor(BaseEstimator, RegressorMixin):
    def __init__(self, base_model=None, meta_model=None, cv=5):
        self.base_model = base_model
        self.meta_model = meta_model
        self.cv = cv # Number of cross-validation folds

    def fit(self, X, y):
        # 1. Initialize defaults
        if self.base_model is None:
            self.base_model_ = KNeighborsRegressor(random_state=42, n_neighbors=5, weights='distance', algorithm='auto', leaf_size=30, p=2, metric='minkowski', n_jobs=-1)
        else:
            self.base_model_ = clone(self.base_model)

        if self.meta_model is None:
            self.meta_model_ = LightGBM.LGBMRegressor(random_state=42, n_estimators=100, learning_rate=0.1, max_depth=10, num_leaves=31, subsample=0.8, colsample_bytree=0.8)
        else:
            self.meta_model_ = clone(self.meta_model)

        # 2. Generate "out-of-sample" predictions for the meta model
        # We use cross_val_predict ensures that for every point in X,
        # the prediction comes from a model that didn't see that point during training.
        base_predictions = cross_val_predict(self.base_model_, X, y, cv=self.cv)

        # 3. Stack features (Out-of-sample predictions + Original features)
        # Reshape base_predictions to be 2D (n_samples, 1)
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)
        X_meta = np.hstack((X, base_predictions))

        # 4. Train the Meta Model on these "honest" features
        self.meta_model_.fit(X_meta, y)

        # 5. Refit the Base Model on the FULL dataset 
        # (So it is ready for future .predict() calls on new data)
        self.base_model_.fit(X, y)

        return self 

    def predict(self, X):
        if not hasattr(self, 'base_model_') or not hasattr(self, 'meta_model_'):
             raise RuntimeError("You must train the model before predicting!")

        # 1. Get base predictions (Normal predict, since we are now live)
        base_predictions = self.base_model_.predict(X)

        # Ensure 2D shape for concatenation
        if base_predictions.ndim == 1:
            base_predictions = base_predictions.reshape(-1, 1)

        # 2. Stack features
        X_meta = np.hstack((X, base_predictions))

        # 3. Final prediction
        return self.meta_model_.predict(X_meta).reshape(-1, 1)