import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowEdge, StreamlitFlowNode
from streamlit_flow.state import StreamlitFlowState

page_map = {
    "0": "book",
    "1": "quiz",
    "2": "vision",
    "3": "nlp",
    "4": "collab",
    "5": "ml",
    "6": "book",
}


def reset_session_state():
    """Reset session state variables used by the AI assistant to their initial values."""
    st.session_state.messages = []
    st.session_state.message_placeholders = {}

    st.session_state.tutor_messages = []
    st.session_state.tutor_message_placeholders = {}


def button_graph():
    nodes = [
        StreamlitFlowNode(
            id="0",
            pos=(100, 300),
            data={"content": "人工智能基础"},
            node_type="input",
            source_position="right",
            draggable=False,
        ),
        StreamlitFlowNode("1", (250, 300), {"content": "智能体"}, "default", "right", "left", draggable=False),

        StreamlitFlowNode("2", (400, 150), {"content": "计算机视觉"}, "default", "right", "left", draggable=False),
        StreamlitFlowNode("3", (400, 250), {"content": "自然语言处理"}, "default", "right", "left", draggable=False),
        StreamlitFlowNode("4", (400, 350), {"content": "推荐系统"}, "default", "right", "left", draggable=False),
        StreamlitFlowNode("5", (400, 450), {"content": "传统机器学习"}, "default", "right", "left", draggable=False),

        StreamlitFlowNode("6", (600, 300), {"content": "行业应用"}, "output", target_position="left", draggable=False),
    ]

    edges = [
        StreamlitFlowEdge("0-1", "0", "1", animated=True),
        StreamlitFlowEdge("1-2", "1", "2", animated=True),
        StreamlitFlowEdge("1-3", "1", "3", animated=True),
        StreamlitFlowEdge("1-4", "1", "4", animated=True),
        StreamlitFlowEdge("1-5", "1", "5", animated=True),
        StreamlitFlowEdge("2-6", "2", "6", animated=True),
        StreamlitFlowEdge("3-6", "3", "6", animated=True),
        StreamlitFlowEdge("4-6", "4", "6", animated=True),
        StreamlitFlowEdge("5-6", "5", "6", animated=True),
    ]

    if "click_interact_state" not in st.session_state:
        st.session_state.click_interact_state = StreamlitFlowState(nodes, edges)

    updated_state = streamlit_flow(
        "ret_val_flow",
        st.session_state.click_interact_state,
        fit_view=True,
        get_node_on_click=True,
        get_edge_on_click=True,
    )

    # st.write(f"Clicked on: {updated_state.nodes[int(updated_state.selected_id)].data['content']}")

    st.session_state.redirect_to = updated_state.selected_id

    # Check for redirect flag from button_graph component
    if "redirect_to" in st.session_state and st.session_state["redirect_to"]:
        node_id = st.session_state["redirect_to"]
        page = page_map.get(node_id)
        # Only navigate if there is a valid mapping
        if page:
            reset_session_state()
            st.session_state.redirect_to = None
            # Use Streamlit's programmatic navigation
            st.switch_page(f"pages/{page}.py")
        else:
            # Clear redirect flag if no mapping found to avoid repeated attempts
            st.session_state.redirect_to = None
