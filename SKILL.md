---
name: excel-data-analyst
description: 企业级 Excel 数据分析专家。用于：(1) 读取和分析大量 Excel 表格数据 (2) 自动发现表格间的关联关系 (3) 多表联合数据分析 (4) 风险预警和异常检测 (5) 数据洞察和挖掘 (6) 业务领域专项分析 (7) 生成多维度分析报告。当用户需要分析 Excel 数据、做数据挖掘、发现数据关联、生成分析报告时使用此技能。
---

# Excel 数据分析专家

## 核心能力

1. **数据读取** - 批量读取多个 Excel 文件，支持 .xlsx/.xls/.csv
2. **关联发现** - AI 自动识别表格间的关联字段和关系
3. **联合分析** - 多表 JOIN、聚合、透视分析
4. **风险预警** - 异常检测、阈值告警、趋势预警
5. **数据洞察** - 模式发现、关联规则、聚类分析
6. **业务领域分析** - 销售、库存、财务、客户专项分析
7. **报告生成** - 多维度分析报告，支持图表和可视化

## 分析流程

### 1. 数据加载与探索

```bash
python scripts/data_loader.py --dir <数据目录> --output .cache/data_summary.json
```

### 2. 表格关联发现

```bash
python scripts/relation_discovery.py --input .cache/loaded_data.pkl --output .cache/relations.json
```

### 3. 风险预警分析

```bash
python scripts/risk_analysis.py --data .cache/loaded_data.pkl --output .cache/risk_analysis.json
```

### 4. 业务领域分析

```bash
python scripts/business_analysis.py --data .cache/loaded_data.pkl --output .cache/business_analysis.json
```

### 5. 报告生成

```bash
# Markdown 报告
python scripts/report_generator.py --data .cache/loaded_data.pkl --output report/

# HTML 交互式报告（精美可视化）
python scripts/html_report_generator.py --data .cache/loaded_data.pkl --output report/
```

**HTML 报告特点：**
- 🎨 深色科技风主题
- 📊 交互式图表（Chart.js）
- ✨ 动态数字动画
- 📱 响应式设计
- 🏷️ Tab 切换展示
- 🔴🟡 风险等级可视化

## 业务领域分析

### 销售分析 (Sales)

自动识别销售相关表格，分析：
- **销售趋势** - 按时间维度的销售额变化
- **客户分析** - Top 客户、客户分布
- **状态分布** - 订单状态统计
- **异常订单** - 高额订单预警

### 库存分析 (Inventory)

自动识别库存相关表格，分析：
- **库存统计** - 总量、均值、零库存数量
- **库存预警** - 低于安全库存的产品
- **周转分析** - 库存周转率

### 财务分析 (Finance)

自动识别财务相关表格，分析：
- **盈利能力** - 收入、成本、利润率
- **月度趋势** - 财务指标变化
- **亏损预警** - 负利润期间识别

### 客户分析 (Customer)

自动识别客户相关表格，分析：
- **客户分层** - A/B/C 级客户分布
- **地区分布** - 客户地理分布
- **信用分析** - 信用额度统计

## 一键分析脚本

```bash
# 完整分析流程
cd /root/.openclaw/workspace/skills/excel-data-analyst

# 1. 加载数据
python scripts/data_loader.py --dir /path/to/excel/files

# 2. 发现关联
python scripts/relation_discovery.py

# 3. 风险分析
python scripts/risk_analysis.py

# 4. 业务分析
python scripts/business_analysis.py

# 5. 生成报告
python scripts/report_generator.py --output report/
```

## 报告结构

```markdown
# 数据分析报告

## 1. 执行摘要
- 核心发现（3-5 条）
- 关键风险提示
- 建议行动

## 2. 数据概览
- 数据源说明
- 数据质量评估
- 分析范围

## 3. 关联分析
- 表格关系图
- 关键关联字段

## 4. 业务领域分析
- 销售分析
- 库存分析
- 财务分析
- 客户分析

## 5. 风险预警
- 风险等级分类
- 预警指标列表

## 6. 深度洞察
- 模式发现
- 业务建议

## 7. 建议与行动
- 短期建议
- 长期建议
- 监控指标
```

## Resources

### scripts/
- `data_loader.py` - 批量数据加载器
- `relation_discovery.py` - 表格关联发现
- `risk_analysis.py` - 风险预警分析
- `business_analysis.py` - 业务领域分析（销售/库存/财务/客户）
- `report_generator.py` - Markdown 报告生成器
- `html_report_generator.py` - HTML 交互式报告生成器

### references/
- `analysis_methods.md` - 详细分析方法说明
- `visualization_guide.md` - 可视化最佳实践

### assets/
- `report_template.md` - 报告模板
- `risk_rules.yaml` - 风险规则配置示例
