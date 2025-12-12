# Need a refacor later

import asyncio

import pandas as pd
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

# 在文件开头修改常量定义
MSG_TYPE_DATAFRAME = "<<DATAFRAME>>"
MSG_TYPE_JSON = "<<JSON>>"
MSG_TYPE_HTML = "<<HTML>>"
MSG_TYPE_IMAGE = "<<IMAGE>>"
MSG_TYPE_CODE = "<<CODE>>"
MSG_TYPE_TEXT = "<<TEXT>>"
MSG_TYPE_END = "<<END>>"  # 添加结束标记


def create_ai_assistant(monitor, run_code=True, task_type="ml") -> None:
    # 初始化聊天历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 创建一个占据大部分页面的主容器
    main_container = st.container()

    # 创建底部输入区域
    input_container = st.container()

    # 在底部容器中放置输入框
    with input_container:
        prompt = st.chat_input("请输入您的问题...")

        suggested_questions = []

        if task_type == "ml":
            suggested_questions = [
                ("解释代码", "请帮我使用通俗易懂语言详细解释代码"),
                ("绘制图形", "请帮我选取两个特征使用seaborn绘制散点图"),
                ("查看数据统计值", "请帮我查看数据的基本统计值"),
                ("查看数据", "请帮我查看数据的前几行"),
            ]
        else:
            suggested_questions = [
                ("解释代码", "请帮我使用通俗易懂语言详细解释代码"),
                ("优化模型", "请帮我优化当前的模型的超参数"),
            ]

        # Add suggested questions as hints
        cols = st.columns(len(suggested_questions))
        for idx, (question, hint) in enumerate(suggested_questions):
            with cols[idx]:
                if st.button(question, use_container_width=True):
                    st.session_state.prompt = hint

        # Handle the prompt from button clicks
        if hasattr(st.session_state, "prompt"):
            prompt = st.session_state.prompt
            del st.session_state.prompt

    # 在主容器中显示消息历史
    with main_container:
        # 创建一个消息占位符字典，避免重复创建
        if "message_placeholders" not in st.session_state:
            st.session_state.message_placeholders = {}

        for idx, message in enumerate(st.session_state.messages):
            role = "user" if isinstance(message, HumanMessage) else "assistant"
            with st.chat_message(role):
                if isinstance(message, HumanMessage):
                    # 用户消息是静态的，直接使用st.markdown
                    st.markdown(message.content)
                else:
                    # AI消息可能需要动态更新，使用placeholder
                    if idx not in st.session_state.message_placeholders:
                        st.session_state.message_placeholders[idx] = st.empty()
                    _show_formatted_content(message.content, st.session_state.message_placeholders[idx])

    # 处理用户输入
    if prompt:
        # Create and add user message
        user_message = HumanMessage(content=prompt)
        st.session_state.messages.append(user_message)

        # Display user message in chat message container - static content
        with main_container.chat_message("user"):
            st.markdown(prompt)

        # Update graph state with new message
        st.session_state.graph_state["messages"] = st.session_state.messages

        # Get response from helper node through graph
        async def _get_helper_response():
            # Create a placeholder for streaming output
            with main_container.chat_message("assistant"):
                message_placeholder = st.empty()

                # Use the graph's helper node through monitor
                async for state_update in monitor.graph.helper_node(
                    state=st.session_state.graph_state,
                    config=st.session_state.data_config,
                ):
                    # Update graph state with all history messages
                    if state_update and "messages" in state_update:
                        st.session_state.graph_state["messages"] = state_update["messages"]

                    if "chunk" in state_update:
                        formatted_answer = "\n\n" + state_update["chunk"]
                        message_placeholder.markdown(formatted_answer)
                        if state_update["chunk"] != "🤔 思考中...":
                            st.session_state.messages.append(AIMessage(content=formatted_answer))

                    if "code" in state_update and run_code:
                        # Create a new placeholder for code block
                        code = state_update["code"]

                        # Handle code execution results with new placeholder
                        code_run_result = await _handle_code_run_results(code)

                        # Add to session state message history
                        if code_run_result:
                            assistant_message = AIMessage(content=code_run_result.strip())
                            st.session_state.messages.append(assistant_message)

            # return state_update

        # Run the async function
        asyncio.run(_get_helper_response())


def _show_formatted_content(content, content_placeholder):
    """显示格式化内容，使用传入的placeholder"""
    parts = content.split(MSG_TYPE_END)
    for part in parts:
        part = part.strip()
        if not part:
            continue

        try:
            msg_type = part[: part.index("\n")]
            msg_content = part[part.index("\n") + 1 :].strip()
        except:  # noqa: E722
            # 如果解析失败，作为普通文本显示
            content_placeholder.markdown(part)
            continue

        if msg_type == MSG_TYPE_DATAFRAME:
            try:
                df = pd.read_json(msg_content)
                content_placeholder.dataframe(df)
            except:  # noqa: E722
                content_placeholder.markdown(f"```\n{msg_content}\n```")
        elif msg_type == MSG_TYPE_JSON:
            try:
                json_data = eval(msg_content)
                content_placeholder.json(json_data)
            except:  # noqa: E722
                content_placeholder.markdown(f"```json\n{msg_content}\n```")
        elif msg_type == MSG_TYPE_HTML:
            content_placeholder.markdown(msg_content, unsafe_allow_html=True)
        elif msg_type == MSG_TYPE_IMAGE:
            content_placeholder.markdown(msg_content, unsafe_allow_html=True)
        elif msg_type == MSG_TYPE_CODE:
            content_placeholder.markdown(msg_content)
        elif msg_type == MSG_TYPE_TEXT:
            content_placeholder.markdown(msg_content)
        else:
            content_placeholder.markdown(msg_content)


def _format_message_content(content_type: str, content: str) -> str:
    """格式化消息内容，确保每个部分都有明确的开始和结束标记"""
    return f"{content_type}\n{content}\n{MSG_TYPE_END}"


async def _handle_img(code):
    altered_code = (
        """
import base64
from io import BytesIO
def fig_to_base64(fig):
    # Save the figure to a temporary buffer with high DPI
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    # Encode the bytes as base64
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return img_base64
"""
        + code
        + """
if "plot" in locals():
    if hasattr(plot, 'figure'):
        # If plot is an Axes object
        base64_string = fig_to_base64(plot.figure)
    elif hasattr(plot, 'fig'):
        # If plot has a fig attribute
        base64_string = fig_to_base64(plot.fig)
    else:
        # Assume plot is already a Figure object
        base64_string = fig_to_base64(plot)
elif "fig" in locals():
    base64_string = fig_to_base64(fig)
elif plt.get_fignums():
    base64_string = fig_to_base64(plt.gcf())
else:
    base64_string = ""

print("START_BASE64")
print(base64_string)
print("END_BASE64")
"""
    )

    result = await st.session_state.code_interpreter.run(altered_code, ignore_keep_len=True)
    base64_start = result[0].find("START_BASE64")
    base64_end = result[0].find("END_BASE64")
    base64_string = result[0][base64_start + len("START_BASE64") : base64_end]
    return base64_string


async def _handle_code_run_results(code):
    # Create a new placeholder for code execution results
    result_placeholder = st.empty()

    response = ""

    if "import matplotlib.pyplot as plt" in code:
        base64_string = await _handle_img(code)
        # Create a container with proper styling for the image
        img_container = f"""
        <div style="width:100%; overflow:auto; margin:10px 0;">
            <img src="data:image/png;base64,{base64_string}"
                 style="max-width:100%; height:auto; display:block; margin:0 auto;"
                 onerror="this.style.display='none'"/>
        </div>
        """
        result_placeholder.markdown(img_container, unsafe_allow_html=True)
        # Add image to message history with type
        response = "\n" + _format_message_content(MSG_TYPE_IMAGE, img_container)
    else:
        try:
            code = code.replace("# Final Answer is below:", "")
            result = await st.session_state.code_interpreter.run(code)
            if result[0] and result[1]:  # Check both success and output
                output = result[0]
                # Handle different types of output
                if isinstance(output, pd.DataFrame):
                    result_placeholder.dataframe(output)
                    # Add dataframe to message history with type
                    response = "\n" + _format_message_content(MSG_TYPE_DATAFRAME, output.to_json())
                elif isinstance(output, (dict, list)):
                    result_placeholder.json(output)
                    # Add json to message history with type
                    response = "\n" + _format_message_content(MSG_TYPE_JSON, str(output))
                elif isinstance(output, str) and output.startswith("<div"):
                    result_placeholder.markdown(output, unsafe_allow_html=True)
                    # Add html output to message history with type
                    response = "\n" + _format_message_content(MSG_TYPE_HTML, output)
                else:
                    result_placeholder.write(output)
                    # Add output to message history with type
                    response = "\n" + _format_message_content(MSG_TYPE_TEXT, str(output))
        except Exception as e:
            error_msg = f"❌ 代码执行错误: {str(e)}"
            result_placeholder.write(error_msg)
            # Add error message to message history with type
            response = "\n" + _format_message_content(MSG_TYPE_TEXT, error_msg)
    return response
