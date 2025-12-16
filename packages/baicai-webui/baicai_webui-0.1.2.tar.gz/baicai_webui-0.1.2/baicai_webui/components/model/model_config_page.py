import streamlit as st
from baicai_base.configs import ConfigManager, LLMConfig
from baicai_base.services.llms import LLM
from baicai_webui.components.model.model_config_form import render_model_config_form
import os


def get_page_llm(
    config_id: str = None,
    title: str = None,
    info_text: str = None,
    expanded: bool = False,
    use_default_config: bool = True,
) -> LLM:
    """Get LLM instance for a page with configuration UI

    Args:
        config_id: Unique identifier for the page's configuration
        title: Title for the configuration section
        info_text: Help text to display above the configuration
        expanded: Whether the configuration section should be expanded by default
        use_default_config: Whether to use global settings instead of page-specific settings

    Returns:
        LLM: Configured LLM instance
    """
    # Initialize ConfigManager
    config_manager = ConfigManager()

    # Get all available configurations
    all_configs = config_manager.list_configs()
    default_config = config_manager.load_default_config()

    # Initialize config with default value
    config = default_config

    # Create configuration UI
    with st.expander(title or "模型配置", expanded=expanded):
        if info_text:
            st.info(info_text)

        # Add checkbox for using global settings
        use_global = st.checkbox("使用大模型全局配置", value=use_default_config, key=f"{config_id}_use_global")

        if not use_global:
            # Show configuration selector
            config_options = ["创建新配置"] + all_configs
            selected_config = st.selectbox(
                "选择配置",
                options=config_options,
                index=config_options.index(config_id) if config_id in config_options else 0,
                key=f"{config_id}_select_config",
            )

            if selected_config == "创建新配置":
                # Create new configuration
                config_name = st.text_input("配置名称", value=config_id or "new_config")
                # Create a default config for new configurations
                new_config = LLMConfig(provider="groq", model_name="qwen/qwen3-32b", temperature=0.0)

                # Define save callback that updates the configuration list
                def save_new_config(config):
                    config_manager.save_config(config_name, config)
                    # Force a rerun to refresh the configuration list
                    st.rerun()

                render_model_config_form(
                    config=new_config,
                    key_prefix=config_name or "new_config",
                    on_save=save_new_config,
                    show_delete=False,
                )
                config = new_config
            else:
                # Load and show existing configuration
                config = config_manager.load_config(selected_config, LLMConfig)
                render_model_config_form(
                    config=config,
                    key_prefix=selected_config,
                    on_save=lambda config: config_manager.save_config(selected_config, config),
                    on_delete=lambda: config_manager.delete_config(selected_config)
                    if selected_config != "global"
                    else None,
                    show_delete=selected_config != "global",
                )
        else:
            # Show global configuration
            st.info("使用全局配置")
            config = default_config

    # Ensure we have a valid configuration
    if config is None:
        # If no configuration is available, create a default one
        config = LLMConfig(provider="groq", model_name="qwen/qwen3-32b", temperature=0.0)
        # Save the default configuration as global
        config_manager.save_config("global", config)

    # Create and return LLM instance with just the config_id
    return LLM(config_id=config_id or "global").llm
