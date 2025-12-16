"""
Regression Notebook Template

回归任务的 Notebook 模板
"""
from typing import Dict, Any, List
from wedata_automl.notebook_generator.templates.base import BaseNotebookTemplate


class RegressionNotebookTemplate(BaseNotebookTemplate):
    """
    回归任务 Notebook 模板
    """
    
    # 估计器名称映射
    ESTIMATOR_MAP = {
        "lgbm": ("LGBMRegressor", "lightgbm"),
        "xgboost": ("XGBRegressor", "xgboost"),
        "xgb_limitdepth": ("XGBRegressor", "xgboost"),
        "rf": ("RandomForestRegressor", "sklearn.ensemble"),
        "extra_tree": ("ExtraTreesRegressor", "sklearn.ensemble"),
    }
    
    def _create_preprocessing_cells(self) -> List[Dict[str, Any]]:
        """创建预处理 Cells"""
        cells = []
        
        # 数据分割说明
        cells.append(self._create_markdown_cell([
            "## Train-Validation-Test Split\n",
            "\n",
            "The data is split into:\n",
            "- **Train** (60%): Used to train the model\n",
            "- **Validation** (20%): Used to tune hyperparameters\n",
            "- **Test** (20%): Used to evaluate final performance\n",
        ]))
        
        # 数据分割代码
        cells.append(self._create_code_cell([
            "from sklearn.model_selection import train_test_split\n",
            "\n",
            f"# Separate features and target\n",
            f"X = df[{self.features}]\n",
            f"y = df['{self.target_col}']\n",
            "\n",
            "# Split into train+val and test\n",
            "X_trainval, X_test, y_trainval, y_test = train_test_split(\n",
            "    X, y, test_size=0.2, random_state=42\n",
            ")\n",
            "\n",
            "# Split train+val into train and val\n",
            "X_train, X_val, y_train, y_val = train_test_split(\n",
            "    X_trainval, y_trainval, test_size=0.25, random_state=42\n",
            ")\n",
            "\n",
            "print(f'Train size: {len(X_train)}')\n",
            "print(f'Validation size: {len(X_val)}')\n",
            "print(f'Test size: {len(X_test)}')\n",
        ]))
        
        # 预处理 Pipeline
        cells.append(self._create_markdown_cell([
            "## Preprocessing Pipeline\n",
            "\n",
            "Create a preprocessing pipeline for numerical features:\n",
            "- Impute missing values with mean\n",
            "- Standardize features\n",
        ]))
        
        cells.append(self._create_code_cell([
            "from sklearn.compose import ColumnTransformer\n",
            "from sklearn.preprocessing import StandardScaler\n",
            "from sklearn.impute import SimpleImputer\n",
            "\n",
            "# Numerical preprocessing\n",
            "numerical_pipeline = Pipeline([\n",
            "    ('imputer', SimpleImputer(strategy='mean')),\n",
            "    ('scaler', StandardScaler()),\n",
            "])\n",
            "\n",
            f"numerical_features = {self.features}\n",
            "\n",
            "preprocessor = ColumnTransformer(\n",
            "    transformers=[\n",
            "        ('num', numerical_pipeline, numerical_features),\n",
            "    ],\n",
            "    remainder='passthrough'\n",
            ")\n",
        ]))
        
        return cells
    
    def _create_model_training_cells(self) -> List[Dict[str, Any]]:
        """创建模型训练 Cells"""
        cells = []
        
        # 获取估计器信息
        estimator_class, estimator_module = self.ESTIMATOR_MAP.get(
            self.best_estimator,
            ("UnknownRegressor", "unknown")
        )
        
        # 模型训练说明
        cells.append(self._create_markdown_cell([
            f"## Train {estimator_class}\n",
            "\n",
            f"Train the best model found by AutoML: **{estimator_class}**\n",
            "\n",
            "The hyperparameters below are the best configuration found during AutoML search.\n",
        ]))
        
        # 导入模型
        cells.append(self._create_code_cell([
            f"from {estimator_module} import {estimator_class}\n",
        ]))
        
        # 超参数配置
        config_str = self._format_config(self.best_config)
        cells.append(self._create_code_cell([
            f"# Best hyperparameters found by AutoML\n",
            f"best_config = {config_str}\n",
        ]))
        
        # 获取模型名称（从 kwargs 或生成默认名称）
        model_name = self.kwargs.get('model_name', f'automl_regression_{self.best_estimator}')

        # 创建和训练模型
        cells.append(self._create_code_cell([
            f"# Create full pipeline\n",
            f"model = Pipeline([\n",
            f"    ('preprocessor', preprocessor),\n",
            f"    ('regressor', {estimator_class}(**best_config)),\n",
            f"])\n",
            f"\n",
            f"# Model name for registration (three-part name: catalog.schema.model)\n",
            f"# You can customize this name\n",
            f"MODEL_NAME = '{model_name}'\n",
            f"\n",
            f"# Train model and register to TCCatalog\n",
            f"with mlflow.start_run(experiment_id='{self.experiment_id}') as run:\n",
            f"    # Disable autolog to have more control\n",
            f"    # mlflow.sklearn.autolog()\n",
            f"    \n",
            f"    # Train the model\n",
            f"    model.fit(X_train, y_train)\n",
            f"    \n",
            f"    # Evaluate on validation set\n",
            f"    val_score = model.score(X_val, y_val)\n",
            f"    mlflow.log_metric('val_{self.metric}', val_score)\n",
            f"    print(f'Validation {self.metric}: {{val_score:.4f}}')\n",
            f"    \n",
            f"    # Infer model signature\n",
            f"    from mlflow.models import infer_signature\n",
            f"    y_pred = model.predict(X_val)\n",
            f"    signature = infer_signature(X_val, y_pred)\n",
            f"    \n",
            f"    # Log and register model to TCCatalog\n",
            f"    mlflow.sklearn.log_model(\n",
            f"        sk_model=model,\n",
            f"        artifact_path='model',\n",
            f"        signature=signature,\n",
            f"        registered_model_name=MODEL_NAME,  # Register to TCCatalog\n",
            f"    )\n",
            f"    \n",
            f"    print(f'✅ Model registered: {{MODEL_NAME}}')\n",
            f"    print(f'   Run ID: {{run.info.run_id}}')\n",
        ]))
        
        return cells
    
    def _create_evaluation_cells(self) -> List[Dict[str, Any]]:
        """创建评估 Cells"""
        cells = []
        
        cells.append(self._create_markdown_cell([
            "## Model Evaluation\n",
            "\n",
            "Evaluate the model on the test set.\n",
        ]))
        
        cells.append(self._create_code_cell([
            "from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score\n",
            "import matplotlib.pyplot as plt\n",
            "\n",
            "# Predictions\n",
            "y_pred = model.predict(X_test)\n",
            "\n",
            "# Metrics\n",
            "mse = mean_squared_error(y_test, y_pred)\n",
            "mae = mean_absolute_error(y_test, y_pred)\n",
            "r2 = r2_score(y_test, y_pred)\n",
            "\n",
            "print(f'Test MSE: {mse:.4f}')\n",
            "print(f'Test MAE: {mae:.4f}')\n",
            "print(f'Test R2: {r2:.4f}')\n",
            "\n",
            "# Scatter plot\n",
            "plt.figure(figsize=(8, 6))\n",
            "plt.scatter(y_test, y_pred, alpha=0.5)\n",
            "plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)\n",
            "plt.xlabel('True Values')\n",
            "plt.ylabel('Predictions')\n",
            "plt.title('True vs Predicted Values')\n",
            "plt.show()\n",
        ]))
        
        return cells
    
    def _format_config(self, config: Dict[str, Any]) -> str:
        """格式化配置为 Python 代码"""
        import json
        return json.dumps(config, indent=4)

