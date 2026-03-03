# Excel Data Analyst Skill

🦞 企业级 Excel 数据分析专家

## 核心能力

- **数据读取** - 批量读取多个 Excel 文件，支持 .xlsx/.xls/.csv，多编码支持
- **关联发现** - AI 自动识别表格间的关联字段和关系
- **联合分析** - 多表 JOIN、聚合、透视分析
- **风险预警** - 异常检测、阈值告警、趋势预警
- **数据洞察** - 模式发现、关联规则、聚类分析
- **业务领域分析** - 销售、库存、财务、客户专项分析
- **多维度深度分析** - 时间序列、相关性、RFM分层、预测分析
- **行业定制分析** - 跨境电商、海外仓物流专属分析
- **报告生成** - Markdown 报告 + 精美 HTML 交互式报告

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/wtlhs/excel-data-analyst.git
cd excel-data-analyst

# 2. 安装依赖
pip install pandas openpyxl numpy pyyaml

# 3. 运行分析
python scripts/data_loader.py --dir /path/to/excel/files
python scripts/relation_discovery.py
python scripts/risk_analysis.py
python scripts/business_analysis.py
python scripts/advanced_analysis.py
python scripts/yuexin_analysis.py    # 跨境电商/海外仓定制分析
python scripts/html_report_generator.py --output report/
```

## 分析模块

### 1. 基础分析
- `data_loader.py` - 批量数据加载
- `relation_discovery.py` - 表格关联发现

### 2. 风险分析
- `risk_analysis.py` - 异常检测、风险预警

### 3. 业务分析
- `business_analysis.py` - 销售/库存/财务/客户四大领域
- `yuexin_analysis.py` - 跨境电商/海外仓定制分析

### 4. 高级分析
- `advanced_analysis.py` - 时间序列、相关性、RFM、预测

### 5. 报告生成
- `report_generator.py` - Markdown 报告
- `html_report_generator.py` - HTML 交互式报告

## 行业定制分析

### 跨境电商/海外仓业务分析

支持以下业务场景：

| 业务场景 | 分析内容 |
|----------|----------|
| 业务趋势 | 入库/出库趋势、同比/环比增长 |
| 渠道分析 | Amazon、Temu、TikTok、Shopify、Wayfair 占比 |
| 面单来源 | 有面单 vs 无面单 发货占比 |
| 客户价值 | A/B/C 客户分层、收入贡献 |
| SKU分析 | 爆品、滞销品、周转率 |
| 时效分析 | 处理时效、妥投率 |
| 仓库分析 | 各仓库使用情况 |
| 财务分析 | 收入、成本、利润、利润率 |

### 业务背景配置

编辑 `assets/business_context.yaml` 自定义业务参数：

```yaml
company:
  name: "公司名称"
  type: "海外仓代理"

suppliers:
  logistics: "物流供应商"
  warehouse: "仓库供应商"

customers:
  platforms:
    - "Amazon"
    - "Temu"
    - "TikTok"
```

## 报告类型

### Markdown 报告
- 执行摘要
- 数据概览
- 关联分析
- 核心指标
- 风险预警
- 业务洞察
- 建议与行动

### HTML 交互式报告
- 🎨 深色科技风主题
- 📊 交互式图表（Chart.js）
- ✨ 动态数字动画
- 📱 响应式设计
- 🔴🟡 风险等级可视化
- 📈 多维度深度分析卡片

## 文件结构

```
excel-data-analyst/
├── SKILL.md                         # Skill 主文件
├── scripts/
│   ├── data_loader.py              # 数据加载
│   ├── relation_discovery.py        # 关联发现
│   ├── risk_analysis.py            # 风险预警
│   ├── business_analysis.py         # 业务分析
│   ├── advanced_analysis.py         # 高级分析
│   ├── yuexin_analysis.py          # 跨境电商定制分析
│   ├── report_generator.py          # Markdown报告
│   └── html_report_generator.py    # HTML报告
├── references/
│   ├── analysis_methods.md
│   └── visualization_guide.md
└── assets/
    ├── business_context.yaml       # 业务背景配置
    ├── report_template.html        # HTML模板
    └── risk_rules.yaml             # 风险规则
```

## 在 OpenClaw 中使用

```bash
cp -r excel-data-analyst ~/.openclaw/skills/
```

## 依赖

- Python 3.10+
- pandas
- openpyxl
- numpy
- pyyaml

## License

MIT License

---

🦞 Powered by OpenClaw
