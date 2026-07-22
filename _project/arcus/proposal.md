## Why

routing_law.py 目前既是「邏輯引擎」也是「記憶載體」——每次系統學到新模式，就要改一段 Python 程式碼。這帶來三個問題：每次演化都有語法出錯的風險；改代碼需要重啟服務；無法用數值梯度量化哪條規則最有效。

IQ 350 張量流動架構把「邏輯」與「記憶」完全分離：routing_law.py 凍結為不變的物理定律，所有系統演化只調整 DNA_weights.json 裡的浮點數。系統從此不需要碰代碼就能變聰明。

## What Changes

- **DNA_weights.json**：每條規則一個 weight 值（0.0–1.0），routing_law.py 啟動時讀入，決定哪些規則要注入 prompt、注入多強
- **error_tensors.json**：每輪結束後記錄失敗事件（違規類型、偏差值 L、時間戳），作為 weight_baker.py 的訓練信號
- **weight_baker.py**：讀取 error_tensors.json，計算各規則的命中率與平均 L 值，做梯度調整後更新 DNA_weights.json；可手動觸發或定時執行
- **routing_law.py**：凍結現行版本，只在啟動時讀取 DNA_weights.json，不再有任何演化邏輯
- **Kitchen 快照**：把現行 server.py + kitchen_hooks.py + routing_law.py 全部納入 arcus 版控，作為基準起點

## Capabilities

### New Capabilities

- `tensor-weight-reader`：routing_law.py 啟動時讀取 DNA_weights.json，把 weight 轉換為規則注入強度
- `error-tensor-writer`：每輪 Stop 後，scan() 把違規事件序列化進 error_tensors.json
- `weight-baker`：梯度調整引擎，讀取 error_tensors.json 輸出新的 DNA_weights.json

### Modified Capabilities

- `routing-law`：移除所有演化邏輯，只保留靜態規則定義與權重讀取介面

## Impact

- 修改 `routing_law.py`（移除 dynamic rule generation，加入 weight loader）
- 新增 `DNA_weights.json`（初始值全設 0.5）
- 新增 `error_tensors.json`（初始為空陣列）
- 新增 `weight_baker.py`
- 系統演化流程從「改代碼 → 重啟」變為「跌倒 → error_tensor 記錄 → baker 梯度調整 → 下輪啟動生效」
- routing_law.py 凍結後，每次變更 DNA_weights.json 無需重啟服務（下輪 prompt 建構時自動讀入）
