from typing import Any, Dict

import streamlit as st
from baicai_dev.agents.graphs.action_builder import ActionBuilder
from baicai_dev.agents.graphs.baseline_builder import BaselineBuilder
from baicai_dev.agents.graphs.dl_builder.dl_builder import DLBuilder
from baicai_dev.agents.graphs.ml_graph import MLGraph
from baicai_dev.agents.graphs.optimization_builder import OptimizationBuilder
from baicai_dev.agents.graphs.workflow_builder import WorkflowBuilder
from baicai_dev.utils.data import TaskType
from baicai_dev.utils.setups import create_dl_config


class GraphExecutor:
    """Handles execution of ML and DL graphs"""

    def __init__(self, llm=None):
        """Initialize GraphExecutor with optional LLM instance"""
        self.llm = llm

    def execute_ml_graph(
        self,
        config: Dict[str, Any],
        code_interpreter=None,
        auto=False,
        start_builder="baseline_builder",
        baseline_codes=None,
        workflow_codes=None,
        actions=None,
    ):
        """Execute ML graph with given configuration"""
        # 验证必要参数
        configurable = config.get("configurable", config)  # 如果没有 configurable 字段，使用原始配置
        required_fields = ["path", "target"]
        missing_fields = [field for field in required_fields if not configurable.get(field)]
        if missing_fields:
            raise ValueError(f"缺少必要的配置参数: {', '.join(missing_fields)}")

        try:
            if auto:
                graph = MLGraph(
                    config=config,
                    start_builder=start_builder,
                    code_interpreter=code_interpreter,
                    need_helper=True,
                    llm=self.llm,
                )
                return graph
            else:
                if start_builder == "baseline_builder":
                    graph = BaselineBuilder(
                        config=config, need_helper=True, code_interpreter=code_interpreter, llm=self.llm
                    )
                elif start_builder == "action_builder":
                    graph = ActionBuilder(
                        config=config,
                        need_helper=True,
                        code_interpreter=code_interpreter,
                        baseline_codes=baseline_codes,
                        llm=self.llm,
                    )
                elif start_builder == "workflow_builder":
                    graph = WorkflowBuilder(
                        config=config,
                        need_helper=True,
                        code_interpreter=code_interpreter,
                        baseline_codes=baseline_codes,
                        actions=actions,
                        llm=self.llm,
                    )
                elif start_builder == "optimization_builder":
                    graph = OptimizationBuilder(
                        config=config,
                        need_helper=True,
                        code_interpreter=code_interpreter,
                        workflow_codes=workflow_codes,
                        llm=self.llm,
                    )
                return graph
        except Exception as e:
            raise ValueError(f"配置参数错误: {str(e)}")

    def execute_dl_graph(self, config: Dict[str, Any], code_interpreter=None):
        """Execute DL graph with given configuration"""
        try:
            # 使用create_dl_config创建标准配置
            dl_config = create_dl_config(config)

            # 创建DLBuilder并返回其app
            builder = DLBuilder(config=dl_config, need_helper=True, code_interpreter=code_interpreter, llm=self.llm)
            return builder
        except Exception as e:
            raise ValueError(f"配置参数错误: {str(e)}")

    def get_graph_for_task(self, task_type: str):
        """Get appropriate graph executor for task type"""
        task_map = {
            TaskType.VISION.value: self.execute_dl_graph,
            TaskType.VISION_CSV.value: self.execute_dl_graph,
            TaskType.VISION_FUNC.value: self.execute_dl_graph,
            TaskType.VISION_RE.value: self.execute_dl_graph,
            TaskType.VISION_MULTI_LABEL.value: self.execute_dl_graph,
            TaskType.VISION_SINGLE_LABEL.value: self.execute_dl_graph,
            TaskType.NLP.value: self.execute_dl_graph,
            TaskType.COLLABORATIVE.value: self.execute_dl_graph,
            TaskType.ML.value: self.execute_ml_graph,
            TaskType.NLP_SENTIMENT_TRAINER.value: self.execute_dl_graph,
            TaskType.NLP_SENTIMENT_INFERENCE.value: self.execute_dl_graph,
            TaskType.NLP_NER_INFERENCE.value: self.execute_dl_graph,
            TaskType.NLP_SEMANTIC_MATCH_INFERENCE.value: self.execute_dl_graph,
        }

        return task_map.get(task_type)


def create_graph_executor(llm=None):
    """Create or get graph executor from session state"""
    if "graph_executor" not in st.session_state:
        st.session_state.graph_executor = GraphExecutor(llm=llm)
    return st.session_state.graph_executor
