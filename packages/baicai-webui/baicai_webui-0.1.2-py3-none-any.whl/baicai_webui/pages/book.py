import json
import os
import tempfile
from pathlib import Path

import streamlit as st
from baicai_tutor.agents.roles.text_rewriter import rewriter
from baicai_tutor.utils.md_process import MarkdownProcessor, generate_output_filenames

from baicai_webui.utils import (
    create_chapter_selector,
    find_selected_chapter_file,
    get_available_chapters,
    get_callout_css,
    get_chapter_from_url_params,
    load_chapter_content,
    render_special_content,
    update_chapter_url_param,
)


def get_user_profile():
    """获取用户配置文件"""
    profile_path = Path.home() / ".baicai" / "tmp" / "user_info" / "profile.json"
    if profile_path.exists():
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
                return profile.get("personalized_recommendations", []), profile.get("summary", "")
        except Exception as e:
            st.warning(f"读取用户配置文件失败: {e}")
    return [], "AI初学者，对人工智能概念感兴趣，希望获得通俗易懂的解释"


def process_single_chunk_with_llm(chunk, profile_summary, personalized_recommendations):
    """使用LLM处理单个chunk"""
    try:
        result = rewriter().invoke({
            "messages": [],
            "textbook": chunk["content"],
            "profile": profile_summary,
            "personalized_recommendations": "\n".join(personalized_recommendations) if personalized_recommendations else "使用更多生活化的例子来解释AI概念"
        })

        # 提取重写后的内容
        content = result.content
        start_tag = "<obsidian_md>"
        end_tag = "</obsidian_md>"
        start_idx = content.find(start_tag)
        end_idx = content.find(end_tag)

        if start_idx != -1 and end_idx != -1:
            rewritten = content[start_idx + len(start_tag):end_idx].strip()
        else:
            rewritten = content

        return rewritten, None

    except Exception as e:
        return None, f"重写chunk '{chunk.get('title', 'unknown')}' 失败: {e}"


def process_chapter_with_llm(selected_chapter, selected_chapter_name, book_path):
    """使用LLM处理章节内容 - 分段处理版本"""

    need_rewrite_titles = ["思想实验", "知识基础", "知识进阶"]

    try:
        # 创建Markdown处理器
        processor = MarkdownProcessor(
            max_chunk_length=2000,
            preserve_metadata=True,
            modify_length_for_titles=need_rewrite_titles
        )

        # 处理章节文件
        chunks = processor.process_file(str(selected_chapter))

        # 获取用户配置
        personalized_recommendations, profile_summary = get_user_profile()

        # 创建输出目录
        output_dir = Path.home() / ".baicai" / "textbook"
        output_dir.mkdir(exist_ok=True)

        # 生成输出文件名
        filenames = generate_output_filenames(str(selected_chapter), output_dir)

        # 导出分块结果
        processor.export_chunks_to_json(chunks, str(filenames["json"]))

        # 读取分块结果
        with open(filenames["json"], "r", encoding="utf-8") as f:
            textbook_chunks = json.load(f)

        # 初始化session state
        if "rewrite_progress" not in st.session_state:
            st.session_state.rewrite_progress = {
                "chunks": textbook_chunks,
                "current_index": 0,
                "processed_chunks": [],
                "is_processing": False
            }

        return textbook_chunks, profile_summary, personalized_recommendations

    except Exception as e:
        st.error(f"初始化AI优化过程中发生错误: {e}")
        return None, None, None


def continue_rewriting(chunks, profile_summary, personalized_recommendations, selected_chapter_name):
    """继续处理下一个需要重写的chunk"""
    progress = st.session_state.rewrite_progress

    if progress["is_processing"]:
        st.warning("正在处理中，请稍候...")
        return

    progress["is_processing"] = True

    # 找到下一个需要处理的chunk
    current_index = progress["current_index"]
    while current_index < len(chunks):
        chunk = chunks[current_index]

        # 检查是否需要重写
        if any(keyword in chunk.get("title", "") for keyword in ["思想实验", "知识基础", "知识进阶"]):
            # 处理这个chunk
            with st.spinner(f"🤖 AI正在优化: {chunk.get('title', f'chunk_{current_index}')}"):
                rewritten_content, error = process_single_chunk_with_llm(
                    chunk, profile_summary, personalized_recommendations
                )

                if rewritten_content:
                    chunk["rewritten_content"] = rewritten_content
                    progress["processed_chunks"].append(current_index)
                    st.success(f"✅ 完成: {chunk.get('title', f'chunk_{current_index}')}")
                else:
                    st.error(f"❌ {error}")
                    chunk["rewritten_content"] = chunk["content"]  # 失败时保持原内容

            # 更新进度
            progress["current_index"] = current_index + 1
            progress["is_processing"] = False

            # 保存当前进度
            save_rewrite_progress(chunks, selected_chapter_name)

            # 检查下一个chunk是否需要重写
            next_needs_rewrite = False
            if progress["current_index"] < len(chunks):
                next_chunk = chunks[progress["current_index"]]
                next_needs_rewrite = any(keyword in next_chunk.get("title", "")
                                       for keyword in ["思想实验", "知识基础", "知识进阶"])

            if next_needs_rewrite:
                st.info("下一个部分需要AI优化，点击'继续优化'继续处理")
            else:
                st.success("下一个部分无需优化，内容将自动显示")

            return

        else:
            # 不需要重写的chunk，直接跳过
            current_index += 1
            progress["current_index"] = current_index

    # 所有chunk都处理完了
    progress["is_processing"] = False
    st.success("🎉 所有内容处理完成！")


def save_rewrite_progress(chunks, selected_chapter_name):
    """保存重写进度到文件"""
    try:
        output_dir = Path.home() / ".baicai" / "textbook"
        output_dir.mkdir(exist_ok=True)

        # 保存重写后的内容
        rewritten_json_path = output_dir / f"{selected_chapter_name}_rewritten.json"
        with open(rewritten_json_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)

        st.info(f"💾 进度已保存到: {rewritten_json_path}")

    except Exception as e:
        st.error(f"保存进度失败: {e}")


def load_rewrite_progress(selected_chapter_name):
    """加载已保存的重写进度"""
    try:
        output_dir = Path.home() / ".baicai" / "textbook"
        rewritten_json_path = output_dir / f"{selected_chapter_name}_rewritten.json"
        
        if rewritten_json_path.exists():
            with open(rewritten_json_path, "r", encoding="utf-8") as f:
                chunks = json.load(f)
            
            # 检查是否有重写过的内容
            has_rewritten_content = any("rewritten_content" in chunk for chunk in chunks)
            
            if has_rewritten_content:
                # 计算已处理的chunk数量
                processed_chunks = [i for i, chunk in enumerate(chunks) 
                                 if "rewritten_content" in chunk]
                
                # 找到下一个需要处理的索引
                current_index = 0
                for i, chunk in enumerate(chunks):
                    if any(keyword in chunk.get("title", "") for keyword in ["思想实验", "知识基础", "知识进阶"]):
                        if i not in processed_chunks:
                            current_index = i
                            break
                    current_index = i + 1
                
                return {
                    "chunks": chunks,
                    "current_index": current_index,
                    "processed_chunks": processed_chunks,
                    "is_processing": False
                }
        
        return None
    except Exception as e:
        st.error(f"加载进度失败: {e}")
        return None


def get_rewritten_content_display(chunks):
    """获取重写后的内容用于显示"""
    content_parts = []

    for chunk in chunks:
        if "rewritten_content" in chunk:
            content_parts.append(chunk["rewritten_content"])
        else:
            content_parts.append(chunk["content"])

    return "\n\n".join(content_parts)


def show():
    st.title("AI 入门教材学习")

    # 注入 callout 的 CSS 样式
    st.markdown(get_callout_css(), unsafe_allow_html=True)

    # Get portable path to AI_intro_book folder
    current_file = Path(__file__)
    book_path = current_file.parent.parent.parent / "AI_intro_book"

    # 检查书籍路径是否存在
    if not book_path.exists():
        st.error(f"未找到 AI_intro_book 文件夹: {book_path}")
        st.info("请确保 AI_intro_book 文件夹存在于项目根目录中。")
        return

    # 获取可用章节
    chapters = get_available_chapters(book_path)

    if not chapters:
        st.warning("AI_intro_book 文件夹中没有找到可用的章节文件。")
        return

    # 创建章节名称列表（用于下拉菜单），去除 .md 扩展名
    chapter_names = [chapter.name.replace(".md", "") for chapter in chapters]

    # 从 URL 参数获取当前章节，如果没有则使用默认值
    default_chapter = chapter_names[0] if chapter_names else ""
    current_chapter, match_info = get_chapter_from_url_params(chapter_names, default_chapter)

    # 显示匹配信息（如果有的话）
    if match_info:
        st.write(match_info)

    # 创建章节选择器
    selected_chapter_name = create_chapter_selector(chapter_names, current_chapter)

    # 如果选择的章节与当前 URL 参数不同，更新 URL
    if update_chapter_url_param(selected_chapter_name, current_chapter):
        st.rerun()

    # 找到选中的章节文件
    selected_chapter = find_selected_chapter_file(chapters, selected_chapter_name)

    # 检查章节是否发生变化，如果变化了需要清除重写进度
    if "current_chapter_name" not in st.session_state:
        st.session_state.current_chapter_name = selected_chapter_name
    elif st.session_state.current_chapter_name != selected_chapter_name:
        # 章节发生变化，清除重写进度
        if "rewrite_progress" in st.session_state:
            del st.session_state.rewrite_progress
        if "profile_summary" in st.session_state:
            del st.session_state.profile_summary
        if "personalized_recommendations" in st.session_state:
            del st.session_state.personalized_recommendations
        # 更新当前章节名称
        st.session_state.current_chapter_name = selected_chapter_name

    # 显示选中的章节内容
    if selected_chapter:
        # 显示章节标题
        st.subheader(selected_chapter_name)

        # 加载章节内容并处理图片
        content, error = load_chapter_content(selected_chapter, book_path)

        if content:
            # 创建两个tab：原始章节和LLM修改后的章节
            tab1, tab2 = st.tabs(["📖 原始章节", "🤖 AI优化章节"])

            # Tab 1: 原始章节内容
            with tab1:
                st.markdown("**原始章节内容：**")
                # 使用工具函数渲染特殊内容
                render_special_content(content)

            # Tab 2: LLM修改后的章节内容
            with tab2:
                st.markdown("**AI优化后的章节内容：**")

                # 首先尝试加载已保存的进度
                if "rewrite_progress" not in st.session_state:
                    saved_progress = load_rewrite_progress(selected_chapter_name)
                    if saved_progress:
                        st.session_state.rewrite_progress = saved_progress
                        st.session_state.profile_summary = "已加载保存的进度"
                        st.session_state.personalized_recommendations = []
                        st.info("📚 检测到已保存的优化进度，已自动加载")

                # 检查是否有重写进度
                if "rewrite_progress" in st.session_state and st.session_state.rewrite_progress["chunks"]:
                    progress = st.session_state.rewrite_progress

                    # 显示进度信息
                    total_chunks = len(progress["chunks"])
                    processed_count = len(progress["processed_chunks"])
                    current_index = progress["current_index"]

                    st.info(f"📊 处理进度: {processed_count}/{total_chunks} 个部分已完成")

                    # 智能显示内容：已处理的部分 + 不需要改写的部分
                    display_content = []
                    display_until_index = current_index

                    # 找到下一个需要改写的部分
                    next_rewrite_index = None
                    for i in range(current_index, len(progress["chunks"])):
                        chunk = progress["chunks"][i]
                        if any(keyword in chunk.get("title", "") for keyword in ["思想实验", "知识基础", "知识进阶"]):
                            next_rewrite_index = i
                            break
                        else:
                            # 不需要改写的部分，可以继续显示
                            display_until_index = i + 1

                    # 构建显示内容
                    for i in range(display_until_index):
                        chunk = progress["chunks"][i]
                        if "rewritten_content" in chunk:
                            display_content.append(chunk["rewritten_content"])
                        else:
                            display_content.append(chunk["content"])

                    # 显示内容
                    if display_content:
                        st.markdown("**当前显示内容：**")
                        full_content = "\n\n".join(display_content)

                        # 处理重写后的内容，确保图片和特殊格式能正确显示
                        # 创建一个临时文件来模拟原始章节文件，这样可以使用load_chapter_content处理

                        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as temp_file:
                            temp_file.write(full_content)
                            temp_file_path = Path(temp_file.name)

                        try:
                            # 使用load_chapter_content处理临时文件
                            processed_content, error = load_chapter_content(temp_file_path, book_path)
                            if processed_content:
                                render_special_content(processed_content)
                            else:
                                st.error(f"处理内容失败: {error}")
                                # 如果处理失败，直接显示原始内容
                                render_special_content(full_content)
                        finally:
                            # 清理临时文件
                            try:
                                os.unlink(temp_file_path)
                            except:
                                pass

                    # 检查是否还有需要处理的部分
                    if next_rewrite_index is not None:
                        remaining_chunks = [i for i in range(len(progress["chunks"]))
                                            if i >= next_rewrite_index and
                                            any(keyword in progress["chunks"][i].get("title", "")
                                                for keyword in ["思想实验", "知识基础", "知识进阶"])]

                        if remaining_chunks:
                            st.info(f"还有 {len(remaining_chunks)} 个部分需要优化，点击'继续优化'继续处理")

                            # 继续优化按钮
                            if st.button("🔄 继续优化", type="primary"):
                                continue_rewriting(
                                    progress["chunks"],
                                    st.session_state.get("profile_summary", ""),
                                    st.session_state.get("personalized_recommendations", []),
                                    selected_chapter_name
                                )
                                st.rerun()
                    else:
                        st.success("🎉 所有需要优化的部分已完成！")

                        # 根据是否有已保存的进度来决定按钮文本
                        has_saved_progress = False
                        try:
                            output_dir = Path.home() / ".baicai" / "textbook"
                            rewritten_json_path = output_dir / f"{selected_chapter_name}_rewritten.json"
                            has_saved_progress = rewritten_json_path.exists()
                        except:
                            pass

                        if has_saved_progress:
                            # 有已保存的进度，显示"重新开始"按钮
                            if st.button("🔄 重新开始"):
                                # 删除session state中的进度
                                if "rewrite_progress" in st.session_state:
                                    del st.session_state.rewrite_progress
                                # 删除已保存的文件
                                try:
                                    if rewritten_json_path.exists():
                                        os.unlink(rewritten_json_path)
                                except:
                                    pass
                                st.rerun()
                        else:
                            # 没有已保存的进度，显示"重新开始"按钮
                            if st.button("🔄 重新开始"):
                                if "rewrite_progress" in st.session_state:
                                    del st.session_state.rewrite_progress
                                st.rerun()

                else:
                    # 检查是否有已保存的进度
                    has_saved_progress = False
                    try:
                        output_dir = Path.home() / ".baicai" / "textbook"
                        rewritten_json_path = output_dir / f"{selected_chapter_name}_rewritten.json"
                        has_saved_progress = rewritten_json_path.exists()
                    except:
                        pass

                    if has_saved_progress:
                        # 有已保存的进度，显示"继续优化"按钮
                        if st.button("🔄 继续优化", type="primary"):
                            # 加载已保存的进度
                            saved_progress = load_rewrite_progress(selected_chapter_name)
                            if saved_progress:
                                st.session_state.rewrite_progress = saved_progress
                                st.session_state.profile_summary = "已加载保存的进度"
                                st.session_state.personalized_recommendations = []
                                st.success("📚 已加载保存的进度，可以继续优化")
                                st.rerun()
                            else:
                                st.error("加载保存的进度失败，请重试")
                        else:
                            # 显示功能说明
                            st.info("💡 检测到已保存的优化进度，点击'继续优化'可以继续之前的优化工作。")
                    else:
                        # 没有已保存的进度，显示"开始AI优化"按钮
                        if st.button("🚀 开始AI优化", type="primary"):
                            chunks, profile_summary, personalized_recommendations = process_chapter_with_llm(
                                selected_chapter, selected_chapter_name, book_path
                            )

                            if chunks:
                                # 保存到session state
                                st.session_state.rewrite_progress = {
                                    "chunks": chunks,
                                    "current_index": 0,
                                    "processed_chunks": [],
                                    "is_processing": False
                                }
                                st.session_state.profile_summary = profile_summary
                                st.session_state.personalized_recommendations = personalized_recommendations

                                st.success("✅ 初始化完成！点击'继续优化'开始处理第一个部分")
                                st.rerun()
                            else:
                                st.error("AI优化初始化失败，请重试")
                        else:
                            # 显示功能说明
                            st.info("💡 点击上方按钮开始AI优化，系统将根据您的学习情况对章节内容进行优化。")

        else:
            st.error(f"{error}")


show()
