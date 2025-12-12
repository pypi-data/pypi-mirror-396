import base64
import re
from pathlib import Path

import streamlit as st
from baicai_base.configs import ConfigManager
from dotenv import load_dotenv
from streamlit_markmap import markmap
from streamlit_mermaid import st_mermaid
from streamlit_pdf_viewer import pdf_viewer


def guard_llm_setting():
    env_path = ConfigManager.get_env_path()
    env_exists = env_path.exists() and env_path.stat().st_size > 0

    if env_exists:
        load_dotenv(dotenv_path=env_path, override=True)
    return env_exists


def reset_session_state():
    """Reset session state variables used by the AI assistant to their initial values."""
    st.session_state.messages = []
    st.session_state.message_placeholders = {}
    st.session_state.tutor_messages = []
    st.session_state.tutor_message_placeholders = {}




def extract_chapter_number(filename):
    """从文件名中提取章节数字"""
    match = re.search(r"第(\d+)章", filename)
    if match:
        return int(match.group(1))
    return 0


def get_available_chapters(book_path):
    """获取可用的章节列表，排除结构文件，按章节数字排序"""
    if not book_path.exists():
        return []

    md_files = list(book_path.glob("*.md"))
    # 过滤掉结构文件，并按章节数字排序
    chapters = [f for f in md_files if f.name != "结构.md"]
    # 按章节数字排序（1, 2, 3, ..., 12）
    chapters.sort(key=lambda x: extract_chapter_number(x.name))
    return chapters


def process_markdown_images(content, book_path):
    """处理 Markdown 内容中的图片，将相对路径转换为可显示的格式，保留原始尺寸设置"""
    if not content:
        return content

    def replace_image(match):
        alt_text = match.group(1)
        image_path = match.group(2)

        # 检查 alt_text 是否包含尺寸信息（如 "50", "500" 等）
        width = None
        height = None

        # 尝试从 alt_text 中提取尺寸信息
        if alt_text.isdigit():
            # 如果 alt_text 是纯数字，认为是宽度
            width = int(alt_text)
        elif "x" in alt_text.lower():
            # 如果包含 x，可能是 "100x200" 格式
            try:
                parts = alt_text.lower().split("x")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    width = int(parts[0])
                    height = int(parts[1])
            except:
                pass

        # 如果是相对路径，构建绝对路径
        if image_path.startswith("attachments/"):
            absolute_path = book_path / image_path

            # 检查文件是否存在
            if absolute_path.exists():
                # 获取文件扩展名
                file_ext = absolute_path.suffix.lower()

                # 构建样式字符串
                style_parts = []
                if width:
                    style_parts.append(f"width: {width}px")
                if height:
                    style_parts.append(f"height: {height}px")
                else:
                    # 如果没有设置高度，保持宽高比
                    style_parts.append("height: auto")

                # 确保图片不会超出容器
                style_parts.append("max-width: 100%")

                style_str = "; ".join(style_parts)

                # 对于支持的图片格式，返回 HTML img 标签
                if file_ext in [".png", ".jpg", ".jpeg", ".webp"]:
                    # 使用 base64 编码图片数据
                    try:
                        with open(absolute_path, "rb") as f:
                            image_data = f.read()
                            base64_data = base64.b64encode(image_data).decode()
                            mime_type = f"image/{file_ext[1:]}" if file_ext != ".jpg" else "image/jpeg"
                            return f'<img src="data:{mime_type};base64,{base64_data}" alt="{alt_text}" style="{style_str}">'
                    except Exception:
                        # 如果 base64 编码失败，返回文件路径信息
                        return f"<p><strong>图片加载失败:</strong> {alt_text}</p>"

                elif file_ext == ".svg":
                    # 对于 SVG 文件，使用 object 标签或 iframe 来确保完整显示
                    try:
                        # 将 SVG 文件转换为 base64 编码
                        with open(absolute_path, "rb") as f:
                            svg_data = f.read()
                            svg_base64 = base64.b64encode(svg_data).decode()

                        # 使用 object 标签显示 SVG，这样可以确保完整显示
                        if width and height:
                            return f'<object data="data:image/svg+xml;base64,{svg_base64}" type="image/svg+xml" width="{width}" height="{height}" style="{style_str}"></object>'
                        elif width:
                            return f'<object data="data:image/svg+xml;base64,{svg_base64}" type="image/svg+xml" width="{width}" style="{style_str}"></object>'
                        else:
                            # 如果没有指定尺寸，使用 SVG 的原始尺寸
                            return f'<object data="data:image/svg+xml;base64,{svg_base64}" type="image/svg+xml" style="{style_str}"></object>'

                    except Exception as e:
                        # 如果 SVG 处理失败，尝试直接读取内容
                        try:
                            svg_content = absolute_path.read_text(encoding="utf-8")
                            # 确保 SVG 有正确的 viewBox 属性
                            if "viewBox" not in svg_content and "<svg" in svg_content:
                                # 如果没有 viewBox，尝试添加一个
                                svg_match = re.search(r"<svg([^>]*)>", svg_content)
                                if svg_match:
                                    svg_attrs = svg_match.group(1)
                                    # 提取宽度和高度
                                    width_match = re.search(r'width="(\d+)"', svg_attrs)
                                    height_match = re.search(r'height="(\d+)"', svg_attrs)
                                    if width_match and height_match:
                                        w = width_match.group(1)
                                        h = height_match.group(1)
                                        viewbox_attr = f' viewBox="0 0 {w} {h}"'
                                        svg_content = re.sub(
                                            r"<svg([^>]*)>", f"<svg\\1{viewbox_attr}>", svg_content, count=1
                                        )

                            # 添加样式到 SVG
                            if width or height:
                                style_attr = f' style="{style_str}"'
                                svg_content = re.sub(r"<svg([^>]*)>", f"<svg\\1{style_attr}>", svg_content, count=1)

                            return svg_content
                        except Exception:
                            return f"<p><strong>SVG 加载失败:</strong> {alt_text}</p>"

                elif file_ext == ".pdf":
                    # 对于 PDF 文件，返回一个特殊的标记，稍后处理
                    return f"__PDF_PLACEHOLDER__{absolute_path}__END_PDF__"

                else:
                    return f"<p><strong>不支持的图片格式:</strong> {alt_text} ({file_ext})</p>"
            else:
                return f"<p><strong>图片文件不存在:</strong> {alt_text}</p>"

        # 如果是其他路径（如 HTTP 链接），保持原样
        return match.group(0)

    # 使用正则表达式替换图片引用
    processed_content = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace_image, content)

    return processed_content


def get_callout_css():
    """返回 callout 的 CSS 样式"""
    return """
    <style>
    .callout {
        margin: 1rem 0;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
    }
    
    .callout-header {
        display: flex;
        align-items: flex-start;
        margin-bottom: 0.75rem;
        font-weight: 600;
        font-size: 1.1em;
        line-height: 1.4;
        min-height: 1.5em;
        flex-wrap: wrap;
        gap: 0.5rem;
        width: 100%;
        box-sizing: border-box;
        position: relative;
        overflow: visible;
    }
    
    .callout-icon {
        margin-right: 0;
        font-size: 1.3em;
        flex-shrink: 0;
    }
    
    .callout-title {
        font-weight: 600;
        color: inherit;
        display: inline-block;
        margin: 0;
        padding: 0;
        line-height: 1.4;
        flex: 1;
        word-wrap: break-word;
        overflow-wrap: break-word;
        hyphens: auto;
        text-align: left;
        white-space: normal;
        min-width: 0;
        box-sizing: border-box;
        overflow: visible;
        text-overflow: clip;
    }
    
    .callout-content {
        color: #374151;
        line-height: 1.7;
        margin: 0;
    }
    
    .callout-content p {
        margin: 0.5rem 0;
    }
    
    .callout-content p:first-child {
        margin-top: 0;
    }
    
    .callout-content p:last-child {
        margin-bottom: 0;
    }
    
    .callout-info { 
        background-color: #eff6ff; 
        border-left-color: #3b82f6; 
        border-color: #dbeafe;
    }
    .callout-note { 
        background-color: #ecfdf5; 
        border-left-color: #059669; 
        border-color: #a7f3d0;
    }
    .callout-warning { 
        background-color: #fffbeb; 
        border-left-color: #d97706; 
        border-color: #fed7aa;
    }
    .callout-error { 
        background-color: #fef2f2; 
        border-left-color: #dc2626; 
        border-color: #fecaca;
    }
    .callout-success { 
        background-color: #ecfdf5; 
        border-left-color: #059669; 
        border-color: #a7f3d0;
    }
    .callout-question { 
        background-color: #f3f4f6; 
        border-left-color: #7c3aed; 
        border-color: #ddd6fe;
    }
    .callout-todo { 
        background-color: #f0fdf4; 
        border-left-color: #059669; 
        border-color: #bbf7d0;
    }
    .callout-tip { 
        background-color: #f0f9ff; 
        border-left-color: #0891b2; 
        border-color: #7dd3fc;
    }
    .callout-abstract { 
        background-color: #fef3c7; 
        border-left-color: #7c2d12; 
        border-color: #fcd34d;
    }
    .callout-quote { 
        background-color: #f9fafb; 
        border-left-color: #6b7280; 
        border-color: #d1d5db;
    }
    .callout-example { 
        background-color: #faf5ff; 
        border-left-color: #7c3aed; 
        border-color: #c4b5fd;
    }
    
    .callout-info .callout-header { color: #3b82f6; }
    .callout-note .callout-header { color: #059669; }
    .callout-warning .callout-header { color: #d97706; }
    .callout-error .callout-header { color: #dc2626; }
    .callout-success .callout-header { color: #059669; }
    .callout-question .callout-header { color: #7c3aed; }
    .callout-todo .callout-header { color: #059669; }
    .callout-tip .callout-header { color: #0891b2; }
    .callout-abstract .callout-header { color: #7c2d12; }
    .callout-quote .callout-header { color: #6b7280; }
    .callout-example .callout-header { color: #7c3aed; }
    
    /* 确保在 Streamlit 中正确显示 */
    .callout * {
        box-sizing: border-box;
    }
    
    .callout img {
        max-width: 100%;
        height: auto;
        display: inline-block;
        vertical-align: middle;
    }
    
    .callout-content img {
        margin: 0.5rem 0;
    }
    
    /* 确保列表在 callout 中正确显示 */
    .callout-content ul,
    .callout-content ol {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .callout-content li {
        margin: 0.25rem 0;
        line-height: 1.5;
    }
    
    .callout-content ul li {
        list-style-type: disc;
    }
    
    .callout-content ol li {
        list-style-type: decimal;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .callout {
            margin: 0.5rem 0;
            padding: 0.75rem;
        }
        
        .callout-header {
            font-size: 1em;
        }
        
        .callout-icon {
            font-size: 1.1em;
        }
    }
    </style>
    """


def process_obsidian_callouts(content):
    """处理 Obsidian 特有的 callout 格式，转换为美观的 HTML 样式"""
    if not content:
        return content

    # 改进的 Obsidian callout 正则表达式模式
    # 匹配 > [!type] title 格式，支持多行内容，标题可以为空
    callout_pattern = r"> \[!([^\]]+)\]\s*([^\n]*?)(?:\n|$)((?:> [^\n]*\n?)*)"

    def replace_callout(match):
        callout_type = match.group(1).lower()
        title = match.group(2).strip()
        content_lines = match.group(3).strip()

        # 处理多行内容，移除每行开头的 "> " 并合并
        content_text = ""
        if content_lines:
            content_lines_list = content_lines.split("\n")
            processed_lines = []
            for line in content_lines_list:
                line = line.strip()
                if line.startswith("> "):
                    # 移除 "> " 前缀
                    content = line[2:].strip()
                    # 如果内容不为空，添加到处理后的行中
                    if content:
                        processed_lines.append(content)
                    # 如果内容为空（只有 ">" 的空白行），添加一个空行来保持格式
                    else:
                        processed_lines.append("")
                elif line:
                    processed_lines.append(line)
            # 过滤掉连续的空行，保持格式整洁
            filtered_lines = []
            for i, line in enumerate(processed_lines):
                if line.strip() or (i > 0 and processed_lines[i - 1].strip()):
                    filtered_lines.append(line)

            # 直接处理callout内容中的列表，转换为HTML格式
            content_text = process_lists_in_callout("\n".join(filtered_lines))

        # 如果内容为空，提供默认内容
        if not content_text.strip():
            content_text = "这是一个 " + callout_type + " 提示框。"

        # 定义不同类型的 callout 样式
        callout_styles = {
            "info": {"icon": "ℹ️", "color": "#3b82f6", "bg_color": "#eff6ff", "border_color": "#dbeafe"},
            "note": {"icon": "📝", "color": "#059669", "bg_color": "#ecfdf5", "border_color": "#a7f3d0"},
            "warning": {"icon": "⚠️", "color": "#d97706", "bg_color": "#fffbeb", "border_color": "#fed7aa"},
            "error": {"icon": "❌", "color": "#dc2626", "bg_color": "#fef2f2", "border_color": "#fecaca"},
            "success": {"icon": "✅", "color": "#059669", "bg_color": "#ecfdf5", "border_color": "#a7f3d0"},
            "question": {"icon": "❓", "color": "#7c3aed", "bg_color": "#f3f4f6", "border_color": "#ddd6fe"},
            "todo": {"icon": "📋", "color": "#059669", "bg_color": "#f0fdf4", "border_color": "#bbf7d0"},
            "tip": {"icon": "💡", "color": "#0891b2", "bg_color": "#f0f9ff", "border_color": "#7dd3fc"},
            "abstract": {"icon": "📚", "color": "#7c2d12", "bg_color": "#fef3c7", "border_color": "#fcd34d"},
            "quote": {"icon": "💬", "color": "#6b7280", "bg_color": "#f9fafb", "border_color": "#d1d5db"},
            "example": {"icon": "🔍", "color": "#7c3aed", "bg_color": "#faf5ff", "border_color": "#c4b5fd"},
        }

        # 获取样式，如果没有找到对应的类型，使用默认样式
        style = callout_styles.get(callout_type, callout_styles["info"])

        # 构建 HTML，使用 CSS 类，确保标题正确显示
        display_title = title if title else callout_type.title()
        # 使用正确的HTML结构，确保标签正确关闭，并在后面添加换行符
        html = f'<div class="callout callout-{callout_type}"><div class="callout-header"><span class="callout-icon">{style["icon"]}</span><span class="callout-title">{display_title}</span></div><div class="callout-content">{content_text}</div></div>\n'

        return html

    # 使用正则表达式替换 callout
    processed_content = re.sub(callout_pattern, replace_callout, content, flags=re.DOTALL)

    return processed_content


def process_lists_in_callout(content):
    """在callout内容中处理列表格式，转换为HTML格式以保持一致性"""
    if not content:
        return content

    lines = content.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 检查是否在表格中（包含 | 符号的行）
        if "|" in line:
            result_lines.append(line)
            i += 1
            continue

        # 检查是否是有序列表
        if re.match(r"^\s*\d+\.\s", line):
            # 收集连续的有序列表项
            list_items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s", lines[i]):
                item_content = re.sub(r"^\s*\d+\.\s", "", lines[i])
                list_items.append(f'<li style="margin: 0.25rem 0;">{item_content}</li>')
                i += 1

            if list_items:
                result_lines.append('<ol style="margin: 0.5rem 0; padding-left: 1.5rem;">')
                result_lines.extend(list_items)
                result_lines.append("</ol>")

        # 检查是否是无序列表
        elif re.match(r"^\s*[-*]\s", line):
            # 收集连续的无序列表项
            list_items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s", lines[i]):
                item_content = re.sub(r"^\s*[-*]\s", "", lines[i])
                list_items.append(f'<li style="margin: 0.25rem 0;">{item_content}</li>')
                i += 1

            if list_items:
                result_lines.append('<ul style="margin: 0.5rem 0; padding-left: 1.5rem;">')
                result_lines.extend(list_items)
                result_lines.append("</ul>")

        # 普通行，直接添加
        else:
            result_lines.append(line)
            i += 1

    return "\n".join(result_lines)


def process_lists_in_text(content):
    """在文本中处理列表格式，保持Markdown格式而不是转换为HTML"""
    if not content:
        return content

    lines = content.split("\n")
    result_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # 检查是否在表格中（包含 | 符号的行）
        if "|" in line:
            result_lines.append(line)
            i += 1
            continue

        # 检查是否是有序列表
        if re.match(r"^\s*\d+\.\s", line):
            # 收集连续的有序列表项，保持Markdown格式
            while i < len(lines) and re.match(r"^\s*\d+\.\s", lines[i]):
                # 保持原始的Markdown格式，不转换为HTML
                result_lines.append(lines[i])
                i += 1

        # 检查是否是无序列表
        elif re.match(r"^\s*[-*]\s", line):
            # 收集连续的无序列表项，保持Markdown格式
            while i < len(lines) and re.match(r"^\s*[-*]\s", lines[i]):
                # 保持原始的Markdown格式，不转换为HTML
                result_lines.append(lines[i])
                i += 1

        # 普通行，直接添加
        else:
            result_lines.append(line)
            i += 1

    return "\n".join(result_lines)


def process_obsidian_frontmatter(content):
    """处理 Obsidian 的 frontmatter（文件头部元数据）"""
    if not content:
        return content

    # 匹配 frontmatter 格式：以 --- 开始和结束的 YAML 内容，直接删除
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"

    # 直接删除 frontmatter，不显示任何内容
    content = re.sub(frontmatter_pattern, "", content, flags=re.DOTALL)

    return content


def process_obsidian_special_formats(content):
    """处理其他 Obsidian 特有的格式"""
    if not content:
        return content

    # 处理 markmap 格式
    markmap_pattern = r"```markmap\s*\n(.*?)\n```"

    def replace_markmap(match):
        markmap_content = match.group(1).strip()
        # 返回一个特殊的标记，稍后在显示内容时处理
        return f"__MARKMAP_PLACEHOLDER__{markmap_content}__END_MARKMAP__"

    # 处理 mermaid 格式
    mermaid_pattern = r"```mermaid\s*\n(.*?)\n```"

    def replace_mermaid(match):
        mermaid_content = match.group(1).strip()
        # 返回一个特殊的标记，稍后在显示内容时处理
        return f"__MERMAID_PLACEHOLDER__{mermaid_content}__END_MERMAID__"

    # 处理 PDF 格式
    pdf_pattern = r"__PDF_PLACEHOLDER__(.*?)__END_PDF__"

    def replace_pdf(match):
        pdf_path = match.group(1).strip()
        # 返回一个特殊的标记，稍后在显示内容时处理
        return f"__PDF_PLACEHOLDER__{pdf_path}__END_PDF__"

    # 应用转换
    content = re.sub(markmap_pattern, replace_markmap, content, flags=re.DOTALL)
    content = re.sub(mermaid_pattern, replace_mermaid, content, flags=re.DOTALL)
    content = re.sub(pdf_pattern, replace_pdf, content, flags=re.DOTALL)

    return content


def process_obsidian_tables(content):
    """处理 Obsidian 的表格格式，使其在 Streamlit 中显示得更好"""
    if not content:
        return content

    # 匹配 Markdown 表格
    table_pattern = r"(\|[^\n]*\|\n\|[^\n]*\|\n(?:\|[^\n]*\|\n?)+)"

    def replace_table(match):
        table_content = match.group(1).strip()
        lines = table_content.split("\n")

        if len(lines) < 3:  # 至少需要表头、分隔行和一行数据
            return match.group(0)

        # 解析表格
        headers = []
        data_rows = []

        for i, line in enumerate(lines):
            if i == 0:  # 表头
                headers = [cell.strip() for cell in line.split("|")[1:-1]]
            elif i == 1:  # 分隔行，跳过
                continue
            else:  # 数据行
                row = [cell.strip() for cell in line.split("|")[1:-1]]
                if len(row) == len(headers):  # 确保行数据与表头匹配
                    data_rows.append(row)

        if not headers or not data_rows:
            return match.group(0)

        # 构建 HTML 表格
        html_parts = ['<div style="overflow-x: auto; margin: 1rem 0;">']
        html_parts.append(
            '<table style="border-collapse: collapse; width: 100%; border: 1px solid #e5e7eb; border-radius: 6px; overflow: hidden;">'
        )

        # 表头
        html_parts.append('<thead style="background-color: #f9fafb;">')
        html_parts.append("<tr>")
        for header in headers:
            html_parts.append(
                f'<th style="padding: 0.75rem; text-align: left; border-bottom: 1px solid #e5e7eb; font-weight: 600; color: #374151;">{header}</th>'
            )
        html_parts.append("</tr>")
        html_parts.append("</thead>")

        # 数据行
        html_parts.append("<tbody>")
        for i, row in enumerate(data_rows):
            bg_color = "#ffffff" if i % 2 == 0 else "#f9fafb"
            html_parts.append(f'<tr style="background-color: {bg_color};">')
            for cell in row:
                html_parts.append(
                    f'<td style="padding: 0.75rem; border-bottom: 1px solid #e5e7eb; color: #374151;">{cell}</td>'
                )
            html_parts.append("</tr>")
        html_parts.append("</tbody>")

        html_parts.append("</table>")
        html_parts.append("</div>")

        return "".join(html_parts)

    # 应用转换
    content = re.sub(table_pattern, replace_table, content, flags=re.MULTILINE)

    return content


def process_obsidian_links(content):
    """处理 Obsidian 的链接格式，包括内部 md 文件链接和外部链接"""
    if not content:
        return content

    # 处理 Markdown 链接 [文本](链接)
    link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

    def replace_link(match):
        text = match.group(1)
        url = match.group(2)

        # 如果是图片链接，保持原样
        if url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")):
            return match.group(0)

        # 如果是 .md 文件链接，转换为内部章节跳转
        if ".md" in url:
            # 移除 .md 扩展名和锚点部分，只保留文件名
            # 先移除 .md 扩展名
            chapter_name = url.replace(".md", "")
            # 再移除锚点部分（# 及其后面的内容）
            if "#" in chapter_name:
                chapter_name = chapter_name.split("#")[0]
            # 构建跳转链接，使用当前页面的 book 路径，确保没有 .md 扩展名和锚点
            # 使用 URL 编码确保中文字符正确传递
            import urllib.parse

            encoded_chapter = urllib.parse.quote(chapter_name, safe="")
            jump_url = f"/book?chapter={encoded_chapter}"
            return f'<a href="{jump_url}" style="color: #3b82f6; text-decoration: underline; cursor: pointer;" title="跳转到: {chapter_name}">{text} 📖</a>'

        # 如果是其他文件链接（如 .txt, .pdf），显示为文件链接
        if url.lower().endswith((".txt", ".pdf")):
            return f'<span style="color: #3b82f6; text-decoration: underline; cursor: pointer;" title="文件链接: {url}">{text} 📄</span>'

        # 外部链接添加图标和样式
        return f'<a href="{url}" target="_blank" style="color: #3b82f6; text-decoration: underline;">{text} 🔗</a>'

    # 应用转换
    content = re.sub(link_pattern, replace_link, content)

    return content


def filter_exercise_section(content):
    """过滤掉 '## 课后练习' 及其后面的所有内容"""
    if not content:
        return content

    # 查找 "## 课后练习" 的位置
    exercise_pattern = r"## 课后练习"
    match = re.search(exercise_pattern, content)

    if match:
        # 找到匹配位置，截取到该位置之前的内容
        start_pos = match.start()
        filtered_content = content[:start_pos].strip()
        return filtered_content

    # 如果没有找到，返回原内容
    return content


def load_chapter_content(md_path, book_path):
    """加载章节内容并处理图片"""
    if not md_path.exists():
        return None, f"未找到文档: {md_path.name}"

    try:
        content = md_path.read_text(encoding="utf-8")
        # 处理 Obsidian frontmatter
        processed_content = process_obsidian_frontmatter(content)
        # 过滤掉课后练习部分
        processed_content = filter_exercise_section(processed_content)
        # 处理图片
        processed_content = process_markdown_images(processed_content, book_path)
        # 处理 Obsidian callouts（包含列表处理）
        processed_content = process_obsidian_callouts(processed_content)
        # 处理其他 Markdown 列表（不在callout中的）
        processed_content = process_lists_in_text(processed_content)
        # 处理其他 Obsidian 特殊格式
        processed_content = process_obsidian_special_formats(processed_content)
        # 处理 Obsidian 链接
        processed_content = process_obsidian_links(processed_content)
        # 处理 Obsidian 表格
        processed_content = process_obsidian_tables(processed_content)
        return processed_content, None
    except Exception as exc:
        return None, f"读取文档失败: {exc}"


def get_chapter_from_url_params(chapter_names, default_chapter=""):
    """
    从URL参数中获取当前章节，支持模糊匹配
    
    Args:
        chapter_names: 可用章节名称列表
        default_chapter: 默认章节名称
    
    Returns:
        tuple: (current_chapter, matched_info)
    """
    if not chapter_names:
        return default_chapter, ""
    
    # 从 URL 参数获取当前章节，如果没有则使用默认值
    current_chapter = st.query_params.get("chapter", default_chapter)
    
    # 如果从URL参数获取到章节，尝试解码并匹配
    if current_chapter and current_chapter != default_chapter:
        try:
            import urllib.parse
            
            # 尝试解码URL参数
            decoded_chapter = urllib.parse.unquote(current_chapter)
            
            # 尝试精确匹配
            if decoded_chapter in chapter_names:
                return decoded_chapter, ""
            else:
                # 尝试模糊匹配，查找包含该章节名称的章节
                matched_chapter = None
                for chapter_name in chapter_names:
                    if decoded_chapter in chapter_name or chapter_name in decoded_chapter:
                        matched_chapter = chapter_name
                        break
                
                if matched_chapter:
                    return matched_chapter, f"✅ 模糊匹配成功: `{decoded_chapter}` → `{matched_chapter}`"
                else:
                    # 如果仍然无法匹配，使用默认章节
                    return default_chapter, f"❌ 匹配失败，使用默认章节: `{default_chapter}`"
        except Exception as e:
            # 如果解码失败，使用默认章节
            return default_chapter, f"❌ 解码失败: {e}，使用默认章节: `{default_chapter}`"
    
    # 如果 URL 中的章节不在可用章节列表中，使用默认章节
    if current_chapter not in chapter_names:
        return default_chapter, ""
    
    return current_chapter, ""


def update_chapter_url_param(selected_chapter_name, current_chapter):
    """
    如果选择的章节与当前URL参数不同，更新URL并重新运行
    
    Args:
        selected_chapter_name: 新选择的章节名称
        current_chapter: 当前URL参数中的章节名称
    
    Returns:
        bool: 是否需要重新运行页面
    """
    if selected_chapter_name != current_chapter:
        st.query_params["chapter"] = selected_chapter_name
        return True
    return False


def render_special_content(content):
    """
    渲染特殊内容（markmap、mermaid、PDF）
    
    Args:
        content: 处理后的内容
    
    Returns:
        None (直接渲染到Streamlit)
    """
    # 检查必要的组件是否可用
    if not all([markmap, st_mermaid, pdf_viewer]):
        st.warning("某些渲染组件不可用，请确保安装了 streamlit-markmap、streamlit-mermaid 和 streamlit-pdf-viewer")
        # 如果组件不可用，直接显示原始内容
        st.markdown(content, unsafe_allow_html=True)
        return
    
    # 定义占位符模式
    markmap_placeholder_pattern = r"__MARKMAP_PLACEHOLDER__(.*?)__END_MARKMAP__"
    mermaid_placeholder_pattern = r"__MERMAID_PLACEHOLDER__(.*?)__END_MERMAID__"
    pdf_placeholder_pattern = r"__PDF_PLACEHOLDER__(.*?)__END_PDF__"
    
    # 用于生成唯一 key 的计数器
    mermaid_counter = 0
    markmap_counter = 0
    pdf_counter = 0
    
    # 首先分割 markmap 占位符
    markmap_parts = re.split(markmap_placeholder_pattern, content, flags=re.DOTALL)
    
    # 处理每个部分
    for i, part in enumerate(markmap_parts):
        if i % 2 == 0:  # 普通内容，需要进一步检查是否包含 mermaid 和 PDF
            if part.strip():
                # 检查这部分是否包含 mermaid 占位符
                mermaid_parts = re.split(mermaid_placeholder_pattern, part, flags=re.DOTALL)
                
                # 交替显示内容和 mermaid
                for j, mermaid_part in enumerate(mermaid_parts):
                    if j % 2 == 0:  # 普通内容，需要进一步检查是否包含 PDF
                        if mermaid_part.strip():
                            # 检查这部分是否包含 PDF 占位符
                            pdf_parts = re.split(pdf_placeholder_pattern, mermaid_part, flags=re.DOTALL)
                            
                            # 交替显示内容和 PDF
                            for k, pdf_part in enumerate(pdf_parts):
                                if k % 2 == 0:  # 普通内容
                                    if pdf_part.strip():
                                        st.markdown(pdf_part, unsafe_allow_html=True)
                                else:  # PDF 内容
                                    if pdf_part.strip():
                                        pdf_counter += 1
                                        try:
                                            pdf_path = Path(pdf_part.strip())
                                            if pdf_path.exists():
                                                pdf_viewer(str(pdf_path), height=400, key=f"pdf_{pdf_counter}")
                                            else:
                                                st.error(f"PDF 文件不存在: {pdf_path}")
                                        except Exception as e:
                                            st.error(f"PDF 加载失败: {e}")
                    else:  # mermaid 内容
                        if mermaid_part.strip():
                            mermaid_counter += 1
                            st_mermaid(mermaid_part.strip(), height=400, key=f"mermaid_{mermaid_counter}")
        else:  # markmap 内容
            if part.strip():
                markmap_counter += 1
                # markmap 函数不支持 key 参数，但我们可以通过其他方式确保唯一性
                markmap(part.strip(), height=400)


def create_chapter_selector(chapter_names, current_chapter):
    """
    创建章节选择器
    
    Args:
        chapter_names: 可用章节名称列表
        current_chapter: 当前选中的章节名称
    
    Returns:
        str: 选择的章节名称
    """
    st.subheader("选择要学习的章节")
    
    # 获取当前章节在列表中的索引
    current_index = chapter_names.index(current_chapter) if current_chapter in chapter_names else 0
    
    # 创建下拉菜单，使用当前选中的章节
    selected_chapter_name = st.selectbox(
        "请选择章节：", 
        options=chapter_names, 
        index=current_index, 
        help="从下拉菜单中选择要阅读的章节"
    )
    
    return selected_chapter_name


def find_selected_chapter_file(chapters, selected_chapter_name):
    """
    根据章节名称找到对应的章节文件
    
    Args:
        chapters: 章节文件列表
        selected_chapter_name: 选择的章节名称
    
    Returns:
        Path: 章节文件路径，如果未找到则返回None
    """
    return next(
        (chapter for chapter in chapters if chapter.name.replace(".md", "") == selected_chapter_name), 
        None
    )

