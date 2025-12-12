import asyncio
import os

import streamlit as st
import torch
from baicai_base.utils.setups import setup_code_interpreter
from baicai_dev.utils.data import TaskType

from baicai_webui.components.chat import ai_assistant
from baicai_webui.components.model import create_training_monitor, result_display


class BasePage:
    """Base page component for different task types"""

    def __init__(self, task_type: TaskType, data_uploader_func):
        self.task_type = task_type
        self.data_uploader_func = data_uploader_func
        
        # 初始化按钮文本
        self.button_text = "开始训练"  # 默认训练

        if "code_interpreter" not in st.session_state:
            st.session_state.code_interpreter = setup_code_interpreter()

        # 初始化页面状态
        if "page_state" not in st.session_state:
            st.session_state.page_state = {
                "monitor": create_training_monitor(),
                "helper_ready": False,
                "post_train_completed": False,
                "data_config": None,
                "pre_train_container": None,
                "run_post_train": False,
            }

        if "data_config" not in st.session_state:
            st.session_state.data_config = None

        # Initialize graph_state in session state
        if "graph_state" not in st.session_state:
            st.session_state.graph_state = {
                "messages": [],
                "dl_codes": [],
                "dl_models": [],
                "dl_success": False,
            }

    def show(self, pre_train=None, post_train=None, title=None):
        """Display the page with common structure"""
        st.title(f"{title or self.task_type.value}")

        # Create tabs
        tab1, tab2, tab3 = st.tabs(["🤖 智能体配置", "📈结果查看", "💬 AI助手"])

        monitor = st.session_state.page_state["monitor"]

        with tab1:
            # Data upload and configuration
            data_config = self.data_uploader_func()
            if not data_config:
                st.warning("请上传数据")
                return

            data_config["configurable"]["from_web_ui"] = True

            if data_config:
                st.session_state.data_config = data_config
                if pre_train:
                    pre_train()

                # 根据任务类型动态设置按钮文本
                if self.task_type == TaskType.NLP:
                    # 检查是否是情感分类训练任务
                    selected_task = data_config["configurable"]["name"]
                    if selected_task == "情感分类训练":
                        button_text = "开始训练"
                    else:
                        button_text = "开始推理"
                else:
                    button_text = "开始训练"

                # Show start training button
                if st.button(button_text, type="primary", key="start_training_button"):
                    st.session_state.page_state["post_train_completed"] = False
                    st.session_state.page_state["run_post_train"] = True
                    try:
                        # 添加内存清理
                        import gc
                        gc.collect()
                        
                        result = asyncio.run(
                            monitor.start_training(
                                task_type=self.task_type.value,
                                config=data_config,
                                code_interpreter=st.session_state.code_interpreter,
                            )
                        )
                        if result:
                            state_values = monitor.app.get_state(data_config).values
                            st.session_state.graph_state["dl_codes"] = state_values.get("dl_codes", [])
                            st.session_state.graph_state["dl_models"] = state_values.get("dl_models", [])
                            st.session_state.graph_state["dl_success"] = state_values.get("dl_success", False)
                            st.session_state.page_state["helper_ready"] = True
                            st.success("训练已启动！")
                        else:
                            st.warning("训练完成，但未返回结果")
                    except Exception as e:
                        st.error(f"训练失败：{str(e)}")
                        import traceback
                        st.code(traceback.format_exc(), language="python")
                    finally:
                        # 强制清理内存
                        import gc
                        gc.collect()

        with tab2:
            # Handle post_train in a separate rerun
            if (
                st.session_state.page_state["run_post_train"]
                and post_train
                and not st.session_state.page_state["post_train_completed"]
            ):
                try:
                    # 添加超时保护
                    asyncio.run(asyncio.wait_for(
                        post_train(st.session_state.code_interpreter),
                        timeout=120.0  # 2分钟超时
                    ))
                    st.session_state.page_state["post_train_completed"] = True
                    st.session_state.page_state["run_post_train"] = False
                except asyncio.TimeoutError:
                    st.error("训练后处理超时，请检查是否有长时间运行的操作")
                    st.session_state.page_state["post_train_completed"] = True
                    st.session_state.page_state["run_post_train"] = False
                except Exception as e:
                    st.error(f"训练后处理失败：{str(e)}")
                    import traceback
                    st.code(traceback.format_exc(), language="python")
                    st.session_state.page_state["post_train_completed"] = True
                    st.session_state.page_state["run_post_train"] = False
            # Display results
            if st.session_state.page_state["helper_ready"]:
                try:
                    result_display.display_results(st.session_state.graph_state, graph="dl")
                except Exception as e:
                    st.error(f"显示结果失败：{str(e)}")

        with tab3:
            if st.session_state.page_state["helper_ready"]:
                try:
                    ai_assistant.create_ai_assistant(monitor, task_type=self.task_type.value)
                except Exception as e:
                    st.error(f"AI助手创建失败：{str(e)}")
            else:
                st.info("请先完成训练")
