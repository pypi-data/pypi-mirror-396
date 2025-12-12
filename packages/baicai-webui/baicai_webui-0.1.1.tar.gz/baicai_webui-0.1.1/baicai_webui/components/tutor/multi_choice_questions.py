import json
from typing import Dict, List

import streamlit as st
from baicai_base.services.llms import LLM
from baicai_base.utils.data import get_tmp_folder
from baicai_tutor.agents.graphs.tutor_builder import TutorBuilder
from baicai_tutor.utils import create_config
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


@st.cache_resource
def create_tutor(config: Dict, _llm: LLM):
    return TutorBuilder(config=config, memory=MemorySaver(), llm=_llm)


def multi_choice_questions(
    llm: LLM,
    subject: str,
    grade: str,
    background: str,
    profile: Dict,
    charpt_name: str,
    keywords: List[str],
    summary: str,
    default_level: str = "Level 3: APPLY",
    default_num_questions: int = 5,
    num_dummy_students: int = 3,
) -> None:
    """
    Streamlit component for displaying multiple choice questions.

    Args:
        subject: The subject area
        grade: Student's grade level
        background: Student's background
        profile: Student's learning profile
        charpt_name: Chapter name
        keywords: List of key concepts
        summary: Chapter summary
        default_level: Default Bloom's Taxonomy level
        default_num_questions: Default number of questions
        num_dummy_students: Number of dummy students
    """
    # Initialize session states
    if "generated_questions" not in st.session_state:
        st.session_state.generated_questions = None
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "selected_level" not in st.session_state:
        st.session_state.selected_level = 3
        st.session_state.num_questions = default_num_questions
    if "config_changed" not in st.session_state:
        st.session_state.config_changed = False
    if "question_sheets" not in st.session_state:
        st.session_state.question_sheets = {}  # List of dicts: [{file.stem: configs}, ...]
    if "basic_configs" not in st.session_state:
        st.session_state.basic_configs = {}

    # Sidebar for user inputs
    with st.sidebar:
        # Check for existing question files
        temp_folder = get_tmp_folder("question")
        temp_folder.mkdir(parents=True, exist_ok=True)
        existing_files = list(temp_folder.glob("*.json"))

        # Level selection
        levels = [
            "Level 1: REMEMBER",
            "Level 2: UNDERSTAND",
            "Level 3: APPLY",
            "Level 4: ANALYZE",
            "Level 5: EVALUATE",
            "Level 6: CREATE",
        ]
        st.session_state.selected_level = st.selectbox("**选择题目难度**", levels, index=levels.index(default_level))

        # Number of questions
        num_questions = st.number_input("题目数量", min_value=1, max_value=20, value=default_num_questions, step=1)

        prob_lower = st.number_input("答对正确概率下限", min_value=0.0, max_value=1.0, value=0.1, step=0.1, help="答对正确概率下限，设置过高可能过滤掉过多题目")
        prob_upper = st.number_input("答对正确概率上限", min_value=0.0, max_value=1.0, value=0.9, step=0.1, help="答对正确概率上限，设置过低可能过滤掉过多题目")

        configs = {
            "generate_new_survey": False,
            "generate_new_profile": False,
            "question_sheet_id": "",
            "generate_students": False,
            "renew_self_ability": True,
            "p_range": [prob_lower, prob_upper],
            "grade": grade,
            "background": background,
            "subject": subject,
            "already_learn_subject": "是",
            "level": st.session_state.selected_level,
            "profile": profile,
            "charpt_name": charpt_name,
            "keywords": keywords,
            "summary": summary,
            "num_questions": num_questions,
            "num_students": num_dummy_students,
        }
        if not st.session_state.basic_configs or any(
            st.session_state.basic_configs.get(k) != v for k, v in configs.items()
        ):
            st.session_state.basic_configs = configs
            st.session_state.config_changed = True
        # Two main buttons in sidebar
        col1, col2 = st.columns(2)
        with col1:
            if st.button("生成题目"):
                if "tutor_config" not in st.session_state or st.session_state.config_changed:
                    st.session_state.tutor_config = create_config(configs)
                    st.session_state.config_changed = False

                st.session_state.tutor = create_tutor(st.session_state.tutor_config, llm)
                with st.spinner("正在生成题目..."):
                    try:
                        # Start from beginning
                        # Interrupt the tutor process, wait for user answer
                        # Questions generated and students answers generated
                        interrupt_result = st.session_state.tutor.app.invoke(
                            {"messages": []}, st.session_state.tutor.config
                        )

                        result = interrupt_result["__interrupt__"][0].value

                        st.session_state.generated_questions = result.get("questions", [])
                        # Reset answers and submitted state when generating new questions
                        st.session_state.answers = []
                        st.session_state.submitted = False
                        
                        # Show success message and prompt user to view saved questions
                        st.success("✅ 题目生成完成！")
                        st.info("💡 提示：你可以点击侧边栏的'使用已有题目'按钮来查看和保存已生成的题目。")
                    except Exception as e:
                        st.error(f"发生错误: {str(e)}")

        with col2:
            if st.button("使用已有题目"):
                st.session_state.show_saved_questions = True
                st.rerun()

    # Main content area
    if st.session_state.get("show_saved_questions", False):
        if existing_files:
            # Get unique chapters from existing files
            chapters = sorted(set(file.stem.split("-")[1] for file in existing_files))

            # Add chapter selection dropdown
            selected_chapter = st.selectbox(
                "**选择章节**", chapters, index=chapters.index(charpt_name) if charpt_name in chapters else 0
            )

            # Get unique grades for the selected chapter
            chapter_files = [file for file in existing_files if file.stem.split("-")[1] == selected_chapter]
            available_grades = sorted(set(file.stem.split("-")[2] for file in chapter_files))

            # Add grade selection dropdown
            selected_grade = st.selectbox(
                "**选择年级**",
                available_grades,
                index=available_grades.index(grade) if grade in available_grades else 0
            )

            # Get unique levels for the selected chapter and grade
            grade_chapter_files = [file for file in chapter_files if file.stem.split("-")[2] == selected_grade]
            available_levels = sorted(set(file.stem.split("-")[3] for file in grade_chapter_files))

            # Add multi-select for levels
            selected_levels = st.multiselect(
                "**选择难度级别**",
                available_levels,
                default=available_levels,  # Select all levels by default
            )

            # Filter files by selected chapter, grade and levels
            filtered_files = [file for file in grade_chapter_files if file.stem.split("-")[3] in selected_levels]

            if filtered_files:
                # Group files by grade
                grade_groups = {}
                for file in filtered_files:
                    saved_grade = file.stem.split("-")[2]  # Grade is at index 2
                    if saved_grade not in grade_groups:
                        grade_groups[saved_grade] = []
                    grade_groups[saved_grade].append(file)

                # Display questions grouped by grade
                for grade, files in grade_groups.items():
                    st.markdown(f"### 适用年级: {grade}")
                    for i, file in enumerate(files, 1):
                        try:
                            with open(file, "r", encoding="utf-8") as f:
                                questions = json.load(f)
                                with st.expander(f"第{i}组题目"):
                                    for q in questions["questions"]:
                                        st.write(f"{q['id']}. {q['question']}")

                            # Add a button to use this specific question set
                            if st.button("使用这组题目", key=f"use_{file.stem}"):
                                # Check if this question sheet is already in the list
                                sheet_exists = any(file.stem in sheet for sheet in st.session_state.question_sheets)
                                sheet_config = configs.copy()
                                sheet_config["question_sheet_id"] = file.stem
                                if sheet_exists:
                                    if st.session_state.config_changed:
                                        configs_with_thread_id = create_config(sheet_config)
                                        st.session_state.question_sheets[file.stem] = configs_with_thread_id
                                        st.session_state.config_changed = False
                                    else:
                                        configs_with_thread_id = st.session_state.question_sheets[file.stem]
                                else:
                                    # Create new config for this question sheet
                                    configs_with_thread_id = create_config(sheet_config)
                                    st.session_state.question_sheets[file.stem] = configs_with_thread_id

                                st.session_state.tutor = create_tutor(configs_with_thread_id, llm)

                                # Start from beginning
                                # Interrupt the tutor process, wait for user answer
                                # Questions and students answers retrieved
                                interrupt_result = st.session_state.tutor.app.invoke(
                                    {"messages": []}, st.session_state.tutor.config
                                )

                                result = interrupt_result["__interrupt__"][0].value

                                st.session_state.generated_questions = result.get("questions", [])
                                st.session_state.answers = []  # Reset answers when loading new questions
                                st.session_state.submitted = False  # Reset submitted state
                                st.session_state.show_saved_questions = False  # Hide saved questions view
                                st.rerun()
                        except UnicodeDecodeError:
                            st.error(f"文件 {file.name} 编码错误，请确保使用 UTF-8 编码。")
                            continue
                    st.divider()
            else:
                st.warning(f"没有找到章节 '{selected_chapter}' 的所选难度级别的题目")
                if st.button("返回"):
                    st.session_state.show_saved_questions = False
                    st.rerun()
        else:
            st.warning("没有找到已保存的题目")
            if st.button("返回"):
                st.session_state.show_saved_questions = False
                st.rerun()
    elif st.session_state.generated_questions is None:
        st.warning("↙️请在侧边栏设置题目难度和数量")
    else:
        # Display questions in a form
        with st.form("questions_form"):
            # Initialize answers with required keys from generated_questions
            st.session_state.answers = [
                {
                    "id": q["id"],
                    "answer": q["answer"],
                    "difficulty": q["difficulty"],
                    "discrimination": q["discrimination"],
                    "user_answer": None,
                    "correct": None,
                }
                for q in st.session_state.generated_questions
            ]

            for q, answer, i in zip(
                st.session_state.generated_questions,
                st.session_state.answers,
                range(len(st.session_state.generated_questions)),
            ):
                user_answer = st.radio(
                    f"**{i + 1}. {q['question']}**",
                    options=q["options"],
                    key=q["id"],
                    index=int(answer["user_answer"]) if answer["user_answer"] is not None else None,
                )

                # Update the answer in session state
                if user_answer is not None:
                    answer["user_answer"] = q["options"].index(user_answer)
                    answer["correct"] = answer["user_answer"] == int(q["answer"])

                # Show answer and explanation if form is submitted
                if st.session_state.submitted:
                    st.write("---")
                    is_correct = answer["correct"]

                    if is_correct:
                        st.success(f"✅ 你的答案: {answer['user_answer']}")
                    else:
                        st.error(f"❌ 你的答案: {answer['user_answer']}")

                    st.write(f"正确答案: {answer['answer']}")
                    st.write(f"解释: {q['explanation']}")
                st.divider()

            # Submit or Regenerate button for the form
            if st.session_state.submitted:
                if st.form_submit_button("重新生成"):
                    st.session_state.generated_questions = None
                    st.session_state.answers = []
                    st.session_state.submitted = False
                    st.rerun()
            else:
                submitted = st.form_submit_button("提交答案")
                if submitted:
                    # Check if all questions are answered
                    unanswered = [i for i, q in enumerate(st.session_state.answers, 1) if q["user_answer"] is None]
                    if unanswered:
                        st.error(f"请回答以下问题: {', '.join(map(str, unanswered))}")
                    else:
                        st.session_state.submitted = True
                        # Resume the tutor process
                        # Start from the user answer
                        st.session_state.tutor.app.invoke(
                            Command(resume=st.session_state.answers), st.session_state.tutor.config
                        )

                        st.rerun()
