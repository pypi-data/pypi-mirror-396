"""
Base Notebook Template

所有 Notebook 模板的基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseNotebookTemplate(ABC):
    """
    Notebook 模板基类
    """
    
    def __init__(
        self,
        best_estimator: str,
        best_config: Dict[str, Any],
        experiment_id: str,
        run_id: str,
        mlflow_tracking_uri: str,
        features: List[str],
        target_col: str,
        metric: str,
        data_source_table: Optional[str] = None,
        **kwargs
    ):
        """
        初始化模板

        Args:
            best_estimator: 最佳估计器名称
            best_config: 最佳超参数配置
            experiment_id: MLflow 实验 ID
            run_id: MLflow Run ID
            mlflow_tracking_uri: MLflow Tracking URI
            features: 特征列名列表
            target_col: 目标列名
            metric: 评估指标
            data_source_table: 数据源表名（如果用户传入表名）
            **kwargs: 其他参数
        """
        self.best_estimator = best_estimator
        self.best_config = best_config
        self.experiment_id = experiment_id
        self.run_id = run_id
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.features = features
        self.target_col = target_col
        self.metric = metric
        self.data_source_table = data_source_table
        self.kwargs = kwargs
    
    def generate(self) -> Dict[str, Any]:
        """
        生成 Notebook

        Returns:
            Notebook 字典
        """
        cells = []

        # 添加各个 Cell
        cells.append(self._create_header_cell())
        cells.append(self._create_import_cell())
        cells.append(self._create_mlflow_setup_cell())
        cells.append(self._create_load_data_cell())
        cells.extend(self._create_preprocessing_cells())
        cells.extend(self._create_model_training_cells())
        cells.extend(self._create_evaluation_cells())
        cells.extend(self._create_model_registration_cells())
        cells.append(self._create_inference_cell())

        # 构建 Notebook
        notebook = {
            "cells": cells,
            "metadata": self._create_metadata(),
            "nbformat": 4,
            "nbformat_minor": 5
        }
        
        return notebook
    
    @abstractmethod
    def _create_preprocessing_cells(self) -> List[Dict[str, Any]]:
        """创建预处理 Cells"""
        pass
    
    @abstractmethod
    def _create_model_training_cells(self) -> List[Dict[str, Any]]:
        """创建模型训练 Cells"""
        pass
    
    @abstractmethod
    def _create_evaluation_cells(self) -> List[Dict[str, Any]]:
        """创建评估 Cells"""
        pass
    
    def _create_header_cell(self) -> Dict[str, Any]:
        """创建标题 Cell"""
        task_name = self.__class__.__name__.replace("NotebookTemplate", "")
        return self._create_markdown_cell([
            f"# {task_name} Training - Auto-generated Notebook\n",
            "\n",
            "- This is an auto-generated notebook by WeData AutoML.\n",
            f"- Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"- Best Estimator: **{self.best_estimator}**\n",
            f"- Metric: **{self.metric}**\n",
            f"- MLflow Experiment: [{self.experiment_id}]({self.mlflow_tracking_uri}/#/experiments/{self.experiment_id})\n",
            f"- MLflow Run: [{self.run_id}]({self.mlflow_tracking_uri}/#/experiments/{self.experiment_id}/runs/{self.run_id})\n",
        ])
    
    def _create_import_cell(self) -> Dict[str, Any]:
        """创建导入 Cell"""
        return self._create_code_cell([
            "import os\n",
            "import mlflow\n",
            "import mlflow.sklearn\n",
            "import pandas as pd\n",
            "import numpy as np\n",
            "from sklearn.pipeline import Pipeline\n",
            "from sklearn.preprocessing import StandardScaler\n",
            "from sklearn.impute import SimpleImputer\n",
        ])
    
    def _create_mlflow_setup_cell(self) -> Dict[str, Any]:
        """创建 MLflow 设置 Cell"""
        return self._create_code_cell([
            f"# Set MLflow tracking URI\n",
            f"mlflow.set_tracking_uri('{self.mlflow_tracking_uri}')\n",
            f"\n",
            f"# Set MLflow registry URI (TCLake plugin for model registration)\n",
            f"region = os.environ.get('QCLOUD_REGION', 'ap-guangzhou')\n",
            f"mlflow.set_registry_uri(f'tclake:{{region}}')\n",
            f"print(f'Registry URI: tclake:{{region}}')\n",
            f"\n",
            f"# Set experiment\n",
            f"mlflow.set_experiment(experiment_id='{self.experiment_id}')\n",
        ])
    
    def _create_load_data_cell(self) -> Dict[str, Any]:
        """创建数据加载 Cell"""
        if self.data_source_table:
            # 用户传入了表名，使用 spark.table() 加载数据
            return self._create_code_cell([
                f"# Load training data from the same table used during training\n",
                f"from pyspark.sql import SparkSession\n",
                f"\n",
                f"# Get or create Spark session\n",
                f"spark = SparkSession.builder.getOrCreate()\n",
                f"\n",
                f"# Load data from table\n",
                f"table_name = '{self.data_source_table}'\n",
                f"df = spark.table(table_name).toPandas()\n",
                f"print(f'Data source: {{table_name}}')\n",
                f"print(f'Data shape: {{df.shape}}')\n",
                f"df.head()\n",
            ])
        else:
            # 用户传入的是 DataFrame，无法自动加载
            return self._create_code_cell([
                f"# Load training data\n",
                f"# Note: The original training used a DataFrame directly (not a table name).\n",
                f"# Please load your data using one of the following methods:\n",
                f"#   1. Load from table: df = spark.table('catalog.database.table_name').toPandas()\n",
                f"#   2. Load from parquet: df = pd.read_parquet('path/to/your/data.parquet')\n",
                f"#   3. Load from CSV: df = pd.read_csv('path/to/your/data.csv')\n",
                f"\n",
                f"# df = spark.table('your_table_name').toPandas()\n",
                f"# print(f'Data shape: {{df.shape}}')\n",
                f"# df.head()\n",
            ])
    
    def _create_model_registration_cells(self) -> List[Dict[str, Any]]:
        """创建模型注册到 Catalog 的 Cells

        使用 mlflow-tclake-plugin 将模型注册到 TencentCloud Catalog。
        需要先安装：pip install mlflow-tclake-plugin

        环境变量要求：
        - TENCENTCLOUD_SECRET_ID: 腾讯云 Secret ID
        - TENCENTCLOUD_SECRET_KEY: 腾讯云 Secret Key
        - TENCENTCLOUD_ENDPOINT: tccatalog API 端点
        - WEDATA_PROJECT_ID: WeData 项目 ID
        - QCLOUD_REGION: 腾讯云地域（如 ap-beijing）
        """
        cells = []

        # 获取 region，优先从 kwargs 获取，否则使用默认值
        region = self.kwargs.get('catalog_region', 'ap-beijing')

        if not self.data_source_table:
            # 没有数据源表名，提供手动配置的示例
            cells.append(self._create_markdown_cell([
                "## Register Model to TCCatalog\n",
                "\n",
                "Use `mlflow-tclake-plugin` to register the model to TencentCloud Catalog.\n",
                "\n",
                "**Note**: No data source table was provided during training.\n",
                "Please provide the catalog, schema, and model name manually.\n",
                "\n",
                "**Required environment variables**:\n",
                "- `TENCENTCLOUD_SECRET_ID`\n",
                "- `TENCENTCLOUD_SECRET_KEY`\n",
                "- `TENCENTCLOUD_ENDPOINT`\n",
                "- `WEDATA_PROJECT_ID`\n",
            ]))
            cells.append(self._create_code_cell([
                "# Install mlflow-tclake-plugin if not already installed\n",
                "# !pip install mlflow-tclake-plugin\n",
                "\n",
                "import mlflow\n",
                "import os\n",
                "\n",
                "# Configure TCLake as MLflow model registry\n",
                f"region = os.getenv('QCLOUD_REGION', '{region}')\n",
                "mlflow.set_registry_uri(f'tclake:{region}')\n",
                "\n",
                "# TODO: Uncomment and fill in the values below\n",
                "# registered_model_name = 'catalog.schema.model_name'\n",
                "#\n",
                "# # Re-log the model with registration\n",
                "# with mlflow.start_run(run_id=run_id):\n",
                "#     mlflow.sklearn.log_model(\n",
                "#         sk_model=model,\n",
                "#         artifact_path='model',\n",
                "#         registered_model_name=registered_model_name,\n",
                "#     )\n",
                "#     print(f'✅ Model registered to: {registered_model_name}')\n",
            ]))
            return cells

        # 解析三段式表名并生成模型注册代码
        cells.append(self._create_markdown_cell([
            "## Register Model to TCCatalog\n",
            "\n",
            "Use `mlflow-tclake-plugin` to register the trained model to TencentCloud Catalog.\n",
            "\n",
            "The model will be registered using the same catalog and schema as the training data.\n",
            "\n",
            "**Required environment variables**:\n",
            "- `TENCENTCLOUD_SECRET_ID`\n",
            "- `TENCENTCLOUD_SECRET_KEY`\n",
            "- `TENCENTCLOUD_ENDPOINT`\n",
            "- `WEDATA_PROJECT_ID`\n",
        ]))

        # 获取模型名称
        model_name = self.kwargs.get('model_name', f'automl_{self.best_estimator}')

        cells.append(self._create_code_cell([
            "# Install mlflow-tclake-plugin if not already installed\n",
            "# !pip install mlflow-tclake-plugin\n",
            "\n",
            "import mlflow\n",
            "import os\n",
            "\n",
            "# Parse the three-part table name (catalog.schema.table_name)\n",
            f"data_source_table = '{self.data_source_table}'\n",
            "table_parts = data_source_table.split('.')\n",
            "\n",
            "if len(table_parts) >= 3:\n",
            "    catalog_name = table_parts[0]\n",
            "    schema_name = table_parts[1]\n",
            "elif len(table_parts) == 2:\n",
            "    catalog_name = os.getenv('TENCENTCLOUD_DEFAULT_CATALOG_NAME', 'default')\n",
            "    schema_name = table_parts[0]\n",
            "else:\n",
            "    catalog_name = os.getenv('TENCENTCLOUD_DEFAULT_CATALOG_NAME', 'default')\n",
            "    schema_name = os.getenv('TENCENTCLOUD_DEFAULT_SCHEMA_NAME', 'default')\n",
            "\n",
            f"# Model name for registration (format: catalog.schema.model_name)\n",
            f"model_name = '{model_name}'\n",
            "registered_model_name = f'{catalog_name}.{schema_name}.{model_name}'\n",
            "\n",
            "print(f'Catalog: {catalog_name}')\n",
            "print(f'Schema: {schema_name}')\n",
            "print(f'Model Name: {model_name}')\n",
            "print(f'Registered Model Name: {registered_model_name}')\n",
        ]))

        cells.append(self._create_code_cell([
            "# Configure TCLake as MLflow model registry\n",
            f"region = os.getenv('QCLOUD_REGION', '{region}')\n",
            "mlflow.set_registry_uri(f'tclake:{region}')\n",
            "\n",
            "# Register the model to TCCatalog\n",
            "model_uri = f'runs:/{run_id}/model'\n",
            "result = mlflow.register_model(model_uri, registered_model_name)\n",
            "\n",
            "print(f'✅ Model registered to TCCatalog!')\n",
            "print(f'   Model Name: {result.name}')\n",
            "print(f'   Version: {result.version}')\n",
            "print(f'   Source: {result.source}')\n",
        ]))

        return cells

    def _create_inference_cell(self) -> Dict[str, Any]:
        """创建推理 Cell"""
        return self._create_code_cell([
            f"# Load model for inference\n",
            f"model_uri = f'runs:/{{run_id}}/model'\n",
            f"model = mlflow.pyfunc.load_model(model_uri)\n",
            f"\n",
            f"# Make predictions\n",
            f"# predictions = model.predict(test_data)\n",
            f"# print(predictions)\n",
        ])
    
    @staticmethod
    def _create_code_cell(source: List[str]) -> Dict[str, Any]:
        """创建代码 Cell"""
        return {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source
        }
    
    @staticmethod
    def _create_markdown_cell(source: List[str]) -> Dict[str, Any]:
        """创建 Markdown Cell"""
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": source
        }
    
    def _create_metadata(self) -> Dict[str, Any]:
        """创建 Notebook 元数据"""
        return {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        }

