from random   import randint
from funcy    import *
from operator import *
from math     import log
import time

# ランダムプレイ
def Random(state):
    actions = state.legal_actions()
    return actions[randint(0, len(actions) - 1)]

#状態stateからランダムに最後までプレイ(プレイアウト)した時に得られる報酬
def playout(state):
    #ゲームが終わっている場合
    if state.lose():
        return -1
    if state.draw():
        return  0
    #ゲームが終わっていない場合
    # -(次の手番のプレイヤーの得る報酬)
    return -playout(state.next(Random(state), real_flag=False))

# 集合の最大値のインデックス
def argmax(collection, key=None):
    return collection.index(max(collection, key=key) if key else max(collection))

# 原始モンテカルロ探索
def PureMCT(state):
    values = [0] * len(state.legal_actions())
    PLAY_OUT_TIMES = 10
    for i, action in enumerate(state.legal_actions()):
        for _ in range(PLAY_OUT_TIMES):
            #action[i]からランダムにPLAY_OUT_TIMES回プレイアウトする時の報酬を採用
            #マイナスをつけることに注意(視点が切り替わる)
            values[i] += -playout(state.next(action))

    #ランダムなプレイアウトの結果最も報酬の多かったactionを返す
    return state.legal_actions()[argmax(values)]

#モンテカルロ木探索
def UCT(state):
    TRY_TIMES = 200
    EXPAND_THRESHOLD = 10
    class node:
        def __init__(self, state):
            self.state       = state
            self.w           = 0     #価値
            self.n           = 0     #試行回数
            self.child_nodes = None  #子ノード(合法手で行動した後の状態,未展開)

        def evaluate(self):         #盤面評価
            self.n += 1
            if self.child_nodes:  #子ノードが展開されている場合
                self.w += -self.next_child_node().evaluate()
                #子ノードを選んでその価値を"引く"(子ノードは相手の手番なので)

            else:                 #子ノードが展開されていない場合
                self.w += playout(self.state)    #まずはランダムにシミュレーション
                if self.n == EXPAND_THRESHOLD:   #しばらくしたら子ノードを列挙
                    self.expand

            return self.w

        def expand(self):   #子ノードを列挙
            self.child_nodes = tuple(node(self.state.next(action, real_flag=False))for action in self.state.legal_actions())

        def next_child_node(self):
            def ucb1_values():  #子ノード達のUCB1のリスト
                t = sum(map(attrgetter('n'), self.child_nodes))
                return tuple(-child_node.w / child_node.n + 2 * \
                (2 * log(t) / child_node.n) ** 0.5 for child_node in self.child_nodes)

            for child_node in self.child_nodes: #まだ試してない子ノードは調べる(0除算の都合)
                if child_node.n == 0:
                    return child_node

            return self.child_nodes[argmax(ucb1_values())] #UCB1が最大の子ノードをreturn

    root_node = node(state)
    root_node.expand()

    for _ in range(TRY_TIMES):  #TRY_TIMES回の盤面評価を行う
        root_node.evaluate()
    #試行回数(n)のもっとも多いlegal_actionを採用
    return state.legal_actions()[argmax(root_node.child_nodes, key=attrgetter('n'))]