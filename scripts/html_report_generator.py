#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 报告生成器
生成精美的交互式 HTML 报告
"""

# Windows 兼容性：设置 UTF-8 编码
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import pickle
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

def generate_html_report(dataframes, relations, risks, business, output_dir):
    """生成 HTML 报告"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 读取模板
    template_path = Path(__file__).parent.parent / "assets" / "report_template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # 计算统计数据
    total_rows = sum(df.shape[0] for df in dataframes.values())
    total_cols = sum(df.shape[1] for df in dataframes.values())
    total_nulls = sum(df.isnull().sum().sum() for df in dataframes.values())
    data_quality = 1 - (total_nulls / (total_rows * total_cols))
    
    # 生成核心发现
    insights_html = generate_insights_html(risks, business, dataframes)
    
    # 生成业务领域卡片
    domain_cards_html = generate_domain_cards_html(business)
    
    # 生成预警卡片
    alerts_html = generate_alerts_html(risks, business)
    
    # 生成数据表行
    table_rows_html = generate_table_rows_html(dataframes)
    
    # 生成关联图
    relation_nodes_html = generate_relation_nodes_html(relations)
    
    # 生成指标内容
    metrics_content_html = generate_metrics_content_html(dataframes)
    
    # 生成图表数据
    chart_labels, chart_data = generate_chart_data(business)
    
    # 替换模板变量
    html = template.replace('{{generated_at}}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    html = html.replace('{{total_tables}}', str(len(dataframes)))
    html = html.replace('{{total_rows}}', f"{total_rows:,}")
    html = html.replace('{{total_relations}}', str(relations.get('total_relations', 0)))
    html = html.replace('{{high_risks}}', str(count_high_risks(risks, business)))
    html = html.replace('{{data_quality}}', f"{data_quality:.1%}")
    html = html.replace('{{insights}}', insights_html)
    html = html.replace('{{domain_cards}}', domain_cards_html)
    html = html.replace('{{alerts}}', alerts_html)
    html = html.replace('{{table_rows}}', table_rows_html)
    html = html.replace('{{relation_nodes}}', relation_nodes_html)
    html = html.replace('{{metrics_content}}', metrics_content_html)
    html = html.replace('{{chart_labels}}', json.dumps(chart_labels))
    html = html.replace('{{chart_data}}', json.dumps(chart_data))
    
    # 保存报告
    report_file = output_path / "report.html"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return report_file

def generate_insights_html(risks, business, dataframes):
    """生成核心发现 HTML"""
    insights = []
    
    # 数据规模
    total_rows = sum(df.shape[0] for df in dataframes.values())
    insights.append(f"分析 {len(dataframes)} 个数据表，共 {total_rows:,} 行数据")
    
    # 业务洞察
    if business:
        for domain, data in business.get("domains", {}).items():
            for insight in data.get("insights", [])[:2]:
                insights.append(insight)
    
    html = '<ul class="insight-list">\n'
    for insight in insights[:8]:
        html += f'<li><span style="color: var(--primary);">→</span> {insight}</li>\n'
    html += '</ul>'
    
    return html

def generate_domain_cards_html(business):
    """生成业务领域卡片 HTML"""
    domain_info = {
        "sales": {"icon": "📈", "name": "销售分析"},
        "inventory": {"icon": "📦", "name": "库存分析"},
        "finance": {"icon": "💰", "name": "财务分析"},
        "customer": {"icon": "👥", "name": "客户分析"}
    }
    
    html = ""
    for domain, data in business.get("domains", {}).items():
        info = domain_info.get(domain, {"icon": "📊", "name": domain})
        
        html += f'''
        <div class="domain-card">
            <div class="domain-header">
                <div class="domain-icon {domain}">{info["icon"]}</div>
                <div class="domain-title">{info["name"]}</div>
            </div>
            <ul class="insight-list">
        '''
        
        for insight in data.get("insights", [])[:4]:
            html += f'<li>{insight}</li>\n'
        
        # 添加预警数量
        alerts = data.get("alerts", [])
        if alerts:
            high_count = len([a for a in alerts if a.get("level") == "high"])
            medium_count = len([a for a in alerts if a.get("level") == "medium"])
            if high_count > 0:
                html += f'<li><span class="tag high">{high_count} 个高风险</span></li>\n'
            if medium_count > 0:
                html += f'<li><span class="tag medium">{medium_count} 个中风险</span></li>\n'
        
        html += '''
            </ul>
        </div>
        '''
    
    return html

def generate_alerts_html(risks, business):
    """生成预警卡片 HTML"""
    alerts = []
    
    # 从业务分析中获取预警
    if business:
        for alert in business.get("all_alerts", [])[:10]:
            alerts.append(alert)
    
    # 从风险分析中获取
    if risks:
        for risk in risks.get("details", [])[:5]:
            alerts.append({
                "level": risk.get("level", "low"),
                "domain": risk.get("table", ""),
                "message": f"{risk.get('table', '')}.{risk.get('column', '')}: {risk.get('type', '')}"
            })
    
    html = ""
    for alert in alerts[:12]:
        level = alert.get("level", "medium")
        icon = "🔴" if level == "high" else ("🟡" if level == "medium" else "🟢")
        
        html += f'''
        <div class="alert-card {level}">
            <div class="alert-icon">{icon}</div>
            <div class="alert-content">
                <div class="alert-title">[{alert.get('domain', '').upper()}]</div>
                <div class="alert-message">{alert.get('message', '')}</div>
            </div>
        </div>
        '''
    
    if not alerts:
        html = '<p style="color: var(--text-secondary); text-align: center;">暂无风险预警</p>'
    
    return html

def generate_table_rows_html(dataframes):
    """生成数据表行 HTML"""
    html = ""
    for name, df in dataframes.items():
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        completeness = 1 - (null_cells / total_cells) if total_cells > 0 else 1
        
        html += f'''
        <tr>
            <td><strong>{name}</strong></td>
            <td>{df.shape[0]:,}</td>
            <td>{df.shape[1]}</td>
            <td>{len(df.select_dtypes(include=[np.number]).columns)}</td>
            <td>
                <div class="progress-bar">
                    <div class="progress" style="width: {completeness:.1%}"></div>
                </div>
                {completeness:.1%}
            </td>
        </tr>
        '''
    
    return html

def generate_relation_nodes_html(relations):
    """生成关联图 HTML"""
    html = ""
    
    for rel in relations.get("relations", [])[:8]:
        html += f'''
        <div class="relation-node">
            <div class="table-name">{rel["table1"]}</div>
            <div class="column-name">{rel["column1"]}</div>
        </div>
        <div class="relation-arrow">→</div>
        <div class="relation-node">
            <div class="table-name">{rel["table2"]}</div>
            <div class="column-name">{rel["column2"]}</div>
        </div>
        '''
    
    if not relations.get("relations"):
        html = '<p style="color: var(--text-secondary); text-align: center;">暂无关联关系</p>'
    
    return html

def generate_metrics_content_html(dataframes):
    """生成指标内容 HTML"""
    html = ""
    
    for name, df in dataframes.items():
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:3]
        
        if len(numeric_cols) > 0:
            html += f'<h4 style="color: var(--primary); margin: 1rem 0 0.5rem;">{name}</h4>\n'
            html += '<table class="data-table"><thead><tr><th>指标</th><th>均值</th><th>中位数</th><th>最小值</th><th>最大值</th></tr></thead><tbody>\n'
            
            for col in numeric_cols:
                series = df[col].dropna()
                if len(series) > 0:
                    html += f'''
                    <tr>
                        <td>{col}</td>
                        <td>{series.mean():,.2f}</td>
                        <td>{series.median():,.2f}</td>
                        <td>{series.min():,.2f}</td>
                        <td>{series.max():,.2f}</td>
                    </tr>
                    '''
            
            html += '</tbody></table>\n'
    
    return html

def generate_chart_data(business):
    """生成图表数据"""
    labels = []
    data = []
    
    # 从销售趋势获取数据
    if business:
        sales_data = business.get("domains", {}).get("sales", {}).get("metrics", {})
        for key, value in sales_data.items():
            if "trend" in key and isinstance(value, dict):
                labels = value.get("periods", [])
                data = value.get("sums", [])
                break
    
    # 如果没有数据，使用默认
    if not labels:
        labels = ["1月", "2月", "3月", "4月", "5月"]
        data = [0] * 5
    
    return labels, data

def count_high_risks(risks, business):
    """计算高风险数量"""
    count = 0
    
    if risks:
        count += risks.get("summary", {}).get("high_risk", 0)
    
    if business:
        for alert in business.get("all_alerts", []):
            if alert.get("level") == "high":
                count += 1
    
    return count

def main():
    parser = argparse.ArgumentParser(description='生成 HTML 报告')
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
    
    print("Generating HTML report...\n")
    
    report_file = generate_html_report(dataframes, relations, risks, business, args.output)
    
    print(f"✓ HTML report saved to {report_file}")

if __name__ == '__main__':
    main()
