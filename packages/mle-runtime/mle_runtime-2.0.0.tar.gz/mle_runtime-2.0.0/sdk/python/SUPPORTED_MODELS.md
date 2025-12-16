# Supported Models - MLE Runtime v1.0.4

## ✅ Fully Supported Models

### Linear Models
- ✅ **LogisticRegression** (multi-class only)
- ✅ **LinearRegression**
- ✅ **Ridge**
- ✅ **Lasso**
- ✅ **SGDRegressor**
- ✅ **LinearSVR**

### Neural Networks
- ✅ **MLPClassifier** (multi-class only)
- ✅ **MLPRegressor**

## ⚠️ Partially Supported Models

### Linear Models
- ⚠️ **LogisticRegression (binary)** - Known issue with binary classification
- ⚠️ **SGDClassifier** - Returns raw logits, not class labels
- ⚠️ **LinearSVC** - Returns raw logits, not class labels

### Neural Networks
- ⚠️ **MLPClassifier (binary)** - Known issue with binary classification

## ❌ Not Yet Supported

### Tree Models
- ❌ **DecisionTreeClassifier** - C++ implementation pending
- ❌ **DecisionTreeRegressor** - C++ implementation pending

### Ensemble Models
- ❌ **RandomForestClassifier** - C++ implementation pending
- ❌ **RandomForestRegressor** - C++ implementation pending
- ❌ **GradientBoostingClassifier** - C++ implementation pending
- ❌ **GradientBoostingRegressor** - C++ implementation pending

### SVM
- ❌ **SVC** - C++ implementation pending
- ❌ **SVR** - C++ implementation pending

### Other Models
- ❌ **GaussianNB** - C++ implementation pending
- ❌ **KNeighborsClassifier** - C++ implementation pending
- ❌ **KNeighborsRegressor** - C++ implementation pending
- ❌ **KMeans** - C++ implementation pending
- ❌ **PCA** - Use transform() instead of predict()

## Known Limitations

### Binary Classification Issue
Binary classification models (LogisticRegression, MLPClassifier with 2 classes) currently have issues because:
- Sklearn outputs 1 value for binary classification
- Our softmax expects 2 values
- **Workaround**: Use multi-class (3+ classes) instead

### Classifier Output Format
Some classifiers (SGDClassifier, LinearSVC) return raw decision function values instead of:
- Class labels (for predict())
- Probabilities (for predict_proba())

This is because they don't have a softmax/sigmoid layer in the export.

## Recommendations

For production use, we recommend:
1. **Regression**: All linear models work great
2. **Multi-class Classification**: LogisticRegression, MLPClassifier
3. **Avoid**: Binary classification, tree-based models (for now)

## Roadmap

Future versions will add:
- Binary classification support
- Decision tree inference
- Ensemble model support (Random Forest, Gradient Boosting)
- SVM kernel implementations
- KNN distance calculations
- Clustering algorithms
