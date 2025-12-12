import streamlit as st
from baicai_base.configs import ConfigManager, LLMConfig
from baicai_base.services.llms import ensure_api_key

from baicai_webui.components.model.model_config_form import render_model_config_form


def format_api_key(key: str) -> str:
    """Format API key to show first and last 4 digits."""
    if len(key) <= 8:
        return "*" * len(key)
    return f"{key[:4]}{'*' * (len(key) - 8)}{key[-4:]}"


def save_env_file(env_path, env_vars):
    """Save environment variables to .env file."""
    try:
        with open(env_path, "w") as f:
            for k, v in env_vars.items():
                f.write(f'{k}="{v}"\n')
        return True
    except Exception as e:
        st.error(f"保存文件时出错: {str(e)}")
        return False


def load_env_file(env_path):
    """Load environment variables from .env file."""
    env_vars = {}
    if env_path.exists():
        try:
            with open(env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        key, value = line.split("=", 1)
                        # Remove quotes if present
                        value = value.strip("\"'")
                        env_vars[key] = value
        except Exception as e:
            st.error(f"读取文件时出错: {str(e)}")
    return env_vars


def render_model_settings():

    # Initialize config manager
    config_manager = ConfigManager()

    # Get available configs (excluding default and global)
    available_configs = config_manager.list_configs()

    # Create tabs for different configuration types
    tab1, tab2, tab3 = st.tabs(["API密钥管理", "全局模型设置", "特定模型设置"])

    with tab1:
        st.subheader("API密钥管理")
        st.info("管理不同模型提供商的API密钥。")

        # Read current .env file
        env_path = config_manager.env_file
        env_vars = load_env_file(env_path)

        # Display current API keys
        st.write("当前API密钥：")
        for key, value in env_vars.items():
            col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
            with col1:
                st.text(key)
            with col2:
                st.text(format_api_key(value))
            with col3:
                if st.button("修改", key=f"edit_{key}"):
                    st.session_state[f"editing_{key}"] = True
            with col4:
                if st.button("删除", key=f"del_{key}"):
                    st.session_state[f"to_delete_{key}"] = True

            # Show delete confirmation if needed
            if st.session_state.get(f"to_delete_{key}", False):
                if st.checkbox(f"确认删除 {key}？", key=f"confirm_del_{key}"):
                    # Remove the key from env_vars
                    del env_vars[key]
                    # Write back to .env file
                    if save_env_file(env_path, env_vars):
                        st.success(f"{key} 已删除！")
                        del st.session_state[f"to_delete_{key}"]
                        st.rerun()

            # Show edit form if editing
            if st.session_state.get(f"editing_{key}", False):
                with st.form(key=f"edit_form_{key}"):
                    st.text_input("密钥值", value=value, type="password", key=f"edit_value_{key}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("保存"):
                            new_value = st.session_state[f"edit_value_{key}"]
                            env_vars[key] = new_value
                            # Write back to .env file
                            if save_env_file(env_path, env_vars):
                                st.success(f"{key} 已更新！")
                                st.session_state[f"editing_{key}"] = False
                                st.rerun()
                    with col2:
                        if st.form_submit_button("取消"):
                            st.session_state[f"editing_{key}"] = False
                            st.rerun()

        # Add new API key
        st.subheader("添加新API密钥")

        # Key type selection
        key_type_options = ["OPENAI_API_KEY", "GROQ_API_KEY", "其他"]
        selected_key_type = st.selectbox("选择密钥类型", key_type_options)

        # Get the actual key name
        if selected_key_type == "其他":
            new_key = st.text_input("密钥名称", placeholder="请输入自定义密钥名称")
        else:
            new_key = selected_key_type

        new_value = st.text_input("密钥值", type="password")

        if st.button("添加密钥") and new_key and new_value:
            if new_key in env_vars:
                st.error("该密钥已存在！")
            else:
                # Add the new key
                env_vars[new_key] = new_value
                # Write back to .env file
                if save_env_file(env_path, env_vars):
                    st.success(f"{new_key} 已添加！")
                    st.rerun()

    with tab2:
        # Load global config (falls back to default if not exists)
        global_config = LLMConfig.load()

        def save_global_config(new_config):
            new_config.save_global()
            st.success("全局设置已保存！")
            ensure_api_key(new_config.provider)
            st.rerun()

        def delete_global_config():
            LLMConfig.delete("global")
            st.success("全局设置已删除！")
            st.rerun()

        render_model_config_form(
            config=global_config,
            key_prefix="global",
            on_save=save_global_config,
            on_delete=delete_global_config,
            title="全局设置",
            info_text="全局设置将作为所有未指定配置的默认值。如果未设置全局配置，将使用系统默认值。",
        )

    with tab3:
        st.subheader("特定设置")
        st.info("特定设置将覆盖全局设置。选择或创建一个特定设置以进行自定义配置。")

        # Show available configs
        if available_configs:
            selected_config = st.selectbox("选择配置", available_configs, index=0)
            # Load the selected config
            config = LLMConfig.load(selected_config)

            def save_specific_config(new_config):
                new_config.save(selected_config)
                st.success(f"配置 '{selected_config}' 已保存！")
                ensure_api_key(new_config.provider)
                st.rerun()

            def delete_specific_config():
                LLMConfig.delete(selected_config)
                st.success(f"配置 '{selected_config}' 已删除！")
                st.rerun()

            render_model_config_form(
                config=config,
                key_prefix=f"specific_{selected_config}",
                on_save=save_specific_config,
                on_delete=delete_specific_config,
            )
        else:
            st.info("当前没有特定配置。")

        # Create new configuration
        st.subheader("新建设置")
        st.info("创建一个新的特定配置。新配置将继承当前全局设置的值。")

        # Load current global config as default values
        current_config = LLMConfig.load()

        # Initialize new_config_name in session state if not exists
        if "new_config_name" not in st.session_state:
            st.session_state["new_config_name"] = ""

        new_config_name = st.text_input(
            "新配置名称", value=st.session_state["new_config_name"], key="new_config_name_input"
        )

        # Update session state with the new value
        st.session_state["new_config_name"] = new_config_name

        if new_config_name:
            if new_config_name in ["default", "global"] or new_config_name in available_configs:
                st.error("配置名称已存在或为保留名称！")
            else:

                def save_new_config(new_config):
                    new_config.save(new_config_name)
                    st.success(f"新配置 '{new_config_name}' 已创建！")
                    ensure_api_key(new_config.provider)
                    # Clear the new_config_name from session state
                    st.session_state["new_config_name"] = ""
                    st.rerun()

                render_model_config_form(
                    config=current_config,
                    key_prefix=f"new_{new_config_name}",
                    on_save=save_new_config,
                    show_delete=False,
                )
