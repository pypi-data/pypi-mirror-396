import asyncio
import glob
import os

import streamlit as st
from baicai_base.utils.data import get_tmp_folder
from baicai_dev.utils.data import TaskType

from baicai_webui.components.model import create_graph_executor


class TrainingMonitor:
    """训练监控组件"""

    # 定义滚动容器样式为类属性
    SCROLL_CONTAINER_TEMPLATE = """
        <div style="height: 800px;
                    overflow-y: scroll;
                    padding: 10px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f5f5f5;
                    resize: vertical;
                    min-height: 200px;
                    max-height: 1200px;">
            {content}
        </div>
    """

    def __init__(self, llm=None):
        self.graph_executor = create_graph_executor(llm=llm)
        self.result = None
        self.graph = None
        self.app = None
        self._training_lock = asyncio.Lock()  # 添加异步锁
        self._is_training = False  # 添加训练状态标志
        self._current_log_file = None  # 添加当前日志文件路径

    async def start_training(
        self,
        task_type: str,
        config: dict,
        code_interpreter=None,
        auto=False,
        start_builder="baseline_builder",
        baseline_codes=None,
        workflow_codes=None,
        actions=None,
    ):
        """启动训练过程

        Args:
            task_type: 任务类型（如 'vision', 'text' 等）
            config: 训练配置
            code_interpreter: 代码解释器
            auto: 是否自动配置
            start_builder: 起始构建器
            baseline_codes: 基准代码
            workflow_codes: 工作流代码
            actions: 动作列表
        """
        if self._is_training:
            st.error("当前已有训练任务在运行中，请等待完成后再试")
            return None

        async with self._training_lock:
            try:
                self._is_training = True
                result = await self._start_training_async(
                    task_type, config, code_interpreter, auto, start_builder, baseline_codes, workflow_codes, actions
                )
                return result
            except Exception as e:
                st.error(f"训练启动失败：{str(e)}")
                return None
            finally:
                self._is_training = False

    async def _start_training_async(
        self,
        task_type: str,
        config: dict,
        code_interpreter=None,
        auto=False,
        start_builder="baseline_builder",
        baseline_codes=None,
        workflow_codes=None,
        actions=None,
    ):
        """异步执行训练过程"""
        executor = self.graph_executor.get_graph_for_task(task_type)
        if not executor:
            st.error(f"未找到任务类型 {task_type} 对应的执行器")
            return None

        try:
            # 重置当前日志文件
            self._current_log_file = None

            # 根据任务类型选择不同的执行器配置
            if task_type == TaskType.ML.value:  # 机器学习任务
                self.graph = executor(
                    config,
                    code_interpreter,
                    auto=auto,
                    start_builder=start_builder,
                    baseline_codes=baseline_codes,
                    workflow_codes=workflow_codes,
                    actions=actions,
                )
            else:  # 深度学习任务
                self.graph = executor(
                    config,
                    code_interpreter,
                )
            self.app = self.graph.app
            log_container = st.empty()
            md_log_container = log_container.empty()

            # 创建任务
            graph_task = asyncio.create_task(self.app.ainvoke({"messages": []}, config))

            # 等待一小段时间确保任务已经开始运行
            await asyncio.sleep(0.5)

            # 获取当前最新的日志文件
            self._current_log_file = self._get_latest_log_file()

            # 监控日志直到任务完成
            await self._monitor_log_updates(graph_task, md_log_container)

            # 获取结果
            result = await graph_task
            self.result = result

            # 显示最终日志
            self._display_final_log(md_log_container)

            if not result:
                st.warning("执行完成，但未返回结果")
                return None

            return result

        except Exception as e:
            st.error(f"训练过程中出错: {str(e)}")
            import traceback

            st.code(traceback.format_exc(), language="python")
            return None
        finally:
            # 清理当前日志文件引用
            self._current_log_file = None
            
            # 强制清理内存
            import gc
            gc.collect()
            
            # 清理matplotlib缓存
            try:
                import matplotlib.pyplot as plt
                plt.close('all')
            except:
                pass

    def _get_latest_log_file(self):
        """获取最新的非空日志文件路径"""
        log_dir = get_tmp_folder("log")
        if not os.path.exists(log_dir):
            return None

        log_files = glob.glob(os.path.join(log_dir, "app_log_*.md"))
        if not log_files:
            return None

        # 按修改时间排序，最新的在前
        log_files.sort(key=os.path.getmtime, reverse=True)

        # 如果是第一次获取日志文件，记录当前最新的文件
        if self._current_log_file is None:
            for log_file in log_files:
                if os.path.getsize(log_file) > 0:
                    self._current_log_file = log_file
                    return log_file
            return None

        # 如果已经有当前日志文件，检查是否有更新的文件
        for log_file in log_files:
            if log_file == self._current_log_file:
                return log_file
            if os.path.getsize(log_file) > 0:
                self._current_log_file = log_file
                return log_file

        return self._current_log_file

    def _display_log_content(self, content: str, md_log_container) -> None:
        """显示带滚动条的日志内容"""
        formatted_content = self.SCROLL_CONTAINER_TEMPLATE.format(content=content)
        md_log_container.markdown(formatted_content, unsafe_allow_html=True)

    def _read_log_file(self, file_path: str, start_pos: int = 0) -> tuple[str, int]:
        """读取日志文件内容

        Args:
            file_path: 日志文件路径
            start_pos: 开始读取位置

        Returns:
            tuple[str, int]: (文件内容, 当前文件位置)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if start_pos:
                    f.seek(start_pos)
                content = f.read()
                return content, f.tell()
        except Exception as e:
            st.error(f"读取日志文件时出错: {str(e)}")
            return "", start_pos

    async def _monitor_log_updates(self, graph_task, md_log_container):
        """监控日志文件更新并显示"""
        latest_log = self._get_latest_log_file()
        last_size = 0
        all_log_content = ""

        while not graph_task.done():
            if latest_log and os.path.exists(latest_log):
                current_size = os.path.getsize(latest_log)
                if current_size > last_size:
                    new_content, last_size = self._read_log_file(latest_log, last_size)
                    if new_content:
                        all_log_content += new_content
                        self._display_log_content(all_log_content, md_log_container)
            await asyncio.sleep(0.1)

    def _display_final_log(self, md_log_container):
        """显示最终的完整日志"""
        latest_log = self._get_latest_log_file()
        if latest_log and os.path.exists(latest_log):
            content, _ = self._read_log_file(latest_log)
            if content:
                self._display_log_content(content, md_log_container)


def create_training_monitor(llm=None) -> TrainingMonitor:
    """创建训练监控组件"""
    return TrainingMonitor(llm=llm)
