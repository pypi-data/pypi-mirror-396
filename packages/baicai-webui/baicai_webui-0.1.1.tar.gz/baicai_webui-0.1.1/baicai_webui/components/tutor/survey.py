import json

import streamlit as st
from baicai_base.services import LLM
from baicai_base.utils.data import get_tmp_folder, safe_extract_json
from baicai_tutor.agents.roles import analyst, surveyor

survey_template = {
    "questions": [
        {
            "id": 1,
            "question": "你为什么选择学习人工智能？",
            "options": ["对AI技术感兴趣", "为未来的职业规划", "课程安排需要", "其他"],
        },
        {
            "id": 2,
            "question": "你对人工智能领域哪些方面最感兴趣？",
            "options": ["机器学习", "自然语言处理", "计算机视觉", "机器人技术"],
        },
        {
            "id": 3,
            "question": "你每周花多少时间学习人工智能相关内容？",
            "options": ["少于5小时", "5-10小时", "10-15小时", "超过15小时"],
        },
        {
            "id": 4,
            "question": "你如何评估自己在人工智能基础知识上的掌握情况？",
            "options": ["非常好", "好", "一般", "不好"],
        },
        {
            "id": 5,
            "question": "你在学习人工智能时遇到的主要困难是什么？",
            "options": ["理论难懂", "缺乏实践机会", "学习资源不足", "时间不够"],
        },
        {
            "id": 6,
            "question": "你是否认为学习人工智能对你的职业发展有帮助？",
            "options": ["非常有帮助", "有帮助", "一般", "不太有帮助"],
        },
        {
            "id": 7,
            "question": "你是否对人工智能的实际应用感兴趣？",
            "options": ["非常感兴趣", "感兴趣", "一般", "不感兴趣"],
        },
        {
            "id": 8,
            "question": "你是否有兴趣深入研究人工智能的前沿领域？",
            "options": ["非常有兴趣", "有兴趣", "一般", "不感兴趣"],
        },
        {
            "id": 9,
            "question": "你是否愿意参与人工智能相关的项目或竞赛？",
            "options": ["非常愿意", "愿意", "一般", "不愿意"],
        },
        {
            "id": 10,
            "question": "你在学习人工智能时，通常如何处理遇到的难点？",
            "options": ["查阅资料", "请教老师或同学", "参加讨论组", "放弃"],
        },
        {"id": 11, "question": "你是否有计划定期复习人工智能课程内容？", "options": ["是", "否"]},
        {"id": 12, "question": "你是否经常在课后做人工智能相关的练习题？", "options": ["经常", "偶尔", "很少", "不做"]},
        {
            "id": 13,
            "question": "你是否主动与同学讨论人工智能相关的学习内容？",
            "options": ["经常", "偶尔", "很少", "不主动"],
        },
        {"id": 14, "question": "你是否使用多种资源（如在线课程、书籍）来学习人工智能？", "options": ["是", "否"]},
        {"id": 15, "question": "你是否在遇到学习困难时主动寻求帮助？", "options": ["是", "否"]},
        {
            "id": 16,
            "question": "你对人工智能的基本概念（如机器学习、神经网络）是否有清晰的理解？",
            "options": ["非常清晰", "较清晰", "不太清晰", "不清晰"],
        },
        {
            "id": 17,
            "question": "你对人工智能中的数据结构和算法是否有良好的掌握？",
            "options": ["非常好", "好", "一般", "不好"],
        },
        {"id": 18, "question": "你是否能够理解和应用人工智能的基本算法？", "options": ["是", "否"]},
        {"id": 19, "question": "你对人工智能课程的整体掌握情况如何？", "options": ["非常好", "好", "一般", "不好"]},
        {
            "id": 20,
            "question": "你是否愿意继续深入学习人工智能相关课程？",
            "options": ["非常愿意", "愿意", "一般", "不愿意"],
        },
    ]
}


def collect_user_info():
    """Collect user information before generating survey."""
    st.title("学情调研信息收集")
    st.write("请填写以下信息，帮助我们为您生成合适的问卷。")

    # Initialize session state for form values if not exists
    if "form_values" not in st.session_state:
        st.session_state.form_values = {
            "subject": "人工智能",
            "already_learn_subject": "否",
            "education_level": "本科",
            "specific_grade": "大一",
            "background": "",
        }

    # Split grade selection into two parts - outside the form for real-time updates
    education_level = st.selectbox(
        "教育阶段",
        ["小学", "中学", "高职", "本科", "研究生", "已工作"],
        index=["小学", "中学", "高职", "本科", "研究生", "已工作"].index(
            st.session_state.form_values.get("education_level", "本科")
        ),
    )

    # Get current specific grade from session state
    current_specific_grade = st.session_state.form_values.get("specific_grade", "大一")

    # Show appropriate options based on education level
    if education_level == "小学":
        grade_options = ["一年级", "二年级", "三年级", "四年级", "五年级", "六年级"]
        default_grade = "一年级"
    elif education_level == "中学":
        grade_options = ["初一", "初二", "初三", "高一", "高二", "高三"]
        default_grade = "初一"
    elif education_level == "高职":
        grade_options = ["大一", "大二", "大三"]
        default_grade = "大一"
    elif education_level == "本科":
        grade_options = ["大一", "大二", "大三", "大四"]
        default_grade = "大一"
    elif education_level == "研究生":
        grade_options = ["研一", "研二", "研三", "低年级博士", "高年级博士"]
        default_grade = "研一"
    else:  # 已工作
        grade_options = ["1-3年", "3-5年", "5-10年", "10年以上"]
        default_grade = "1-3年"

    # If current grade is not in the new options, use default
    if current_specific_grade not in grade_options:
        current_specific_grade = default_grade

    # Create a form to group other inputs
    with st.form("user_info_form"):
        specific_grade = st.selectbox(
            "年级" if education_level != "已工作" else "工作年限",
            grade_options,
            index=grade_options.index(current_specific_grade),
        )

        # Update session state immediately when education level or grade changes
        st.session_state.form_values["education_level"] = education_level
        st.session_state.form_values["specific_grade"] = specific_grade

        # Combine education level and specific grade
        grade = f"{education_level}{specific_grade}"

        subject = st.text_input(
            "学科", placeholder="请输入您要学习的学科，例如：人工智能", value=st.session_state.form_values["subject"]
        )
        already_learn_subject = st.selectbox(
            "已经学习过当前学科",
            ["是", "否"],
            index=["是", "否"].index(st.session_state.form_values["already_learn_subject"]),
        )
        background = st.text_area(
            "学习背景",
            placeholder="请描述您的学习背景，例如：不熟悉人工智能、有编程基础等",
            value=st.session_state.form_values["background"],
        )

        # Update session state with current values
        st.session_state.form_values.update(
            {
                "subject": subject,
                "already_learn_subject": already_learn_subject,
                "background": background,
            }
        )

        submitted = st.form_submit_button("生成问卷")

        if submitted:
            if not all([grade, background, subject]):
                st.error("请填写所有信息后再生成问卷")
                return None

            user_info = {
                "grade": grade,
                "background": background,
                "subject": subject,
                "already_learn_subject": already_learn_subject,
            }
            return user_info
    return None


def generate_survey(user_info, llm):
    """Generate survey based on user information."""
    original_result, extracted_result, reflections, failed = safe_extract_json(
        surveyor(llm),
        {
            "messages": [],
            **user_info,
        },
    )
    return extracted_result


def display_survey(questions=None):
    """Display the survey and collect answers."""
    st.title("学习情况调查问卷")

    if questions is None:
        questions = survey_template

    # Initialize session state for answers if not exists
    if "answers" in st.session_state and st.session_state.answers == {}:
        # Initialize all answers as None
        for question in questions["questions"]:
            answer_key = f"q_{question['id']}"
            st.session_state.answers[answer_key] = None

    # Create a form to group all questions
    with st.form("survey_form"):
        # Display each question and collect answers
        for question in questions["questions"]:
            st.subheader(f"问题 {question['id']}")

            # Create a unique key for each question
            answer_key = f"q_{question['id']}"

            # Display radio buttons for options with current selection
            current_answer = st.session_state.answers[answer_key]
            answer = st.radio(
                f"**{question['question']}**",
                options=question["options"],
                key=answer_key,
                index=current_answer if current_answer is not None else None,
            )

            # Update the answer in session state
            if answer is not None:
                st.session_state.answers[answer_key] = question["options"].index(answer)

        # Add submit button within the form
        submitted = st.form_submit_button("提交问卷")

        if submitted:
            # Check for unanswered questions
            unanswered_questions = []
            for question in questions["questions"]:
                answer_key = f"q_{question['id']}"
                if st.session_state.answers[answer_key] is None:
                    unanswered_questions.append({"id": question["id"], "question": question["question"]})

            # If there are unanswered questions, show error message
            if unanswered_questions:
                error_message = "请完成以下未回答的问题后再提交：\n\n"
                for q in unanswered_questions:
                    error_message += f"问题 {q['id']}: {q['question']}\n\n"
                st.error(error_message)
                return None

            # Update questions with answers
            for question in questions["questions"]:
                answer_key = f"q_{question['id']}"
                question["user_answer"] = st.session_state.answers[answer_key]

            st.success("问卷提交成功！开始分析结果...")
            return questions

    return None


def analyze_survey_results(questions, llm):
    """Analyze survey results using the analyst agent."""
    # Get analysis from the analyst agent
    original_result, extracted_result, reflections, failed = safe_extract_json(
        analyst(llm),
        {
            "messages": [
                ("user", "用户问卷反馈数据：\n" + str(questions)),
            ],
        },
    )

    return extracted_result


def survey_flow():
    llm = LLM().llm
    """Main survey flow that handles user info collection and survey display."""
    # Initialize session state for survey if not exists
    if "generated_survey" not in st.session_state:
        st.session_state.generated_survey = None
    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "form_values" not in st.session_state:
        st.session_state.form_values = {
            "subject": "人工智能",
            "already_learn_subject": "否",
            "education_level": "本科",
            "specific_grade": "大一",
            "background": "",
        }

    # If survey is not generated, collect user info
    if st.session_state.generated_survey is None:
        user_info = collect_user_info()
        if user_info:
            st.session_state.user_info = user_info
            st.session_state.generated_survey = generate_survey(user_info, llm)
            st.rerun()
    elif st.session_state.analysis_result is None:
        # Display the generated survey
        result = display_survey(questions=st.session_state.generated_survey)
        if result:
            st.session_state.analysis_result = {"basic_info": st.session_state.user_info}
            # Analyze the results
            analysis_result = analyze_survey_results(st.session_state.generated_survey, llm)
            st.session_state.analysis_result.update(analysis_result)
            st.rerun()

    elif st.session_state.generated_survey and st.session_state.analysis_result:
        # Display analysis results
        result = st.session_state.analysis_result
        try:
            st.subheader("分析结果概要")
            st.markdown(f"学生类型为{result['summary']['type']}, {result['summary']['description']}")

            with st.expander("查看详细分析结果"):
                st.json(result)

        except Exception as e:
            st.error(f"分析结果无法显示，错误信息：{e}")
            st.json(result)

        # Add a button to start a new survey
        if st.button("继续"):
            # Reset all session state variables to their initial values
            reset_session_state()
            st.rerun()

        temp_folder = get_tmp_folder("user_info")
        temp_folder.mkdir(parents=True, exist_ok=True)
        with open(temp_folder / "survey.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.generated_survey, f, ensure_ascii=False, indent=2)
        with open(temp_folder / "profile.json", "w", encoding="utf-8") as f:
            json.dump(st.session_state.analysis_result, f, ensure_ascii=False, indent=2)


def reset_session_state():
    st.session_state.analysis_result = None
    st.session_state.generated_survey = None
    st.session_state.answers = {}
    st.session_state.form_values = {
        "subject": "人工智能",
        "already_learn_subject": "否",
        "education_level": "本科",
        "specific_grade": "大一",
        "background": "",
    }
