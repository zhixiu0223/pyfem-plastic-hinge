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

### Case-04:非線性 M-θ(Mp 封頂)—— **[已完成]**
`notebooks/case04_nonlinear_Mtheta.ipynb`

新增 `RotSpring2DPlastic`(獨立檔案,不動 Case-01/02/03 已通過的
`RotSpring2D`)。用 `self.history` 記錄降伏狀態(elastic-perfectly-plastic)。

**Part A**(孤立元件):骨架線多點驗證誤差 0;額外驗證「加載到降伏→
commitHistory→卸載」正確走彈性卸載線——這是 calculix-hinge2 的 HINGE2
目前不具備的能力(HINGE2 是單調載重限定版)。

**Part B**(跟 BeamNL 組合,力控制):**必檢項目**——明確驗證 Newton-Raphson
真的有逐步疊代修正,不是像 CalculiX NLGEOM 那次一樣被矇混成一次到位的
線性解。過程中真的踩到一個坑:單一大步直接跳到目標載重在降伏臨界值附近
不收斂,改成增量式載重(20子步驟)才成功,且收斂後物理行為合理(P略超
臨界值時位移跳增到接近機構量級,彈簧彎矩精確封頂在 Mp)。

**補充(第5-7節)**:結構示意圖、完整 P-Δ capacity curve(增量式力控制
密集取樣)、以及獨立驗證用的題目摘要表(參數+邊界條件+手算公式,不需要
讀懂程式碼就能用自己的工具重建同一個模型比對)。

### Case-05:完整 portal frame pushover,四方比對 —— **[已完成]**
`notebooks/case05_portal_pushover.ipynb`

跟 `portal_frame_thesis`/`calculix-hinge2` 完全同一組參數(h=3.5, L=6.0,
E=2.05e8, Ic=2e-4, Ib=4e-4, Ac=Ab=0.02, ktheta=1e10, Mp=300, k_big=1e10,
target_disp=0.20)。第一個超靜定結構(兩柱並聯),第一次真正需要位移
控制(4鉸全降伏後結構退化成 sway mechanism,力控制在那之前就會失敗)。

`RotSpring2DPlastic` 新增選用的 `k_big` 平移綁定參數(預設0,不影響
Case-01~04 已通過的結果),用來處理柱頂鉸這種「浮空」節點——不像柱底鉸
旁邊就是地面BC,樑柱交會節點本身平移沒有其他東西固定,要靠這個項目自己
把兩節點的平移鎖住(跟 calculix-hinge2 的 HINGE2 加 k_big 的理由完全
一樣)。

過程中連續踩了四個坑(結構圖後面的說明段落有完整記錄):浮空鉸的平移
綁定機制、收斂容忍值抓錯(用 ktheta*du 當比例基準鬆到形同虛設)、忘記
呼叫 commitHistory() 導致降伏事件偵測不到(單調載重下數值巧合是對的,
但邏輯本身錯誤)、接近全機構形成的臨界點固定步長不收斂(改成失敗退回、
步長減半重試的對分法)。

**四方比對結果**:

| | K (kN/m) | 跟 OpenSeesPy 差異 | Hu (kN) | 跟 OpenSeesPy 差異 |
|---|---|---|---|---|
| 手算 | 16691.23 | +0.186% | 342.857 | 0.000% |
| OpenSeesPy | 16660.21 | — | 342.857 | — |
| CalculiX HINGE2+UB | 16660.21 | 0.000% | 342.8572 | 0.000% |
| pyFEM(這個repo) | 16559.81 | -0.603% | 343.4255 | +0.166% |

Hu 幾乎完全對上,K 差 0.6%,有明確物理來源:`BeamNL` 內建剪力變形項
(OpenSeesPy/CalculiX 都是純 Euler-Bernoulli),用很大的 G 去逼近剪力
剛性極限但沒有真的無窮大,殘留一點差異,不是巧合湊出來的。

---

## Validation Log

| ID | 主題 | 比對對象 | 結果 | 詳見 |
|---|---|---|---|---|
| VL-01 | RotSpring2D 孤立線性行為 | 手算 M/k | 相對誤差 0.000e+00,殘差 0.000e+00 | Case-01 |
| VL-02 | RotSpring2D+BeamNL 組合撓度 | 手算疊加(θ₀L+PL³/3EI) | P=10N: 相對誤差 1.363e-08;誤差隨P²衰減特徵確認殘餘來自幾何非線性 | Case-02 |
| VL-03 | RotSpring2D+BeamNL 組合撓度(垂直柱方向) | 手算疊加 + Case-02 數值比對 | 相對誤差 1.363e-08,跟 Case-02 差異 3.37e-07mm | Case-03 |
| VL-04a | RotSpring2DPlastic 骨架線(孤立) | 手算彈塑性骨架線 | 誤差 0(多個測試點) | Case-04 |
| VL-04b | 加載-卸載的彈性卸載行為 | 手算彈性卸載線 | 誤差 0,驗證了 HINGE2 目前不具備的能力 | Case-04 |
| VL-04c | 組合模型力控制過降伏點 | Mp 封頂 + 疊代收斂行為 | 彎矩精確封頂,60次疊代確認非線性有被處理到 | Case-04 |
| VL-05 | 完整 portal frame pushover(4鉸,位移控制) | 手算/OpenSeesPy/CalculiX K與Hu | K差-0.603%(剪力變形項導致,有物理解釋),Hu差+0.166% | Case-05 |
| VL-06 | 換真實Mp(238.10)後 Hu 是否隨 Mp 線性縮放 | 虛功法 mechanism 理論(Hu∝Mp) | Hu比值0.7937 = Mp比值0.7937,差異0.0005% | Case-06 |

### Case-06:換成真實配筋 Mp + 求解器 fallback 策略 —— **[已完成]**
`notebooks/case06_real_Mp.ipynb`

把 Case-05 假設的 Mp=300 換成 `taiwan-seismic-code-calc` Case-08.4
`design_column_PM()` 在 Pu=147.6kN 算出的真實標稱容量 Mp=238.10(無圍束
假設,跟手算應變相容法、`concreteproperties` 三方驗證在2%內)。

過程中真的卡住一次:C1_top/C2_top 兩個鉸幾乎同時降伏的臨界點,原本
Case-05 那套「固定步長+對分法續走」卡住不收斂(拉大疊代次數、加深對分
深度都沒用)。改成三層 fallback 策略(標準 Newton → 固定初始切線的
Modified Newton → 阻尼 Newton,全部失敗才縮步長)後才收斂,借用了
OpenSeesPy `analyze_with_fallback()` 的精神。

**驗證**:Hu(Mp=238.10)/Hu(Mp=300) = 0.7937,跟 Mp 比值(238.10/300=
0.7937)完全吻合,差異0.0005%——sway mechanism 極限剪力理論上應與 Mp
成正比(虛功法標準結論),這個線性關係直接當獨立檢驗用。

**仍待補的缺口**(不在這一課範圍內):轉角容量檢核(IO/LS/CP)、真實
桃園2層8柱幾何驗證。
