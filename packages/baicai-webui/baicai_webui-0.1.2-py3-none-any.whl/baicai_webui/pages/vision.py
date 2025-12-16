import matplotlib.pyplot as plt
import streamlit as st
from baicai_dev.utils.data import TaskType
from fastai.vision.all import *

from baicai_webui.components.base_page import BasePage
from baicai_webui.components.image_viewer import ImageViewer
from baicai_webui.components.model import vision_uploader


def get_config(key=None):
    """
    获取配置

    Args:
        key: 配置的key
    Returns:
        配置的值
    """
    if not st.session_state.data_config:
        return None

    if key is None:
        return st.session_state.data_config["configurable"]
    else:
        value = st.session_state.data_config["configurable"][key]
        # Remove single quotes if the value is a string and is enclosed in quotes
        if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return value


def check_original_images():
    # 使用 session_state 来保持按钮状态
    if "show_image" not in st.session_state:
        st.session_state.show_image = False

    # 使用 st.button 的 key 参数来保持按钮状态
    if st.button("查看原始图片", key="view_images_button"):
        st.session_state.show_image = not st.session_state.show_image

    if st.session_state.show_image:
        image_path = get_config("path")
        image_viewer = ImageViewer(image_path)
        image_viewer.show()


def check_dls(train=True, batch_size=4):
    # 使用 session_state 来保持展开状态
    if "show_dls_expander" not in st.session_state:
        st.session_state.show_dls_expander = False

    with st.expander("查看批次数据", expanded=st.session_state.show_dls_expander):
        # 更新展开状态
        st.session_state.show_dls_expander = True

        resize = st.radio("缩放图片", ["固定缩放", "随机剪裁"], horizontal=True)

        with st.form("check_dls_form"):
            max_n = st.number_input("最大显示数量", value=4, min_value=1, max_value=batch_size, step=1)
            nrows = st.number_input("行数", value=1, min_value=1, max_value=batch_size // max_n, step=1)
            image_size = st.number_input("图片大小", value=28, min_value=1, max_value=228, step=1)

            resize_method = None
            pad_mode = None
            min_scale = None
            item_tfms = None
            unique = False
            if resize == "固定缩放":
                resize_method = st.radio("缩放方法", ["squish", "pad", "crop", "mro"], horizontal=True)
                pad_mode = st.radio("填充模式", ["zeros", "reflection"], horizontal=True)
                item_tfms = Resize(image_size, resize_method, pad_mode)

            elif resize == "随机剪裁":
                unique = st.checkbox("显示同一张图片的变换", value=True)
                min_scale = st.number_input("最小缩放比例", value=0.3, min_value=0.1, max_value=1.0, step=0.01)
                item_tfms = RandomResizedCrop(image_size, min_scale=min_scale)

            if st.form_submit_button("Show Batch"):
                dls = load_data(item_tfms=item_tfms)
                # Get the appropriate dataloader
                loader = dls.train if train else dls.valid

                # Create a figure and axes
                fig, ax = plt.subplots(nrows, max_n // nrows)

                # Use fastai's show_batch with our custom figure
                loader.show_batch(max_n=max_n, nrows=nrows, ctxs=ax, unique=unique)

                # Display in Streamlit
                st.pyplot(fig)
                plt.close(fig)


def load_data(item_tfms=None):
    """加载数据"""
    image_path = get_config("path")
    task_type = get_config("task_type")

    # 通用参数
    common_params = {
        "valid_pct": get_config("valid_pct"),
        "item_tfms": item_tfms,
        "batch_size": get_config("batch_size"),
        "num_workers": get_config("num_workers"),
    }

    if task_type == TaskType.VISION_SINGLE_LABEL.value:
        # 单标签分类 - 从文件夹加载，每个子文件夹是一个类别
        dls = ImageDataLoaders.from_folder(
            path=image_path, train=get_config("train_folder"), valid=get_config("valid_folder"), **common_params
        )
    elif task_type == TaskType.VISION_MULTI_LABEL.value:
        # 多标签分类 - 从CSV文件加载，支持多个标签
        dls = ImageDataLoaders.from_csv(
            path=image_path,
            csv_fname=get_config("csv_file"),
            folder=get_config("folder"),
            fn_col=get_config("image_col"),
            label_col=get_config("label_col"),
            valid_col=get_config("valid_col"),
            delimiter=get_config("delimiter"),
            label_delim=get_config("label_delim"),
            **common_params,
        )
    elif task_type == TaskType.VISION_CSV.value:
        # CSV标注的分类 - 从CSV文件加载，指定图片列和标签列
        dls = ImageDataLoaders.from_csv(
            path=image_path,
            csv_fname=get_config("csv_file"),
            folder=get_config("folder"),
            fn_col=get_config("image_col"),
            label_col=get_config("label_col"),
            valid_col=get_config("valid_col"),
            delimiter=get_config("delimiter"),
            **common_params,
        )
    elif task_type == TaskType.VISION_FUNC.value:
        # 函数标注的分类 - 使用自定义函数从文件名或路径提取标签

        def label_func(x):
            func_str = get_config("label_func")
            # Create a function from the string and execute it
            func_code = f"def temp_func(x):\n    {func_str}\n"
            namespace = {}
            exec(func_code, namespace)
            return namespace["temp_func"](x)

        dls = ImageDataLoaders.from_path_func(
            path=image_path, fnames=get_image_files(image_path), label_func=label_func, **common_params
        )
    elif task_type == TaskType.VISION_RE.value:
        # 正则表达式标注的分类 - 使用正则表达式从文件名提取标签
        dls = ImageDataLoaders.from_name_re(
            path=image_path,
            fnames=get_image_files(image_path),
            pat=get_config("pat"),
            **common_params,
        )
    else:
        raise ValueError(f"不支持的任务类型: {task_type}")
    return dls


def pre_train():
    """训练前执行的代码"""
    # Create containers for different sections
    if "pre_train_container" not in st.session_state:
        st.session_state.pre_train_container = st.container()
        st.session_state.show_image = False
        st.session_state.show_dls_expander = False

    # 使用 st.empty() 来保持容器位置
    container = st.empty()
    with container.container():
        if st.session_state.data_config:
            check_original_images()
            check_dls(batch_size=get_config("batch_size"))


async def post_train(code_interpreter):
    """训练后执行的代码"""
    # Create a container for post-train content
    if "post_train_container" not in st.session_state:
        st.session_state.post_train_container = st.container()

    with st.session_state.post_train_container:
        if not st.session_state.data_config:
            st.warning("请先上传数据并开始训练")
            return

        try:
            # 添加内存清理
            import gc
            gc.collect()
            
            code = """
import base64
from io import BytesIO
def fig_to_base64(fig):
    # Save the figure to a temporary buffer with high DPI
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0.1)
    buf.seek(0)
    # Encode the bytes as base64
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return img_base64


import torch
import matplotlib.pyplot as plt
import numpy as np

def visualize_tensor_images(tensor_images, titles=None, rows=1, cols=1):
    \"""
    Visualize multiple tensor images in a grid layout.

    Args:
        tensor_images: A single tensor image or a list/tensor of multiple images
        titles: Optional title or list of titles for each subplot
        rows: Number of rows in the grid
        cols: Number of columns in the grid
    \"""
    # Convert single image to list for consistent handling
    if isinstance(tensor_images, torch.Tensor) and len(tensor_images.shape) == 3:
        tensor_images = [tensor_images]
    elif isinstance(tensor_images, torch.Tensor) and len(tensor_images.shape) == 4:
        tensor_images = [img for img in tensor_images]

    # Convert single title to list if needed
    if titles is not None and not isinstance(titles, (list, tuple)):
        titles = [titles] * len(tensor_images)

    # Calculate total number of images and adjust grid if needed
    total_images = len(tensor_images)
    if rows * cols < total_images:
        rows = (total_images + cols - 1) // cols

    # Create figure with appropriate size
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
    if rows == 1 and cols == 1:
        axes = np.array([axes])
    axes = axes.ravel()

    # Process and display each image
    for idx, tensor_image in enumerate(tensor_images):
        if idx >= len(axes):
            break

        # Handle batch dimension if present
        if len(tensor_image.shape) == 4:
            tensor_image = tensor_image[0]

        # Convert to numpy and change channel order
        image = tensor_image.permute(1, 2, 0).numpy()

        mean = [0.485, 0.456, 0.406]  # ImageNet mean
        std = [0.229, 0.224, 0.225]   # ImageNet std
        image = image * std + mean
        image = np.clip(image, 0, 1)  # Clip to valid range

        # Display image
        axes[idx].imshow(image)
        axes[idx].axis('off')

        # Add title if provided
        if titles is not None and idx < len(titles):
            axes[idx].set_title(titles[idx])

    # Hide any unused subplots
    for idx in range(total_images, len(axes)):
        axes[idx].axis('off')

    # Adjust layout
    plt.tight_layout()

    base64_string = fig_to_base64(fig)
    print("START_BASE64")
    print(base64_string)
    print("END_BASE64")
    plt.close(fig)

try:
    # 检查interp和idxs是否存在
    if 'interp' in globals() and 'idxs' in globals():
        images, preds, targs, decoded, _ = interp[idxs]
        # Create titles for each image showing loss value
        titles = [f"Target: {interp.vocab[t]}/Predict: {interp.vocab[d]}" for t,d in zip(targs, decoded)]
        visualize_tensor_images(images, titles, rows=2, cols=2)
    else:
        print("interp or idxs not found in global scope")
except Exception as e:
    print(f"获取最大损失失败: {str(e)}")
    import traceback
    print(traceback.format_exc())
"""
            
            # 设置超时时间，防止长时间阻塞
            import asyncio
            try:
                result = await asyncio.wait_for(
                    code_interpreter.run(code, ignore_keep_len=True),
                    timeout=60.0  # 60秒超时
                )
                
                # 检查结果是否包含base64数据
                if result and len(result) > 0:
                    base64_start = result[0].find("START_BASE64")
                    base64_end = result[0].find("END_BASE64")
                    
                    if base64_start != -1 and base64_end != -1:
                        base64_string = result[0][base64_start + len("START_BASE64") : base64_end].strip()
                        
                        if base64_string:
                            img_container = f"""
                                <div style="width:100%; overflow:auto; margin:10px 0;">
                                    <img src="data:image/png;base64,{base64_string}"
                                            style="max-width:100%; height:auto; display:block; margin:0 auto;"
                                            onerror="this.style.display='none'"/>
                                </div>
                                """
                            st.subheader("损失值最大的若干图片")
                            st.markdown(img_container, unsafe_allow_html=True)
                        else:
                            st.warning("未能生成图片数据")
                    else:
                        st.warning("代码执行完成，但未找到图片数据")
                else:
                    st.warning("代码执行完成，但未返回结果")
                    
            except asyncio.TimeoutError:
                st.error("代码执行超时，请检查代码是否有死循环或长时间运行的操作")
            except Exception as e:
                st.error(f"代码执行失败: {str(e)}")
                import traceback
                st.code(traceback.format_exc(), language="python")
                
        except Exception as e:
            st.error(f"训练后处理失败: {str(e)}")
            import traceback
            st.code(traceback.format_exc(), language="python")
        finally:
            # 强制清理内存
            import gc
            gc.collect()
            
            # 清理matplotlib缓存
            try:
                import matplotlib.pyplot as plt
                plt.close('all')
            except:
                pass


def show():
    """显示计算机视觉任务页面"""
    page = BasePage(TaskType.VISION, vision_uploader)
    page.show(pre_train=pre_train, post_train=post_train, title="计算机视觉")

show()