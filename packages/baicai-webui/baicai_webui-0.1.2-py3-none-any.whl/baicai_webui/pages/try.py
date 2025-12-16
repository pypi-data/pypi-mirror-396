import streamlit as st


def try_display_results():
    from baicai_dev.utils.setups import (
        ACTIONS_WITH_CODE_IRIS,
        BASELINE_CODES_IRIS,
        WORKFLOW_CODE_IRIS,
    )

    from baicai_webui.components.model import display_results

    st.title("结果展示")

    state = {
        "baseline_codes": [BASELINE_CODES_IRIS[0], BASELINE_CODES_IRIS[0]],
        "baseline_success": True,
        "actions": ACTIONS_WITH_CODE_IRIS,
        "action_success": True,
        "workflow_codes": WORKFLOW_CODE_IRIS,
        "workflow_success": True,
        "optimization_codes": WORKFLOW_CODE_IRIS,
        "optimization_success": True,
    }

    display_results(state)


def try_stepper():
    import time

    import streamlit as st

    from baicai_webui.components.stepper import StepperBar

    async def run_baseline_builder():
        time.sleep(1)
        st.write("运行基线模型")
        return True

    async def run_action_builder():
        time.sleep(1)
        st.write("运行特征工程")
        return True

    async def run_workflow_builder():
        time.sleep(1)
        st.write("运行工作流构建")
        return True

    async def run_optimization_builder():
        time.sleep(1)
        st.write("运行模型优化")
        return True

    NORMAL_GRAPH = """
    graph LR;
        __start__[开始]
        coder[{graph_name}构建]:::first
        run[{graph_name}运行]
        debugger[{graph_name}调试]
        helper[{graph_name}问答]
        __end__[结束]:::last
        __start__ --> coder
        helper --> __end__
        coder -.-> run
        coder -.-> helper
        run -.-> debugger
        run -.-> helper
        debugger -.-> run
        debugger -.-> helper
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
    """

    ACTION_GRAPH = """
    graph LR;
        __start__[开始]:::first
        reasoner[特征工程分析]
        action_coder[特征工程代码生成]
        run_action[特征工程运行]
        action_evaluator[特征工程评估]
        action_debugger[特征工程调试]
        helper[特征工程问答]
        __end__[结束]:::last
        __start__ --> reasoner
        action_coder --> run_action
        helper --> __end__
        reasoner -.-> action_coder
        reasoner -.-> __end__
        run_action -.-> action_debugger
        run_action -.-> action_evaluator
        run_action -.-> __end__
        action_debugger -.-> run_action
        action_debugger -.-> __end__
        action_evaluator -.-> helper
        action_evaluator -.-> __end__
        classDef default fill:#f2f0ff,line-height:1.2
        classDef first fill-opacity:0
        classDef last fill:#bfb6fc
    """

    st.title("Stepper Bar")

    steps = [
        ("1. 基线模型", run_baseline_builder, NORMAL_GRAPH.format(graph_name="基线模型")),
        ("2. 特征工程", run_action_builder, ACTION_GRAPH),
        ("3. 工作流构建", run_workflow_builder, NORMAL_GRAPH.format(graph_name="工作流")),
        ("4. 模型优化", run_optimization_builder, NORMAL_GRAPH.format(graph_name="模型优化")),
    ]

    # 创建步骤条
    if "stepper" not in st.session_state:
        st.session_state.stepper = StepperBar(steps, 0)

    # 显示步骤条
    stepper = st.session_state.stepper
    st.markdown(stepper(), unsafe_allow_html=True)


def try_tabular_shap():
    from pathlib import Path

    from baicai_webui.components.model import create_shap_analysis

    create_shap_analysis(
        data_path=Path(r"C:\Users\gengyabc\.baicai\tmp\data\churn\baseline_20250409-082117.pkl"),
        model_path=Path(r"C:\Users\gengyabc\.baicai\tmp\models\churn\baseline_20250409-082117.pkl"),
    )


def try_surveyor():
    from baicai_webui.components.tutor import survey_flow

    result = survey_flow()
    if result:
        st.json(result)


def try_book_chapters():
    from baicai_webui.components.tutor import select_book_chapters

    select_book_chapters()


def try_ai_tutor():
    from baicai_webui.components.tutor import create_ai_tutor

    create_ai_tutor(from_level=3, terms=["线性回归", "逻辑回归", "神经网络"], debug=True)


def try_button_graph():
    from baicai_webui.components.button_graph import button_graph

    button_graph()


def try_model_settings():
    from baicai_webui.components.model.model_settings import render_model_settings

    render_model_settings()


def show():
    # try_display_results()
    # try_stepper()
    # try_plot()
    # try_surveyor()
    # try_ai_tutor()
    # try_book_chapters()
    # try_tabular_shap()
    # try_button_graph()
    try_model_settings()

show()