import streamlit as st
from baicai_base.configs import LLMConfig


def render_model_config_form(
    config: LLMConfig,
    key_prefix: str,
    on_save=None,
    on_delete=None,
    show_delete: bool = True,
    title: str = None,
    info_text: str = None,
):
    """Render a model configuration form.

    Args:
        config: The LLMConfig instance to use as default values
        key_prefix: Prefix for all widget keys to avoid conflicts
        on_save: Callback function when save button is clicked, receives the new config
        on_delete: Callback function when delete button is clicked
        show_delete: Whether to show the delete button
        title: Optional title for the form
        info_text: Optional info text to display above the form
    """
    if title:
        st.subheader(title)
    if info_text:
        st.info(info_text)

    # Provider selection
    provider = st.selectbox(
        "模型提供商",
        ["openai兼容", "groq"],
        index=0 if config.provider == "openai兼容" else 1,
        key=f"{key_prefix}_provider",
    )

    # Model input with default value
    default_model = "deepseek-chat" if provider == "openai兼容" else "qwen/qwen3-32b"
    model = st.text_input(
        "模型名称", value=config.model_name or default_model, help=f"默认值: {default_model}", key=f"{key_prefix}_model"
    )

    # Base URL input only for openai-compatible
    if provider == "openai兼容":
        base_url = st.text_input(
            "Base URL",
            value=config.base_url or "https://api.deepseek.com/",
            help="可选，用于自定义API端点",
            key=f"{key_prefix}_base_url",
        )
    else:
        base_url = None

    # Temperature slider
    temperature = st.slider(
        "温度", min_value=0.0, max_value=1.0, value=config.temperature, step=0.1, key=f"{key_prefix}_temperature"
    )

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("保存设置", key=f"{key_prefix}_save"):
            new_config = LLMConfig(
                provider=provider, model_name=model, temperature=temperature, base_url=base_url if base_url else None
            )
            if on_save:
                on_save(new_config)
            else:
                st.success("设置已保存！")

    if show_delete:
        with col2:
            # Initialize delete state if not exists
            if f"{key_prefix}_delete_state" not in st.session_state:
                st.session_state[f"{key_prefix}_delete_state"] = False

            # Show delete confirmation if in delete state
            if st.session_state[f"{key_prefix}_delete_state"]:
                if st.checkbox("确认删除？", key=f"{key_prefix}_confirm_delete"):
                    if on_delete:
                        on_delete()
                        st.session_state[f"{key_prefix}_delete_state"] = False
                        st.rerun()
            else:
                if st.button("删除设置", type="secondary", key=f"{key_prefix}_delete"):
                    st.session_state[f"{key_prefix}_delete_state"] = True
                    st.rerun()
