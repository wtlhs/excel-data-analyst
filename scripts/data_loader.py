#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel 数据批量加载器
支持 .xlsx, .xls, .csv 格式
"""

# Windows 兼容性：设置 UTF-8 编码
import sys
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import argparse
import json
import os
import pickle
from pathlib import Path
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def load_excel_files(directory, cache_dir=".cache"):
    """批量加载目录下的所有 Excel 文件"""
    Path(cache_dir).mkdir(exist_ok=True)
    
    files = []
    for ext in ['*.xlsx', '*.xls', '*.csv']:
        files.extend(Path(directory).glob(ext))
    
    dataframes = {}
    summary = {
        "total_files": len(files),
        "files": [],
        "load_time": pd.Timestamp.now().isoformat()
    }
    
    for file_path in files:
        try:
            if file_path.suffix == '.csv':
                # Windows 兼容：尝试多种编码
                df = None
                for encoding in ['utf-8-sig', 'gbk', 'gb2312', 'utf-8', 'latin-1']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if df is None:
                    raise UnicodeDecodeError("无法识别文件编码")
            else:
                df = pd.read_excel(file_path)
            
            name = file_path.stem
            dataframes[name] = df
            
            # 生成摘要
            file_summary = {
                "name": name,
                "path": str(file_path),
                "shape": list(df.shape),
                "columns": list(df.columns),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "null_counts": {col: int(df[col].isnull().sum()) for col in df.columns},
                "sample_values": {col: df[col].dropna().head(3).tolist() for col in df.columns}
            }
            summary["files"].append(file_summary)
            
            print(f"✓ Loaded: {name} ({df.shape[0]} rows, {df.shape[1]} columns)")
            
        except Exception as e:
            print(f"✗ Failed to load {file_path}: {e}")
    
    # 缓存数据
    cache_file = Path(cache_dir) / "loaded_data.pkl"
    with open(cache_file, 'wb') as f:
        pickle.dump(dataframes, f)
    
    return summary, dataframes

def main():
    parser = argparse.ArgumentParser(description='批量加载 Excel 数据')
    parser.add_argument('--dir', required=True, help='数据文件目录')
    parser.add_argument('--output', default='.cache/data_summary.json', help='摘要输出路径')
    parser.add_argument('--cache', default='.cache', help='缓存目录')
    
    args = parser.parse_args()
    
    summary, _ = load_excel_files(args.dir, args.cache)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Summary saved to {args.output}")
    print(f"✓ Data cached to {args.cache}/loaded_data.pkl")

if __name__ == '__main__':
    main()
