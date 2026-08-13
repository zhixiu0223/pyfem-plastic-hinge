# ROADMAP

本 repo 的定位:在 pyFEM 裡重新實作 CalculiX `HINGE2` 的塑性鉸方法論,
用來跟 [[plastic-hinge-cross-verification]] 現有的 OpenSeesPy / CalculiX
兩條線做第三方交叉驗證。跟 `taiwan-seismic-code-calc` 一樣的核心原則:

> 越大的模型,越不知道錯在哪。

每個 Case 獨立驗證、獨立當教學節點。新 Case 只在前一個**完全通過**後開始。

## Case 序列

### Case-01:RotSpring2D 孤立最小測試 —— **[已完成]**
`notebooks/case01_rotspring_isolated.ipynb`

線性彈性轉角彈簧元素(M=k·Δθ),兩重合節點,節點1固定當地面、節點2固定
平移轉角自由,施加彎矩比對手算 M/k。純線性問題,理論上應為機器精度一致。

### Case-02:跟 BeamNL 組合 —— **[已完成]**
`notebooks/case02_rotspring_beam_combo.ipynb`

彈簧接梁一端,尖端施力,驗證總撓度 = 彈簧貢獻 + 梁本身撓度(手算疊加)。
對應 calculix-hinge2 專案的 UB+HINGE2 Stage 4 combination test。

P=10N(小變形範圍)時相對誤差 1.363e-08。額外做了診斷:P=1000N 時誤差
1.362e-4,且誤差隨載重呈平方衰減(每次減半降到約1/4)——確認殘餘誤差
是 `BeamNL` 的幾何非線性(co-rotational)造成,不是元素組合寫錯,元素
本身在小變形線性範圍內驗證通過。

### Case-03:柱子方向幾何驗證 —— **[已完成]**
`notebooks/case03_column_orientation.ipynb`

垂直柱(非水平)+底部塑鉸+側向力,對應 calculix-hinge2 的
「portal-frame-relevant geometry test」。

P=10N 時相對誤差 1.363e-08,跟 Case-02(水平梁)數值比對差異 3.37e-07mm
(浮點雜訊等級)——確認 `BeamNL` 座標轉換在垂直方向正確,`RotSpring2D`
不受方向影響。

### Case-04:非線性 M-θ(Mp 封頂)—— **[尚未開始]**
用 `self.history` 記錄降伏狀態(elastic-perfectly-plastic,監控式加載)。
**必檢項目**:明確驗證 Newton-Raphson 疊代真的有處理到這個自訂元素的
非線性(殘差收斂到位),不是像 CalculiX 那次 `NLGEOM` 陷阱一樣被隱藏的
線性解矇混過去。

### Case-05:完整 portal frame pushover,三方比對 —— **[尚未開始]**
跟 OpenSeesPy(`pynite_event_pushover.py` 那條線)、CalculiX HINGE2+UB
(已完成,K_ccx 對 K_ops 差 0.00000%)三方比對。

---

## Validation Log

| ID | 主題 | 比對對象 | 結果 | 詳見 |
|---|---|---|---|---|
| VL-01 | RotSpring2D 孤立線性行為 | 手算 M/k | 相對誤差 0.000e+00,殘差 0.000e+00 | Case-01 |
| VL-02 | RotSpring2D+BeamNL 組合撓度 | 手算疊加(θ₀L+PL³/3EI) | P=10N: 相對誤差 1.363e-08;誤差隨P²衰減特徵確認殘餘來自幾何非線性 | Case-02 |
| VL-03 | RotSpring2D+BeamNL 組合撓度(垂直柱方向) | 手算疊加 + Case-02 數值比對 | 相對誤差 1.363e-08,跟 Case-02 差異 3.37e-07mm | Case-03 |
