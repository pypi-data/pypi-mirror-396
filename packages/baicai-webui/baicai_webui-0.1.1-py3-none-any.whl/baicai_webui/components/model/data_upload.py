import os
from pathlib import Path
from typing import Any, Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import torch
from baicai_base.utils.data import get_tmp_folder, load_data
from baicai_dev.utils.data import TaskType, load_example_data
from baicai_dev.utils.setups import (
    bears_func_config,
    bears_re_config,
    bears_single_label_config,
    collab_config,
    create_dl_config,
    create_ml_config,
    garment_config_data,
    house_config_data,
    iris_config_data,
    mnist_csv_config,
    multi_label_config,
    ner_inference_config,
    semantic_match_inference_config,
    sentiment_classifier_trainer_config,
    sentiment_inference_config,
    titanic_config_data,
)

# 设置matplotlib中文显示，支持多平台
plt.rcParams["font.sans-serif"] = [
    "SimHei", "Microsoft YaHei", "Arial Unicode MS", "STHeiti", "PingFang SC", "Heiti TC", "WenQuanYi Micro Hei", "sans-serif"
]
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号


@st.cache_data
def create_histogram(df_clean, col_name):
    """创建直方图的缓存函数"""
    try:
        # 清理之前的图形
        plt.close("all")

        fig, ax = plt.subplots(figsize=(4, 3))
        df_clean[col_name].hist(ax=ax, bins=20, alpha=0.7, edgecolor="black")
        ax.set_title(f"{col_name}")
        ax.set_xlabel(col_name)
        ax.set_ylabel("频次")
        return fig
    except Exception:
        plt.close("all")  # 确保出错时也清理图形
        return None


@st.cache_data
def create_bar_chart(df_clean, col_name):
    """创建柱状图的缓存函数"""
    try:
        # 清理之前的图形
        plt.close("all")

        value_counts = df_clean[col_name].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(4, 3))
        value_counts.plot(kind="bar", ax=ax, alpha=0.7)
        ax.set_title(f"{col_name}")
        ax.set_xlabel(col_name)
        ax.set_ylabel("频次")
        ax.tick_params(axis="x", rotation=45)
        plt.tight_layout()
        return fig
    except Exception:
        plt.close("all")  # 确保出错时也清理图形
        return None


@st.cache_data
def create_scatter_plot_simple(df_clean, x_col, y_col, use_sampling, jitter_amount):
    """创建散点图的缓存函数（使用固定的采样策略和可控制的抖动）"""
    try:
        # 清理之前的图形
        plt.close("all")

        # 准备数据（已经清理过缺失值）
        plot_data = df_clean[[x_col, y_col]]

        # 使用固定的采样策略
        if use_sampling and len(plot_data) > 2000:
            plot_data = plot_data.sample(n=2000, random_state=42)

        # 获取列类型
        numeric_cols = df_clean.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df_clean.select_dtypes(include=["object", "category"]).columns.tolist()

        # 数据预处理：为分类数据添加抖动
        x_data = plot_data[x_col].copy()
        y_data = plot_data[y_col].copy()

        # 为分类数据添加抖动
        x_col_categorical = x_col in categorical_cols
        y_col_categorical = y_col in categorical_cols

        if x_col_categorical:
            # 将分类数据转换为数值，并添加随机抖动
            x_unique = x_data.unique()
            x_mapping = {val: i for i, val in enumerate(x_unique)}
            x_data = x_data.map(x_mapping)
            # 添加可控制的抖动
            x_jitter = np.random.normal(0, jitter_amount, len(x_data))
            x_data = x_data + x_jitter
        else:
            x_unique = None

        if y_col_categorical:
            # 将分类数据转换为数值，并添加随机抖动
            y_unique = y_data.unique()
            y_mapping = {val: i for i, val in enumerate(y_unique)}
            y_data = y_data.map(y_mapping)
            # 添加可控制的抖动
            y_jitter = np.random.normal(0, jitter_amount, len(y_data))
            y_data = y_data + y_jitter
        else:
            y_unique = None

        # 创建散点图
        fig, ax = plt.subplots(figsize=(10, 8))

        # 普通散点图
        ax.scatter(x_data, y_data, alpha=0.6, s=20)

        # 设置坐标轴标签
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(f"{x_col} vs {y_col} 散点图")
        ax.grid(True, alpha=0.3)

        # 为分类数据设置刻度标签
        if x_col_categorical:
            ax.set_xticks(range(len(x_unique)))
            ax.set_xticklabels(x_unique, rotation=45, ha="right")

        if y_col_categorical:
            ax.set_yticks(range(len(y_unique)))
            ax.set_yticklabels(y_unique)

        # 添加趋势线（仅当两列都是数值型时）
        if x_col in numeric_cols and y_col in numeric_cols and len(plot_data) > 1:
            z = np.polyfit(plot_data[x_col], plot_data[y_col], 1)
            p = np.poly1d(z)
            ax.plot(plot_data[x_col], p(plot_data[x_col]), "r--", alpha=0.8, linewidth=2)

            # 计算相关系数
            correlation = plot_data[x_col].corr(plot_data[y_col])
            ax.text(0.05, 0.95, f"相关系数: {correlation:.3f}",
                   transform=ax.transAxes, fontsize=10,
                   verticalalignment="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

        plt.tight_layout()
        return fig, plot_data, x_col_categorical, y_col_categorical, numeric_cols
    except Exception:
        plt.close("all")  # 确保出错时也清理图形
        return None, None, False, False, []


@st.cache_data
def process_data_for_visualization(df):
    """处理数据用于可视化的缓存函数"""
    # 处理缺失值，创建干净的数据副本
    df_clean = df.copy()

    # 只对仍然是object类型的列进行字符串缺失值替换
    string_missing_values = ["NA", "N/A", "null", "NULL", "missing", "Missing", "MISSING", "", " "]

    # 将字符串缺失值替换为NaN（只对object类型）
    for col in df_clean.columns:
        if df_clean[col].dtype == "object":
            for missing_val in string_missing_values:
                df_clean[col] = df_clean[col].replace(missing_val, pd.NA)

    # 删除所有缺失值
    df_clean = df_clean.dropna()

    return df_clean


def display_data_info(df: pd.DataFrame) -> None:
    """显示数据框的基本信息"""
    with st.expander("数据信息", expanded=False):
        # 数据类型转换功能 - 放在最开始
        st.markdown("#### 数据类型调整")
        st.write("如果某些列的数据类型不正确，可以在这里进行调整：")

        # 数据类型转换选项
        col1, col2 = st.columns(2)
        with col1:
            convert_col = st.selectbox("选择要转换的列", df.columns.tolist())
        with col2:
            target_dtype = st.selectbox(
                "目标数据类型",
                ["object", "int64", "float64", "datetime64", "category"],
                format_func=lambda x: {
                    "object": "文本 (object)",
                    "int64": "整数 (int64)",
                    "float64": "浮点数 (float64)",
                    "datetime64": "日期时间 (datetime64)",
                    "category": "分类 (category)"
                }[x]
            )

        # 转换按钮
        if st.button("🔄 转换数据类型"):
            try:
                original_dtype = df[convert_col].dtype

                if target_dtype == "datetime64":
                    # 尝试自动解析日期时间
                    df[convert_col] = pd.to_datetime(df[convert_col], errors="coerce")
                elif target_dtype == "int64":
                    # 转换为整数
                    df[convert_col] = pd.to_numeric(df[convert_col], errors="coerce").astype("Int64")
                elif target_dtype == "float64":
                    # 转换为浮点数
                    df[convert_col] = pd.to_numeric(df[convert_col], errors="coerce")
                elif target_dtype == "category":
                    # 转换为分类
                    df[convert_col] = df[convert_col].astype("category")
                elif target_dtype == "object":
                    # 转换为文本
                    df[convert_col] = df[convert_col].astype("object")

                new_dtype = df[convert_col].dtype
                st.success(f"✅ 成功将列 '{convert_col}' 从 {original_dtype} 转换为 {new_dtype}")

                # 清除缓存，因为数据类型发生了变化
                process_data_for_visualization.clear()
                create_histogram.clear()
                create_bar_chart.clear()
                create_scatter_plot_simple.clear()

            except Exception as e:
                st.error(f"❌ 转换失败: {str(e)}")

        # 显示当前数据类型（转换后）
        st.write("**当前数据类型：**")
        dtype_info = df.dtypes.to_frame("数据类型").reset_index()
        dtype_info.columns = ["列名", "数据类型"]
        # 将dtype对象转换为字符串
        dtype_info["数据类型"] = dtype_info["数据类型"].astype(str)
        st.dataframe(dtype_info, use_container_width=True)

        st.markdown("#### 数据样本")
        st.dataframe(df.head())

        # 检测各种形式的缺失值
        st.markdown("#### 数据缺失值信息")

        # 创建数据副本，避免修改原始数据
        df_clean = df.copy()

        # 定义常见的字符串缺失值
        string_missing_values = ["NA", "N/A", "null", "NULL", "missing", "Missing", "MISSING", "", " "]

        # 将字符串缺失值替换为NaN
        for col in df_clean.columns:
            if df_clean[col].dtype == "object":
                for missing_val in string_missing_values:
                    df_clean[col] = df_clean[col].replace(missing_val, pd.NA)

        # 使用isnull()检测所有缺失值
        all_missing = df_clean.isnull().sum()
        st.dataframe(all_missing)


def display_data_visualization(df: pd.DataFrame) -> None:
    """显示数据可视化"""
    with st.expander("数据可视化", expanded=False):
        # 使用缓存函数处理数据
        df_clean = process_data_for_visualization(df)

        if len(df_clean) == 0:
            st.warning("处理缺失值后没有剩余数据，无法进行可视化")
            return

        # 获取所有列
        all_cols = df_clean.columns.tolist()
        numeric_cols = df_clean.select_dtypes(include=["number"]).columns.tolist()
        categorical_cols = df_clean.select_dtypes(include=["object", "category"]).columns.tolist()

        # 分布图可视化
        st.markdown("#### 数据分布可视化")

        # 让用户选择要显示的列
        st.write("选择要查看分布的列（最多6列）：")
        selected_cols = st.multiselect(
            "选择列",
            options=all_cols,
            default=all_cols[:min(6, len(all_cols))],  # 默认选择前6列
            max_selections=6,
            format_func=lambda x: f"{x}" if x in numeric_cols else f"{x}" if x in categorical_cols else x
        )

        if len(selected_cols) > 0:
            # 显示选择的列信息
            st.write(f"已选择 {len(selected_cols)} 列进行可视化")

            # 创建多列布局
            cols = st.columns(min(3, len(selected_cols)))

            for i, col_name in enumerate(selected_cols):
                col_idx = i % 3

                with cols[col_idx]:
                    st.markdown(f"**{col_name}**")

                    if col_name in numeric_cols:
                        # 数值型数据：显示直方图
                        fig = create_histogram(df_clean, col_name)
                        if fig is not None:
                            st.pyplot(fig)
                            plt.close(fig)
                        else:
                            st.write(f"无法绘制 {col_name} 的直方图")

                    elif col_name in categorical_cols:
                        # 分类数据：显示柱状图
                        fig = create_bar_chart(df_clean, col_name)
                        if fig is not None:
                            st.pyplot(fig)
                            plt.close(fig)
                        else:
                            st.write(f"无法绘制 {col_name} 的柱状图")
        else:
            st.info("请选择要查看的列")

        # 散点图可视化
        if len(all_cols) >= 2:
            st.markdown("#### 散点图分析")

            # 采样设置
            max_sample_size = st.number_input(
                "最大采样数量（大数据集时使用）",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100,
                help="当数据超过此数量时，将随机采样以提升性能"
            )

            # 抖动设置
            jitter_amount = st.slider(
                "分类数据抖动大小",
                min_value=0.0,
                max_value=0.5,
                value=0.1,
                step=0.01,
                help="控制分类数据的随机抖动大小，0表示无抖动，数值越大抖动越明显"
            )

            # 选择散点图的X和Y轴
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("选择X轴列", all_cols, index=0)
            with col2:
                y_col = st.selectbox("选择Y轴列", all_cols, index=min(1, len(all_cols)-1))

            if x_col != y_col:
                try:
                    # 决定是否使用采样
                    use_sampling = len(df_clean) > max_sample_size

                    # 使用缓存函数创建散点图（使用固定的采样策略和可控制的抖动）
                    fig, plot_data, x_col_categorical, y_col_categorical, numeric_cols = create_scatter_plot_simple(df_clean, x_col, y_col, use_sampling, jitter_amount)

                    if fig is not None:
                        # 显示采样信息
                        if use_sampling:
                            st.info(f"数据量较大（{len(df_clean)}条），已随机采样2000条进行可视化")

                        # 显示抖动信息
                        if x_col_categorical or y_col_categorical:
                            st.info(f"分类数据抖动大小: {jitter_amount:.2f}")

                        st.pyplot(fig)
                        plt.close(fig)

                        # 显示基本统计信息
                        st.write("**散点图统计信息：**")
                        st.write(f"- 数据点数量: {len(plot_data)}")

                        if x_col in numeric_cols:
                            st.write(f"- X轴({x_col})范围: {plot_data[x_col].min():.2f} - {plot_data[x_col].max():.2f}")
                        else:
                            st.write(f"- X轴({x_col})类别数: {plot_data[x_col].nunique()}")

                        if y_col in numeric_cols:
                            st.write(f"- Y轴({y_col})范围: {plot_data[y_col].min():.2f} - {plot_data[y_col].max():.2f}")
                        else:
                            st.write(f"- Y轴({y_col})类别数: {plot_data[y_col].nunique()}")
                    else:
                        st.error("绘制散点图时出错")

                except Exception as e:
                    st.error(f"绘制散点图时出错: {str(e)}")
            else:
                st.warning("请选择不同的列作为X轴和Y轴")
        else:
            st.info("需要至少2列才能绘制散点图")


def get_metric_display_name(metric: str) -> str:
    """获取评价指标的显示名称"""
    metric_names = {
        "accuracy": "准确率 (Accuracy)",
        "precision": "精确率 (Precision)",
        "recall": "召回率 (Recall)",
        "f1": "F1分数 (F1-Score)",
        "mse": "均方误差 (MSE)",
        "mae": "平均绝对误差 (MAE)",
        "r2": "决定系数 (R²)",
        "rmse": "均方根误差 (RMSE)",
    }
    return metric_names.get(metric, metric)


def configure_metrics_ui(df, target_col=None, default_is_classification=None, config_data=None, default_name=None):
    """配置任务类型、基本信息和评价指标的UI组件

    Args:
        df: 数据框
        target_col: 目标列名，如果为None则会提示用户选择
        default_is_classification: 默认的任务类型是否为分类，None则默认为分类
        config_data: 可选的默认配置数据
        default_name: 默认任务名称，如果没有提供config_data或config_data中没有name

    Returns:
        tuple: (name, domain, domain_context, target_col, ignore_cols, is_classification, is_time_series, selected_metric, goal, ordinal_categories_list, date_feature, need_time, threshold)
               任务名称、领域、领域上下文、目标列、忽略的列、任务类型、是否为时序数据、选择的评价指标、目标值、有序特征类别列表、日期特征列、是否需要解析时间、时间阈值
    """
    # 如果没有提供config_data，初始化一个空字典
    if config_data is None:
        config_data = {}

    # 基本信息配置
    name = st.text_input("✏️ 任务名称", value=config_data.get("name", default_name or ""))
    domain = st.text_input("🌐 领域", value=config_data.get("domain", "machine learning"))
    domain_context = st.text_input("📚 领域上下文", value=config_data.get("domain_context", ""))

    # 让用户选择目标列
    cols = df.columns.tolist()
    if target_col is None:
        target_col = st.selectbox(
            "🎯 选择目标列",
            cols,
            index=cols.index(config_data.get("target", cols[-1])) if "target" in config_data else len(cols) - 1,
        )

    # 让用户选择要忽略的列
    ignore_cols = st.multiselect("🚫 选择要忽略的列", cols, default=config_data.get("ignored_features", []))

    # 选择任务类型
    task_type_index = 0 if default_is_classification in (True, None) else 1
    is_classification = (
        st.radio("📊 任务类型", ["🔍 分类", "📈 回归"], index=task_type_index, horizontal=True) == "🔍 分类"
    )

    # 根据任务类型提供可选的评价指标
    available_metrics = ["accuracy", "precision", "recall", "f1"] if is_classification else ["mse", "mae", "r2", "rmse"]
    selected_metric = st.selectbox("📏 选择评价指标", options=available_metrics, format_func=get_metric_display_name)

    # 根据选择的指标设置合适的目标值范围和默认值
    if selected_metric in ["accuracy", "precision", "recall", "f1"]:
        goal = st.slider(f"🎯 {get_metric_display_name(selected_metric)}目标值", 0.0, 1.0, 0.8)
    elif selected_metric in ["r2"]:
        goal = st.slider(f"🎯 {get_metric_display_name(selected_metric)}目标值", 0.0, 1.0, 0.6)
    elif selected_metric in ["mse", "mae", "rmse"]:
        # 显示目标列的基本统计信息，帮助用户设置合理的目标值
        target_stats = df[target_col].describe()
        st.write(f"📊 目标列 '{target_col}' 的基本统计信息：")
        st.write(f"- 平均值：{target_stats['mean']:.4f}")
        st.write(f"- 标准差：{target_stats['std']:.4f}")
        st.write(f"- 最小值：{target_stats['min']:.4f}")
        st.write(f"- 最大值：{target_stats['max']:.4f}")

        # 使用number_input让用户自由输入目标值
        st.info(f"🔍 请根据数据特征设置{get_metric_display_name(selected_metric)}的目标值（越小越好）")
        goal = st.number_input(
            "🎯 目标值",
            min_value=0.0,
            value=target_stats["std"],  # 默认使用标准差作为参考值
            format="%.4f",
        )

    with st.expander("⚙️ 高级设置", expanded=False):
        ## 特征工程建议
        st.write("💡 特征工程建议")
        requirements = st.text_input("特征工程建议", value=config_data.get("requirements", ""))

        # 有序分类数据
        ordinal_features_config = config_data.get("ordinal_features", [])
        # 从配置中提取特征名称列表
        ordinal_feature_names = []
        for feature_dict in ordinal_features_config:
            # Each item is a dict with a single key (feature name)
            if feature_dict:  # Skip empty dicts
                ordinal_feature_names.extend(feature_dict.keys())

        ordinal_features = st.multiselect("🔍 选择有序分类数据", cols, default=ordinal_feature_names)

        # 为每个有序特征设置类别顺序
        ordinal_categories = {}
        if ordinal_features:
            st.write("📊 设置有序特征的类别顺序")
            st.info("请为每个有序特征指定类别的顺序，类别之间用逗号分隔")

            # 创建字典来存储配置中的顺序信息
            config_orders = {}
            for feature_dict in ordinal_features_config:
                for feature, order in feature_dict.items():
                    config_orders[feature] = order

            for feature in ordinal_features:
                # 获取该特征的唯一值
                unique_values = df[feature].unique().tolist()
                if len(unique_values) > 10:
                    st.warning(f"🚨 {feature} 可能不是分类特征，不作为有序特征处理")
                    continue

                # 如果配置中有该特征的顺序，使用它作为默认值，否则使用数据中的唯一值
                if feature in config_orders:
                    default_order = ", ".join(map(str, config_orders[feature]))
                else:
                    default_order = ", ".join(map(str, unique_values))

                # 获取用户输入的顺序
                order_input = st.text_input(
                    f"📝 {feature} 的类别顺序",
                    value=default_order,
                    help=f"当前所有值: {', '.join(map(str, unique_values))}",
                )

                # 解析输入的顺序
                if order_input:
                    order = [item.strip() for item in order_input.split(",")]
                    ordinal_categories[feature] = order

                    # 显示预览效果
                    st.info(f"✅ {feature} 的类别顺序已设置为: {order}")

        # 将ordinal_categories转换为模型代码期望的格式：[{feature1: [order1]}, {feature2: [order2]}]
        ordinal_categories_list = []
        for feature, order in ordinal_categories.items():
            ordinal_categories_list.append({feature: order})

        # 想要解析时间的列
        date_feature = config_data.get("date_feature") if config_data.get("date_feature") != "" else cols[1]
        date_options = ["不选择"] + cols
        date_index = cols.index(date_feature) + 1 if date_feature in cols else 0
        date_feature = st.selectbox("🕒 选择需要解析日期时间的列", date_options, index=0)
        date_feature = "" if date_feature == "不选择" else date_feature

        if date_feature != "":
            need_time = st.radio("🕒 是否需要解析时间", ["✅ 是", "❌ 否"], index=1, horizontal=True) == "✅ 是"

            # 选择按照日期时间分割的阈值
            if "need_time" in locals() and need_time:
                date_col = st.columns(1)[0]
                threshold_date = date_col.date_input(
                    "🕒 选择按照日期分割的阈值日期", value=pd.Timestamp("2015-09-01").date()
                )

                time_cols = st.columns(3)
                threshold_hour = time_cols[0].number_input("小时", min_value=0, max_value=23, value=0, step=1)
                threshold_minute = time_cols[1].number_input("分钟", min_value=0, max_value=59, value=0, step=1)
                threshold_second = time_cols[2].number_input("秒", min_value=0, max_value=59, value=0, step=1)

                # 合并日期和时间
                threshold = pd.Timestamp(
                    year=threshold_date.year,
                    month=threshold_date.month,
                    day=threshold_date.day,
                    hour=threshold_hour,
                    minute=threshold_minute,
                    second=threshold_second,
                )

                # 将Timestamp转换为字典格式
                threshold_dict = {
                    "year": threshold_date.year,
                    "month": threshold_date.month,
                    "day": threshold_date.day,
                    "hour": threshold_hour,
                    "minute": threshold_minute,
                    "second": threshold_second,
                }
            else:
                threshold = st.date_input("🕒 选择按照日期时间分割的阈值", value=pd.Timestamp("2015-09-01"))

                # 将date转换为字典格式
                threshold_dict = {
                    "year": threshold.year,
                    "month": threshold.month,
                    "day": threshold.day,
                }

        # 选择是否为时序数据
        is_time_series = st.radio("🕒 是否为时序问题", ["✅ 是", "❌ 否"], index=1, horizontal=True) == "✅ 是"
        if is_time_series:
            if date_feature == "":
                st.error("🚨 请选择需要解析日期时间的列")
                return

    return (
        name,
        domain,
        domain_context,
        target_col,
        ignore_cols,
        is_classification,
        is_time_series,
        selected_metric,
        goal,
        ordinal_categories_list,
        date_feature,
        need_time if "need_time" in locals() else False,
        threshold_dict if is_time_series and "threshold_dict" in locals() else {},
        requirements,
    )


def vision_uploader() -> Dict[str, Any]:
    """视觉基础设置组件"""
    st.subheader("基础设置")

    upload_type = st.radio("选择上传方式", ["📁 文件夹上传", "💾 示例数据集"])

    if upload_type == "📁 文件夹上传":
        # 选择标注方式
        label_type = st.radio("选择标注方式", ["📁 文件夹结构标注", "📄 CSV文件标注"], horizontal=True)
        
        if label_type == "📁 文件夹结构标注":
            st.info("📂 请选择包含图片的文件夹，每个子文件夹名为类别名")
            train_path = st.text_input("🔍 训练数据路径")
            valid_path = st.text_input("🔍 验证数据路径（可选）")

            if train_path:
                # 基础配置
                st.subheader("模型配置")
                batch_size = st.number_input("批次大小", 1, 128, 4)
                model = st.selectbox("模型", ["resnet18", "resnet34", "resnet50"], index=0)
                valid_pct = st.slider("验证集比例", 0.0, 0.5, 0.2)
                num_workers = st.number_input("数据加载线程数", 0, 16, 4)
                size = st.number_input("图片大小", 16, 256, 128)

                # 创建配置数据
                config_data = {
                    "path": train_path,
                    "valid_path": valid_path,
                    "name": Path(train_path).name,
                    "task_type": TaskType.VISION_SINGLE_LABEL.value,
                    "model": model,
                    "batch_size": batch_size,
                    "valid_pct": valid_pct,
                    "num_workers": num_workers,
                    "size": size,
                    "train_folder": None,
                    "valid_folder": None,
                    "device": "cuda" if torch.cuda.is_available() else "cpu",
                }
                return create_dl_config(config_data)
        
        else:  # CSV文件标注
            st.info("📄 请选择包含图片的文件夹，并提供CSV标注文件")
            
            # 数据路径配置
            data_path = st.text_input("🔍 数据根目录路径", help="包含图片文件夹和CSV标注文件的根目录")
            
            if data_path:
                # CSV文件配置
                st.subheader("CSV标注文件配置")
                col1, col2 = st.columns(2)
                
                with col1:
                    folder = st.text_input("📁 图片文件夹名称", value="", help="图片所在子文件夹名称，如果图片在根目录请留空")
                    csv_file = st.text_input("📄 CSV文件名", value="labels.csv", help="CSV标注文件名")
                
                with col2:
                    image_col = st.text_input("🖼️ 图片列名", value="image", help="CSV文件中图片文件名所在列名")
                    label_col = st.text_input("🏷️ 标签列名", value="label", help="CSV文件中标签所在列名")
                
                # 任务类型选择
                task_type_option = st.radio("任务类型", ["🔍 单标签分类", "🏷️ 多标签分类"], horizontal=True)
                
                # 基础配置
                st.subheader("模型配置")
                batch_size = st.number_input("批次大小", 1, 128, 4)
                model = st.selectbox("模型", ["resnet18", "resnet34", "resnet50"], index=0)
                valid_pct = st.slider("验证集比例", 0.0, 0.5, 0.2)
                num_workers = st.number_input("数据加载线程数", 0, 16, 4)
                size = st.number_input("图片大小", 16, 256, 128)

                # 确定任务类型
                if task_type_option == "🏷️ 多标签分类":
                    task_type = TaskType.VISION_MULTI_LABEL.value
                else:
                    task_type = TaskType.VISION_CSV.value

                # 创建配置数据
                config_data = {
                    "path": data_path,
                    "name": Path(data_path).name,
                    "task_type": task_type,
                    "model": model,
                    "batch_size": batch_size,
                    "valid_pct": valid_pct,
                    "num_workers": num_workers,
                    "size": size,
                    "device": "cuda" if torch.cuda.is_available() else "cpu",
                    "folder": f"'{folder}'" if folder else None,
                    "csv_file": f"'{csv_file}'",
                    "image_col": f"'{image_col}'",
                    "label_col": f"'{label_col}'",
                }
                return create_dl_config(config_data)

    else:  # 示例数据集
        vision_configs = {
            "熊分类（单标签）": bears_single_label_config,
            "熊分类（函数标注）": bears_func_config,
            "熊分类（正则标注）": bears_re_config,
            "MNIST手写数字": mnist_csv_config,
            "PASCAL多标签分类": multi_label_config,
        }

        selected_dataset = st.selectbox("🔍 选择示例数据集", list(vision_configs.keys()))
        default_config = vision_configs[selected_dataset]

        # 显示数据集基本信息
        st.write(f"数据集: {default_config['name']}")
        st.write(f"数据路径: {default_config['path']}")
        st.write(f"任务类型: {default_config['task_type']}")

        # 基础配置
        batch_size = st.number_input("批次大小", 1, 128, default_config["batch_size"])
        model = st.selectbox(
            "模型",
            ["resnet18", "resnet34", "resnet50"],
            index=["resnet18", "resnet34", "resnet50"].index(default_config["model"]),
        )
        valid_pct = st.slider("验证集比例", 0.0, 0.5, default_config["valid_pct"])
        num_workers = st.number_input("数据加载线程数", 0, 16, default_config["num_workers"])
        size = st.number_input("图片大小", 16, 256, default_config["size"])

        # 根据任务类型显示不同的配置选项
        if default_config["task_type"] == TaskType.VISION_CSV.value:
            folder = st.text_input("数据集文件夹", value=default_config.get("folder", None))
            csv_file = st.text_input("CSV文件名", value=default_config["csv_file"])
            image_col = st.text_input("图片列名", value=default_config["image_col"])
            label_col = st.text_input("标签列名", value=default_config["label_col"])
            valid_col = st.text_input("验证集列名", value=default_config.get("valid_col", None))
            delimiter = st.text_input("分隔符", value=default_config.get("delimiter", None))
            label_delim = st.text_input("标签分隔符", value=default_config.get("label_delim", None))
            extra_config = {
                "folder": folder,
                "csv_file": csv_file,
                "image_col": image_col,
                "label_col": label_col,
                "valid_col": valid_col,
                "delimiter": delimiter,
                "label_delim": label_delim,
            }
        elif default_config["task_type"] == TaskType.VISION_FUNC.value:
            label_func = st.text_input("标注函数", value=default_config["label_func"])
            extra_config = {"label_func": label_func}
        elif default_config["task_type"] == TaskType.VISION_RE.value:
            pat = st.text_input("标注正则表达式", value=default_config["pat"])
            extra_config = {"pat": pat}
        elif default_config["task_type"] == TaskType.VISION_MULTI_LABEL.value:
            folder = st.text_input("数据集文件夹", value=default_config.get("folder", None))
            csv_file = st.text_input("CSV文件名", value=default_config["csv_file"])
            image_col = st.text_input("图片列名", value=default_config["image_col"])
            label_col = st.text_input("标签列名", value=default_config["label_col"])
            valid_col = st.text_input("验证集列名", value=default_config.get("valid_col", None))
            delimiter = st.text_input("分隔符", value=default_config.get("delimiter", None))
            label_delim = st.text_input("标签分隔符", value=default_config.get("label_delim", None))
            extra_config = {
                "folder": folder,
                "csv_file": csv_file,
                "image_col": image_col,
                "label_col": label_col,
                "valid_col": valid_col,
                "delimiter": delimiter,
                "label_delim": label_delim,
            }
        else:  # VISION_SINGLE_LABEL
            train_folder = st.text_input("训练集文件夹", value=default_config.get("train_folder", None))
            valid_folder = st.text_input("验证集文件夹", value=default_config.get("valid_folder", None))
            extra_config = {
                "train_folder": train_folder,
                "valid_folder": valid_folder,
            }

        # 创建配置数据
        config_data = {
            "path": default_config["path"],
            "name": default_config["name"],
            "task_type": default_config["task_type"],
            "batch_size": batch_size,
            "model": model,
            "valid_pct": valid_pct,
            "num_workers": num_workers,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "size": size,
            **extra_config,
        }
        return create_dl_config(config_data)

    return {}


def nlp_uploader() -> Dict[str, Any]:
    """NLP基础设置组件"""
    st.subheader("基础设置")

    # 只选择任务类型
    nlp_configs = {
        "情感分析推理": sentiment_inference_config,
        "命名实体识别": ner_inference_config,
        "语义匹配": semantic_match_inference_config,
        "情感分类训练": sentiment_classifier_trainer_config,
    }

    selected_dataset = st.selectbox("🔍 选择任务", list(nlp_configs.keys()))
    default_config = nlp_configs[selected_dataset]

    # 显示任务类型
    st.write(f"任务类型: {default_config['task_type']}")

    # 如果是"情感分类训练"，提供数据路径输入
    if selected_dataset == "情感分类训练":
        data_path = st.text_input("🔍 数据路径", value=default_config.get("path", ""))
        if data_path:
            text_column = st.text_input("文本列名", value=default_config.get("text_column", ""))
            label_column = st.text_input("标签列名", value=default_config.get("label_column", ""))
            num_labels = st.number_input("类别数量", 2, 100, default_config.get("num_labels", 2))
            num_epochs = st.number_input("训练轮数", 1, 100, default_config.get("num_epochs", 1))

            # 创建配置数据
            config_data = {
                "path": data_path,
                "name": default_config.get("name", selected_dataset),
                "task_type": default_config["task_type"],  # 使用预设的任务类型
                "model": default_config.get("model", "bert-base-chinese"),
                "batch_size": default_config.get("batch_size", 32),
                "num_epochs": num_epochs,
                "text_column": text_column,
                "label_column": label_column,
                "num_labels": num_labels,
            }

            if "label_mapping" in default_config:
                config_data["label_mapping"] = default_config["label_mapping"]

            return create_dl_config(config_data)

    else:  # 推理任务
        if "input" in default_config:
            input_text = st.text_input("输入文本", value=default_config["input"])
            config_data = {
                "name": selected_dataset,  # 添加任务名称
                "task_type": default_config["task_type"],  # 使用预设的任务类型
                "model": default_config.get("model", "bert-base-chinese"),
                "input": input_text,
            }
        elif "input1" in default_config:
            input1 = st.text_input("输入文本1", value=default_config["input1"])
            input2 = st.text_input("输入文本2", value=default_config["input2"])
            config_data = {
                "name": selected_dataset,  # 添加任务名称
                "task_type": default_config["task_type"],  # 使用预设的任务类型
                "model": default_config.get("model", "bert-base-chinese"),
                "input1": input1,
                "input2": input2,
            }
        return create_dl_config(config_data)

    return {}


def collab_uploader() -> Dict[str, Any]:
    """推荐系统基础设置组件"""
    st.subheader("基础设置")

    upload_type = st.radio("选择上传方式", ["💾 示例数据集"])

    if upload_type == "💾 示例数据集":
        default_config = collab_config

        # 显示数据集信息
        st.write(f"任务类型: {default_config['task_type']}")
        st.write(f"数据路径: {default_config['path']}")

        # 可调整的配置
        user_name = st.text_input("用户列名", value=default_config["user_name"])
        item_name = st.text_input("物品列名", value=default_config["item_name"])
        rating_name = st.text_input("评分列名", value=default_config["rating_name"])
        valid_pct = st.slider("验证集比例", 0.0, 0.5, default_config["valid_pct"])
        y_range = st.slider("评分范围", 0.0, 10.0, (default_config["y_range_min"], default_config["y_range_max"]))

        # 创建配置数据
        config_data = {
            "path": default_config["path"],
            "name": "MovieLens",
            "task_type": TaskType.COLLABORATIVE.value,
            "model": default_config.get("model", "collaborative_filtering"),
            "batch_size": default_config.get("batch_size", 32),
            "num_epochs": default_config.get("num_epochs", 3),
            "user_name": user_name,
            "item_name": item_name,
            "rating_name": rating_name,
            "valid_pct": valid_pct,
            "y_range_min": y_range[0],
            "y_range_max": y_range[1],
        }
        return create_dl_config(config_data)

    return {}


def ml_uploader() -> Dict[str, Any]:
    """机器学习基础设置组件"""
    st.subheader("基础设置")

    upload_type = st.radio("选择数据集", ["📤 上传数据集", "💾 使用示例数据集"])

    if upload_type == "📤 上传数据集":
        # Update supported file types based on load_data capabilities
        supported_types = ["csv", "xls", "xlsx", "json", "html", "parquet", "pkl", "h5", "txt", "xml", "db"]
        file = st.file_uploader("📎 上传数据文件", type=supported_types)

        if file:
            # 保存上传的文件
            save_path = get_tmp_folder() / "from_user" / "ml"
            save_path.mkdir(exist_ok=True, parents=True)
            file_path = save_path / file.name
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            # 根据文件类型设置额外参数
            file_extension = file_path.suffix.lower().strip(".")
            extra_params = {}

            # 显示特定文件类型的额外选项
            if file_extension in ["txt", "csv"]:
                delimiter_options = {
                    ",": "逗号 (,)",
                    ";": "分号 (;)",
                    "\t": "制表符 (Tab)",
                    "|": "竖线 (|)",
                    " ": "空格 (Space)",
                    "custom": "自定义分隔符",
                }
                default_delimiter = "," if file_extension == "csv" else "\t"
                delimiter_choice = st.selectbox(
                    "📏 分隔符",
                    options=list(delimiter_options.keys()),
                    format_func=lambda x: delimiter_options[x],
                    index=list(delimiter_options.keys()).index(default_delimiter),
                )

                if delimiter_choice == "custom":
                    custom_delimiter = st.text_input("✏️ 请输入自定义分隔符")
                    if custom_delimiter:  # 确保用户输入了分隔符
                        delimiter = custom_delimiter
                    else:
                        st.warning("⚠️ 请输入有效的分隔符")
                        delimiter = default_delimiter  # 如果用户没有输入，使用默认分隔符
                else:
                    delimiter = delimiter_choice

                extra_params["delimiter"] = delimiter
            elif file_extension == "h5":
                key = st.text_input("🔑 数据键", value="df")
                extra_params["key"] = key
            elif file_extension == "db":
                query = st.text_input("🔍 SQL查询", value="SELECT * FROM table_name")
                extra_params["query"] = query

            try:
                # 使用load_data加载数据
                df = load_data(path=file_path, **extra_params)
                display_data_info(df)
                display_data_visualization(df)

                # 让用户设置基本配置并配置任务类型和评价指标
                (
                    name,
                    domain,
                    domain_context,
                    target_col,
                    ignore_cols,
                    is_classification,
                    is_time_series,
                    selected_metric,
                    goal,
                    ordinal_categories_list,
                    date_feature,
                    need_time,
                    threshold,
                    requirements,
                ) = configure_metrics_ui(df, None, None, {}, file.name.split(".")[0].replace(" ", "_"))

                # 创建配置数据
                config_data = {
                    "delimiter": extra_params.get("delimiter", ","),
                    "path": str(file_path),
                    "target": target_col,
                    "ignored_features": ignore_cols,
                    "classification": is_classification,
                    "time_series": is_time_series,
                    "metrics": selected_metric,
                    "selected_metric": selected_metric,
                    "name": name,
                    "domain": domain,
                    "domain_context": domain_context,
                    "goal": goal,
                    "task_type": TaskType.ML.value,
                    "ordinal_features": ordinal_categories_list,
                    "date_feature": date_feature,
                    "need_time": need_time,
                    "threshold": threshold,
                    "requirements": requirements,
                }

                # 使用create_ml_config创建标准配置
                return create_ml_config(config_data)

            except Exception as e:
                st.error(f"加载数据时出错: {str(e)}")
                return {}

    else:  # 示例数据集
        dataset_configs = {
            "iris": iris_config_data,
            "titanic": titanic_config_data,
            "house": house_config_data,
            "garment": garment_config_data,
        }
        selected_dataset = st.selectbox("🔍 选择示例数据集", list(dataset_configs.keys()))

        if selected_dataset:
            if selected_dataset == "iris":
                with st.expander("🔍 了解iris数据集", expanded=False):
                    st.write(
                        "iris数据集是一个经典的机器学习数据集，用于分类任务。它包含150个样本，每个样本有4个特征（花萼长度、花萼宽度、花瓣长度、花瓣宽度）和一个目标变量（花的种类）。"
                    )
                    st.write("- 花萼长度 (sepal length)")
                    st.write("- 花萼宽度 (sepal width)")
                    st.write("- 花瓣长度 (petal length)")
                    st.write("- 花瓣宽度 (petal width)")
                    st.write("**目标变量：**")
                    st.write("- 花的种类 (iris)")

                if not os.path.exists(iris_config_data["path"]):
                    with st.status("自动下载iris数据集"):
                        from sklearn import datasets

                        iris = datasets.load_iris()
                        iris_df = pd.DataFrame(iris.data, columns=iris.feature_names)
                        iris_df["iris"] = iris.target_names[iris.target]
                        iris_df.to_csv(iris_config_data["path"], index=False)

            if selected_dataset == "titanic":
                with st.expander("🔍 了解titanic数据集", expanded=False):
                    st.markdown("https://seaborn.pydata.org/generated/seaborn.load_dataset.html")

                if not os.path.exists(titanic_config_data["path"]):
                    with st.status("自动下载titanic数据集"):
                        from seaborn import load_dataset

                        titanic = load_dataset("titanic")
                        titanic.to_csv(titanic_config_data["path"], index=False)

            if selected_dataset == "house":
                with st.expander("🔍 了解house数据集", expanded=False):
                    st.markdown("https://scikit-learn.org/stable/datasets/real_world.html#california-housing-dataset")

                if not os.path.exists(house_config_data["path"]):
                    with st.status("自动下载house数据集"):
                        from sklearn.datasets import fetch_california_housing

                        housing = fetch_california_housing(as_frame=True)
                        housing_df = pd.concat([housing.data, housing.target], axis=1)
                        housing_df.to_csv(house_config_data["path"], index=False)

            if selected_dataset == "garment":
                with st.expander("🔍 了解garment数据集", expanded=False):
                    st.markdown(
                        "Productivity Prediction of Garment Employees [Dataset]. (2020). UCI Machine Learning Repository. <https://doi.org/10.24432/C51S6D>"
                    )

            config_data = dataset_configs[selected_dataset]
            df = load_example_data(selected_dataset)
            display_data_info(df)
            display_data_visualization(df)

            # 配置任务类型和评价指标，使用已有配置作为默认值
            (
                name,
                domain,
                domain_context,
                target_col,
                ignore_cols,
                is_classification,
                is_time_series,
                selected_metric,
                goal,
                ordinal_categories_list,
                date_feature,
                need_time,
                threshold,
                requirements,
            ) = configure_metrics_ui(
                df, None, config_data.get("classification"), config_data, config_data.get("name")
            )

            # 创建配置数据
            config_data = {
                "delimiter": ",",
                "path": config_data["path"],
                "target": target_col,
                "ignored_features": ignore_cols,
                "classification": is_classification,
                "time_series": is_time_series,
                "metrics": selected_metric,
                "selected_metric": selected_metric,
                "name": name,
                "domain": domain,
                "domain_context": domain_context,
                "goal": goal,
                "task_type": TaskType.ML.value,
                "ordinal_features": ordinal_categories_list,
                "date_feature": date_feature,
                "need_time": need_time,
                "threshold": threshold,
                "requirements": requirements,
            }

            # 使用create_ml_config创建标准配置
            return create_ml_config(config_data)

    return {}
