#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
表格关联发现器
自动识别表格间的关联关系
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
from collections import defaultdict
import pandas as pd
import numpy as np
from difflib import SequenceMatcher

def find_similar_columns(col1, col2, threshold=0.8):
    """判断两个列名是否相似"""
    # 直接匹配
    if col1.lower() == col2.lower():
        return True
    
    # 常见同义词
    synonyms = {
        'id': ['id', '编号', '代码', 'code', 'no'],
        'name': ['name', '名称', '姓名', 'title'],
        'date': ['date', '日期', 'time', '时间'],
        'amount': ['amount', '金额', 'money', '总额', 'total'],
        'quantity': ['quantity', '数量', 'count', 'num', 'qty'],
    }
    
    for key, values in synonyms.items():
        if col1.lower() in values and col2.lower() in values:
            return True
    
    # 字符串相似度
    return SequenceMatcher(None, col1.lower(), col2.lower()).ratio() > threshold

def analyze_column_values(df, col):
    """分析列的值特征"""
    series = df[col].dropna()
    return {
        "unique_count": series.nunique(),
        "total_count": len(series),
        "uniqueness_ratio": series.nunique() / len(series) if len(series) > 0 else 0,
        "sample_values": series.head(5).tolist(),
        "dtype": str(series.dtype)
    }

def find_relations(dataframes, summary):
    """发现表格间的关联关系"""
    relations = []
    
    file_names = list(dataframes.keys())
    
    for i, name1 in enumerate(file_names):
        for name2 in file_names[i+1:]:
            df1 = dataframes[name1]
            df2 = dataframes[name2]
            
            # 检查列名匹配
            for col1 in df1.columns:
                for col2 in df2.columns:
                    if find_similar_columns(col1, col2):
                        # 检查值重叠
                        values1 = set(df1[col1].dropna().astype(str).head(1000))
                        values2 = set(df2[col2].dropna().astype(str).head(1000))
                        
                        overlap = values1 & values2
                        if len(overlap) > 0:
                            overlap_ratio = len(overlap) / min(len(values1), len(values2))
                            
                            if overlap_ratio > 0.1:  # 10% 以上重叠
                                relation = {
                                    "table1": name1,
                                    "column1": col1,
                                    "table2": name2,
                                    "column2": col2,
                                    "relation_type": classify_relation(col1, overlap_ratio),
                                    "overlap_count": len(overlap),
                                    "overlap_ratio": round(overlap_ratio, 3),
                                    "sample_overlap": list(overlap)[:5]
                                }
                                relations.append(relation)
                                print(f"  Found: {name1}.{col1} <-> {name2}.{col2} ({overlap_ratio:.1%} overlap)")
    
    return relations

def classify_relation(column_name, overlap_ratio):
    """判断关联类型"""
    col_lower = column_name.lower()
    
    if any(k in col_lower for k in ['id', '编号', 'code', 'no']):
        return 'primary_key' if overlap_ratio > 0.9 else 'foreign_key'
    elif any(k in col_lower for k in ['date', '日期', 'time', '时间']):
        return 'time_relation'
    elif any(k in col_lower for k in ['部门', '类型', '分类', 'category', 'type', 'department']):
        return 'category_relation'
    else:
        return 'value_relation'

def main():
    parser = argparse.ArgumentParser(description='发现表格关联关系')
    parser.add_argument('--input', default='.cache/loaded_data.pkl', help='加载的数据文件')
    parser.add_argument('--summary', default='.cache/data_summary.json', help='数据摘要文件')
    parser.add_argument('--output', default='.cache/relations.json', help='关联输出路径')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.input, 'rb') as f:
        dataframes = pickle.load(f)
    
    with open(args.summary, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    print(f"Analyzing {len(dataframes)} tables for relations...\n")
    
    relations = find_relations(dataframes, summary)
    
    result = {
        "total_relations": len(relations),
        "relations": relations,
        "analysis_time": pd.Timestamp.now().isoformat()
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Found {len(relations)} relations")
    print(f"✓ Saved to {args.output}")

if __name__ == '__main__':
    main()
