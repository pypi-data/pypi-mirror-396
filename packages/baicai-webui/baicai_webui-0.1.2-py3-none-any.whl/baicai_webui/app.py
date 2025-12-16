import sys
from pathlib import Path

import streamlit as st

from baicai_webui.utils import guard_llm_setting

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

if guard_llm_setting():
    # Define your pages with custom titles and icons
    pages = [
        st.Page("pages/home.py", title="主页", icon="🏠"),
        st.Page("pages/book.py", title="教材学习", icon="📚"),
        st.Page("pages/quiz.py", title="小测验", icon="📝"),
        st.Page("pages/vision.py", title="计算机视觉", icon="👁️"),
        st.Page("pages/nlp.py", title="自然语言处理", icon="💬"),
        st.Page("pages/collab.py", title="推荐系统", icon="🤝"),
        st.Page("pages/ml.py", title="传统机器学习", icon="📊"),
        st.Page("pages/llm_setting.py", title="大模型配置", icon="⚙️"),
        # st.Page("pages/try.py", title="开发", icon="🛠️"),
    ]
else:
    pages = [
        st.Page("pages/llm_setting.py", title="大模型配置", icon="⚙️"),
    ]


# Set up navigation
pg = st.navigation(pages)
st.set_page_config(page_title="白菜人工智能平台", page_icon="🥬", layout="wide", initial_sidebar_state="expanded")
pg.run()
