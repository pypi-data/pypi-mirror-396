import asyncio

import streamlit as st
from baicai_base.utils.data import get_saved_pickle_path
from baicai_base.utils.setups import setup_code_interpreter
from baicai_dev.utils.data import TaskType

from baicai_webui.components.chat import ai_assistant
from baicai_webui.components.model import (
    create_shap_analysis,
    create_training_monitor,
    display_results,
    get_page_llm,
    ml_uploader,
)
from baicai_webui.components.stepper import StepperBar

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


def run():
    st.session_state.running = True


def restart():
    st.session_state.runned = False
    st.session_state.result = None
    st.session_state.helper_ready = False
    st.session_state.messages = []
    st.session_state.graph_state = None
    st.session_state.running = False
    # 重置 stepper 相关状态
    if "stepper" in st.session_state:
        st.session_state.stepper.reset_states()
    # 重置步骤相关状态
    st.session_state.current_step = 0
    st.session_state.step_status = [False] * 4  # 4个步骤的状态
    # 重置保存的模型代码
    st.session_state.baseline_codes = None
    st.session_state.baseline_success = False
    st.session_state.actions = None
    st.session_state.action_success = False
    st.session_state.workflow_codes = None
    st.session_state.workflow_success = False
    st.session_state.optimization_codes = None
    st.session_state.optimization_success = False
    # 清理消息占位符
    if "message_placeholders" in st.session_state:
        st.session_state.message_placeholders = {}
    # 重新运行页面以刷新UI
    st.rerun()


def _init_session_state():
    # Initialize LLM with the new configuration method
    llm = get_page_llm(
        config_id="ml_llm", title="机器学习模型配置", info_text="配置用于机器学习任务的模型参数", expanded=False
    )

    # 训练监控
    if "monitor" not in st.session_state:
        st.session_state.monitor = create_training_monitor(llm=llm)
    monitor = st.session_state.monitor

    if "code_interpreter" not in st.session_state:
        st.session_state.code_interpreter = setup_code_interpreter()

    if "running" not in st.session_state:
        st.session_state.running = False
        st.session_state.result = None
        st.session_state.helper_ready = False

    # 初始化运行模式
    if "run_mode" not in st.session_state:
        st.session_state.run_mode = "manual"

    if "baseline_codes" not in st.session_state:
        st.session_state.baseline_codes = None

    if "baseline_success" not in st.session_state:
        st.session_state.baseline_success = False

    if "actions" not in st.session_state:
        st.session_state.actions = None

    if "action_success" not in st.session_state:
        st.session_state.action_success = False

    if "workflow_codes" not in st.session_state:
        st.session_state.workflow_codes = None

    if "workflow_success" not in st.session_state:
        st.session_state.workflow_success = False

    if "optimization_codes" not in st.session_state:
        st.session_state.optimization_codes = None

    if "optimization_success" not in st.session_state:
        st.session_state.optimization_success = False

    # 初始化错误消息状态
    if "error_message" not in st.session_state:
        st.session_state.error_message = None

    if "runned" not in st.session_state:
        st.session_state.runned = False

    if "graph_state" not in st.session_state:
        st.session_state.graph_state = None

    return monitor


def show():
    """
    显示机器学习任务页面
    参考：https://stackoverflow.com/questions/76321835/hide-button-while-model-is-running-in-streamlit
    """
    monitor = _init_session_state()

    st.title("传统机器学习")

    # 创建选项卡
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 智能体配置", "📈结果查看", "🔍 模型解释", "💬 AI助手"])

    if "running" not in st.session_state:
        st.session_state.running = False

    if "result" not in st.session_state:
        st.session_state.result = None

    lock = st.session_state.running or st.session_state.result is not None

    with tab1:
        # 数据上传和配置
        data_config = ml_uploader()

        if not data_config:
            st.warning("请上传数据")
            return

        data_config["configurable"]["from_web_ui"] = True
        name = data_config["configurable"]["name"]

        st.session_state.data_config = data_config

        # 选择运行模式
        st.subheader("运行模式")

        # 初始化 run_mode_radio key
        if "run_mode_radio" not in st.session_state:
            st.session_state.run_mode_radio = "自动模式" if st.session_state.run_mode == "auto" else "手动模式"

        # 使用 on_change 回调来更新 run_mode
        def update_run_mode():
            st.session_state.run_mode = "auto" if st.session_state.run_mode_radio == "自动模式" else "manual"

        # 直接使用 session_state 作为 radio 的值
        st.radio(
            "选择运行模式",
            options=["自动模式", "手动模式"],
            horizontal=True,
            key="run_mode_radio",
            on_change=update_run_mode,
        )

        st.markdown("---")

        # 根据模式显示不同的操作界面
        if st.session_state.run_mode == "auto":
            show_auto_mode(monitor, lock, run, restart)
        else:
            show_manual_mode(monitor, lock, restart)

    with tab2:
        # 显示结果组件
        if "graph_state" in st.session_state:
            display_results(st.session_state.graph_state)
        else:
            st.warning("请先上传数据并运行训练过程")

    with tab3:
        if not st.session_state.runned:
            st.warning("没有模型结果，请稍后再试")
            return

        if st.session_state.run_mode == "auto":
            title = "最终模型解释"
            model_prefix = "best"
            data_prefix = "workflow"
        else:
            if st.session_state.current_step == 1 or st.session_state.current_step == 2 or st.session_state.current_step == 3:
                title = "基线模型解释"
                model_prefix = "baseline"
                data_prefix = "baseline"

            elif st.session_state.current_step == 0 and st.session_state.runned:
                title = "最终模型解释"
                model_prefix = "best"
                data_prefix = "workflow"

        data_path = get_saved_pickle_path(name=name, file_prefix=data_prefix, type="data")
        model_path = get_saved_pickle_path(name=name, file_prefix=model_prefix, type="model")
        create_shap_analysis(
            title=title,
            model_path=model_path,
            data_path=data_path,
        )

    with tab4:
        # 确保自动模式完成后可以问答
        if not st.session_state.helper_ready:
            st.warning("请先在智能体配置页面运行模型，完成后即可开始问答")
            return

        # 确保graph_state存在
        if "graph_state" not in st.session_state and st.session_state.baseline_codes:
            st.session_state.graph_state = {
                "messages": [],
                "baseline_codes": st.session_state.baseline_codes or [],
                "actions": st.session_state.actions or [],
                "workflow_codes": st.session_state.workflow_codes or [],
                "optimization_codes": st.session_state.optimization_codes or [],
            }

        # 确保存在必要的graph状态
        if "graph_state" not in st.session_state:
            st.warning("智能体配置不完整，请在智能体配置页面先完成训练")
            return

        ai_assistant.create_ai_assistant(monitor)


def _display_logs(monitor, md_log_container, require_result=False):
    """显示执行日志

    Args:
        monitor: 训练监控器
        md_log_container: 日志显示容器
        require_result: 是否需要等待结果完成才显示日志
    """
    if st.session_state.runned:
        latest_log = monitor._get_latest_log_file()
        if latest_log and (not require_result or st.session_state.result):
            content, _ = monitor._read_log_file(latest_log)
        if content:
            monitor._display_log_content(content, md_log_container)


def show_auto_mode(monitor, lock, run, restart):
    """显示自动模式界面"""
    st.markdown("### 自动模式")
    st.markdown("系统将自动完成整个机器学习流程，从基线模型构建到优化。")

    # 创建两列布局来放置按钮
    col1, col2 = st.columns(2)
    with col1:
        st.button("开始运行", on_click=run, disabled=lock, type="primary")

    # 创建日志容器
    log_container = st.empty()
    md_log_container = log_container.empty()

    if st.session_state.running:
        if st.session_state.result is None:
            st.success("智能体已启动！")

        # 显示实时日志
        _display_logs(monitor, md_log_container, require_result=False)

        st.session_state.result = asyncio.run(
            monitor.start_training(
                task_type=TaskType.ML.value,
                config=st.session_state.data_config,
                code_interpreter=st.session_state.code_interpreter,
                auto=True,  # 自动模式
            )
        )

        st.session_state.runned = True

        # 提取并保存各个模型状态
        if st.session_state.result:
            state_values = monitor.app.get_state(st.session_state.data_config).values
            st.session_state.baseline_codes = state_values.get("baseline_codes", [])
            st.session_state.baseline_success = state_values.get("baseline_success", False)
            st.session_state.actions = state_values.get("actions", [])
            st.session_state.action_success = state_values.get("action_success", False)
            st.session_state.workflow_codes = state_values.get("workflow_codes", [])
            st.session_state.workflow_success = state_values.get("workflow_success", False)
            st.session_state.optimization_codes = state_values.get("optimization_codes", [])
            st.session_state.optimization_success = state_values.get("optimization_success", False)

        # Store the graph state
        st.session_state.graph_state = {
            "messages": [],
            "baseline_codes": st.session_state.baseline_codes,
            "baseline_success": st.session_state.baseline_success,
            "actions": st.session_state.actions,
            "action_success": st.session_state.action_success,
            "workflow_codes": st.session_state.workflow_codes,
            "workflow_success": st.session_state.workflow_success,
            "optimization_codes": st.session_state.optimization_codes,
            "optimization_success": st.session_state.optimization_success,
        }
        st.session_state.running = False
        st.session_state.helper_ready = True
    else:
        # 显示最终日志
        _display_logs(monitor, md_log_container, require_result=True)

        # 显示流程状态
        if hasattr(st.session_state, "result") and st.session_state.result:
            st.success("✅ 智能体已完成全部模型流程")
            # 确保helper_ready标志设置正确
            if st.session_state.baseline_codes and not st.session_state.helper_ready:
                st.session_state.helper_ready = True

    with col2:
        if st.session_state.result is not None:
            st.success("智能体运行完成, 点击重启按钮重新开始")
            st.button("重启", on_click=restart, type="secondary")


def show_manual_mode(monitor, lock, restart):
    """显示手动模式界面"""
    st.markdown("### 手动模式")
    st.markdown("手动逐步执行机器学习流程")

    # 初始化状态
    if "current_step" not in st.session_state:
        st.session_state.current_step = 0
    if "step_status" not in st.session_state:
        st.session_state.step_status = [False] * 4  # 4个步骤的状态

    # 显示错误消息（如果存在）
    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    # 如果已经完成了基线模型但helper_ready未设置，确保设置它
    if st.session_state.baseline_codes and not st.session_state.helper_ready:
        st.session_state.helper_ready = True
        st.session_state.graph_state = {
            "messages": [],
            "baseline_codes": st.session_state.baseline_codes,
            "baseline_success": st.session_state.baseline_success,
            "actions": st.session_state.actions or [],
            "workflow_codes": st.session_state.workflow_codes or [],
        }

    # 定义步骤列表
    steps = [
        ("1. 基线模型", run_baseline_builder, NORMAL_GRAPH.format(graph_name="基线模型")),
        ("2. 特征工程", run_action_builder, ACTION_GRAPH),
        ("3. 工作流构建", run_workflow_builder, NORMAL_GRAPH.format(graph_name="工作流")),
        ("4. 模型优化", run_optimization_builder, NORMAL_GRAPH.format(graph_name="模型优化")),
    ]

    # 创建步骤条
    if "stepper" not in st.session_state:
        st.session_state.stepper = StepperBar(steps, 0, reset_func=restart)

    # 显示步骤条
    stepper = st.session_state.stepper
    st.markdown(stepper(), unsafe_allow_html=True)

    # 显示流程状态
    process_status = st.empty()

    # 显示当前流程状态
    if st.session_state.baseline_codes and st.session_state.baseline_success:
        process_status.success("✅ 基线模型已构建")
    if st.session_state.actions and st.session_state.action_success:
        process_status.success("✅ 优化行动已生成")
    if st.session_state.workflow_codes and st.session_state.workflow_success:
        process_status.success("✅ 工作流已构建")
    if hasattr(st.session_state, "result") and st.session_state.result and st.session_state.workflow_codes:
        process_status.success("✅ 模型优化已完成")

    # 显示日志容器
    st.markdown("### 执行日志")
    log_container = st.empty()
    md_log_container = log_container.empty()

    # 显示最终日志
    _display_logs(monitor, md_log_container, require_result=False)


# 定义每个步骤的异步执行函数
async def run_baseline_builder():
    """运行基线模型构建器"""
    run()
    with st.spinner("正在构建基线模型..."):
        try:
            result = await st.session_state.monitor.start_training(
                task_type=TaskType.ML.value,
                config=st.session_state.data_config,
                code_interpreter=st.session_state.code_interpreter,
                auto=False,
                start_builder="baseline_builder",
            )
            st.session_state.runned = True
            if result:
                # 保存基线模型的状态
                state_values = st.session_state.monitor.app.get_state(st.session_state.data_config).values
                st.session_state.baseline_codes = state_values.get("baseline_codes", [])
                st.session_state.baseline_success = state_values.get("baseline_success", False)

                # 初始化 graph_state
                st.session_state.graph_state = {
                    "messages": [],
                    "baseline_codes": st.session_state.baseline_codes,
                    "baseline_success": st.session_state.baseline_success,
                }
                st.session_state.helper_ready = True
                st.session_state.result = result
                st.session_state.step_status[0] = True
                # 清除错误消息
                st.session_state.error_message = None
                return True
            return False
        except Exception as e:
            st.session_state.error_message = f"基线模型构建失败: {str(e)}"
            return False
        finally:
            st.session_state.running = False


async def run_action_builder():
    """运行特征工程构建器"""
    run()
    with st.spinner("正在生成特征工程..."):
        if not st.session_state.baseline_codes or not st.session_state.baseline_success:
            st.session_state.error_message = "需要先完成基线模型构建"
            st.session_state.running = False
            return False

        try:
            result = await st.session_state.monitor.start_training(
                task_type=TaskType.ML.value,
                config=st.session_state.data_config,
                code_interpreter=st.session_state.code_interpreter,
                auto=False,
                start_builder="action_builder",
                baseline_codes=st.session_state.baseline_codes,
            )
            st.session_state.runned = True
            if result:
                # 保存行动构建器的状态
                state_values = st.session_state.monitor.app.get_state(st.session_state.data_config).values
                st.session_state.actions = state_values.get("actions", [])
                st.session_state.action_success = state_values.get("action_success", False)

                # 更新 graph_state
                if "graph_state" in st.session_state:
                    st.session_state.graph_state.update(
                        {
                            "actions": st.session_state.actions,
                            "action_success": st.session_state.action_success,
                        }
                    )
                st.session_state.result = result
                st.session_state.step_status[1] = True
                # 清除错误消息
                st.session_state.error_message = None
                return True
            return False
        except Exception as e:
            st.session_state.error_message = f"行动构建失败: {str(e)}"
            return False
        finally:
            st.session_state.running = False


async def run_workflow_builder():
    """运行工作流构建器"""
    run()
    with st.spinner("正在构建工作流..."):
        if (
            not st.session_state.baseline_codes
            or not st.session_state.baseline_success
            or not st.session_state.actions
        ):
            st.session_state.error_message = "需要先完成基线模型构建和特征工程"
            st.session_state.running = False
            return False

        try:
            result = await st.session_state.monitor.start_training(
                task_type=TaskType.ML.value,
                config=st.session_state.data_config,
                code_interpreter=st.session_state.code_interpreter,
                auto=False,
                start_builder="workflow_builder",
                baseline_codes=st.session_state.baseline_codes,
                actions=st.session_state.actions,
            )
            st.session_state.runned = True
            if result:
                # 保存工作流构建器的状态
                state_values = st.session_state.monitor.app.get_state(st.session_state.data_config).values
                st.session_state.workflow_codes = state_values.get("workflow_codes", [])
                st.session_state.workflow_success = state_values.get("workflow_success", False)

                # 更新 graph_state
                if "graph_state" in st.session_state:
                    st.session_state.graph_state.update(
                        {
                            "workflow_codes": st.session_state.workflow_codes,
                            "workflow_success": st.session_state.workflow_success,
                        }
                    )
                st.session_state.result = result
                st.session_state.step_status[2] = True
                # 清除错误消息
                st.session_state.error_message = None
                return True
            return False
        except Exception as e:
            st.session_state.error_message = f"工作流构建失败: {str(e)}"
            return False
        finally:
            st.session_state.running = False


async def run_optimization_builder():
    """运行优化构建器"""
    run()
    with st.spinner("正在进行模型优化..."):
        if not st.session_state.workflow_codes or not st.session_state.workflow_success:
            st.session_state.error_message = "需要先完成工作流构建"
            st.session_state.running = False
            return False

        try:
            result = await st.session_state.monitor.start_training(
                task_type=TaskType.ML.value,
                config=st.session_state.data_config,
                code_interpreter=st.session_state.code_interpreter,
                auto=False,
                start_builder="optimization_builder",
                workflow_codes=st.session_state.workflow_codes,
            )

            st.session_state.runned = True
            if result:
                state_values = st.session_state.monitor.app.get_state(st.session_state.data_config).values
                st.session_state.optimization_codes = state_values.get("optimization_codes", [])
                st.session_state.optimization_success = state_values.get("optimization_success", False)
                # 更新 graph_state
                if "graph_state" in st.session_state:
                    st.session_state.graph_state.update(
                        {
                            "optimization_codes": st.session_state.optimization_codes,
                            "optimization_success": st.session_state.optimization_success,
                        }
                    )
                st.session_state.result = result
                st.session_state.step_status[3] = True
                # 清除错误消息
                st.session_state.error_message = None
                return True
            return False
        except Exception as e:
            st.session_state.error_message = f"模型优化失败: {str(e)}"
            return False
        finally:
            st.session_state.running = False


show()