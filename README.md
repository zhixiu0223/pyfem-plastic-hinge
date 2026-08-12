# pyfem-plastic-hinge

把 CalculiX `HINGE2`(見 [calculix-hinge2-element](https://github.com/zhixiu0223/calculix-hinge2-element))
的塑性鉸方法論,在 [pyFEM](https://github.com/jjcremmers/PyFEM) 裡用原生 Python
自訂元素介面重新實作——不是移植 Fortran 程式碼,是移植驗證流程與力學公式。

格式仿照 [taiwan-seismic-code-calc](https://github.com/zhixiu0223/taiwan-seismic-code-calc):
每個 Case 獨立驗證、獨立教學節點,前一個完全通過才開下一個;ROADMAP.md
維護 Validation Log;GitHub Actions 在每次 push 時重跑所有 notebook。

## Case 序列

| Case | 內容 | 狀態 |
|---|---|---|
| Case-01 | `RotSpring2D` 孤立最小測試(線性彈性,θ=M/k 對手算) | **已完成** |
| Case-02 | 跟 `BeamNL` 串接(彈簧+梁組合撓度對手算疊加) | 尚未開始 |
| Case-03 | 柱子方向(垂直)幾何驗證 | 尚未開始 |
| Case-04 | 非線性 M-θ(Mp 封頂)+ 疊代自我檢查 | 尚未開始 |
| Case-05 | 完整 portal frame pushover,跟 OpenSeesPy + CalculiX HINGE2 三方比對 | 尚未開始 |

詳見 `ROADMAP.md`。
