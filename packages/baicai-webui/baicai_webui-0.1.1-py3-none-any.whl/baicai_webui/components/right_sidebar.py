import streamlit as st

from baicai_webui.components.chat.ai_tutor import create_ai_tutor


def show_right_sidebar(from_level: int = 1, terms: list[str] = None):
    # Initialize session state for right sidebar
    if "right_sidebar_expanded" not in st.session_state:
        st.session_state.right_sidebar_expanded = True
    if "sidebar_width" not in st.session_state:
        st.session_state.sidebar_width = 5  # 默认宽度

    # Add custom CSS to reduce padding and margin and handle resizable sidebar
    st.markdown(
        """
        <style>
        .stContainer {
            padding: 0.5rem !important;
            margin: 0 !important;
        }
        .element-container {
            padding: 0.25rem !important;
            margin: 0 !important;
        }
        .stChatMessage {
            padding: 0.5rem !important;
            margin: 0.25rem 0 !important;
        }
        .sidebar-resize {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Create a container for the right sidebar
    right_sidebar = st.container()

    # Add controls for sidebar
    with right_sidebar:
        # Add a button to toggle the right sidebar
        if st.button("↔️", key="toggle_right_sidebar", help="点击展开/折叠右侧边栏", type="secondary"):
            st.session_state.right_sidebar_expanded = not st.session_state.right_sidebar_expanded
            st.rerun()

        # Add width control if sidebar is expanded
        if st.session_state.right_sidebar_expanded:
            st.markdown('<div class="sidebar-resize">', unsafe_allow_html=True)
            new_width = st.slider(
                "调整边栏宽度",
                min_value=5,
                max_value=10,
                value=st.session_state.sidebar_width,
                step=1,
                key="sidebar_width_slider",
                help="拖动滑块调整右侧边栏宽度",
            )
            st.markdown("</div>", unsafe_allow_html=True)

            if new_width != st.session_state.sidebar_width:
                st.session_state.sidebar_width = new_width
                st.rerun()

            # Show content with adjusted width
            create_ai_tutor(from_level=from_level, terms=terms)
