# Excel Data Analyst Skill

🦞 企业级 Excel 数据分析专家

## 核心能力

- **数据读取** - 批量读取多个 Excel 文件，支持 .xlsx/.xls/.csv
- **关联发现** - AI 自动识别表格间的关联字段和关系
- **联合分析** - 多表 JOIN、聚合、透视分析
- **风险预警** - 异常检测、阈值告警、趋势预警
- **数据洞察** - 模式发现、关联规则、聚类分析
- **业务领域分析** - 销售、库存、财务、客户专项分析
- **报告生成** - Markdown 报告 + 精美 HTML 交互式报告

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/excel-data-analyst.git
cd excel-data-analyst

# 2. 安装依赖
pip install pandas openpyxl numpy

# 3. 运行分析
python scripts/data_loader.py --dir /path/to/excel/files
python scripts/relation_discovery.py
python scripts/risk_analysis.py
python scripts/business_analysis.py
python scripts/report_generator.py --output report/
python scripts/html_report_generator.py --output report/
```

## 分析流程

```
Excel 文件 → 数据加载 → 关联发现 → 风险分析 → 业务分析 → 报告生成
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

## 业务领域分析

| 模块 | 功能 |
|------|------|
| 销售分析 | 销售趋势、Top客户、异常订单预警 |
| 库存分析 | 库存统计、低库存预警、周转分析 |
| 财务分析 | 盈利能力、利润率趋势、异常月份识别 |
| 客户分析 | 客户分层、地区分布、信用分析 |

## 文件结构

```
excel-data-analyst/
├── SKILL.md                    # Skill 主文件（OpenClaw 使用）
├── scripts/                    # Python 脚本
│   ├── data_loader.py          # 批量数据加载
│   ├── relation_discovery.py   # 表格关联发现
│   ├── risk_analysis.py        # 风险预警分析
│   ├── business_analysis.py    # 业务领域分析
│   ├── report_generator.py     # Markdown 报告生成
│   └── html_report_generator.py # HTML 报告生成
├── references/                 # 参考文档
│   ├── analysis_methods.md     # 分析方法详解
│   └── visualization_guide.md  # 可视化指南
└── assets/                     # 资源文件
    ├── report_template.md      # Markdown 模板
    ├── report_template.html    # HTML 模板
    └── risk_rules.yaml         # 风险规则配置
```

## 在 OpenClaw 中使用

将此目录复制到 OpenClaw skills 目录：

```bash
cp -r excel-data-analyst ~/.openclaw/skills/
```

## 依赖

- Python 3.10+
- pandas
- openpyxl
- numpy

## License

MIT License

---

🦞 Powered by OpenClaw
