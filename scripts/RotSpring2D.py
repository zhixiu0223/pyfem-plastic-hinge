# RotSpring2D — 2-node 2D 轉角彈簧元素 (pyFEM 自訂元素, Stage 1: 線性彈性)
#
# 定位:pyfem-plastic-hinge 專案 Case-01 的核心元件。對應 calculix-hinge2
# 專案裡 HINGE2 的角色,但用 pyFEM 原生 Python 元素介面實作,不是 CalculiX
# *USER ELEMENT。
#
# 力學假設(跟 HINGE2 Stage 1-2 完全對應):
#   - 兩個節點理論上重合(同一個實體位置的兩側)
#   - 只有轉角自由度 rz 之間有相對勁度 k(即 M = k * (rz2 - rz1))
#   - 平移自由度 u, v 本元件不提供任何勁度貢獻——如果要讓兩節點的位移被
#     綁在一起,必須另外處理(邊界條件或極大剛度平移彈簧),這是 Stage 1
#     刻意先不做的簡化,留給 Stage 3(跟樑元素組合)時處理
#
# 尚未實作(刻意留到後面階段,不是遺漏):
#   - Mp 降伏封頂(Stage 4)
#   - 跨增量步的降伏狀態記憶 self.history(Stage 4 才需要)

from .Element import Element
from numpy import zeros


class RotSpring2D(Element):

    # 跟 pyFEM 既有的 BeamNL / TimoshenkoBeam 用同一組 dofTypes,
    # 這樣才能跟樑元素共用同一個節點的自由度空間(Stage 3 需要)
    dofTypes = ['u', 'v', 'rz']

    def __init__(self, elnodes, props):
        Element.__init__(self, elnodes, props)
        self.family = "BEAM"

    def getTangentStiffness(self, elemdat):

        k = elemdat.props.k

        # state 向量排列: [u1, v1, rz1, u2, v2, rz2] (每個節點按 dofTypes 順序排)
        theta1 = elemdat.state[2]
        theta2 = elemdat.state[5]
        dtheta = theta2 - theta1

        M = k * dtheta

        elemdat.fint = zeros(6)
        elemdat.fint[2] = -M
        elemdat.fint[5] = M

        elemdat.stiff = zeros((6, 6))
        elemdat.stiff[2, 2] = k
        elemdat.stiff[2, 5] = -k
        elemdat.stiff[5, 2] = -k
        elemdat.stiff[5, 5] = k

    def getInternalForce(self, elemdat):
        # 跟 getTangentStiffness 共用同一套內力計算,避免兩處各寫一次公式
        # 導致不一致(這正是上次在 diagnostic 裡抓到 def_releases bug 的
        # 教訓——重複邏輯是 bug 的溫床)
        self.getTangentStiffness(elemdat)
