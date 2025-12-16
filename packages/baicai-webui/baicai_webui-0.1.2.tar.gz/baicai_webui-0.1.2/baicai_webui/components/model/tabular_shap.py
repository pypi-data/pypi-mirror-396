import random
import string
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import streamlit as st
from baicai_base.utils.data import load_data as load_clean_data

from baicai_webui.components.model import draw_matplotlib

# TODO: https://www.kaggle.com/code/dansbecker/advanced-uses-of-shap-values

BAR_PLOT_INFO = """
## 📊 什么是 SHAP Bar 图？
SHAP Bar 图展示的是 **特征对模型预测影响的平均绝对贡献值（mean(|SHAP|)）**，也就是：
> **每个特征平均对模型输出的影响大小（不管正负方向，只看绝对值）**

通俗理解：
- 谁的平均"影响力"最大，谁就排在最上面
- 完全不管方向（增加还是降低预测值）

---

## 🧠 Bar 图怎么看？
| 图元素         | 说明 |
|---------------|------|
| **Y轴（特征名）** | 按重要性从上往下排，越上面代表对模型影响越大 |
| **X轴（平均绝对SHAP值）** | 代表这个特征对模型预测的平均影响力大小 |
| **条的长度**    | 越长，代表越重要，越影响模型输出 |

---

## ✅ 示例：
假设你在做贷款违约预测，SHAP bar 图排出来是：
```
特征              平均|SHAP|值
---------------------------------
负债率              ➡️➡️➡️➡️➡️➡️➡️➡️➡️➡️➡️
信用卡逾期次数       ➡️➡️➡️➡️➡️➡️➡️
年龄                ➡️➡️➡️➡️
收入                ➡️➡️➡️
```

解读：
- **负债率** 是模型里影响最大的特征（无论是推高还是拉低违约概率）
- **信用卡逾期** 其次
- **年龄** 和 **收入** 影响相对小

注意：
这里完全不关心"年龄大是增加还是减少风险"，**只看影响大不大**

---
## ⚠️ 常见误区：
| 误区                               | 正确理解 |
|------------------------------------|----------|
| 以为 bar 图有"正负方向"                | ❌ 没有正负，只有绝对值大小 |
| 以为 bar 图可以直接解释"特征大就风险高" | ❌ 不行，此图不带方向，只能看重要性 |
---

## ✅ 什么时候用 bar 图？
- 快速了解**哪些特征重要**
- 比较特征对模型预测的平均影响力大小
- 不关心方向时用（方向要看 beeswarm）
---
"""

BEESWARM_PLOT_INFO = """
## 🐝 什么是 SHAP Beeswarm 图？
Beeswarm 图是将所有样本的 SHAP 值（即每个特征对模型输出的影响）集中展示在一张图上，横轴是 SHAP 值，纵轴是特征名。每一条特征对应的横向散点，就是这个特征在所有样本上的 SHAP 值分布。

---

## 🧠 图上每个元素代表什么？
| 图中元素           | 含义 |
|---------------------|------|
| **Y轴（特征）**       | 重要性从上到下排序的特征名，最上面的是对模型最重要的特征。 |
| **X轴（SHAP值）**     | 该特征对预测值的贡献，值为正表示推高预测结果，值为负表示降低预测结果。 |
| **每个小点（一个样本）** | 代表单个样本下，该特征的 SHAP 值（即这个特征对该样本预测结果的贡献）。|
| **点的颜色（特征值大小）** | 一般为渐变色，红色表示特征值大，蓝色表示特征值小。|

---

## 🎯 如何解读？
假设横轴是预测"信用风险"（风险越大模型输出越高）：

- **特征重要性**（按y轴从上往下）：
- 越靠上，说明这个特征整体对模型贡献越大。

- **SHAP值（x轴位置）**：
- **> 0**：该特征让模型预测值增加（增加风险）。
- **< 0**：该特征让模型预测值降低（降低风险）。

- **点的颜色（特征值）**：
- 如果"年龄"特征中，红色（年龄大）点多在左边（负SHAP值），说明"年龄大"降低风险；
- 如果蓝色（年龄小）点多在右边（正SHAP值），说明"年龄小"增加风险。

---

## 🖍 举个例子
假设你分析贷款违约预测模型，beeswarm 里有：
```
特征                             SHAP值分布（横向）
----------------------------------------------------------
年龄                🦀🦀🦀🦀🦀🦀🦀🦀🦀|🐟🐟🐟🐟🐟🐟
收入                               🦀🦀🦀|🐟🐟🐟🐟
负债比率                              🐟🐟|🦀🦀
```
解释：
- **年龄**：年龄越小（蓝色）越容易增加违约风险（右侧），年龄大（红色）降低风险（左侧）。
- **收入**：收入高（红色）降低风险（左），收入低（蓝色）增加风险（右）。
- **负债比率**：负债比率越高（红色），违约风险越大（右）。

---

## ✅ 分析重点总结
1. **先看最上面的特征**，这是模型最重要的。
2. **看红蓝分布和左右趋势**，判断特征值大还是小对预测影响大。
3. **关注异常点或宽度**，宽度大说明该特征对不同样本影响差异大。

---

## 🌟 结论
SHAP beeswarm 图不仅告诉你"谁重要"，还能直观告诉你：
- 重要特征的方向性（推高 or 拉低预测）；
- 特征取值大小带来的不同影响；
- 哪些特征对不同样本的影响特别不一样（可能是模型解释的关键点）。
"""

BAR_VS_BEESWARM_INFO = """
| 图种类 | 作用 | 有没有方向 | 能看离散/异常吗 |
| --- | --- | --- | --- |
| **SHAP Bar** | 看特征重要性排名（平均影响） | ❌ 无方向 | ❌ 看不到 |
| **SHAP Beeswarm** | 看重要性+正负方向+离散 | ✅ 有方向 | ✅ 能看到 |
"""

FORCE_PLOT_INFO = """
**SHAP Force Plot（力图）** 是 SHAP 可视化里最直观、最能解释"单个样本预测过程"的图。它直接告诉你：
👉 每个特征到底是 **"拉高"** 预测结果，还是 **"拉低"** 预测结果。

## ✅ Force Plot 是什么？
它的核心思想：
- 把模型的"基础值"（base value）作为起点
- 然后每个特征像"力"一样，往 **右（推高预测）** 或 **左（降低预测）** 施加影响
- 最终合力，得到预测值

---

## 📈 Force Plot 结构
```
Base Value （模型平均预测值），Final Output（本条样本预测值）
|
|———红色🔴（正向，增加预测）——→|←———蓝色🔵（负向，降低预测）———|
|

```

颜色：
- 🔴 **红色**：该特征在当前样本上 **推高了模型预测**
- 🔵 **蓝色**：该特征在当前样本上 **拉低了模型预测**

---

## ✅ 举个直观例子：
### 背景：贷款违约预测（0-1 概率）
- Base Value（平均违约率）：0.2
- 这条样本预测违约概率：0.8

Force Plot：
```
Base Value: 0.2，Final Output: 0.8
|
|——— 红🔴（年龄小 +0.3） ———|——— 红🔴（负债率高 +0.4） ———||——— 蓝🔵（收入高 -0.1） ———|
|
```

### 解读：
- 这个人本来平均违约概率 0.2
- 因为负债率高（+0.4）、年龄小（+0.3）→ **大幅推高风险**
- 收入高（-0.1）→ **降低了一点风险**
- 最终预测是 **0.8**（**0.2**+0.3+0.4-0.1=0.8）

---

## ✅ Force Plot 看什么？
| 看点 | 解释 |
|-----|------|
| **Base Value** | 模型平均预测 |
| **每个特征的"力"** | 具体特征对结果的"推拉" |
| **颜色** | 红推高，蓝拉低 |
| **最终输出值** | 这条样本的最终预测 |
---

## ⚠ Force Plot 适用场景：
✅ 单个样本的详细解释
✅ 领导问："为啥这个人被判高风险？" —— 看 force plot 秒懂
✅ 可以对接 **dashboards**，做 explainable AI

---

## ✅ 总结一张话术：
> **SHAP Force Plot** 就是"模型预测拉力图"，告诉你一条数据为什么会预测高或低。红的在推高预测，蓝的在拉低预测，最后合力走向最终预测值。

"""

WATERFALL_PLOT_INFO = """
很多人容易把 **SHAP Waterfall Plot（水瀑图）** 和 **Force Plot** 混淆。
但其实，Waterfall 是更"稳重"和"详细"的单样本解释图，特别适合写报告或给业务看。

---

## ✅ 什么是 SHAP Waterfall Plot？
**Waterfall 图** 是针对 **单个样本（Single Instance）**，按特征贡献从大到小排序，把预测值的变化过程一步步"堆积"出来，像"瀑布"一样流向最终结果。

核心结构：
```
Base Value（全局平均预测值）
↓
+ 特征1（贡献最大）
↓
+ 特征2
↓
...
↓
最终预测值（这条样本的输出）
```

---

## 📈 Waterfall 图的视觉特征：
| 图元素              | 说明 |
|---------------------|------|
| **左边起点**         | base_value（模型对所有数据的平均预测） |
| **每一段红/蓝方块**   | 当前特征的 SHAP 值（正推高，负拉低） |
| **红色**             | 这个特征往右推，增加预测值 |
| **蓝色**             | 这个特征往左拉，降低预测值 |
| **右边终点**         | 当前样本的最终预测值 |

---

## ✅ 举个实际例子（贷款违约预测）：
Base value（平均违约概率） = 0.2
最终模型预测（这个人违约概率） = 0.8

Waterfall 过程：
```
0.2
│
├── +0.4 负债率高 (红)
├── +0.2 年龄小 (红)
├── -0.1 收入高 (蓝)
├── +0.1 教育低 (红)
│
0.8
```

### 结论：
- **负债率高** 是最大风险因素（+0.4）
- **收入高** 帮助降低了一点风险（-0.1）
- 其他特征有正有负
- 最后综合起来，违约概率拉到了 0.8

---

## ✅ Waterfall 图的优势：
| 优势 | 说明 |
|-----|------|
| 清晰的单条样本推理链条 | 一步步解释每个特征怎么影响预测 |
| 按"贡献大小"排序 | 优先看最大原因 |
| 配色直观 | 红→风险推高，蓝→风险降低 |
| 适合业务汇报 | 易于非技术人员理解 |

---

## 🆚 和 Force Plot 有啥区别？
| 图 | 是否排序 | 是否适合汇报 | 适用场景 |
|----|---------|------------|--------|
| **Force Plot** | ❌ 无特征排序 | 互动性强，报告稍弱 | 实时在线解释、Dashboard |
| **Waterfall Plot** | ✅ 按重要性排序 | ✅ 非常适合汇报和写PPT | 单样本详细解释，写报告必备 |

---

## ✅ 总结（秒懂版本）：
👉 **Waterfall Plot** 就是一张详细的"特征贡献账单"：
- 从"模型平均预测"出发
- 一步步"加分"或"减分"
- 最终算到这条样本的预测值

特别适合直接回答：
**"这个人为什么模型判他高风险？"**
—— 看 Waterfall，一目了然。

---

如果你需要代码示例或样图，我可以直接给你！
"""


def get_random_string(length=10):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def is_classification_model(model):
    # Check if the model is a classifier by looking at its class name
    model_type = type(model).__name__.lower()
    return any(classifier in model_type for classifier in ["classifier", "logisticregression"])


# data.train.ys is a dataframe, and data.train.ys.iloc[:, 0] is a series
# data.train.ys.values.ravel() is a numpy array
@st.cache_data
def load_data(
    path: Path | None = None,
    sample_size: int | None = 2000,
    sample_percentage: float | None = 0.1,
    is_classification: bool = True,
):
    """
    Load data from various data sources.
    If none of sample_size and sample_percentage is provided, return the whole testing data.
    If only one of them is provided, sample the testing data accordingly.
    If both are provided, sample the testing data of the smaller size.

    Args:
        path (str): Path to the data source.
        sample_size (int): Number of samples to sample.
        sample_percentage (float): Percentage of samples to sample.
    """

    data = load_clean_data(path)
    mapping = {}
    if isinstance(data, dict):
        X_train, y_train = data["X_train"], data["y_train"]
        X_test, y_test = data["X_test"], data["y_test"]
        vocab = data["vocab"]
        # Create mapping from unique values in y_train
        mapping = dict(enumerate(vocab))
    else:
        X_train, y_train = data.train.xs, data.train.ys.iloc[:, 0]
        X_test, y_test = data.valid.xs, data.valid.ys.iloc[:, 0]
        # get mapping from prediction (idxs) to class names in vocab
        try:
            mapping = dict(enumerate(data.vocab))
        except:
            mapping = {i: v for i, v in enumerate(y_train.unique())}

    test_size = len(X_test)

    if sample_size is None and sample_percentage is None:
        return X_train, X_test, y_train, y_test, mapping

    elif sample_size is not None and sample_percentage is None:
        if sample_size < test_size:
            sampled_indices = np.random.choice(test_size, sample_size, replace=False)
            X_test = X_test.iloc[sampled_indices]
            y_test = y_test.iloc[sampled_indices]

    elif sample_percentage is not None and sample_size is None:
        sampled_indices = np.random.choice(test_size, int(test_size * sample_percentage), replace=False)
        X_test = X_test.iloc[sampled_indices]
        y_test = y_test.iloc[sampled_indices]

    elif sample_size is not None and sample_percentage is not None:
        sample_size = min(sample_size, int(test_size * sample_percentage))
        if sample_size < test_size:
            sampled_indices = np.random.choice(test_size, sample_size, replace=False)
            X_test = X_test.iloc[sampled_indices]
            y_test = y_test.iloc[sampled_indices]

    return X_train, X_test, y_train, y_test, mapping


@st.cache_resource
def load_model(path: Path | None = None, classification: bool = True):
    model = joblib.load(path)
    return model


@st.cache_resource
def create_explainer(_model, X_train, is_classification: bool):
    if is_classification:
        explainer = shap.Explainer(_model.predict_proba, X_train.sample(100))
    else:
        explainer = shap.Explainer(_model, X_train.sample(100))
    return explainer


@st.cache_data
def compute_shap_values(_explainer, X_test, selected_class: int | None = None):
    """Compute SHAP values and return a proper Explanation object."""
    shap_values = _explainer(X_test)
    if selected_class is not None and hasattr(shap_values, "values"):
        # For classification models, we need to handle the multi-class case
        if len(shap_values.shape) > 2:  # Multi-class case
            shap_values = shap.Explanation(
                values=shap_values.values[..., selected_class],
                base_values=shap_values.base_values[..., selected_class],
                data=shap_values.data,
                feature_names=shap_values.feature_names,
            )
    return shap_values


@st.cache_data
def compute_clustering(X_test, y_test):
    """Compute hierarchical clustering for the data."""
    return shap.utils.hclust(X_test, y_test)


def create_shap_analysis(title: str = "SHAP 分析", model_path: Path | None = None, data_path: Path | None = None):
    st.title(title)

    # Initialize session state variables
    if "selected_row" not in st.session_state:
        st.session_state.selected_row = 0
    if "selected_class" not in st.session_state:
        st.session_state.selected_class = 0
    if "plot_type" not in st.session_state:
        st.session_state.plot_type = "Force Plot"
    if "shap_values" not in st.session_state:
        st.session_state.shap_values = None
    if "explainer" not in st.session_state:
        st.session_state.explainer = None
    if "clustering" not in st.session_state:
        st.session_state.clustering = None
    if "cutoff" not in st.session_state:
        st.session_state.cutoff = 0.5
    
    # Track data and model paths to detect changes
    if "current_data_path" not in st.session_state:
        st.session_state.current_data_path = None
    if "current_model_path" not in st.session_state:
        st.session_state.current_model_path = None
    
    # Check if data source or model has changed
    data_path_changed = st.session_state.current_data_path != str(data_path) if data_path else False
    model_path_changed = st.session_state.current_model_path != str(model_path) if model_path else False
    
    if data_path_changed or model_path_changed:
        # Only clear draw_matplotlib related session state caches (图像缓存)
        # Do NOT clear st.cache_data and st.cache_resource as they will naturally refresh with new parameters
        keys_to_remove = []
        for key in st.session_state.keys():
            if key.startswith(("bar-", "beeswarm", "force_plot_", "waterfall_plot_")):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del st.session_state[key]
        
        # Clear height and width caches used by draw_matplotlib
        if "height" in st.session_state:
            del st.session_state["height"]
        if "width" in st.session_state:
            del st.session_state["width"]
        
        # Reset session state variables related to SHAP analysis
        st.session_state.shap_values = None
        st.session_state.explainer = None
        st.session_state.clustering = None
        st.session_state.selected_row = 0
        st.session_state.selected_class = 0
        
        # Update current paths
        st.session_state.current_data_path = str(data_path) if data_path else None
        st.session_state.current_model_path = str(model_path) if model_path else None
        
        # Show info message
        if data_path_changed:
            st.info("检测到数据源变更，已清除图像缓存和重置分析状态")
        if model_path_changed:
            st.info("检测到模型变更，已清除图像缓存和重置分析状态")

    # Load data and model
    try:
        model = load_model(model_path)
        if type(model).__name__ == "GridSearchCV":
            model = model.best_estimator_
    except Exception as e:
        st.error(f"加载模型失败: {str(e)}")
        return

    is_classification = is_classification_model(model)

    try:
        X_train, X_test, y_train, y_test, mapping = load_data(data_path, is_classification=is_classification)
    except Exception as e:
        st.error(f"加载数据失败: {str(e)}")
        return

    # Get unique classes for classification models
    if is_classification:
        if hasattr(model, "classes_") and model.classes_ is not None:
            unique_classes = model.classes_
        else:
            try:
                sample_pred = model.predict_proba(X_train.iloc[[0]])
                unique_classes = np.arange(sample_pred.shape[1])
                st.warning("模型没有classes_属性，使用预测概率的顺序作为类别顺序")
            except Exception:
                unique_classes = sorted(y_train.unique())
                st.warning("无法从模型获取类别顺序，使用训练数据中的类别顺序")
        
        # Ensure unique_classes is not empty and convert to list for compatibility
        if unique_classes is None or len(unique_classes) == 0:
            st.error("无法获取类别信息，请检查数据和模型")
            return
        
        # Convert to list to ensure compatibility with range() and indexing
        unique_classes = list(unique_classes)
        
    else:
        unique_classes = None

    # Create explainer and compute SHAP values
    if st.session_state.explainer is None:
        try:
            st.session_state.explainer = create_explainer(model, X_train, is_classification)
        except Exception as e:
            st.error(f"创建SHAP解释器失败: {str(e)}")
            return

    # Compute clustering if not already done
    if st.session_state.clustering is None:
        try:
            st.session_state.clustering = compute_clustering(X_test, y_test)
        except Exception as e:
            st.warning(f"计算聚类失败: {str(e)}，将使用默认设置")
            st.session_state.clustering = None

    # Update SHAP values when class selection changes
    if is_classification:
        # Create a safe format function that handles different types of unique_classes
        def format_class_name(x):
            try:
                # First check if x is within range
                if x < 0 or x >= len(unique_classes):
                    return f"Class {x}"
                
                class_value = unique_classes[x]
                
                # Simple approach: try mapping by index first
                if x in mapping:
                    return str(mapping[x])
                
                # Try mapping by class value
                if class_value in mapping:
                    return str(mapping[class_value])
                
                # If all else fails, return string representation
                return str(class_value)
            except Exception as e:
                st.write(f"Debug: format_class_name error for x={x}: {e}")
                return f"Class {x}"
        
        try:
            # Create options list safely
            num_classes = len(unique_classes)
            options = list(range(num_classes))
            
            selected_class = st.selectbox(
                "选择要分析的目标类别",
                options,
                format_func=format_class_name,
                key="class_selector",
            )
        except Exception as e:
            st.error(f"创建类别选择器失败: {str(e)}")
            st.write(f"Debug: selectbox error: {e}")
            # Also show the traceback
            import traceback
            st.code(traceback.format_exc())
            
            # Fallback: try without format_func
            try:
                st.warning("尝试使用简化的类别选择器...")
                # Create simple options
                simple_options = [f"Class {i} ({unique_classes[i]})" for i in range(len(unique_classes))]
                selected_class = st.selectbox(
                    "选择要分析的目标类别 (简化版)",
                    range(len(unique_classes)),
                    format_func=lambda x: simple_options[x],
                    key="class_selector_fallback",
                )
            except Exception as e2:
                st.error(f"连简化版类别选择器也失败了: {str(e2)}")
                # Ultimate fallback - create a simple string-based selectbox
                try:
                    st.warning("尝试使用最简单的类别选择器...")
                    class_names = [f"Class {i}" for i in range(len(unique_classes))]
                    selected_class_name = st.selectbox(
                        "选择要分析的目标类别 (最简版)",
                        class_names,
                        key="class_selector_ultimate_fallback",
                    )
                    selected_class = class_names.index(selected_class_name)
                except Exception as e3:
                    st.error(f"所有类别选择器都失败了: {str(e3)}")
                    # Last resort - just use the first class
                    selected_class = 0
                    st.info("使用第一个类别作为默认选择")
        if st.session_state.selected_class != selected_class or st.session_state.shap_values is None:
            st.session_state.selected_class = selected_class
            try:
                st.session_state.shap_values = compute_shap_values(st.session_state.explainer, X_test, selected_class)
            except Exception as e:
                st.error(f"计算SHAP值失败: {str(e)}")
                return
    else:
        if st.session_state.shap_values is None:
            try:
                st.session_state.shap_values = compute_shap_values(st.session_state.explainer, X_test)
            except Exception as e:
                st.error(f"计算SHAP值失败: {str(e)}")
                return

    # Create a DataFrame for preview
    try:
        preview_df = pd.concat([X_test, y_test], axis=1)
    except Exception as e:
        st.error(f"创建预览数据失败: {str(e)}")
        st.write(f"Debug: X_test shape: {X_test.shape if hasattr(X_test, 'shape') else 'N/A'}")
        st.write(f"Debug: y_test shape: {y_test.shape if hasattr(y_test, 'shape') else 'N/A'}")
        return

    st.subheader("Bar 分析")

    # Add cutoff number input in main interface
    st.subheader("聚类设置")
    cutoff = st.number_input(
        "聚类阈值",
        min_value=0.0,
        max_value=10.0,
        value=st.session_state.cutoff,
        step=0.1,
        help="调整聚类阈值，值越大聚类越少",
    )
    if cutoff != st.session_state.cutoff:
        st.session_state.cutoff = cutoff

    if st.session_state.shap_values is not None:
        try:
            draw_matplotlib(
                shap.plots.bar(
                    st.session_state.shap_values,
                    clustering=st.session_state.clustering,
                    clustering_cutoff=st.session_state.cutoff,
                ),
                height=300,
                key=f"bar-{str(st.session_state.selected_class)}-cutoff{cutoff}",
            )
        except Exception as e:
            st.error(f"生成Bar图失败: {str(e)}")
            st.warning("可能是因为SHAP值格式不兼容或聚类参数设置问题")

    with st.expander("Bar 图展示的是 特征对模型预测影响的平均绝对贡献值"):
        st.markdown(BAR_PLOT_INFO)

    st.subheader("Beeswarm 分析")
    if st.session_state.shap_values is not None:
        try:
            draw_matplotlib(
                shap.plots.beeswarm(st.session_state.shap_values),
                height=300,
                key="beeswarm" + str(st.session_state.selected_class),
            )
        except Exception as e:
            st.error(f"生成Beeswarm图失败: {str(e)}")
            st.warning("可能是因为SHAP值格式不兼容")

    with st.expander("Beeswarm 图将所有样本的 SHAP 值集中展示在一张图上"):
        st.markdown(BEESWARM_PLOT_INFO)

    st.subheader("比较Bar和Beeswarm")
    with st.expander("Bar没有方向，Beeswarm有方向"):
        st.markdown(BAR_VS_BEESWARM_INFO)

    st.subheader("单个样本分析")
    st.write("选择要分析的数据行:")

    # Display dataframe with row selection
    event = st.dataframe(preview_df, key="preview_df", selection_mode="single-row", on_select="rerun")

    # Add plot type selection
    plot_type = st.radio("选择图表类型", ["Force Plot", "Waterfall Plot"], horizontal=True)
    if st.session_state.plot_type != plot_type:
        st.session_state.plot_type = plot_type

    # Get selected row index if any
    if event and event["selection"]["rows"]:
        selected_row = event["selection"]["rows"][0]
        if st.session_state.selected_row != selected_row:
            st.session_state.selected_row = selected_row

    # Display selected plot type
    st.subheader(plot_type)

    # Generate a unique key for the plot
    plot_key = (
        f"{plot_type.lower().replace(' ', '_')}_{st.session_state.selected_row}_{st.session_state.selected_class}"
    )

    if st.session_state.shap_values is not None:
        if plot_type == "Force Plot":
            try:
                draw_matplotlib(
                    shap.plots.force(
                        st.session_state.shap_values[st.session_state.selected_row],
                    ),
                    key=plot_key,
                )
            except Exception as e:
                st.error(f"生成Force Plot失败: {str(e)}")
                st.warning("可能是因为SHAP值格式不兼容或选择的行索引超出范围")
            
            with st.expander(
                "Force Plot 是针对 单个样本，告诉你每个特征到底是 **拉高** 预测结果，还是 **拉低** 预测结果"
            ):
                st.markdown(FORCE_PLOT_INFO)
        else:
            try:
                plt.clf()  # Clear the figure to prevent overlapping
                draw_matplotlib(
                    shap.plots.waterfall(
                        st.session_state.shap_values[st.session_state.selected_row],
                    ),
                    key=plot_key,
                )
            except Exception as e:
                st.error(f"生成Waterfall Plot失败: {str(e)}")
                st.warning("可能是因为SHAP值格式不兼容或选择的行索引超出范围")
            
            with st.expander("Waterfall Plot 是针对 单个样本，按特征贡献从大到小排序"):
                st.markdown(WATERFALL_PLOT_INFO)
