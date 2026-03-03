#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务领域分析器
针对不同业务场景的专项分析
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

class BusinessAnalyzer:
    """业务分析器基类"""
    
    def __init__(self, dataframes, relations):
        self.dataframes = dataframes
        self.relations = relations
    
    def analyze(self):
        raise NotImplementedError

class SalesAnalyzer(BusinessAnalyzer):
    """销售业务分析"""
    
    def analyze(self):
        results = {
            "domain": "sales",
            "metrics": {},
            "insights": [],
            "alerts": []
        }
        
        # 查找销售相关的表
        sales_keywords = ['order', '订单', 'sales', '销售', 'transaction', '交易']
        sales_tables = self._find_tables_by_keywords(sales_keywords)
        
        if not sales_tables:
            return results
        
        for table_name in sales_tables:
            df = self.dataframes[table_name]
            
            # 1. 销售趋势分析
            date_cols = df.select_dtypes(include=['datetime64', 'object']).columns
            amount_cols = self._find_amount_columns(df)
            
            if len(date_cols) > 0 and len(amount_cols) > 0:
                trend = self._analyze_trend(df, date_cols[0], amount_cols[0])
                results["metrics"][f"{table_name}_trend"] = trend
            
            # 2. 客户分析
            customer_cols = self._find_customer_columns(df)
            if customer_cols and amount_cols:
                customer_analysis = self._analyze_by_dimension(df, customer_cols[0], amount_cols[0])
                results["metrics"][f"{table_name}_by_customer"] = customer_analysis
            
            # 3. 状态分布
            status_cols = self._find_status_columns(df)
            if status_cols:
                status_dist = df[status_cols[0]].value_counts().to_dict()
                results["metrics"][f"{table_name}_status"] = status_dist
            
            # 4. 异常订单检测
            if amount_cols:
                anomalies = self._detect_sales_anomalies(df, amount_cols[0])
                if anomalies:
                    results["alerts"].extend(anomalies)
        
        # 生成洞察
        results["insights"] = self._generate_sales_insights(results["metrics"])
        
        return results
    
    def _find_tables_by_keywords(self, keywords):
        """根据关键词查找表"""
        found = []
        for name in self.dataframes.keys():
            name_lower = name.lower()
            if any(k in name_lower for k in keywords):
                found.append(name)
        return found
    
    def _find_amount_columns(self, df):
        """查找金额列"""
        keywords = ['amount', '金额', 'total', '总额', 'price', '价格', 'revenue', '收入']
        cols = []
        for col in df.columns:
            col_lower = col.lower()
            if any(k in col_lower for k in keywords):
                cols.append(col)
        # 如果没找到，返回第一个数值列
        if not cols:
            numeric = df.select_dtypes(include=[np.number]).columns
            if len(numeric) > 0:
                cols = [numeric[0]]
        return cols
    
    def _find_customer_columns(self, df):
        """查找客户列"""
        keywords = ['customer', '客户', 'client', 'user', '用户', 'buyer', '买家']
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return [col]
        return []
    
    def _find_status_columns(self, df):
        """查找状态列"""
        keywords = ['status', '状态', 'state', 'type', '类型']
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return [col]
        return []
    
    def _analyze_trend(self, df, date_col, amount_col):
        """分析趋势"""
        try:
            df_temp = df.copy()
            df_temp['_date'] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=['_date'])
            df_temp['_period'] = df_temp['_date'].dt.to_period('M')
            
            trend = df_temp.groupby('_period')[amount_col].agg(['sum', 'mean', 'count']).to_dict()
            return {
                "periods": [str(p) for p in trend['sum'].keys()],
                "sums": list(trend['sum'].values()),
                "averages": list(trend['mean'].values()),
                "counts": list(trend['count'].values())
            }
        except:
            return {}
    
    def _analyze_by_dimension(self, df, dim_col, metric_col):
        """按维度分析"""
        try:
            grouped = df.groupby(dim_col)[metric_col].agg(['sum', 'mean', 'count'])
            top10 = grouped.nlargest(10, 'sum')
            return {
                "top_items": list(top10.index.astype(str)),
                "sums": [float(x) for x in top10['sum'].values],
                "averages": [float(x) for x in top10['mean'].values],
                "counts": [int(x) for x in top10['count'].values]
            }
        except:
            return {}
    
    def _detect_sales_anomalies(self, df, amount_col):
        """检测销售异常"""
        alerts = []
        series = df[amount_col].dropna()
        
        # 极大值检测
        mean = series.mean()
        std = series.std()
        threshold = mean + 3 * std
        
        anomalies = df[df[amount_col] > threshold]
        for _, row in anomalies.iterrows():
            alerts.append({
                "type": "high_value_order",
                "level": "medium",
                "message": f"发现异常高额订单: {row[amount_col]:.2f}，均值为 {mean:.2f}"
            })
        
        return alerts[:10]  # 最多返回10条
    
    def _generate_sales_insights(self, metrics):
        """生成销售洞察"""
        insights = []
        
        for key, value in metrics.items():
            if 'trend' in key and value:
                if value.get('sums'):
                    trend_direction = "上升" if value['sums'][-1] > value['sums'][0] else "下降"
                    change_pct = (value['sums'][-1] - value['sums'][0]) / value['sums'][0] * 100 if value['sums'][0] != 0 else 0
                    insights.append(f"销售趋势{trend_direction}，变化率 {change_pct:.1f}%")
            
            if 'customer' in key and value:
                if value.get('top_items'):
                    insights.append(f"Top客户: {', '.join(value['top_items'][:3])}")
        
        return insights

class InventoryAnalyzer(BusinessAnalyzer):
    """库存业务分析"""
    
    def analyze(self):
        results = {
            "domain": "inventory",
            "metrics": {},
            "insights": [],
            "alerts": []
        }
        
        # 查找库存相关的表
        inv_keywords = ['inventory', '库存', 'stock', '仓库', 'warehouse']
        inv_tables = self._find_tables_by_keywords(inv_keywords)
        
        for table_name in inv_tables:
            df = self.dataframes[table_name]
            
            # 查找库存量和安全库存列
            stock_col = self._find_column_by_keywords(df, ['quantity', '数量', 'stock', '库存'])
            safety_col = self._find_column_by_keywords(df, ['safety', '安全', 'min', '最低'])
            
            if stock_col:
                # 库存统计
                results["metrics"][f"{table_name}_stats"] = {
                    "total": float(df[stock_col].sum()),
                    "mean": float(df[stock_col].mean()),
                    "zero_count": int((df[stock_col] == 0).sum()),
                    "low_count": int((df[stock_col] < df[stock_col].quantile(0.1)).sum())
                }
                
                # 库存不足预警
                if safety_col:
                    low_stock = df[df[stock_col] < df[safety_col]]
                    for _, row in low_stock.iterrows():
                        results["alerts"].append({
                            "type": "low_stock",
                            "level": "high",
                            "product_id": row.get('product_id', 'unknown'),
                            "current": float(row[stock_col]),
                            "safety": float(row[safety_col]),
                            "message": f"库存不足: 当前 {row[stock_col]}，安全库存 {row[safety_col]}"
                        })
        
        # 生成洞察
        results["insights"] = self._generate_inventory_insights(results["metrics"])
        
        return results
    
    def _find_tables_by_keywords(self, keywords):
        found = []
        for name in self.dataframes.keys():
            name_lower = name.lower()
            if any(k in name_lower for k in keywords):
                found.append(name)
        return found
    
    def _find_column_by_keywords(self, df, keywords):
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return col
        return None
    
    def _generate_inventory_insights(self, metrics):
        insights = []
        
        for key, value in metrics.items():
            if 'stats' in key:
                if value.get('zero_count', 0) > 0:
                    insights.append(f"有 {value['zero_count']} 个产品库存为零")
                if value.get('low_count', 0) > 0:
                    insights.append(f"有 {value['low_count']} 个产品库存偏低")
        
        return insights

class FinanceAnalyzer(BusinessAnalyzer):
    """财务业务分析"""
    
    def analyze(self):
        results = {
            "domain": "finance",
            "metrics": {},
            "insights": [],
            "alerts": []
        }
        
        # 查找财务相关的表
        fin_keywords = ['finance', '财务', 'revenue', '收入', 'profit', '利润', 'cost', '成本']
        fin_tables = self._find_tables_by_keywords(fin_keywords)
        
        for table_name in fin_tables:
            df = self.dataframes[table_name]
            
            # 查找关键财务指标
            revenue_col = self._find_column_by_keywords(df, ['revenue', '收入', 'sales'])
            cost_col = self._find_column_by_keywords(df, ['cost', '成本', 'expense', '费用'])
            profit_col = self._find_column_by_keywords(df, ['profit', '利润', 'margin'])
            
            # 计算利润率
            if revenue_col and cost_col:
                df['_profit'] = df[revenue_col] - df[cost_col]
                df['_profit_margin'] = df['_profit'] / df[revenue_col]
                
                results["metrics"][f"{table_name}_profitability"] = {
                    "total_revenue": float(df[revenue_col].sum()),
                    "total_cost": float(df[cost_col].sum()),
                    "total_profit": float(df['_profit'].sum()),
                    "avg_profit_margin": float(df['_profit_margin'].mean()),
                    "min_profit_margin": float(df['_profit_margin'].min()),
                    "max_profit_margin": float(df['_profit_margin'].max())
                }
                
                # 亏损预警
                loss_periods = df[df['_profit_margin'] < 0]
                for _, row in loss_periods.iterrows():
                    results["alerts"].append({
                        "type": "loss_period",
                        "level": "high",
                        "message": f"发现亏损期间，利润率: {row['_profit_margin']:.2%}"
                    })
            
            # 月度趋势
            if revenue_col:
                results["metrics"][f"{table_name}_revenue_stats"] = {
                    "mean": float(df[revenue_col].mean()),
                    "std": float(df[revenue_col].std()),
                    "min": float(df[revenue_col].min()),
                    "max": float(df[revenue_col].max())
                }
        
        # 生成洞察
        results["insights"] = self._generate_finance_insights(results["metrics"])
        
        return results
    
    def _find_tables_by_keywords(self, keywords):
        found = []
        for name in self.dataframes.keys():
            name_lower = name.lower()
            if any(k in name_lower for k in keywords):
                found.append(name)
        return found
    
    def _find_column_by_keywords(self, df, keywords):
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return col
        return None
    
    def _generate_finance_insights(self, metrics):
        insights = []
        
        for key, value in metrics.items():
            if 'profitability' in key:
                margin = value.get('avg_profit_margin', 0)
                if margin > 0.2:
                    insights.append(f"整体利润率健康: {margin:.1%}")
                elif margin > 0:
                    insights.append(f"利润率偏低: {margin:.1%}，建议优化成本结构")
                else:
                    insights.append(f"⚠️ 整体亏损: {margin:.1%}")
        
        return insights

class CustomerAnalyzer(BusinessAnalyzer):
    """客户业务分析"""
    
    def analyze(self):
        results = {
            "domain": "customer",
            "metrics": {},
            "insights": [],
            "alerts": []
        }
        
        # 查找客户相关的表
        cust_keywords = ['customer', '客户', 'client', 'user', '用户']
        cust_tables = self._find_tables_by_keywords(cust_keywords)
        
        for table_name in cust_tables:
            df = self.dataframes[table_name]
            
            # 客户分层分析
            level_col = self._find_column_by_keywords(df, ['level', '等级', 'tier', 'class', '类别'])
            if level_col:
                level_dist = df[level_col].value_counts().to_dict()
                results["metrics"][f"{table_name}_level_distribution"] = level_dist
            
            # 地区分布
            region_col = self._find_column_by_keywords(df, ['region', '地区', 'area', 'zone', '区域'])
            if region_col:
                region_dist = df[region_col].value_counts().to_dict()
                results["metrics"][f"{table_name}_region_distribution"] = region_dist
            
            # 信用额度分析
            credit_col = self._find_column_by_keywords(df, ['credit', '信用', 'limit', '额度'])
            if credit_col:
                results["metrics"][f"{table_name}_credit_stats"] = {
                    "total": float(df[credit_col].sum()),
                    "mean": float(df[credit_col].mean()),
                    "max": float(df[credit_col].max()),
                    "min": float(df[credit_col].min())
                }
        
        # RFM 分析（如果有订单数据）
        results["insights"] = self._generate_customer_insights(results["metrics"])
        
        return results
    
    def _find_tables_by_keywords(self, keywords):
        found = []
        for name in self.dataframes.keys():
            name_lower = name.lower()
            if any(k in name_lower for k in keywords):
                found.append(name)
        return found
    
    def _find_column_by_keywords(self, df, keywords):
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return col
        return None
    
    def _generate_customer_insights(self, metrics):
        insights = []
        
        for key, value in metrics.items():
            if 'level_distribution' in key:
                total = sum(value.values())
                a_count = value.get('A', 0)
                a_ratio = a_count / total if total > 0 else 0
                insights.append(f"A级客户占比: {a_ratio:.1%}")
            
            if 'region_distribution' in key:
                top_region = max(value, key=value.get)
                insights.append(f"客户主要分布在: {top_region}")
        
        return insights

def run_business_analysis(dataframes, relations):
    """运行所有业务领域分析"""
    analyzers = [
        SalesAnalyzer(dataframes, relations),
        InventoryAnalyzer(dataframes, relations),
        FinanceAnalyzer(dataframes, relations),
        CustomerAnalyzer(dataframes, relations)
    ]
    
    results = {
        "analysis_time": datetime.now().isoformat(),
        "domains": {}
    }
    
    for analyzer in analyzers:
        domain_result = analyzer.analyze()
        domain = domain_result.pop("domain")
        results["domains"][domain] = domain_result
    
    # 汇总所有预警
    all_alerts = []
    for domain, data in results["domains"].items():
        for alert in data.get("alerts", []):
            alert["domain"] = domain
            all_alerts.append(alert)
    
    results["all_alerts"] = sorted(all_alerts, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("level", "low")))
    
    return results

def main():
    parser = argparse.ArgumentParser(description='业务领域分析')
    parser.add_argument('--data', default='.cache/loaded_data.pkl', help='数据文件')
    parser.add_argument('--relations', default='.cache/relations.json', help='关联文件')
    parser.add_argument('--output', default='.cache/business_analysis.json', help='输出路径')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.data, 'rb') as f:
        dataframes = pickle.load(f)
    
    relations = {}
    if Path(args.relations).exists():
        with open(args.relations, 'r', encoding='utf-8') as f:
            relations = json.load(f)
    
    print("Running business domain analysis...\n")
    
    results = run_business_analysis(dataframes, relations)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    for domain, data in results["domains"].items():
        print(f"=== {domain.upper()} ===")
        for insight in data.get("insights", []):
            print(f"  • {insight}")
        if data.get("alerts"):
            print(f"  Alerts: {len(data['alerts'])}")
        print()
    
    print(f"✓ Business analysis saved to {args.output}")

if __name__ == '__main__':
    main()
