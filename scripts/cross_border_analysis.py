#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨境电商海外仓业务分析器 v2
基于业务背景的专项分析 - 修复版
"""

import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class CrossBorderAnalyzerV2:
    """跨境电商海外仓分析器 v2 - 修复版"""
    
    def __init__(self, dataframes):
        self.dataframes = dataframes
        self.results = {
            "analysis_time": datetime.now().isoformat(),
            "company": "悦信物流",
            "business_type": "海外仓代理",
            "data_quality": {},
            "core_findings": [],
            "warnings": [],
            "metrics": {}
        }
        
        # 客户表（关键：用于识别真正客户）
        self.customer_map = self._build_customer_map()
        
    def _build_customer_map(self):
        """构建客户映射表"""
        customer_map = {}
        if '4.客户' in self.dataframes:
            df = self.dataframes['4.客户']
            if '客户名称' in df.columns and '客户简称' in df.columns:
                for _, row in df.iterrows():
                    customer_map[row.get('客户简称', '')] = row.get('客户名称', '')
        return customer_map
    
    def run_analysis(self):
        """运行完整分析"""
        print("Running Cross-Border Analysis v2...")
        
        # 1. 数据质量检查
        self._check_data_quality()
        
        # 2. 仓库分析
        self._warehouse_analysis()
        
        # 3. 入库业务分析
        self._inbound_analysis()
        
        # 4. 退货业务分析
        self._return_analysis()
        
        # 5. 库存分析（修复版）
        self._inventory_analysis_v2()
        
        # 6. 客户分析（修复版）
        self._customer_analysis_v2()
        
        # 7. 财务分析（修复版）
        self._financial_analysis_v2()
        
        # 8. SKU分析（修复版）
        self._sku_analysis_v2()
        
        # 9. 业务预警（新增）
        self._business_alerts()
        
        # 10. 战略建议（新增）
        self._strategic_recommendations()
        
        return self.results
    
    def _check_data_quality(self):
        """数据质量检查"""
        quality = {}
        for name, df in self.dataframes.items():
            null_counts = df.isnull().sum()
            total = len(df)
            null_cols = null_counts[null_counts > 0].to_dict()
            
            quality[name] = {
                "total_rows": total,
                "total_cols": len(df.columns),
                "null_columns": null_cols,
                "null_ration": round(null_counts.sum() / (total * len(df.columns)) * 100, 2) if total > 0 else 0
            }
        
        self.results["data_quality"] = quality
        self.results["core_findings"].append(f"共分析 {len(self.dataframes)} 个数据表，{sum(df.shape[0] for df in self.dataframes.values()):,} 条记录")
    
    def _warehouse_analysis(self):
        """仓库分析"""
        if '1.仓库列表' not in self.dataframes:
            return
            
        df = self.dataframes['1.仓库列表']
        
        # 仓库分布
        country_dist = df['国家'].value_counts().to_dict() if '国家' in df.columns else {}
        type_dist = df['仓库类型'].value_counts().to_dict() if '仓库类型' in df.columns else {}
        
        # 按区域分类
        us_warehouses = df[df['国家'] == 'US']['仓库名称'].tolist() if '国家' in df.columns else []
        east_warehouses = [w for w in us_warehouses if any(x in str(w) for x in ['NJ', 'GA', 'Edison', '亚特兰大', '美东'])]
        west_warehouses = [w for w in us_warehouses if any(x in str(w) for x in ['CA', '洛杉矶', '美西'])]
        
        self.results["metrics"]["warehouse"] = {
            "total": len(df),
            "by_country": country_dist,
            "by_type": type_dist,
            "us_east_count": len(east_warehouses),
            "us_west_count": len(west_warehouses),
            "us_east": east_warehouses[:5],
            "us_west": west_warehouses[:5]
        }
        
        self.results["core_findings"].append(f"仓库总数：{len(df)}个，其中美国{east_warehouses.__len__()}个(美东)、{len(west_warehouses)}个(美西)")
    
    def _inbound_analysis(self):
        """入库业务分析"""
        if '10.入库单_已入库' not in self.dataframes:
            return
            
        df = self.dataframes['10.入库单_已入库']
        
        # 正确的客户识别
        customer_col = '客户名称' if '客户名称' in df.columns else None
        
        if customer_col:
            # 使用客户表过滤真正的客户
            valid_customers = set(self.customer_map.values())
            df_filtered = df[df[customer_col].isin(valid_customers) | df[customer_col].isin(self.customer_map.keys())]
            
            customer_count = df_filtered[customer_col].nunique()
            total_inbound = len(df_filtered)
        else:
            customer_count = df[customer_col].nunique() if customer_col else 0
            total_inbound = len(df)
        
        # 目的仓库分布
        warehouse_col = '目的仓库' if '目的仓库' in df.columns else None
        warehouse_dist = df[warehouse_col].value_counts().head(10).to_dict() if warehouse_col else {}
        
        self.results["metrics"]["inbound"] = {
            "total": total_inbound,
            "customer_count": customer_count,
            "top_warehouses": warehouse_dist,
            "warehouse_count": df[warehouse_col].nunique() if warehouse_col else 0
        }
        
        self.results["core_findings"].append(f"入库单：{total_inbound}单，服务客户{customer_count}家")
    
    def _return_analysis(self):
        """退货业务分析"""
        if '12.退货单_全部' not in self.dataframes:
            return
            
        df = self.dataframes['12.退货单_全部']
        
        status_dist = df['状态'].value_counts().to_dict() if '状态' in df.columns else {}
        
        # 退货率计算
        total_returns = len(df)
        completed_returns = len(df[df['状态'] == '已入库']) if '状态' in df.columns else 0
        return_rate = round(completed_returns / total_returns * 100, 2) if total_returns > 0 else 0
        
        self.results["metrics"]["return"] = {
            "total": total_returns,
            "by_status": status_dist,
            "completed": completed_returns,
            "return_rate": f"{return_rate}%"
        }
        
        self.results["core_findings"].append(f"退货单：{total_returns}单，退货完成率{return_rate}%")
    
    def _inventory_analysis_v2(self):
        """库存分析 v2 - 修复版"""
        if '6.剩余库存' not in self.dataframes:
            # 尝试从入库数据推断库存
            if '10.入库单_已入库' in self.dataframes:
                df = self.dataframes['10.入库单_已入库']
                self.results["metrics"]["inventory"] = {
                    "note": "无独立库存表，基于入库数据推断",
                    "total_inbound": len(df)
                }
                return
        
        df = self.dataframes['6.剩余库存']
        
        # 识别真正的客户
        customer_col = '客户名称' if '客户名称' in df.columns else None
        
        # 定义库存状态
        available_col = '可用库存' if '可用库存' in df.columns else None
        in_transit_col = '在途' if '在途' in df.columns else None
        pending_col = '待打包/待发货' if '待打包/待发货' in df.columns else None
        isolated_col = '隔离' if '隔离' in df.columns else None
        
        # 统计
        zero_inventory = 0  # 可用库存为0
        low_inventory = 0   # 低于安全库存
        in_transit = 0      # 在途
        isolated = 0         # 隔离
        
        if available_col:
            zero_inventory = len(df[df[available_col] == 0])
            # 安全库存比较
            safety_col = '安全库存' if '安全库存' in df.columns else None
            if safety_col:
                low_inventory = len(df[df[available_col] < df[safety_col]])
        
        if in_transit_col:
            in_transit = df[in_transit_col].sum()
        
        if isolated_col:
            isolated = df[isolated_col].sum()
        
        self.results["metrics"]["inventory"] = {
            "total_products": len(df),
            "zero_available": int(zero_inventory),  # 可用库存为0
            "low_stock": int(low_inventory),  # 低于安全库存
            "in_transit": float(in_transit) if in_transit else 0,
            "isolated": float(isolated) if isolated else 0,
            "explanation": {
                "zero_available": "可用库存=0的产品数量，这类产品无法直接销售",
                "low_stock": "可用库存低于安全库存的产品，需要补货",
                "in_transit": "在途数量，已预报但未入库",
                "isolated": "隔离数量，退货待检查"
            }
        }
        
        if zero_inventory > 0:
            self.results["warnings"].append(f"⚠️ {zero_inventory}个SKU可用库存为0，无法直接销售")
        if low_inventory > 0:
            self.results["warnings"].append(f"⚠️ {low_inventory}个SKU库存低于安全库存，需要补货")
    
    def _customer_analysis_v2(self):
        """客户分析 v2 - 修复版"""
        # 使用客户表作为客户来源
        if '4.客户' not in self.dataframes:
            # 从业务表推断客户
            all_customers = set()
            for name, df in self.dataframes.items():
                if '客户名称' in df.columns:
                    all_customers.update(df['客户名称'].dropna().unique())
            
            self.results["metrics"]["customer"] = {
                "total": len(all_customers),
                "note": "从业务表推断，非客户表"
            }
            self.results["core_findings"].append(f"服务客户：约{len(all_customers)}家")
            return
        
        customer_df = self.dataframes['4.客户']
        total_customers = len(customer_df)
        
        # 统计有业务发生的客户
        active_customers = set()
        if '10.入库单_已入库' in self.dataframes:
            inbound_df = self.dataframes['10.入库单_已入库']
            if '客户名称' in inbound_df.columns:
                active_customers.update(inbound_df['客户名称'].unique())
        
        self.results["metrics"]["customer"] = {
            "total_in_customer_table": total_customers,
            "active_with_inbound": len(active_customers),
            "note": "仅统计客户表中的客户，不含订单消费者数据"
        }
        
        self.results["core_findings"].append(f"客户表客户：{total_customers}家，有入库记录：{len(active_customers)}家")
    
    def _financial_analysis_v2(self):
        """财务分析 v2 - 修复版"""
        # 应收费用
        receivable = {}
        if '20.仓库应收费用' in self.dataframes:
            df = self.dataframes['20.仓库应收费用']
            if '应收客户' in df.columns and '费用名称' in df.columns:
                # 过滤有效客户
                valid_customers = set(self.customer_map.values())
                df_filtered = df[df['应收客户'].isin(valid_customers) | df['应收客户'].isin(self.customer_map.keys())]
                
                receivable = {
                    "total_records": len(df_filtered),
                    "unique_customers": df_filtered['应收客户'].nunique() if '应收客户' in df.columns else 0
                }
        
        # 应付费用
        payable = {}
        if '21.仓库应付费用' in self.dataframes:
            df = self.dataframes['21.仓库应付费用']
            payable = {
                "total_records": len(df),
                "unique_suppliers": df['供应商名称'].nunique() if '供应商名称' in df.columns else 0
            }
        
        # 物流费用
        logistics = {}
        if '18.物流费用' in self.dataframes:
            df = self.dataframes['18.物流费用']
            logistics = {
                "total_records": len(df),
                "total_revenue": float(df['应收客户'].sum()) if '应收客户' in df.columns and df['应收客户'].dtype in [np.float64, np.int64] else 0,
                "total_cost": float(df['应付供应商'].sum()) if '应付供应商' in df.columns and df['应付供应商'].dtype in [np.float64, np.int64] else 0
            }
            if logistics["total_revenue"] > 0 and logistics["total_cost"] > 0:
                profit = logistics["total_revenue"] - logistics["total_cost"]
                margin = profit / logistics["total_revenue"] * 100
                logistics["profit"] = round(profit, 2)
                logistics["margin"] = f"{margin:.1f}%"
        
        self.results["metrics"]["financial"] = {
            "receivable": receivable,
            "payable": payable,
            "logistics": logistics,
            "empty_note": "费用表中为空可能是：该客户当期无费用发生、非本仓库操作、非本周期费用"
        }
        
        if logistics.get("margin"):
            self.results["core_findings"].append(f"物流利润率：{logistics['margin']}")
    
    def _sku_analysis_v2(self):
        """SKU分析 v2 - 修复版"""
        if '2.产品' not in self.dataframes:
            return
        
        df = self.dataframes['2.产品']
        
        # 产品类型分布
        type_dist = df['货物类型'].value_counts().to_dict() if '货物类型' in df.columns else {}
        battery_dist = df['电池类型'].value_counts().to_dict() if '电池类型' in df.columns else {}
        
        self.results["metrics"]["sku"] = {
            "total": len(df),
            "by_type": type_dist,
            "by_battery": battery_dist,
            "definitions": {
                "普货": "不含电池的普通商品",
                "含电池货物": "电池在包装内",
                "纯电池货物": "纯电池商品",
                "爆款": "销量前20%的SKU",
                "滞销": "90天无出库的SKU"
            }
        }
        
        self.results["core_findings"].append(f"SKU总数：{len(df)}个，其中普货{type_dist.get('普货', 0)}个")
    
    def _business_alerts(self):
        """业务预警"""
        alerts = []
        
        # 库存预警
        if '6.剩余库存' in self.dataframes:
            df = self.dataframes['6.剩余库存']
            available_col = '可用库存' if '可用库存' in df.columns else None
            if available_col:
                zero_count = len(df[df[available_col] == 0])
                if zero_count > 0:
                    alerts.append({
                        "type": "inventory",
                        "level": "high",
                        "message": f"{zero_count}个SKU可用库存为0，建议尽快补货"
                    })
        
        # 退货预警
        if '12.退货单_全部' in self.dataframes:
            df = self.dataframes['12.退货单_全部']
            if '状态' in df.columns:
                cancelled = len(df[df['状态'] == '已取消'])
                total = len(df)
                if cancelled / total > 0.2:
                    alerts.append({
                        "type": "return",
                        "level": "medium",
                        "message": f"退货取消率{cancelled/total*100:.1f}%超过20%，需关注"
                    })
        
        self.results["metrics"]["alerts"] = alerts
        
        for alert in alerts:
            level_icon = "🔴" if alert["level"] == "high" else "🟡"
            self.results["warnings"].append(f"{level_icon} {alert['message']}")
    
    def _strategic_recommendations(self):
        """战略建议"""
        recommendations = {
            "short_term": [],
            "long_term": []
        }
        
        # 短期建议 - 基于数据分析
        if '1.仓库列表' in self.dataframes:
            df = self.dataframes['1.仓库列表']
            us_warehouses = df[df['国家'] == 'US']
            east = len([w for w in us_warehouses['仓库名称'] if 'NJ' in str(w) or 'GA' in str(w)])
            west = len([w for w in us_warehouses['仓库名称'] if 'CA' in str(w)])
            
            if east < west:
                recommendations["short_term"].append({
                    "title": "美东仓库布局不足",
                    "reason": f"当前美东仓库{east}个，美西{west}个，美东配送更快、成本更低",
                    "action": "建议在美东增加仓库合作"
                })
        
        # 长期战略
        recommendations["long_term"] = [
            {
                "title": "扩大美东仓库布局",
                "reason": "美国人口集中在东海岸，美东仓库配送时效更快、尾程成本更低，能提升客户满意度",
                "action": "考察NJ、GA、FL等区域仓库资源"
            },
            {
                "title": "建立智能补货系统",
                "reason": "基于销售数据+到仓时间(美西20天、美东45天)自动计算补货量",
                "action": "开发补货算法模型"
            },
            {
                "title": "客户流失预警",
                "reason": "监控客户销量变化+入库预报频率，及时发现合作意愿下降",
                "action": "建立客户健康度评分"
            }
        ]
        
        self.results["metrics"]["recommendations"] = recommendations


def main():
    parser = argparse.ArgumentParser(description='跨境电商海外仓分析 v2')
    parser.add_argument('--data', required=True, help='数据文件路径')
    parser.add_argument('--output', default='cross_border_v2.json', help='输出文件')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.data, 'rb') as f:
        dataframes = pickle.load(f)
    
    print("\n=== Cross-Border Analysis v2 ===\n")
    
    analyzer = CrossBorderAnalyzerV2(dataframes)
    results = analyzer.run_analysis()
    
    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印核心发现
    print("\n📊 核心发现:")
    for finding in results["core_findings"]:
        print(f"  • {finding}")
    
    print("\n⚠️ 警告:")
    for warning in results["warnings"]:
        print(f"  • {warning}")
    
    print(f"\n✓ 保存到: {args.output}")

if __name__ == '__main__':
    main()
