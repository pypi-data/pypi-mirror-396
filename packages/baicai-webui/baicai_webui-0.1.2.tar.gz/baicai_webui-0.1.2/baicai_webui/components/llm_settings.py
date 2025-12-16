import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv


def save_env_variable(key, value):
    """Save a key-value pair to the .env file"""
    env_path = Path(Path.home() / ".baicai" / "env" / ".env")

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(env_path), exist_ok=True)

    # Read existing env file
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()

    # Find if key exists
    key_exists = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_exists = True
            break

    # Add key if it doesn't exist
    if not key_exists:
        lines.append(f"{key}={value}\n")

    # Write back to file
    with open(env_path, "w") as f:
        f.writelines(lines)


def load_env_variables():
    """Load environment variables from .env file"""
    env_path = Path(Path.home() / ".baicai" / "env" / ".env")
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)


def render_llm_settings(sidebar=True):
    """Render LLM settings in the sidebar or main area based on the sidebar parameter"""
    # Load environment variables first
    load_env_variables()

    # Determine the container based on the sidebar parameter
    container = st.sidebar if sidebar else st

    with container.expander("大模型设置", expanded=True):
        # LLM Settings
        provider_options = ["openai兼容", "groq"]
        provider = container.selectbox(
            "大模型提供商",
            options=provider_options,
            index=provider_options.index(os.environ.get("LLM_PROVIDER", "groq")),
            help="选择您想要使用的大模型提供商。大多数大模型提供商都兼容OpenAI，而Groq专注于高性能计算。",
        )

        openai_api_key = None
        base_url = None
        groq_api_key = None

        if provider == "openai兼容":
            openai_api_key = container.text_input(
                "OpenAI API Key",
                value=os.environ.get("OPENAI_API_KEY", ""),
                type="password",
                help="输入您的OpenAI API密钥。您可以在OpenAI的官方网站上找到更多信息。",
            )
            base_url = container.text_input(
                "API 基础 URL",
                value=os.environ.get("LLM_BASE_URL", "https://api.deepseek.com" if provider == "openai兼容" else ""),
                help="输入API的基础URL。通常情况下，您可以使用默认值。",
            )
        else:
            groq_api_key = container.text_input(
                "Groq API Key",
                value=os.environ.get("GROQ_API_KEY", ""),
                type="password",
                help="输入您的Groq API密钥。访问Groq的官方网站以获取更多信息。",
            )

        # Model selection based on provider
        model_options = {
            "groq": [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "qwen/qwen3-32b",
                "deepseek-r1-distill-llama-70b",
            ],
            "openai": ["deepseek-chat", "deepseek-reasoner"],
        }

        model_name = container.selectbox(
            "模型名称",
            options=model_options[provider],
            index=0
            if os.environ.get("LLM_MODEL_NAME", "") not in model_options[provider]
            else model_options[provider].index(os.environ.get("LLM_MODEL_NAME", "")),
            help="选择您想要使用的模型名称。不同的模型适用于不同的任务。",
        )

        temperature = container.slider(
            "温度",
            min_value=0.0,
            max_value=1.0,
            value=float(os.environ.get("LLM_TEMPERATURE", "0.0")),
            step=0.1,
            help="调整生成文本的随机性。较高的温度会产生更随机的输出。",
        )

        # Save button
        if container.button("保存设置"):
            # Save API keys
            if openai_api_key:
                save_env_variable("OPENAI_API_KEY", openai_api_key)
                save_env_variable("LLM_BASE_URL", base_url)

            if groq_api_key:
                save_env_variable("GROQ_API_KEY", groq_api_key)

            # Save LLM settings
            save_env_variable("LLM_PROVIDER", provider)
            save_env_variable("LLM_MODEL_NAME", model_name)

            save_env_variable("LLM_TEMPERATURE", str(temperature))

            container.success("设置已保存")

            # Reload environment variables
            load_env_variables()

        # Add documentation link
        container.markdown("[点击这里了解更多关于大模型设置的信息](https://example.com/docs/llm-settings)")
