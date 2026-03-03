#!/usr/bin/env python3
"""
分析报告生成器
生成多维度数据分析报告
"""

import argparse
import json
import pickle
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

def generate_executive_summary(risks, relations, dataframes, business=None):
    """生成执行摘要"""
    findings = []
    
    # 数据规模
    total_rows = sum(df.shape[0] for df in dataframes.values())
    total_cols = sum(df.shape[1] for df in dataframes.values())
    findings.append(f"分析了 {len(dataframes)} 个数据表，共 {total_rows:,} 行、{total_cols:,} 列数据")
    
    # 关联发现
    if relations.get('total_relations', 0) > 0:
        findings.append(f"发现 {relations['total_relations']} 个表格关联关系")
    
    # 风险预警
    if risks.get('summary', {}).get('total_risks', 0) > 0:
        high = risks['summary'].get('high_risk', 0)
        medium = risks['summary'].get('medium_risk', 0)
        findings.append(f"识别出 {high} 个高风险项、{medium} 个中风险项")
    
    # 业务洞察
    if business:
        for domain, data in business.get("domains", {}).items():
            if data.get("insights"):
                findings.extend(data["insights"][:2])
    
    return findings

def generate_data_overview(dataframes):
    """生成数据概览"""
    overview = []
    
    for name, df in dataframes.items():
        overview.append({
            "table": name,
            "rows": df.shape[0],
            "columns": df.shape[1],
            "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
            "text_columns": len(df.select_dtypes(include=['object']).columns),
            "date_columns": len(df.select_dtypes(include=['datetime']).columns),
            "null_cells": int(df.isnull().sum().sum()),
            "completeness": round(1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1]), 4)
        })
    
    return overview

def generate_key_metrics(dataframes):
    """生成关键指标"""
    metrics = {}
    
    for name, df in dataframes.items():
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        table_metrics = {}
        for col in numeric_cols[:5]:  # 只取前5个数值列
            series = df[col].dropna()
            if len(series) > 0:
                table_metrics[col] = {
                    "mean": float(series.mean()),
                    "median": float(series.median()),
                    "std": float(series.std()),
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "sum": float(series.sum())
                }
        
        metrics[name] = table_metrics
    
    return metrics

def generate_business_section(business):
    """生成业务分析部分"""
    section = "\n## 5. 业务领域分析\n\n"
    
    domain_names = {
        "sales": "销售分析",
        "inventory": "库存分析",
        "finance": "财务分析",
        "customer": "客户分析"
    }
    
    for domain, data in business.get("domains", {}).items():
        domain_name = domain_names.get(domain, domain)
        section += f"### {domain_name}\n\n"
        
        # 洞察
        if data.get("insights"):
            section += "**关键洞察：**\n\n"
            for insight in data["insights"]:
                section += f"- {insight}\n"
            section += "\n"
        
        # 预警
        alerts = data.get("alerts", [])
        if alerts:
            high_alerts = [a for a in alerts if a.get("level") == "high"]
            medium_alerts = [a for a in alerts if a.get("level") == "medium"]
            
            if high_alerts:
                section += f"**🔴 高风险预警 ({len(high_alerts)}条)：**\n\n"
                for alert in high_alerts[:5]:
                    section += f"- {alert.get('message', '未知风险')}\n"
                section += "\n"
            
            if medium_alerts:
                section += f"**🟡 中风险预警 ({len(medium_alerts)}条)：**\n\n"
                for alert in medium_alerts[:5]:
                    section += f"- {alert.get('message', '未知风险')}\n"
                section += "\n"
    
    return section

def generate_report(dataframes, relations, risks, business, output_dir):
    """生成完整报告"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成各部分
    summary = generate_executive_summary(risks, relations, dataframes, business)
    overview = generate_data_overview(dataframes)
    metrics = generate_key_metrics(dataframes)
    
    # 生成 Markdown 报告
    report = f"""# 数据分析报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 执行摘要

### 核心发现

"""
    
    for i, finding in enumerate(summary, 1):
        report += f"{i}. {finding}\n"
    
    # 风险提示
    if risks.get('alerts'):
        report += "\n### 关键风险提示\n\n"
        for alert in risks['alerts'][:5]:
            report += f"- {alert}\n"
    
    # 业务预警
    if business and business.get("all_alerts"):
        report += "\n### 业务预警\n\n"
        for alert in business["all_alerts"][:5]:
            level_icon = "🔴" if alert.get("level") == "high" else "🟡"
            report += f"- {level_icon} [{alert.get('domain', '')}] {alert.get('message', '')}\n"
    
    # 数据概览
    report += f"""

## 2. 数据概览

| 数据表 | 行数 | 列数 | 数值列 | 文本列 | 完整度 |
|--------|------|------|--------|--------|--------|
"""
    
    for item in overview:
        report += f"| {item['table']} | {item['rows']:,} | {item['columns']} | {item['numeric_columns']} | {item['text_columns']} | {item['completeness']:.1%} |\n"
    
    # 关联分析
    if relations.get('relations'):
        report += "\n## 3. 关联分析\n\n"
        report += "发现以下表格关联关系：\n\n"
        
        for rel in relations['relations'][:10]:
            report += f"- **{rel['table1']}.{rel['column1']}** ↔ **{rel['table2']}.{rel['column2']}**\n"
            report += f"  - 类型: {rel['relation_type']}\n"
            report += f"  - 重叠率: {rel['overlap_ratio']:.1%}\n"
    
    # 关键指标
    report += "\n## 4. 核心指标分析\n\n"
    
    for table_name, table_metrics in metrics.items():
        if table_metrics:
            report += f"### {table_name}\n\n"
            report += "| 指标 | 均值 | 中位数 | 标准差 | 最小值 | 最大值 |\n"
            report += "|------|------|--------|--------|--------|--------|\n"
            
            for col, stats in table_metrics.items():
                report += f"| {col} | {stats['mean']:.2f} | {stats['median']:.2f} | {stats['std']:.2f} | {stats['min']:.2f} | {stats['max']:.2f} |\n"
            report += "\n"
    
    # 风险预警
    if risks.get('details'):
        report += "## 6. 风险预警\n\n"
        
        high_risks = [r for r in risks['details'] if r['level'] == 'high']
        medium_risks = [r for r in risks['details'] if r['level'] == 'medium']
        
        if high_risks:
            report += "### 🔴 高风险项\n\n"
            for r in high_risks[:10]:
                report += f"- **{r['table']}.{r['column']}**: {r['type']}\n"
        
        if medium_risks:
            report += "\n### 🟡 中风险项\n\n"
            for r in medium_risks[:10]:
                report += f"- **{r['table']}.{r['column']}**: {r['type']}\n"
    
    # 业务领域分析
    if business:
        report += generate_business_section(business)
    
    # 建议
    report += """

## 8. 建议与行动

### 短期建议
1. 优先处理高风险预警项
2. 补充缺失数据
3. 验证异常数据

### 长期建议
1. 建立数据质量监控机制
2. 完善数据采集流程
3. 定期进行数据分析复盘

---

*本报告由 Excel Data Analyst Skill 自动生成*
"""
    
    # 保存报告
    report_file = output_path / "analysis_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 保存 JSON 数据
    json_data = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "overview": overview,
        "metrics": metrics,
        "relations": relations,
        "risks": risks,
        "business": business
    }
    
    json_file = output_path / "analysis_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return report_file

def main():
    parser = argparse.ArgumentParser(description='生成分析报告')
    parser.add_argument('--data', default='.cache/loaded_data.pkl', help='数据文件')
    parser.add_argument('--relations', default='.cache/relations.json', help='关联文件')
    parser.add_argument('--risks', default='.cache/risk_analysis.json', help='风险分析文件')
    parser.add_argument('--business', default='.cache/business_analysis.json', help='业务分析文件')
    parser.add_argument('--output', default='report', help='输出目录')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.data, 'rb') as f:
        dataframes = pickle.load(f)
    
    relations = {}
    if Path(args.relations).exists():
        with open(args.relations, 'r', encoding='utf-8') as f:
            relations = json.load(f)
    
    risks = {}
    if Path(args.risks).exists():
        with open(args.risks, 'r', encoding='utf-8') as f:
            risks = json.load(f)
    
    business = {}
    if Path(args.business).exists():
        with open(args.business, 'r', encoding='utf-8') as f:
            business = json.load(f)
    
    print("Generating report...\n")
    
    report_file = generate_report(dataframes, relations, risks, business, args.output)
    
    print(f"✓ Report saved to {report_file}")
    print(f"✓ JSON data saved to {args.output}/analysis_data.json")

if __name__ == '__main__':
    main()
