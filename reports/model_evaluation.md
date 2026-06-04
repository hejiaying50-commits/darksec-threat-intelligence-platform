# DarkSec Model Evaluation

## Binary Classification
- Model: `RandomForest`
- Accuracy: 1.0000
- Precision: 1.0000
- Recall: 1.0000
- F1-score: 1.0000

### Classification Report
```text
              precision    recall  f1-score   support

      Attack       1.00      1.00      1.00         3
      Normal       1.00      1.00      1.00         1

    accuracy                           1.00         4
   macro avg       1.00      1.00      1.00         4
weighted avg       1.00      1.00      1.00         4
```

### Confusion Matrix
```text
[[3, 0], [0, 1]]
```

## Multi-Class Classification
- Model: `RandomForest`
- Accuracy: 1.0000
- Precision: 1.0000
- Recall: 1.0000
- F1-score: 1.0000

### Classification Report
```text
              precision    recall  f1-score   support

           0       1.00      1.00      1.00         2
           5       1.00      1.00      1.00         2

    accuracy                           1.00         4
   macro avg       1.00      1.00      1.00         4
weighted avg       1.00      1.00      1.00         4
```

### Confusion Matrix
```text
[[2, 0], [0, 2]]
```