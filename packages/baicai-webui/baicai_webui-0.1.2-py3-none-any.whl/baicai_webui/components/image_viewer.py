import os
from pathlib import Path
from typing import List

import streamlit as st


def get_image_files(folder_path: str) -> List[str]:
    """Get all image files from a folder."""
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
    return [str(f) for f in Path(folder_path).glob("*") if f.suffix.lower() in image_extensions]


def get_subfolders(folder_path: str) -> List[str]:
    """Get all subfolders from a folder."""
    return [f.name for f in Path(folder_path).iterdir() if f.is_dir()]


def display_image_group(images: List[str], start_idx: int, group_size: int):
    """Display a group of images."""
    end_idx = min(start_idx + group_size, len(images))
    current_images = images[start_idx:end_idx]

    cols = st.columns(min(4, len(current_images)))
    for idx, img_path in enumerate(current_images):
        with cols[idx % len(cols)]:
            st.image(img_path, use_container_width=True)

    return end_idx < len(images)


def reset_image_viewing_state():
    """Reset all image viewing related session state variables."""
    if "show_image" in st.session_state:
        del st.session_state.show_image
    if "current_folder" in st.session_state:
        del st.session_state.current_folder
    if "folder_history" in st.session_state:
        del st.session_state.folder_history
    if "current_group_start" in st.session_state:
        del st.session_state.current_group_start
    if "group_size" in st.session_state:
        del st.session_state.group_size


class ImageViewer:
    """A component for viewing images in folders with navigation capabilities."""

    def __init__(self, image_path: str):
        """Initialize the image viewer with a path to images."""
        self.image_path = image_path
        self._initialize_state()

    def _initialize_state(self):
        """Initialize session state variables if they don't exist."""
        if "current_folder" not in st.session_state:
            st.session_state.current_folder = self.image_path
            st.session_state.folder_history = [self.image_path]
        if "current_group_start" not in st.session_state:
            st.session_state.current_group_start = 0
        if "group_size" not in st.session_state:
            st.session_state.group_size = 8

    def _handle_dataset_change(self):
        """Handle dataset path changes."""
        if "previous_dataset" not in st.session_state:
            st.session_state.previous_dataset = self.image_path
        elif st.session_state.previous_dataset != self.image_path:
            reset_image_viewing_state()
            st.session_state.previous_dataset = self.image_path

    def _display_folder_navigation(self):
        """Display folder navigation controls."""
        # Display current folder path
        st.write(f"当前路径: {st.session_state.current_folder}")

        # Add back button if not at root
        if len(st.session_state.folder_history) > 1:
            if st.button("返回上级文件夹", key="back_to_parent_button"):
                st.session_state.folder_history.pop()
                st.session_state.current_folder = st.session_state.folder_history[-1]
                st.session_state.current_group_start = 0
                st.rerun()

        # Get and display subfolders
        subfolders = get_subfolders(st.session_state.current_folder)
        if subfolders:
            st.write("选择文件夹:")
            cols = st.columns(4)
            for idx, folder in enumerate(subfolders):
                with cols[idx % 4]:
                    if st.button(folder, key=f"folder_button_{folder}"):
                        new_folder = os.path.join(st.session_state.current_folder, folder)
                        st.session_state.current_folder = new_folder
                        st.session_state.folder_history.append(new_folder)
                        st.session_state.current_group_start = 0
                        st.rerun()

    def _display_image_navigation(self, images: List[str]):
        """Display image navigation controls."""
        # Display current group of images
        has_more = display_image_group(images, st.session_state.current_group_start, st.session_state.group_size)

        # Navigation buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.current_group_start > 0:
                if st.button("上一组", key="prev_group_button"):
                    st.session_state.current_group_start -= st.session_state.group_size
                    st.rerun()

        with col2:
            if has_more:
                if st.button("下一组", key="next_group_button"):
                    st.session_state.current_group_start += st.session_state.group_size
                    st.rerun()

    def show(self):
        """Display the image viewer interface."""
        self._handle_dataset_change()

        if "show_image" in st.session_state and st.session_state.show_image:
            # Allow user to configure group size
            st.session_state.group_size = st.slider(
                "每组图片数量",
                min_value=1,
                max_value=16,
                value=st.session_state.group_size,
                step=1,
            )

            # Check if path is a directory
            if os.path.isdir(st.session_state.current_folder):
                self._display_folder_navigation()

                # Get and display images
                images = get_image_files(st.session_state.current_folder)
                if images:
                    self._display_image_navigation(images)
                else:
                    st.warning("当前文件夹中没有图片文件")
            else:
                # Single image display
                st.image(self.image_path)
