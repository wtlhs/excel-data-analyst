#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
悦信物流业务分析器
基于业务背景的专项分析
"""

# Windows 兼容性
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
import yaml

class YuexinLogisticsAnalyzer:
    """悦信物流业务分析器"""
    
    def __init__(self, dataframes, business_context=None):
        self.dataframes = dataframes
        self.context = business_context or {}
        self.results = {
            "analysis_time": datetime.now().isoformat(),
            "company": "悦信物流",
            "business_type": "海外仓代理",
            "insights": [],
            "warnings": [],
            "metrics": {}
        }
    
    def run_analysis(self):
        """运行完整的业务分析"""
        print("Running Yuexin Logistics analysis...")
        
        # 1. 业务趋势分析
        self._business_trend_analysis()
        
        # 2. 渠道分析
        self._channel_analysis()
        
        # 3. 面单来源分析
        self._label_source_analysis()
        
        # 4. 客户价值分析
        self._customer_value_analysis()
        
        # 5. SKU分析
        self._sku_analysis()
        
        # 6. 时效分析
        self._time_efficiency_analysis()
        
        # 7. 仓库分析
        self._warehouse_analysis()
        
        # 8. 财务分析
        self._financial_analysis()
        
        return self.results
    
    def _business_trend_analysis(self):
        """业务趋势分析"""
        print("  - Business trend analysis...")
        
        trends = {
            "inbound": {},
            "outbound": {}
        }
        
        for name, df in self.dataframes.items():
            # 查找入库相关表
            if any(k in name.lower() for k in ['inbound', '入库', 'receipt', '收货']):
                date_col = self._find_date_column(df)
                amount_col = self._find_amount_column(df)
                if date_col and amount_col:
                    trends["inbound"] = self._calculate_trend(df, date_col, amount_col)
            
            # 查找出库相关表
            if any(k in name.lower() for k in ['outbound', '出库', '发货', 'shipment', 'delivery']):
                date_col = self._find_date_column(df)
                amount_col = self._find_amount_column(df)
                if date_col and amount_col:
                    trends["outbound"] = self._calculate_trend(df, date_col, amount_col)
        
        self.results["metrics"]["business_trend"] = trends
        
        # 生成洞察
        if trends.get("inbound") and trends["inbound"].get("growth_rate"):
            growth = trends["inbound"]["growth_rate"]
            if growth > 10:
                self.results["insights"].append(f"📈 入库业务增长强劲，增长率 {growth:.1f}%")
            elif growth < 0:
                self.results["warnings"].append(f"⚠️ 入库业务下滑 {abs(growth):.1f}%，需关注")
    
    def _channel_analysis(self):
        """渠道分析 - 分析各平台业务占比"""
        print("  - Channel analysis...")
        
        channels = {
            "Amazon": 0,
            "Temu": 0,
            "TikTok": 0,
            "Shopify": 0,
            "Wayfair": 0,
            "其他": 0
        }
        
        for name, df in self.dataframes.items():
            # 查找包含平台信息的列
            platform_col = self._find_column(df, ['platform', '平台', 'channel', '渠道', 'source', '来源'])
            if platform_col:
                value_counts = df[platform_col].value_counts().to_dict()
                for platform in channels.keys():
                    for key in value_counts.keys():
                        if platform.lower() in str(key).lower():
                            channels[platform] += value_counts[key]
        
        # 查找订单表
        for name, df in self.dataframes.items():
            if 'order' in name.lower() or '订单' in name:
                platform_col = self._find_column(df, ['platform', '平台', 'channel', '渠道'])
                if platform_col:
                    value_counts = df[platform_col].value_counts().head(10).to_dict()
                    self.results["metrics"]["channel_distribution"] = value_counts
                    break
        
        # 计算占比
        total = sum(channels.values())
        if total > 0:
            channel_percentage = {k: round(v/total*100, 2) for k, v in channels.items() if v > 0}
            self.results["metrics"]["channel_percentage"] = channel_percentage
            
            # 洞察
            top_channel = max(channel_percentage, key=channel_percentage.get) if channel_percentage else None
            if top_channel:
                self.results["insights"].append(f"🛒 业务主要来自 {top_channel} 平台，占比 {channel_percentage[top_channel]:.1f}%")
    
    def _label_source_analysis(self):
        """面单来源分析 - 有面单 vs 无面单"""
        print("  - Label source analysis...")
        
        label_sources = {
            "有面单": 0,
            "无面单": 0,
            "未知": 0
        }
        
        for name, df in self.dataframes.items():
            # 查找面单相关列
            label_col = self._find_column(df, ['label', '面单', 'tracking', '运单', 'waybill'])
            if label_col:
                # 假设有面单号即为有面单
                has_label = df[df[label_col].notna() & (df[label_col] != '')]
                no_label = df[df[label_col].isna() | (df[label_col] == '')]
                
                label_sources["有面单"] += len(has_label)
                label_sources["无面单"] += len(no_label)
        
        total = sum(label_sources.values())
        if total > 0:
            percentages = {k: round(v/total*100, 2) for k, v in label_sources.items() if v > 0}
            self.results["metrics"]["label_source"] = percentages
            
            # 洞察
            if percentages.get("有面单", 0) > 50:
                self.results["insights"].append(f"📋 大部分订单有平台提供面单 ({percentages['有面单']}%)")
            elif percentages.get("无面单", 0) > 50:
                self.results["insights"].append(f"📋 大部分订单需要向物流商获取面单 ({percentages['无面单']}%)")
    
    def _customer_value_analysis(self):
        """客户价值分析 - ABC分层"""
        print("  - Customer value analysis...")
        
        customer_values = {}
        
        for name, df in self.dataframes.items():
            # 查找客户和金额列
            customer_col = self._find_column(df, ['customer', '客户', 'client', '会员'])
            amount_col = self._find_amount_column(df)
            
            if customer_col and amount_col:
                # 按客户汇总
                customer_sum = df.groupby(customer_col)[amount_col].sum().sort_values(ascending=False)
                
                total = customer_sum.sum()
                if total > 0:
                    customer_sum_cumsum = customer_sum.cumsum() / total
                    
                    # ABC分层
                    a_customers = customer_sum_cumsum[customer_sum_cumsum <= 0.8]
                    b_customers = customer_sum_cumsum[(customer_sum_cumsum > 0.8) & (customer_sum_cumsum <= 0.95)]
                    c_customers = customer_sum_cumsum[customer_sum_cumsum > 0.95]
                    
                    customer_values = {
                        "A类客户": len(a_customers),
                        "B类客户": len(b_customers),
                        "C类客户": len(c_customers),
                        "A类客户贡献": f"{len(a_customers)/len(customer_sum)*100:.1f}%",
                        "A类客户收入占比": "80%"
                    }
                    
                    self.results["metrics"]["customer_value"] = customer_values
                    
                    # 洞察
                    self.results["insights"].append(f"👥 A类客户{len(a_customers)}家，贡献80%收入")
                    break
        
        return customer_values
    
    def _sku_analysis(self):
        """SKU分析 - 周转、滞销、爆品"""
        print("  - SKU analysis...")
        
        sku_metrics = {}
        
        for name, df in self.dataframes.items():
            # 查找SKU相关列
            sku_col = self._find_column(df, ['sku', '产品', 'item', '商品', 'product'])
            quantity_col = self._find_column(df, ['quantity', '数量', 'qty', '库存'])
            
            if sku_col and quantity_col:
                # SKU销量统计
                sku_sales = df.groupby(sku_col)[quantity_col].sum().sort_values(ascending=False)
                
                total = sku_sales.sum()
                if total > 0:
                    # 爆品（销量前20%）
                    top_20_pct = sku_sales.quantile(0.8)
                    hot_items = sku_sales[sku_sales >= top_20_pct]
                    
                    # 滞销品（销量后20%）
                    low_20_pct = sku_sales.quantile(0.2)
                    slow_items = sku_sales[sku_sales <= low_20_pct]
                    
                    sku_metrics = {
                        "总SKU数": len(sku_sales),
                        "爆品数": len(hot_items),
                        "滞销品数": len(slow_items),
                        "爆品占比": f"{len(hot_items)/len(sku_sales)*100:.1f}%",
                        "滞销占比": f"{len(slow_items)/len(sku_sales)*100:.1f}%"
                    }
                    
                    self.results["metrics"]["sku_analysis"] = sku_metrics
                    
                    # 洞察
                    self.results["insights"].append(f"📦 共{len(sku_sales)}个SKU，爆品{len(hot_items)}个，滞销{len(slow_items)}个")
                    break
        
        return sku_metrics
    
    def _time_efficiency_analysis(self):
        """时效分析"""
        print("  - Time efficiency analysis...")
        
        for name, df in self.dataframes.items():
            # 查找日期列
            date_cols = [c for c in df.columns if any(k in c.lower() for k in 
                         ['date', '日期', 'time', '时间', 'create', '创建'])]
            
            if len(date_cols) >= 2:
                try:
                    df_temp = df.copy()
                    df_temp['_date1'] = pd.to_datetime(df_temp[date_cols[0]], errors='coerce')
                    df_temp['_date2'] = pd.to_datetime(df_temp[date_cols[1]], errors='coerce')
                    df_temp = df_temp.dropna(subset=['_date1', '_date2'])
                    
                    if len(df_temp) > 0:
                        df_temp['_days'] = (df_temp['_date2'] - df_temp['_date1']).dt.days
                        
                        avg_days = df_temp['_days'].mean()
                        
                        self.results["metrics"]["time_efficiency"] = {
                            "平均处理天数": round(avg_days, 1),
                            "最快": int(df_temp['_days'].min()),
                            "最慢": int(df_temp['_days'].max())
                        }
                        
                        # 洞察
                        if avg_days <= 1:
                            self.results["insights"].append(f"⏱️ 业务处理时效优秀，平均 {avg_days:.1f} 天")
                        elif avg_days <= 3:
                            self.results["insights"].append(f"⏱️ 业务处理时效正常，平均 {avg_days:.1f} 天")
                        else:
                            self.results["warnings"].append(f"⚠️ 业务处理时效较长，平均 {avg_days:.1f} 天，建议优化")
                        
                        break
                except:
                    continue
    
    def _warehouse_analysis(self):
        """仓库分析"""
        print("  - Warehouse analysis...")
        
        warehouse_stats = {}
        
        for name, df in self.dataframes.items():
            # 查找仓库列
            warehouse_col = self._find_column(df, ['warehouse', '仓库', 'location', '库位'])
            quantity_col = self._find_column(df, ['quantity', '数量', 'stock', '库存'])
            
            if warehouse_col and quantity_col:
                # 仓库库存统计
                warehouse_sum = df.groupby(warehouse_col)[quantity_col].sum().to_dict()
                warehouse_stats = {k: int(v) for k, v in warehouse_sum.items()}
                
                self.results["metrics"]["warehouse_usage"] = warehouse_stats
                
                # 洞察
                top_warehouse = max(warehouse_stats, key=warehouse_stats.get) if warehouse_stats else None
                if top_warehouse:
                    self.results["insights"].append(f"🏭 {top_warehouse} 仓库使用最多，库存 {warehouse_stats[top_warehouse]}")
                break
        
        return warehouse_stats
    
    def _financial_analysis(self):
        """财务分析"""
        print("  - Financial analysis...")
        
        for name, df in self.dataframes.items():
            if 'finance' in name.lower() or '财务' in name:
                revenue_col = self._find_column(df, ['revenue', '收入', 'sales', '销售额'])
                cost_col = self._find_column(df, ['cost', '成本', 'expense', '费用'])
                
                if revenue_col and cost_col:
                    revenue = df[revenue_col].sum()
                    cost = df[cost_col].sum()
                    profit = revenue - cost
                    margin = profit / revenue if revenue > 0 else 0
                    
                    self.results["metrics"]["financial"] = {
                        "总收入": round(revenue, 2),
                        "总成本": round(cost, 2),
                        "利润": round(profit, 2),
                        "利润率": f"{margin*100:.1f}%"
                    }
                    
                    # 洞察
                    if margin > 0.2:
                        self.results["insights"].append(f"💰 利润率健康，为 {margin*100:.1f}%")
                    elif margin > 0:
                        self.results["warnings"].append(f"⚠️ 利润率偏低，为 {margin*100:.1f}%")
                    else:
                        self.results["warnings"].append(f"🔴 亏损状态，利润率 {margin*100:.1f}%")
                    break
    
    def _calculate_trend(self, df, date_col, value_col):
        """计算趋势"""
        try:
            df_temp = df.copy()
            df_temp['_date'] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=['_date', value_col])
            df_temp['_month'] = df_temp['_date'].dt.to_period('M')
            
            monthly = df_temp.groupby('_month')[value_col].sum()
            
            if len(monthly) >= 2:
                first = monthly.iloc[0]
                last = monthly.iloc[-1]
                growth_rate = (last - first) / first * 100 if first != 0 else 0
                
                return {
                    "periods": [str(p) for p in monthly.index],
                    "values": [float(v) for v in monthly.values],
                    "growth_rate": round(growth_rate, 2),
                    "trend": "up" if growth_rate > 0 else "down"
                }
        except:
            pass
        return {}
    
    def _find_date_column(self, df):
        """查找日期列"""
        for col in df.columns:
            if any(k in col.lower() for k in ['date', '日期', 'time', '时间', 'created', '创建']):
                return col
        return None
    
    def _find_column(self, df, keywords):
        """根据关键词查找列"""
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return col
        return None
    
    def _find_amount_column(self, df):
        """查找金额/数量列"""
        for col in df.columns:
            if any(k in col.lower() for k in ['amount', '金额', 'total', '总额', 'quantity', '数量', 'qty', 'weight', '重量']):
                return col
        return None


def load_business_context(config_path):
    """加载业务背景配置"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        return {}

def main():
    parser = argparse.ArgumentParser(description='悦信物流业务分析')
    parser.add_argument('--data', default='.cache/loaded_data.pkl', help='数据文件')
    parser.add_argument('--context', default='assets/business_context.yaml', help='业务背景配置')
    parser.add_argument('--output', default='.cache/yuexin_analysis.json', help='输出路径')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.data, 'rb') as f:
        dataframes = pickle.load(f)
    
    # 加载业务背景
    context = {}
    context_path = Path(args.context)
    if context_path.exists():
        context = load_business_context(context_path)
    
    print("\n=== Yuexin Logistics Analysis ===\n")
    
    analyzer = YuexinLogisticsAnalyzer(dataframes, context)
    results = analyzer.run_analysis()
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print(f"\n✓ Analysis complete!")
    print(f"  Insights: {len(results['insights'])}")
    print(f"  Warnings: {len(results['warnings'])}")
    print(f"  Metrics: {len(results['metrics'])}")
    
    for insight in results['insights']:
        print(f"  ✓ {insight}")
    
    for warning in results['warnings']:
        print(f"  ⚠️ {warning}")
    
    print(f"\n✓ Saved to: {args.output}")

if __name__ == '__main__':
    main()
