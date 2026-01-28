import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from tests.test_glm4_params_mega import MegaParamsTester

def diagnose():
    print("🔍 診斷參數網格生成...")
    print()
    
    tester = MegaParamsTester()
    
    # 檢查各階段
    print(f"階段 1 (粗略採樣): {len(tester.coarse_grid)} 組")
    if tester.coarse_grid:
        print(f"  第一個: {tester.coarse_grid[0]}")
        print(f"  最後一個: {tester.coarse_grid[-1]}")
    
    print()
    print(f"階段 2 (精細採樣): {len(tester.fine_grid)} 組")
    if tester.fine_grid:
        print(f"  第一個: {tester.fine_grid[0]}")
        print(f"  最後一個: {tester.fine_grid[-1]}")
    
    print()
    print(f"階段 3 (驗證採樣): {len(tester.validation_grid)} 組")
    if tester.validation_grid:
        print(f"  第一個: {tester.validation_grid[0]}")
        print(f"  最後一個: {tester.validation_grid[-1]}")
    
    print()
    print(f"總計: {len(tester.param_grid)} 組")
    print()
    
    # 檢查批次劃分
    batch_size = 50
    total_batches = (len(tester.param_grid) + batch_size - 1) // batch_size
    print(f"批次大小: {batch_size}")
    print(f"理論批次數: {total_batches}")
    print()
    
    # 檢查每批參數數量
    print("各批次參數數量:")
    for i in range(min(12, total_batches)):
        start_idx = i * batch_size
        end_idx = min(start_idx + batch_size, len(tester.param_grid))
        count = end_idx - start_idx
        print(f"  批次 {i}: {count} 組 (索引 {start_idx}-{end_idx})")
    
    print()
    
    # 檢查是否有批次超出範圍
    if total_batches < 12:
        print(f"⚠️  警告：只能生成 {total_batches} 批次，不足 12 批次")
        print(f"⚠️  缺少 {12 - total_batches} 批次")
    
    print()
    print("🔍 診斷完成")

if __name__ == "__main__":
    diagnose()
