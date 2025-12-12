import asyncio
from enum import Enum
from typing import Callable

import streamlit as st
from streamlit_mermaid import st_mermaid


class StepState(Enum):
    """步骤状态枚举"""

    PENDING = "pending"  # 待运行
    RUNNING = "running"  # 正在运行
    COMPLETED = "completed"  # 已完成
    DISABLED = "disabled"  # 禁用


class Event(Enum):
    """事件枚举"""

    CLICK = "click"  # 点击
    COMPLETE = "complete"  # 完成
    EMPTY = "empty"  # 空


class StepperBar:
    """
    一个可自定义的步骤条组件，使用有限状态机管理状态
    """

    def __init__(self, steps: list[tuple[str, Callable, str]], current_step: int, reset_func: Callable = None):
        """
        初始化步骤条

        Parameters:
            steps: list[tuple[str, Callable, str]]
                步骤列表，每个元素是一个包含步骤名称、执行函数和mermaid图形的元组
            current_step: int
                当前步骤的索引
        """
        if "step_states" not in st.session_state:
            st.session_state.step_states = [StepState.PENDING] * len(steps)
        if "current_step" not in st.session_state:
            st.session_state.current_step = current_step
        if "event" not in st.session_state:
            st.session_state.event = Event.EMPTY
        if "result" not in st.session_state:
            st.session_state.result = None
        if "state_changed" not in st.session_state:
            st.session_state.state_changed = False
        if "selected_step" not in st.session_state:
            st.session_state.selected_step = current_step

        self.set_states(steps, current_step)
        self.step_container_height = 50
        self.step_container_margin = 10
        self.steps = steps
        self.reset_func = reset_func
        # 定义颜色主题
        self.inactive_color = "#BDBDBD"
        self.inactive_text_color = "#666666"
        self.colors = {
            StepState.PENDING: {"bg": "#FFA726", "text": "#FFFFFF"},
            StepState.RUNNING: {"bg": "#FFA726", "text": "#FFFFFF"},
            StepState.COMPLETED: {"bg": "#2E7D32", "text": "#FFFFFF"},
            StepState.DISABLED: {"bg": f"{self.inactive_color}", "text": f"{self.inactive_text_color}"},
        }

    def set_states(self, steps: list[tuple[str, Callable]], current_step: int):
        """设置状态"""
        for i in range(len(steps)):
            if i < current_step:
                st.session_state.step_states[i] = StepState.COMPLETED
            elif i == current_step:
                if st.session_state.event == Event.CLICK:
                    st.session_state.step_states[i] = StepState.RUNNING
                else:
                    st.session_state.step_states[i] = StepState.PENDING
            else:
                st.session_state.step_states[i] = StepState.DISABLED

    def reset_states(self):
        """重置状态"""
        self.set_states(self.steps, 0)
        st.session_state.current_step = 0
        st.session_state.event = Event.EMPTY
        st.session_state.result = None
        # 重置选择步骤变量，但不直接设置step_selector（这会导致错误）
        st.session_state.selected_step = 0

    def click_transition(self, step_index):
        st.session_state.event = Event.CLICK
        st.session_state.step_states[step_index] = StepState.RUNNING

    def run_transition(self, step_index: int, success: bool = True):
        """开始事件"""

        if success:
            st.session_state.event = Event.COMPLETE
            st.session_state.step_states[step_index] = StepState.COMPLETED
            if step_index < len(self.steps) - 1:
                st.session_state.step_states[step_index + 1] = StepState.PENDING
        else:
            st.session_state.event = Event.EMPTY
            st.session_state.step_states[step_index] = StepState.PENDING

    def get_button_style(self, step_index: int) -> tuple:
        """获取按钮样式"""
        state = st.session_state.step_states[step_index]
        style = self.colors[state]

        if state == StepState.COMPLETED:
            return style["bg"], style["text"], False
        elif state == StepState.PENDING:
            return style["bg"], style["text"], False
        elif state == StepState.RUNNING:
            return style["bg"], style["text"], False
        elif state == StepState.DISABLED:
            return self.inactive_color, self.inactive_text_color, True

    async def run_task(self, func, step_index: int):
        """运行任务"""
        try:
            # 1. 执行异步任务
            st.session_state.result = await func()

            # 2. 更新最终状态
            if st.session_state.result:
                self.run_transition(step_index, success=True)
            else:
                self.run_transition(step_index, success=False)

        except Exception as e:
            st.error(f"Task failed: {str(e)}")
            self.run_transition(step_index, success=False)

        finally:
            # 确保状态更新被记录
            st.session_state.state_changed = True
            st.session_state.task_completed = True

    def __call__(self):
        """渲染步骤条"""
        if not hasattr(st.session_state, "task_completed"):
            st.session_state.task_completed = False

        # 添加自定义CSS
        custom_css = f"""
        <style>
        /* Stepper样式 */
        .step-container {{
            height: {self.step_container_height}px;
            margin: {self.step_container_margin}px 0;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            text-align: center;
        }}
        
        .step-connector {{
            width: 100%;
            height: 5px;
            margin: 10px 0;
        }}
        
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(255, 167, 38, 0.5); }}
            70% {{ box-shadow: 0 0 0 10px rgba(255, 167, 38, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(255, 167, 38, 0); }}
        }}
        
        .step-running {{
            animation: pulse 1s infinite;
        }}
        </style>
        """
        st.markdown(custom_css, unsafe_allow_html=True)

        # 创建步骤条容器
        stepper_container = st.container()

        with stepper_container:
            # 创建列，每个步骤一列，步骤之间有连接器
            cols = st.columns(len(self.steps) * 2 - 1)

            # 显示步骤和连接器
            for i, step in enumerate(self.steps):
                col_idx = i * 2  # 步骤列的索引
                state = st.session_state.step_states[i]

                with cols[col_idx]:
                    # 获取当前状态的样式
                    bg_color, text_color, is_disabled = self.get_button_style(i)

                    # 步骤状态文本
                    animation_class = "step-running" if state == StepState.RUNNING else ""
                    opacity = "opacity: 0.7;" if is_disabled else ""
                    cursor = "cursor: not-allowed;" if is_disabled else "cursor: pointer;"

                    # 创建步骤容器
                    html_content = f"""
                    <div class="step-container {animation_class}" 
                         style="background-color: {bg_color}; color: {text_color}; {opacity} {cursor}">
                        {step[0]}
                    </div>
                    """
                    st.markdown(html_content, unsafe_allow_html=True)

                    # 为PENDING或RUNNING状态添加运行按钮
                    if state in [StepState.PENDING, StepState.RUNNING]:
                        button_label = "运行" if state == StepState.PENDING else "运行中..."
                        disabled = state == StepState.RUNNING

                        if (
                            st.button(
                                button_label,
                                disabled=disabled,
                                key=f"run_step_{i}",
                                use_container_width=True,
                            )
                            and state == StepState.PENDING
                        ):
                            # 设置运行状态
                            self.click_transition(i)
                            st.session_state.current_running_step = i
                            st.session_state.should_run_task = True
                            st.session_state.task_completed = False
                            st.rerun()

                # 更新当前步骤
                try:
                    st.session_state.current_step = st.session_state.step_states.index(StepState.RUNNING)
                except ValueError:
                    try:
                        st.session_state.current_step = st.session_state.step_states.index(StepState.PENDING)
                    except ValueError:
                        st.session_state.current_step = 0

                # 添加步骤之间的连接线
                if i < len(self.steps) - 1:
                    with cols[col_idx + 1]:
                        connector_color = self.colors[StepState.COMPLETED]["bg"] if i < st.session_state.current_step else self.inactive_color
                        connector_html = f"""
                        <div style="display: flex; align-items: center; justify-content: center; height: {self.step_container_height}px; margin-top: {self.step_container_margin}px;">
                            <div class="step-connector" style="background-color: {connector_color};"></div>
                        </div>
                        """
                        st.markdown(connector_html, unsafe_allow_html=True)

            # 添加控制按钮区域
            st.markdown("---")
            control_cols = st.columns([1, 1, 1])

            # 显示当前步骤的mermaid图
            current_state = st.session_state.step_states[st.session_state.current_step]
            if current_state in [StepState.PENDING, StepState.RUNNING]:
                mermaid_diagram = self.steps[st.session_state.current_step][2]
                if mermaid_diagram:
                    try:
                        st.markdown("### 当前步骤流程图")
                        st_mermaid(mermaid_diagram, key=f"mermaid_diagram_{st.session_state.current_step}", show_controls=False)
                    except Exception as e:
                        st.error(f"流程图渲染失败: {str(e)}")

            # 添加步骤选择输入框
            with control_cols[0]:
                # 定义一个回调函数来更新selected_step
                def update_selected_step():
                    # 将UI中的1-based转换为内部的0-based
                    st.session_state.selected_step = st.session_state.step_selector - 1

                # 使用key直接更新session_state，显示1-based索引
                step_number = st.number_input(
                    "选择步骤",
                    min_value=1,
                    max_value=len(self.steps),
                    value=st.session_state.selected_step + 1,  # 内部0-based转换为UI的1-based
                    step=1,
                    key="step_selector",
                    on_change=update_selected_step,
                    placeholder="请输入步骤编号",
                )

            # 添加"设置步骤"按钮
            with control_cols[1]:
                st.markdown("<div style='margin-top: 20px; text-align: right;'></div>", unsafe_allow_html=True)
                if st.button("设置步骤", key="set_step_button", use_container_width=True):
                    # 确保使用当前step_selector的值，但需要转换为0-based索引
                    target_step = st.session_state.step_selector - 1
                    self.set_states(self.steps, target_step)
                    st.session_state.current_step = target_step
                    st.rerun()

            # 添加"重启"按钮
            with control_cols[2]:
                st.markdown("<div style='margin-top: 20px; text-align: right;'></div>", unsafe_allow_html=True)
                if st.button("重启步骤", key="reset_button", use_container_width=True):
                    self.reset_states()
                    if self.reset_func:
                        self.reset_func()
                    # 不直接修改step_selector，而是在下一次渲染时让number_input使用selected_step的值
                    st.rerun()

        # 处理异步任务执行
        if hasattr(st.session_state, "should_run_task") and st.session_state.should_run_task:
            step_index = st.session_state.current_running_step
            asyncio.run(self.run_task(self.steps[step_index][1], step_index))
            st.session_state.should_run_task = False
            st.rerun()

        # 如果任务完成，触发重新渲染以更新最终状态
        if st.session_state.task_completed:
            st.session_state.task_completed = False
            st.session_state.state_changed = False
            st.rerun()

        return ""
