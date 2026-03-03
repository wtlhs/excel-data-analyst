#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级数据分析器
多维度深度分析模块
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
from collections import Counter

class AdvancedAnalyzer:
    """高级数据分析器"""
    
    def __init__(self, dataframes, relations):
        self.dataframes = dataframes
        self.relations = relations
        self.results = {
            "analysis_time": datetime.now().isoformat(),
            "dimensions": {}
        }
    
    def run_full_analysis(self):
        """运行完整的高级分析"""
        print("Running advanced analysis...")
        
        # 时间序列分析
        self._time_series_analysis()
        
        # 相关性分析
        self._correlation_analysis()
        
        # 分层分析
        self._stratification_analysis()
        
        # 对比分析
        self._comparison_analysis()
        
        # 异常深度分析
        self._anomaly_deep_analysis()
        
        # 文本分析
        self._text_analysis()
        
        # 预测分析
        self._forecast_analysis()
        
        return self.results
    
    def _time_series_analysis(self):
        """时间序列分析"""
        print("  - Time series analysis...")
        
        results = {
            "trends": {},
            "seasonality": {},
            "growth": {}
        }
        
        for name, df in self.dataframes.items():
            # 查找日期列
            date_col = self._find_date_column(df)
            if date_col is None:
                continue
            
            # 查找数值列
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                continue
            
            try:
                df_temp = df.copy()
                df_temp['_date'] = pd.to_datetime(df_temp[date_col], errors='coerce')
                df_temp = df_temp.dropna(subset=['_date'])
                
                if len(df_temp) < 10:
                    continue
                
                # 按月聚合
                df_temp['_month'] = df_temp['_date'].dt.to_period('M')
                
                for col in numeric_cols[:3]:  # 最多分析3个列
                    monthly = df_temp.groupby('_month')[col].sum()
                    
                    if len(monthly) >= 3:
                        # 趋势分析
                        first_value = monthly.iloc[0]
                        last_value = monthly.iloc[-1]
                        if first_value != 0:
                            growth_rate = (last_value - first_value) / abs(first_value) * 100
                        else:
                            growth_rate = 0
                        
                        # 环比增长
                        if len(monthly) >= 2:
                            mom_growth = [(monthly.iloc[i] - monthly.iloc[i-1]) / monthly.iloc[i-1] * 100 
                                        for i in range(1, len(monthly)) if monthly.iloc[i-1] != 0]
                            avg_mom = np.mean(mom_growth) if mom_growth else 0
                        else:
                            avg_mom = 0
                        
                        results["trends"][f"{name}.{col}"] = {
                            "periods": [str(p) for p in monthly.index],
                            "values": [float(v) for v in monthly.values],
                            "growth_rate": round(growth_rate, 2),
                            "avg_mom_growth": round(avg_mom, 2),
                            "trend_direction": "up" if growth_rate > 0 else "down"
                        }
                        
                        # 季节性分析（如果有足够数据）
                        if len(monthly) >= 12:
                            monthly_avg = monthly.groupby(monthly.index.month).mean()
                            seasonal_strength = monthly_avg.std() / monthly_avg.mean() if monthly_avg.mean() != 0 else 0
                            results["seasonality"][f"{name}.{col}"] = {
                                "seasonal_strength": round(seasonal_strength, 3),
                                "peak_month": int(monthly_avg.idxmax()),
                                "low_month": int(monthly_avg.idxmin())
                            }
            except Exception as e:
                continue
        
        self.results["dimensions"]["time_series"] = results
    
    def _correlation_analysis(self):
        """相关性分析"""
        print("  - Correlation analysis...")
        
        results = {
            "pearson": {},
            "spearman": {},
            "correlation_matrix": {}
        }
        
        # 合并所有数值数据 - 使用索引对齐
        all_numeric = pd.DataFrame()
        max_len = 0
        
        # 先获取最大长度
        for name, df in self.dataframes.items():
            numeric = df.select_dtypes(include=[np.number])
            if len(numeric) > max_len:
                max_len = len(numeric)
        
        if max_len < 10:
            self.results["dimensions"]["correlation"] = results
            return
        
        # 填充到相同长度
        for name, df in self.dataframes.items():
            numeric = df.select_dtypes(include=[np.number])
            for col in numeric.columns:
                # 转换为 float 以支持 NaN
                values = numeric[col].astype(float).values
                if len(values) < max_len:
                    # 填充 NaN
                    values = np.pad(values, (0, max_len - len(values)), mode='constant', constant_values=np.nan)
                all_numeric[f"{name}_{col}"] = values
        
        # 移除全为 NaN 的列
        all_numeric = all_numeric.dropna(axis=1, how='all')
        
        if all_numeric.shape[1] < 2 or all_numeric.dropna().shape[0] < 10:
            self.results["dimensions"]["correlation"] = results
            return
        
        # 计算相关矩阵
        corr_matrix = all_numeric.corr()
        
        # 找出强相关对
        strong_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if not np.isnan(corr_value) and abs(corr_value) > 0.7:
                    strong_correlations.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": round(corr_value, 3),
                        "strength": "strong" if abs(corr_value) > 0.8 else "moderate",
                        "direction": "positive" if corr_value > 0 else "negative"
                    })
        
        results["strong_correlations"] = sorted(strong_correlations, 
                                                key=lambda x: abs(x['correlation']), 
                                                reverse=True)[:20]
        
        self.results["dimensions"]["correlation"] = results
    
    def _stratification_analysis(self):
        """分层分析"""
        print("  - Stratification analysis...")
        
        results = {
            "rfm": {},      # 客户RFM分析
            "abc": {},      # 产品ABC分析
            "paretto": {}   # 帕累托分析
        }
        
        # 客户分析
        for name, df in self.dataframes.items():
            # 查找订单相关表
            if 'order' not in name.lower() and '订单' not in name:
                continue
            
            # 查找客户ID和日期列
            customer_col = self._find_column(df, ['customer', '客户', 'user', '会员'])
            date_col = self._find_date_column(df)
            amount_col = self._find_amount_column(df)
            
            if customer_col and date_col and amount_col:
                try:
                    # RFM分析
                    df_temp = df.copy()
                    df_temp['_date'] = pd.to_datetime(df_temp[date_col], errors='coerce')
                    df_temp = df_temp.dropna(subset=['_date', customer_col, amount_col])
                    
                    if len(df_temp) < 10:
                        continue
                    
                    # 计算RFM
                    ref_date = df_temp['_date'].max()
                    rfm = df_temp.groupby(customer_col).agg({
                        '_date': lambda x: (ref_date - x.max()).days,  # Recency
                        date_col: 'count',  # Frequency
                        amount_col: 'sum'   # Monetary
                    }).rename(columns={
                        '_date': 'recency',
                        date_col: 'frequency',
                        amount_col: 'monetary'
                    })
                    
                    # RFM评分
                    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1], duplicates='drop')
                    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
                    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1,2,3,4,5])
                    
                    # 客户分层
                    rfm['segment'] = rfm.apply(lambda x: self._rfm_segment(
                        x['r_score'] if hasattr(x['r_score'], '__iter__') else x['r_score'],
                        x['f_score'] if hasattr(x['f_score'], '__iter__') else x['f_score'],
                        x['m_score'] if hasattr(x['m_score'], '__iter__') else x['m_score']
                    ), axis=1)
                    
                    segment_counts = rfm['segment'].value_counts().to_dict()
                    
                    results["rfm"][name] = {
                        "segments": segment_counts,
                        "total_customers": len(rfm),
                        "top_segment": max(segment_counts, key=segment_counts.get) if segment_counts else "N/A"
                    }
                except Exception as e:
                    continue
        
        # 产品ABC分析
        for name, df in self.dataframes.items():
            if 'product' not in name.lower() and '产品' not in name:
                continue
            
            price_col = self._find_column(df, ['price', '价格', 'price', 'cost', '成本'])
            if price_col:
                try:
                    df_sorted = df.sort_values(price_col, ascending=False)
                    total = df[price_col].sum()
                    
                    if total == 0:
                        continue
                    
                    df_sorted['_cumsum'] = df_sorted[price_col].cumsum()
                    df_sorted['_cumsum_pct'] = df_sorted['_cumsum'] / total
                    
                    # ABC分类
                    df_sorted['_abc'] = df_sorted['_cumsum_pct'].apply(
                        lambda x: 'A' if x <= 0.8 else ('B' if x <= 0.95 else 'C')
                    )
                    
                    abc_counts = df_sorted['_abc'].value_counts().to_dict()
                    results["abc"][name] = {
                        "A": abc_counts.get('A', 0),
                        "B": abc_counts.get('B', 0),
                        "C": abc_counts.get('C', 0),
                        "total_products": len(df)
                    }
                except Exception as e:
                    continue
        
        self.results["dimensions"]["stratification"] = results
    
    def _rfm_segment(self, r, f, m):
        """RFM客户分层"""
        try:
            r, f, m = int(r), int(f), int(m)
            if r >= 4 and f >= 4 and m >= 4:
                return "VIP客户"
            elif r >= 3 and f >= 3:
                return "潜力客户"
            elif r >= 3 and f < 3:
                return "新客户"
            elif r < 3 and f >= 4:
                return "重要客户"
            elif r < 3 and f < 3 and m >= 4:
                return "高价值流失客户"
            else:
                return "普通客户"
        except:
            return "普通客户"
    
    def _comparison_analysis(self):
        """对比分析"""
        print("  - Comparison analysis...")
        
        results = {
            "period_comparison": {},
            "category_comparison": {},
            "rankings": {}
        }
        
        for name, df in self.dataframes.items():
            # 类别对比
            category_cols = [c for c in df.columns if any(k in c.lower() for k in 
                         ['category', '类型', '分类', 'region', '地区', 'dept', '部门'])]
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for cat_col in category_cols[:2]:
                for num_col in numeric_cols[:2]:
                    try:
                        grouped = df.groupby(cat_col)[num_col].agg(['sum', 'mean', 'count'])
                        top5 = grouped.nlargest(5, 'sum')
                        
                        results["category_comparison"][f"{name}.{cat_col}.{num_col}"] = {
                            "categories": list(top5.index.astype(str)),
                            "values": [float(v) for v in top5['sum'].values],
                            "total": float(grouped['sum'].sum())
                        }
                    except:
                        continue
            
            # 排名分析
            for num_col in numeric_cols[:2]:
                try:
                    df_sorted = df.nlargest(10, num_col)
                    results["rankings"][f"{name}.{num_col}"] = {
                        "top_items": list(df_sorted.index.astype(str)[:10]),
                        "values": [float(v) for v in df_sorted[num_col].values]
                    }
                except:
                    continue
        
        self.results["dimensions"]["comparison"] = results
    
    def _anomaly_deep_analysis(self):
        """异常深度分析"""
        print("  - Anomaly deep analysis...")
        
        results = {
            "outliers": {},
            "patterns": {},
            "root_causes": []
        }
        
        for name, df in self.dataframes.items():
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                series = df[col].dropna()
                if len(series) < 10:
                    continue
                
                # 多方法异常检测
                outliers_zscore = self._zscore_outliers(series)
                outliers_iqr = self._iqr_outliers(series)
                
                if len(outliers_zscore) > 0 or len(outliers_iqr) > 0:
                    results["outliers"][f"{name}.{col}"] = {
                        "zscore_count": int(len(outliers_zscore)),
                        "iqr_count": int(len(outliers_iqr)),
                        "total_count": int(len(set(outliers_zscore.index) | set(outliers_iqr.index))),
                        "mean": float(series.mean()),
                        "std": float(series.std()),
                        "min": float(series.min()),
                        "max": float(series.max()),
                        "outlier_ratio": round(len(set(outliers_zscore.index) | set(outliers_iqr.index)) / len(series), 4)
                    }
                    
                    # 异常模式识别
                    outlier_indices = list(set(outliers_zscore.index) | set(outliers_iqr.index))
                    outlier_values = series.loc[outlier_indices]
                    
                    # 判断是偏高还是偏低
                    if outlier_values.mean() > series.median():
                        direction = "偏高"
                    else:
                        direction = "偏低"
                    
                    results["root_causes"].append({
                        "field": f"{name}.{col}",
                        "direction": direction,
                        "outlier_count": len(outlier_indices),
                        "description": f"发现{len(outlier_indices)}个{direction}异常值"
                    })
        
        self.results["dimensions"]["anomaly_deep"] = results
    
    def _zscore_outliers(self, series, threshold=3):
        """Z-Score异常检测"""
        z_scores = np.abs((series - series.mean()) / series.std())
        return series[z_scores > threshold]
    
    def _iqr_outliers(self, series):
        """IQR异常检测"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return series[(series < lower) | (series > upper)]
    
    def _text_analysis(self):
        """文本分析"""
        print("  - Text analysis...")
        
        results = {
            "field_distribution": {},
            "keyword_extraction": {},
            "text_statistics": {}
        }
        
        for name, df in self.dataframes.items():
            text_cols = df.select_dtypes(include=['object']).columns
            
            for col in text_cols[:3]:
                try:
                    series = df[col].dropna()
                    if len(series) == 0:
                        continue
                    
                    # 字段分布
                    value_counts = series.value_counts().head(10)
                    results["field_distribution"][f"{name}.{col}"] = {
                        "unique_count": int(series.nunique()),
                        "top_values": {str(k): int(v) for k, v in value_counts.items()},
                        "most_common": str(value_counts.index[0]) if len(value_counts) > 0 else "N/A"
                    }
                    
                    # 文本统计
                    if series.dtype == 'object':
                        lengths = series.astype(str).str.len()
                        results["text_statistics"][f"{name}.{col}"] = {
                            "avg_length": round(lengths.mean(), 2),
                            "max_length": int(lengths.max()),
                            "min_length": int(lengths.min())
                        }
                except Exception as e:
                    continue
        
        self.results["dimensions"]["text"] = results
    
    def _forecast_analysis(self):
        """简单预测分析"""
        print("  - Forecast analysis...")
        
        results = {
            "simple_ma": {},
            "exponential_smoothing": {},
            "trend_forecast": {}
        }
        
        for name, df in self.dataframes.items():
            date_col = self._find_date_column(df)
            if date_col is None:
                continue
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) == 0:
                continue
            
            try:
                df_temp = df.copy()
                df_temp['_date'] = pd.to_datetime(df_temp[date_col], errors='coerce')
                df_temp = df_temp.dropna(subset=['_date'])
                df_temp = df_temp.sort_values('_date')
                
                if len(df_temp) < 10:
                    continue
                
                df_temp['_month'] = df_temp['_date'].dt.to_period('M')
                
                for col in numeric_cols[:2]:
                    monthly = df_temp.groupby('_month')[col].sum()
                    
                    if len(monthly) >= 6:
                        # 简单移动平均
                        ma3 = monthly.rolling(3).mean()
                        ma5 = monthly.rolling(5).mean()
                        
                        last_ma3 = ma3.iloc[-1] if not pd.isna(ma3.iloc[-1]) else monthly.iloc[-1]
                        last_ma5 = ma5.iloc[-1] if not pd.isna(ma5.iloc[-1]) else monthly.iloc[-1]
                        
                        # 趋势判断
                        if last_ma3 > last_ma5:
                            trend = "上升"
                        elif last_ma3 < last_ma5:
                            trend = "下降"
                        else:
                            trend = "平稳"
                        
                        results["simple_ma"][f"{name}.{col}"] = {
                            "ma3": round(float(last_ma3), 2),
                            "ma5": round(float(last_ma5), 2),
                            "current": round(float(monthly.iloc[-1]), 2),
                            "trend": trend,
                            "signal": "买入" if trend == "上升" else ("卖出" if trend == "下降" else "持有")
                        }
            except Exception as e:
                continue
        
        self.results["dimensions"]["forecast"] = results
    
    def _find_date_column(self, df):
        """查找日期列"""
        date_keywords = ['date', '日期', 'time', '时间', 'datetime', '创建时间', '更新时间']
        for col in df.columns:
            if any(k in col.lower() for k in date_keywords):
                return col
        return None
    
    def _find_column(self, df, keywords):
        """根据关键词查找列"""
        for col in df.columns:
            if any(k in col.lower() for k in keywords):
                return col
        return None
    
    def _find_amount_column(self, df):
        """查找金额列"""
        amount_keywords = ['amount', '金额', 'total', '总额', 'price', '价格', 'revenue', '收入', 'sales', '销售']
        for col in df.columns:
            if any(k in col.lower() for k in amount_keywords):
                return col
        return None


def main():
    parser = argparse.ArgumentParser(description='高级数据分析')
    parser.add_argument('--data', default='.cache/loaded_data.pkl', help='数据文件')
    parser.add_argument('--relations', default='.cache/relations.json', help='关联文件')
    parser.add_argument('--output', default='.cache/advanced_analysis.json', help='输出路径')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.data, 'rb') as f:
        dataframes = pickle.load(f)
    
    relations = {}
    if Path(args.relations).exists():
        with open(args.relations, 'r', encoding='utf-8') as f:
            relations = json.load(f)
    
    print("\n=== Advanced Analysis ===\n")
    
    analyzer = AdvancedAnalyzer(dataframes, relations)
    results = analyzer.run_full_analysis()
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 打印摘要
    print(f"\n✓ Analysis complete!")
    print(f"  Dimensions analyzed: {len(results['dimensions'])}")
    print(f"  Saved to: {args.output}")
    
    # 打印关键发现
    if "correlation" in results["dimensions"]:
        corr = results["dimensions"]["correlation"]
        if corr.get("strong_correlations"):
            print(f"\n  📊 Found {len(corr['strong_correlations'])} strong correlations")
    
    if "stratification" in results["dimensions"]:
        strat = results["dimensions"]["stratification"]
        if strat.get("rfm"):
            print(f"\n  👥 RFM analysis: {len(strat['rfm'])} customer tables")
    
    if "forecast" in results["dimensions"]:
        fc = results["dimensions"]["forecast"]
        if fc.get("simple_ma"):
            print(f"\n  📈 Forecast: {len(fc['simple_ma'])} trends analyzed")

if __name__ == '__main__':
    main()
