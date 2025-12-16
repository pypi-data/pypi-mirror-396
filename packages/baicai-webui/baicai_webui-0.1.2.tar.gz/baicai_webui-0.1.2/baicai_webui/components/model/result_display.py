import streamlit as st
import streamlit_mermaid as stmd

BASELINE_STRUCTURE = """
graph LR
    A[数据加载] --> B[数据预处理]
    B --> C[模型训练]
    C --> D[模型评估]
    D --> E[特征重要性分析]
"""

WORKFLOW_STRUCTURE = """
graph LR
    A[加载数据] --> B[特征工程]
    B --> C[模型调参]
    C --> D[模型训练]
    D --> E[模型评估]
"""

name_map = {"baseline": "基线模型", "action": "特征工程", "workflow": "工作流", "optimization": "模型优化", "dl": "深度学习"}


def display_action_items(actions):
    """显示动作项列表"""
    if not actions:
        st.info("没有找到特征工程方法")
        return

    action_map = {
        "id": "ID",
        "action": "特征工程建议",
        "features": "特征",
        "business_justification": "业务理由",
        "expected_impact": "预期影响",
        "domain_rules_compliance": "领域规则合规性",
        "rejected": "是否拒绝",
        "rejection_reason": "拒绝原因",
        "code": "代码",
        "success": "是否成功",
        "result": "执行结果",
        "ignore": "是否忽略",
        "error": "错误",
        "accepted": "是否接受",
    }

    # 初始化session state
    if "expand_all" not in st.session_state:
        st.session_state.expand_all = False

    # 添加控制按钮
    col1, col2 = st.columns([1, 5])
    with col1:
        button_text = "全部折叠" if st.session_state.expand_all else "全部展开"
        if st.button(button_text, key="expand_collapse_button"):
            st.session_state.expand_all = not st.session_state.expand_all
            st.rerun()

    for i, action in enumerate(actions):
        st.subheader(f"{i + 1}: {action.get('action', '未命名动作')}")

        rejected = action.get("rejected", "false") == "true"

        with st.expander(f"特征工程建议 {i + 1}: {'✅ 接受建议' if not rejected else '❌ 拒绝建议'}", expanded=st.session_state.expand_all):
            if action.get("success", False):
                st.success("✅ 该特征工程建议代码运行成功")
            else:
                st.error("❌ 该特征工程建议代码运行失败")
            # 显示其他字段
            for key, value in action.items():
                if key not in ["id", "action", "code", "rejected", "accepted", "success", "result"] and value:
                    st.write(f"**{action_map[key]}**: {value}")
            if action.get("code", ""):
                st.write("**代码**")
                st.code(action.get("code", ""), language="python")

            if action.get("result", ""):
                st.write("**执行结果**")
                st.text(action.get("result", ""))


def display_results(state, graph=None):
    """显示机器学习流程的结果

    Args:
        state: 包含所有模型状态的字典
    """
    if not state:
        st.warning("请先运行训练过程")
        return

    try:
        if graph is None:  # 默认机器学习任务
            # 创建选项卡显示不同模块的结果
            tabs = st.tabs(["基线模型", "特征工程", "工作流", "模型优化"])

            # 基线模型选项卡
            with tabs[0]:
                show_tab(state, "baseline")

            # 特征工程选项卡
            with tabs[1]:
                st.header("特征工程结果")
                actions = state.get("actions", [])
                action_success = state.get("action_success", False)

                st.info(f"特征工程创建{'成功✅' if action_success else '失败❌'}")

                if actions:
                    display_action_items(actions)
                else:
                    st.info("没有找到特征工程方法")

            # 工作流选项卡
            with tabs[2]:
                show_tab(state, "workflow")

            # 模型优化选项卡
            with tabs[3]:
                show_tab(state, "optimization")

                # # 如果是最佳模型，特别标注
                # if "best_model" in code_item and code_item["best_model"]:
                #     st.success("🏆 最佳模型")
        else:
            show_tab(state, graph)

    except Exception as e:
        st.error(f"显示结果时出错: {str(e)}")


def format_code_block(code, language="python"):
    """格式化代码块以便在Streamlit中显示"""
    return f"```{language}\n{code}\n```"


def display_code_result(code_item, index=None):
    """显示单个代码项的结果"""
    with st.expander(f"版本 {index + 1 if index is not None else ''}"):
        if "code" in code_item:
            st.markdown(format_code_block(code_item["code"]))

        if "result" in code_item and code_item["result"]:
            st.subheader("执行结果")
            st.text(code_item["result"])

        if "success" in code_item:
            status = f"当前代码运行{'成功✅' if code_item['success'] else '失败❌'}"
            st.info(status)

        if "error" in code_item and code_item["error"]:
            st.error(f"错误: {code_item['error']}")


def show_tab(state, graph):
    st.header(f"{name_map[graph]}结果")
    codes = state.get(f"{graph}_codes", [])
    success = state.get(f"{graph}_success", False)

    st.info(f"{name_map[graph]}创建{'成功✅' if success else '失败❌'}")

    if graph == "baseline" or graph == "dl":
        stmd.st_mermaid(BASELINE_STRUCTURE, key=f"{graph}_structure", show_controls=False)
    elif graph == "workflow" or graph == "optimization":
        stmd.st_mermaid(WORKFLOW_STRUCTURE, key=f"{graph}_structure", show_controls=False)

    if codes:
        total_codes = len(codes)
        for i, code_item in enumerate(reversed(codes)):
            display_code_result(code_item, total_codes - i - 1)
    else:
        st.info(f"没有找到{name_map[graph]}代码")
