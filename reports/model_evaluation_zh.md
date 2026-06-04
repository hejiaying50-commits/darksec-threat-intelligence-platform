# DarkSec 模型评估报告

## 二分类任务
- 模型：`RandomForest`
- 准确率 Accuracy：`1.0000`
- 精确率 Precision：`1.0000`
- 召回率 Recall：`1.0000`
- F1-score：`1.0000`

### 分类报告
```text
              precision    recall  f1-score   support

      Attack       1.00      1.00      1.00         3
      Normal       1.00      1.00      1.00         1

    accuracy                           1.00         4
   macro avg       1.00      1.00      1.00         4
weighted avg       1.00      1.00      1.00         4
```

### 混淆矩阵
```text
[[3, 0], [0, 1]]
```

## 多分类任务
- 模型：`RandomForest`
- 准确率 Accuracy：`1.0000`
- 精确率 Precision：`1.0000`
- 召回率 Recall：`1.0000`
- F1-score：`1.0000`

### 分类报告
```text
              precision    recall  f1-score   support

           0       1.00      1.00      1.00         2
           5       1.00      1.00      1.00         2

    accuracy                           1.00         4
   macro avg       1.00      1.00      1.00         4
weighted avg       1.00      1.00      1.00         4
```

### 混淆矩阵
```text
[[2, 0], [0, 2]]
```

## 结果说明
- 当前评估结果基于仓库内置的小型演示数据，因此指标较高，仅用于验证项目流程是否跑通。
- 当替换为 Kaggle 下载的 CICIDS2017 全量数据后，评估结果会更具有真实分析价值。
- 在真实数据场景下，建议进一步比较 `RandomForest` 与 `XGBoost` 的表现，并结合类别不平衡情况优化特征工程与采样策略。
