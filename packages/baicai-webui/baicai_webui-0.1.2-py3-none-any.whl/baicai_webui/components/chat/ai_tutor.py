# TODO: Need a refacor later

import asyncio

import streamlit as st
from baicai_tutor.agents.roles import concept_explainer, hinter

from baicai_webui.components.model import get_page_llm


def create_ai_tutor(from_level: int = 1, terms: list[str] = None, debug: bool = False) -> None:
    """
    Create an AI tutor interface for the user to interact with.

    Args:
        from_level: The level of the tutor to create.
        terms: A list of terms to use for the tutor.
    """
    llm = get_page_llm(
        config_id="tutor",
        title="问答模型配置",
        info_text="配置用于问答功能的模型参数",
    )
    # 初始化聊天历史
    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = []

    # 创建一个占据大部分页面的主容器
    main_container = st.container(height=1000)

    # 创建底部输入区域
    input_container = st.container()

    # 在主容器中显示消息历史
    with main_container:
        # 创建一个消息占位符字典，避免重复创建
        if "tutor_message_placeholders" not in st.session_state:
            st.session_state.tutor_message_placeholders = {}

        for idx, message in enumerate(st.session_state.tutor_messages):
            role = message[0]
            content = message[1]
            with st.chat_message(role):
                if idx not in st.session_state.tutor_message_placeholders:
                    st.session_state.tutor_message_placeholders[idx] = st.empty()
                st.session_state.tutor_message_placeholders[idx].markdown(content)

    # 在底部容器中放置输入框
    with input_container:
        prompt = st.chat_input("请输入您的问题...")

        suggested_questions = []

        if from_level == 1 and terms:
            suggested_questions = [(term, f"解释{term}") for term in terms]
        elif terms is not None:
            suggested_questions = [(term, f"{term}是如何工作的?") for term in terms]
        else:
            suggested_questions = [("机器学习?", "机器学习是什么?"), ("深度学习?", "深度学习是什么?")]

        # Add suggested questions as hints
        cols = st.columns(len(suggested_questions))
        for idx, (question, hint) in enumerate(suggested_questions):
            with cols[idx]:
                if st.button(question, use_container_width=True):
                    st.session_state.tutor_prompt = hint

        # Handle the prompt from button clicks
        if hasattr(st.session_state, "tutor_prompt"):
            prompt = st.session_state.tutor_prompt
            del st.session_state.tutor_prompt

    # 处理用户输入
    if prompt:
        # Create and add user message
        user_message = ("user", prompt)
        st.session_state.tutor_messages.append(user_message)

        # Display user message in chat message container - static content
        with main_container.chat_message("user"):
            st.markdown(prompt)

        # Get response from helper node through graph
        async def _get_helper_response():
            # Create a placeholder for streaming output
            with main_container.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                # Get the chain
                chain = concept_explainer(llm) if from_level == 1 else hinter(llm)

                # Stream the response
                async for chunk in chain.astream({"messages": [user_message]}):
                    if hasattr(chunk, "content"):
                        full_response += chunk.content
                        message_placeholder.markdown(full_response + "▌")

                if from_level != 1 and not debug:
                    full_response = full_response.split("</think>")[1]
                message_placeholder.markdown(full_response)
                st.session_state.tutor_messages.append(("assistant", full_response))
                st.session_state.tutor_message_placeholders[len(st.session_state.tutor_messages) - 1] = (
                    message_placeholder
                )

        # Run the async function
        asyncio.run(_get_helper_response())
