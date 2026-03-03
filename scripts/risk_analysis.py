#!/usr/bin/env python3
"""
风险预警分析器
异常检测和风险预警
"""

import argparse
import json
import pickle
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

def detect_anomalies_zscore(series, threshold=3):
    """Z-Score 异常检测"""
    mean = series.mean()
    std = series.std()
    if std == 0:
        return pd.Series([False] * len(series), index=series.index)
    z_scores = np.abs((series - mean) / std)
    return z_scores > threshold

def detect_anomalies_iqr(series, multiplier=1.5):
    """IQR 四分位距异常检测"""
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - multiplier * IQR
    upper = Q3 + multiplier * IQR
    return (series < lower) | (series > upper)

def analyze_risks(dataframes, relations, config=None):
    """综合风险分析"""
    risks = {
        "summary": {
            "total_risks": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0
        },
        "details": []
    }
    
    for name, df in dataframes.items():
        # 数值列风险检测
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) == 0:
                continue
            
            # Z-Score 异常
            zscore_anomalies = detect_anomalies_zscore(series)
            zscore_count = zscore_anomalies.sum()
            
            # IQR 异常
            iqr_anomalies = detect_anomalies_iqr(series)
            iqr_count = iqr_anomalies.sum()
            
            if zscore_count > 0 or iqr_count > 0:
                anomaly_ratio = max(zscore_count, iqr_count) / len(series)
                
                risk_level = "high" if anomaly_ratio > 0.1 else ("medium" if anomaly_ratio > 0.05 else "low")
                
                risk = {
                    "table": name,
                    "column": col,
                    "type": "numeric_anomaly",
                    "level": risk_level,
                    "zscore_anomalies": int(zscore_count),
                    "iqr_anomalies": int(iqr_count),
                    "anomaly_ratio": round(anomaly_ratio, 4),
                    "stats": {
                        "mean": float(series.mean()),
                        "std": float(series.std()),
                        "min": float(series.min()),
                        "max": float(series.max())
                    }
                }
                risks["details"].append(risk)
                risks["summary"]["total_risks"] += 1
                risks["summary"][f"{risk_level}_risk"] += 1
    
    # 数据完整性风险
    for name, df in dataframes.items():
        null_ratios = df.isnull().sum() / len(df)
        high_null_cols = null_ratios[null_ratios > 0.3]
        
        for col, ratio in high_null_cols.items():
            risk = {
                "table": name,
                "column": col,
                "type": "data_completeness",
                "level": "high" if ratio > 0.5 else "medium",
                "null_ratio": round(ratio, 4),
                "missing_count": int(df[col].isnull().sum())
            }
            risks["details"].append(risk)
            risks["summary"]["total_risks"] += 1
    
    return risks

def generate_alerts(risks):
    """生成预警信息"""
    alerts = []
    
    for risk in risks["details"]:
        if risk["level"] == "high":
            if risk["type"] == "numeric_anomaly":
                alerts.append(f"🔴 高风险: {risk['table']}.{risk['column']} 存在 {risk['zscore_anomalies']} 个异常值 ({risk['anomaly_ratio']:.1%})")
            elif risk["type"] == "data_completeness":
                alerts.append(f"🔴 高风险: {risk['table']}.{risk['column']} 缺失率 {risk['null_ratio']:.1%}")
        elif risk["level"] == "medium":
            if risk["type"] == "numeric_anomaly":
                alerts.append(f"🟡 中风险: {risk['table']}.{risk['column']} 存在 {risk['zscore_anomalies']} 个异常值")
            elif risk["type"] == "data_completeness":
                alerts.append(f"🟡 中风险: {risk['table']}.{risk['column']} 缺失率 {risk['null_ratio']:.1%}")
    
    return alerts

def main():
    parser = argparse.ArgumentParser(description='风险预警分析')
    parser.add_argument('--data', default='.cache/loaded_data.pkl', help='数据文件')
    parser.add_argument('--relations', default='.cache/relations.json', help='关联文件')
    parser.add_argument('--config', help='风险规则配置文件 (YAML)')
    parser.add_argument('--output', default='.cache/risk_analysis.json', help='输出路径')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.data, 'rb') as f:
        dataframes = pickle.load(f)
    
    relations = {}
    if Path(args.relations).exists():
        with open(args.relations, 'r', encoding='utf-8') as f:
            relations = json.load(f)
    
    print("Analyzing risks...\n")
    
    risks = analyze_risks(dataframes, relations, args.config)
    alerts = generate_alerts(risks)
    
    risks["alerts"] = alerts
    risks["analysis_time"] = datetime.now().isoformat()
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(risks, f, ensure_ascii=False, indent=2)
    
    # 打印预警
    print("=== Risk Alerts ===")
    for alert in alerts:
        print(alert)
    
    print(f"\n✓ Total risks: {risks['summary']['total_risks']}")
    print(f"  High: {risks['summary']['high_risk']}, Medium: {risks['summary']['medium_risk']}, Low: {risks['summary']['low_risk']}")
    print(f"✓ Saved to {args.output}")

if __name__ == '__main__':
    main()
