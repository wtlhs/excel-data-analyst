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

def generate_html_report(dataframes, relations, risks, business, advanced, output_dir):
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
    insights_html = generate_insights_html(risks, business, dataframes, advanced)
    
    # 生成业务领域卡片
    domain_cards_html = generate_domain_cards_html(business)
    
    # 生成预警卡片
    alerts_html = generate_alerts_html(risks, business)
    
    # 生成高级分析卡片
    advanced_cards_html = generate_advanced_cards_html(advanced)
    
    # 生成数据表行
    table_rows_html = generate_table_rows_html(dataframes)
    
    # 生成关联图
    relation_nodes_html = generate_relation_nodes_html(relations)
    
    # 生成指标内容
    metrics_content_html = generate_metrics_content_html(dataframes)
    
    # 生成图表数据
    chart_labels, chart_data = generate_chart_data(advanced)
    
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
    html = html.replace('{{advanced_cards}}', advanced_cards_html)
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

def generate_insights_html(risks, business, dataframes, advanced=None):
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
    
    # 高级分析洞察
    if advanced:
        dims = advanced.get("dimensions", {})
        
        # 时间序列
        if "time_series" in dims:
            trends = dims["time_series"].get("trends", {})
            for key, trend in trends.items():
                if trend.get("growth_rate"):
                    insights.append(f"{key}: 增长率 {trend['growth_rate']:.1f}%")
        
        # 相关性
        if "correlation" in dims:
            corr = dims["correlation"].get("strong_correlations", [])
            if corr:
                insights.append(f"发现 {len(corr)} 对强相关变量")
        
        # RFM
        if "stratification" in dims:
            rfm = dims["stratification"].get("rfm", {})
            for table, data in rfm.items():
                if data.get("top_segment"):
                    insights.append(f"主要客户群体: {data['top_segment']}")
    
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

def generate_advanced_cards_html(advanced):
    """生成高级分析卡片 HTML"""
    if not advanced or not advanced.get("dimensions"):
        return '<p style="color: var(--text-secondary); text-align: center;">暂无高级分析数据</p>'
    
    dims = advanced.get("dimensions", {})
    html = ""
    
    # 时间序列分析
    if "time_series" in dims:
        trends = dims["time_series"].get("trends", {})
        if trends:
            html += f'''
            <div class="domain-card">
                <div class="domain-header">
                    <div class="domain-icon" style="background: linear-gradient(135deg, #8b5cf6, #6366f1);">📈</div>
                    <div class="domain-title">时间序列分析</div>
                </div>
                <ul class="insight-list">
            '''
            for key, trend in list(trends.items())[:3]:
                direction = "↗️" if trend.get("trend_direction") == "up" else "↘️"
                growth = trend.get("growth_rate", 0)
                html += f'<li>{key.split(".")[-1]}: {direction} {growth:+.1f}%</li>'
            html += '</ul></div>'
    
    # 相关性分析
    if "correlation" in dims:
        corr = dims["correlation"].get("strong_correlations", [])
        if corr:
            html += f'''
            <div class="domain-card">
                <div class="domain-header">
                    <div class="domain-icon" style="background: linear-gradient(135deg, #ec4899, #f43f5e);">🔗</div>
                    <div class="domain-title">相关性分析</div>
                </div>
                <ul class="insight-list">
            '''
            for c in corr[:3]:
                html += f"<li>{c['var1']} ↔ {c['var2']}: {c['correlation']:.2f}</li>"
            html += f'<li>共发现 <strong>{len(corr)}</strong> 对强相关变量</li>'
            html += '</ul></div>'
    
    # RFM客户分层
    if "stratification" in dims:
        rfm = dims["stratification"].get("rfm", {})
        if rfm:
            html += f'''
            <div class="domain-card">
                <div class="domain-header">
                    <div class="domain-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706);">👥</div>
                    <div class="domain-title">RFM客户分层</div>
                </div>
                <ul class="insight-list">
            '''
            for table, data in list(rfm.items())[:2]:
                segments = data.get("segments", {})
                for seg, count in list(segments.items())[:3]:
                    html += f'<li>{seg}: {count}人</li>'
            html += '</ul></div>'
    
    # 预测分析
    if "forecast" in dims:
        fc = dims["forecast"].get("simple_ma", {})
        if fc:
            html += f'''
            <div class="domain-card">
                <div class="domain-header">
                    <div class="domain-icon" style="background: linear-gradient(135deg, #10b981, #059669);">🔮</div>
                    <div class="domain-title">趋势预测</div>
                </div>
                <ul class="insight-list">
            '''
            for key, data in list(fc.items())[:3]:
                signal = data.get("signal", "持有")
                signal_icon = "📈" if signal == "买入" else ("📉" if signal == "卖出" else "➡️")
                html += f'<li>{key.split(".")[-1]}: {signal_icon} {signal}</li>'
            html += '</ul></div>'
    
    # 异常深度分析
    if "anomaly_deep" in dims:
        outliers = dims["anomaly_deep"].get("outliers", {})
        if outliers:
            html += f'''
            <div class="domain-card">
                <div class="domain-header">
                    <div class="domain-icon" style="background: linear-gradient(135deg, #ef4444, #dc2626);">⚠️</div>
                    <div class="domain-title">异常深度分析</div>
                </div>
                <ul class="insight-list">
            '''
            for key, data in list(outliers.items())[:3]:
                html += f"<li>{key}: {data['total_count']}个异常值</li>"
            html += '</ul></div>'
    
    return html if html else '<p style="color: var(--text-secondary); text-align: center;">暂无高级分析数据</p>'

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

def generate_chart_data(advanced=None, business=None):
    """生成图表数据"""
    labels = []
    data = []
    
    # 优先从高级分析获取数据
    if advanced:
        dims = advanced.get("dimensions", {})
        
        # 时间序列数据
        if "time_series" in dims:
            trends = dims["time_series"].get("trends", {})
            for key, value in trends.items():
                if value.get("periods"):
                    labels = value.get("periods", [])
                    data = value.get("values", [])
                    break
        
        # 如果没有时间序列，尝试RFM
        if not labels and "stratification" in dims:
            rfm = dims["stratification"].get("rfm", {})
            for table, data_rfm in rfm.items():
                segments = data_rfm.get("segments", {})
                if segments:
                    labels = list(segments.keys())
                    data = list(segments.values())
                    break
    
    # 从业务分析获取数据
    if not labels and business:
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
    parser.add_argument('--advanced', default='.cache/advanced_analysis.json', help='高级分析文件')
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
    
    advanced = {}
    if Path(args.advanced).exists():
        with open(args.advanced, 'r', encoding='utf-8') as f:
            advanced = json.load(f)
    
    print("Generating HTML report...\n")
    
    report_file = generate_html_report(dataframes, relations, risks, business, advanced, args.output)
    
    print(f"✓ HTML report saved to {report_file}")

if __name__ == '__main__':
    main()
