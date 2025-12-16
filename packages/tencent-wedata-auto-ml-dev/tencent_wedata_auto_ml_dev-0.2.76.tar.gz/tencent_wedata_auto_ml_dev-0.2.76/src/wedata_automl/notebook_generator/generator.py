"""
Notebook Generator

生成可复现的 Jupyter Notebook
"""
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

from wedata_automl.notebook_generator.templates import (
    ClassificationNotebookTemplate,
    RegressionNotebookTemplate,
    ForecastNotebookTemplate,
)


class NotebookGenerator:
    """
    Notebook 生成器
    
    根据 AutoML 训练结果生成可复现的 Jupyter Notebook
    """
    
    TEMPLATE_MAP = {
        "classification": ClassificationNotebookTemplate,
        "regression": RegressionNotebookTemplate,
        "forecast": ForecastNotebookTemplate,
    }
    
    def __init__(
        self,
        task: str,
        best_estimator: str,
        best_config: Dict[str, Any],
        experiment_id: str,
        run_id: str,
        mlflow_tracking_uri: str,
        features: List[str],
        target_col: str,
        metric: str,
        **kwargs
    ):
        """
        初始化 Notebook 生成器
        
        Args:
            task: 任务类型 ("classification", "regression", "forecast")
            best_estimator: 最佳估计器名称
            best_config: 最佳超参数配置
            experiment_id: MLflow 实验 ID
            run_id: MLflow Run ID
            mlflow_tracking_uri: MLflow Tracking URI
            features: 特征列名列表
            target_col: 目标列名
            metric: 评估指标
            **kwargs: 其他任务特定参数
        """
        if task not in self.TEMPLATE_MAP:
            raise ValueError(f"Unsupported task: {task}. Supported: {list(self.TEMPLATE_MAP.keys())}")
        
        self.task = task
        self.best_estimator = best_estimator
        self.best_config = best_config
        self.experiment_id = experiment_id
        self.run_id = run_id
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.features = features
        self.target_col = target_col
        self.metric = metric
        self.kwargs = kwargs
        
        # 获取对应的模板类
        self.template_class = self.TEMPLATE_MAP[task]
    
    def generate(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        生成 Notebook
        
        Args:
            output_path: 输出路径（可选）。如果提供，将保存到文件
        
        Returns:
            Notebook 字典（符合 Jupyter Notebook 格式）
        """
        # 创建模板实例
        template = self.template_class(
            best_estimator=self.best_estimator,
            best_config=self.best_config,
            experiment_id=self.experiment_id,
            run_id=self.run_id,
            mlflow_tracking_uri=self.mlflow_tracking_uri,
            features=self.features,
            target_col=self.target_col,
            metric=self.metric,
            **self.kwargs
        )
        
        # 生成 Notebook
        notebook = template.generate()
        
        # 如果提供了输出路径，保存到文件
        if output_path:
            self._save_notebook(notebook, output_path)
        
        return notebook
    
    def _save_notebook(self, notebook: Dict[str, Any], output_path: str):
        """
        保存 Notebook 到文件
        
        Args:
            notebook: Notebook 字典
            output_path: 输出路径
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # 保存为 JSON
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(notebook, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Notebook 已保存到: {output_path}")
    
    @staticmethod
    def create_cell(cell_type: str, source: List[str], metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        创建 Notebook Cell
        
        Args:
            cell_type: Cell 类型 ("code", "markdown")
            source: Cell 内容（行列表）
            metadata: Cell 元数据
        
        Returns:
            Cell 字典
        """
        cell = {
            "cell_type": cell_type,
            "metadata": metadata or {},
            "source": source
        }
        
        if cell_type == "code":
            cell["execution_count"] = None
            cell["outputs"] = []
        
        return cell

