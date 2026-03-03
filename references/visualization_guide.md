# 数据可视化最佳实践

## 图表选择指南

### 按数据类型选择

| 数据关系 | 推荐图表 | 适用场景 |
|---------|---------|---------|
| 比较 | 条形图、柱状图 | 不同类别数值对比 |
| 趋势 | 折线图、面积图 | 时间序列变化 |
| 占比 | 饼图、环形图、树图 | 部分与整体关系 |
| 分布 | 直方图、箱线图 | 数据分布特征 |
| 相关 | 散点图、气泡图 | 两变量关系 |
| 排名 | 条形图、子弹图 | 排名和目标对比 |

### 按分析目的选择

| 分析目的 | 推荐图表 |
|---------|---------|
| 展示变化趋势 | 折线图 |
| 比较不同类别 | 柱状图 |
| 显示占比关系 | 环形图 |
| 发现异常值 | 箱线图 |
| 分析相关性 | 散点图 |
| 多维对比 | 雷达图 |

## Python 可视化代码示例

### 基础设置
```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
```

### 趋势图
```python
def plot_trend(df, date_col, value_col, title="趋势分析"):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df[date_col], df[value_col], marker='o', linewidth=2)
    ax.set_title(title, fontsize=14)
    ax.set_xlabel(date_col)
    ax.set_ylabel(value_col)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig
```

### 对比图
```python
def plot_comparison(df, category_col, value_col, title="对比分析"):
    fig, ax = plt.subplots(figsize=(10, 6))
    df_sorted = df.sort_values(value_col, ascending=True)
    ax.barh(df_sorted[category_col], df_sorted[value_col])
    ax.set_title(title, fontsize=14)
    ax.set_xlabel(value_col)
    plt.tight_layout()
    return fig
```

### 分布图
```python
def plot_distribution(df, value_col, title="分布分析"):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 直方图
    axes[0].hist(df[value_col], bins=30, edgecolor='black')
    axes[0].set_title('直方图')
    axes[0].set_xlabel(value_col)
    
    # 箱线图
    axes[1].boxplot(df[value_col].dropna(), vert=True)
    axes[1].set_title('箱线图')
    axes[1].set_ylabel(value_col)
    
    plt.suptitle(title, fontsize=14)
    plt.tight_layout()
    return fig
```

### 热力图
```python
def plot_correlation_heatmap(df, title="相关性热力图"):
    numeric_df = df.select_dtypes(include=['number'])
    corr = numeric_df.corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='coolwarm', center=0, ax=ax)
    ax.set_title(title, fontsize=14)
    plt.tight_layout()
    return fig
```

## 配色方案

### 商业报告配色
```python
# 专业配色
colors = {
    'primary': '#2E86AB',    # 主色
    'secondary': '#A23B72',  # 辅色
    'success': '#28A745',    # 成功/正向
    'warning': '#FFC107',    # 警告
    'danger': '#DC3545',     # 危险/负向
    'neutral': '#6C757D'     # 中性
}

# 渐变色
gradient = ['#E8F4F8', '#B8D4E3', '#7FB3D5', '#3498DB', '#2980B9']
```

### 数据可视化配色
```python
# 分类配色
categorical = ['#4E79A7', '#F28E2B', '#E15759', '#76B7B2', 
               '#59A14F', '#EDC948', '#B07AA1', '#FF9DA7']

# 连续配色
sequential = 'Blues'  # 蓝色渐变
diverging = 'RdBu'    # 红蓝双色
```

## 图表导出

### 保存为文件
```python
def save_figure(fig, filename, dpi=150):
    """保存图表到文件"""
    fig.savefig(filename, dpi=dpi, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close(fig)
```

### 嵌入报告
```python
def figure_to_base64(fig):
    """将图表转换为 base64 用于嵌入 HTML"""
    import io
    import base64
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"
```
