import json

import streamlit as st
from baicai_base.utils.data import get_saved_user_info_path

from baicai_webui.components.model import get_page_llm
from baicai_webui.components.right_sidebar import show_right_sidebar
from baicai_webui.components.tutor import multi_choice_questions, select_book_chapters


def show():
    llm = get_page_llm(
        config_id="quiz",
        title="小测验模型配置",
        info_text="配置用于小测验功能的模型参数",
    )
    st.title("小测验")

    if "right_sidebar_expanded" not in st.session_state:
        st.session_state.right_sidebar_expanded = False
    if "sidebar_width" not in st.session_state:
        st.session_state.sidebar_width = 5

    if st.session_state.right_sidebar_expanded:
        # Create main content area and right sidebar columns with dynamic width
        main_width = 20 - st.session_state.sidebar_width
        main_content, right_sidebar = st.columns([main_width, st.session_state.sidebar_width])
    else:
        main_content, right_sidebar = st.columns([19, 1])

    with main_content:
        if "generated_questions" not in st.session_state or st.session_state.generated_questions is None:
            selected_chapter = select_book_chapters()
            st.session_state.chapter_name = selected_chapter["name"]
            st.session_state.keywords = selected_chapter["keywords"]
            st.session_state.summary = selected_chapter["summary"]

            try:
                _, analysis_result_path = get_saved_user_info_path()
                with open(analysis_result_path, "r", encoding="utf-8") as f:
                    analysis_result = json.load(f)
            except FileNotFoundError:
                st.error("No analysis result found.")
                return
            except UnicodeDecodeError:
                st.error("文件编码错误，请确保使用 UTF-8 编码。")
                return

            # Example usage
            st.session_state.profile = analysis_result["summary"]
            st.session_state.basic_info = analysis_result["basic_info"]
            st.session_state.background = st.session_state.basic_info["background"]
            st.session_state.grade = st.session_state.basic_info["grade"]
            st.session_state.subject = st.session_state.basic_info["subject"]

        else:
            if st.button("重新选择章节"):
                st.session_state.generated_questions = None
                st.rerun()

        multi_choice_questions(
            llm=llm,
            subject=st.session_state.subject,
            grade=st.session_state.grade,
            background=st.session_state.background,
            profile=st.session_state.profile,
            charpt_name=st.session_state.chapter_name,
            keywords=st.session_state.keywords,
            summary=st.session_state.summary,
        )

    # Right sidebar
    with right_sidebar:
        if "selected_level" in st.session_state and st.session_state.selected_level:
            level = st.session_state.selected_level
        else:
            level = 3
        show_right_sidebar(from_level=level, terms=st.session_state.keywords)

show()