import pygame
from abc import ABCMeta, abstractmethod
from copy import deepcopy
import time

def easeOutExp(t):
    return 1 if t==1 else 1 - 2 ** (-10 * t)

class Game(metaclass=ABCMeta):
    def __init__(self, edge_num, child_num, field_size, edge_len, interval, start_x, start_y, radius_k, radius_c, move_time_limit=1):
        self.LEN = edge_num
        self.NUM = child_num
        self.FIELD_SIZE = field_size
        self.pow3 = [3**i for i in range(self.FIELD_SIZE)]  #3の累乗
        self.EDGE_LEN = edge_len
        self.INTERVAL = interval
        self.START_X = start_x
        self.START_Y = start_y
        self.RADIUS_K = radius_k
        self.RADIUS_C = radius_c
        self.myKColor = (255, 105, 180)
        self.myCColor = (199, 21, 133)
        self.enKColor = (0, 191, 255)
        self.enCColor = (0, 0, 255)
        self.MOVE_TIME_LIMIT = move_time_limit
        self.move_status = 0
        self.start_time = time.perf_counter()

    def set_field(self, screen):
        for field in self.fields:
            pygame.draw.rect(screen, (0, 80, 0), field, 5)

    def set_pieces(self, screen, move_status=0):
        self.move_status = (time.perf_counter() - self.start_time) / self.MOVE_TIME_LIMIT

        #色指定
        firstKcolor = self.myKColor if self.state.all_pieces.ox == 1 else self.enKColor
        secondKcolor = self.enKColor if self.state.all_pieces.ox == 1 else self.myKColor
        firstCcolor = self.myCColor if self.state.all_pieces.ox == 1 else self.enCColor
        secondCcolor = self.enCColor if self.state.all_pieces.ox == 1 else self.myCColor

        if self.move_status >= 1:
            self.state.old_pieces = self.state.all_pieces

        myKcenter, enKcenter, myCcenter, enCcenter = self.points_with_easing(easeOutExp)
        #描画
        pygame.draw.circle(screen, firstKcolor, myKcenter, self.RADIUS_K)
        pygame.draw.circle(screen, secondKcolor, enKcenter, self.RADIUS_K)
        for center in myCcenter:
            pygame.draw.circle(screen, firstCcolor, center, self.RADIUS_C)
        for center in enCcenter:
            pygame.draw.circle(screen, secondCcolor, center, self.RADIUS_C)

    @abstractmethod
    def default_all_pieces(self):
        pass

    def next(self, strategy):
        self.state = self.state.next(strategy(self.state))

    def points_with_easing(self, func):
        myK, enK, myC, enC = self.state.all_pieces.each_piece()
        myKpos = myK.pos if self.state.all_pieces.ox == 1 else -1 - myK.pos
        enKpos = enK.pos if self.state.all_pieces.ox == 1 else -1 - enK.pos
        myCpos = [p.pos if self.state.all_pieces.ox == 1 else -1 - p.pos for p in myC]
        enCpos = [p.pos if self.state.all_pieces.ox == 1 else -1 - p.pos for p in enC]
        myKcenter = self.CENTERS[myKpos]
        enKcenter = self.CENTERS[enKpos]
        myCcenter = [self.CENTERS[pos] for pos in myCpos]
        enCcenter = [self.CENTERS[pos] for pos in enCpos]

        #前回状態の座標
        fromMyK, fromEnK, fromMyC, fromEnC = self.state.all_pieces.pick_dif(self.state.old_pieces).each_piece()
        fromMyKpos = fromMyK.pos if self.state.old_pieces.ox == 1 else -1 - fromMyK.pos
        fromEnKpos = fromEnK.pos if self.state.old_pieces.ox == 1 else -1 - fromEnK.pos
        fromMyCpos = [p.pos if self.state.old_pieces.ox == 1 else -1 - p.pos for p in fromMyC]
        fromEnCpos = [p.pos if self.state.old_pieces.ox == 1 else -1 - p.pos for p in fromEnC]

        myKcenterFrom = self.CENTERS[fromMyKpos]
        enKcenterFrom = self.CENTERS[fromEnKpos]
        myCcenterFrom = [self.CENTERS[pos] for pos in fromMyCpos]
        enCcenterFrom = [self.CENTERS[pos] for pos in fromEnCpos]

        k = func(self.move_status)
        myKcenter = (myKcenter[0] * k + myKcenterFrom[0] * (1 - k), myKcenter[1] * k + myKcenterFrom[1] * (1 - k))
        enKcenter = (enKcenter[0] * k + enKcenterFrom[0] * (1 - k), enKcenter[1] * k + enKcenterFrom[1] * (1 - k))
        for i in range(len(myCcenter)):
            myCcenter[i] = (myCcenter[i][0] * k + myCcenterFrom[i][0] * (1 - k), myCcenter[i][1] * k + myCcenterFrom[i][1] * (1 - k))
        for i in range(len(enCcenter)):
            enCcenter[i] = (enCcenter[i][0] * k + enCcenterFrom[i][0] * (1 - k), enCcenter[i][1] * k + enCcenterFrom[i][1] * (1 - k))

        return myKcenter, enKcenter, myCcenter, enCcenter

    class State(metaclass=ABCMeta):
        def __init__(self, parent, all_pieces=None, old_pieces=None):
            self.parent = parent
            self.LEN = self.parent.LEN
            self.FIELD_SIZE = self.parent.FIELD_SIZE
            self.NUM = self.parent.NUM
            self.pow3 = self.parent.pow3
            self.all_pieces = all_pieces if all_pieces else self.parent.default_all_pieces()
            self.old_pieces = old_pieces if old_pieces else self.all_pieces
            self.myK, self.enK, self.myC, self.enC = self.all_pieces.each_piece()

            self.myPiece = 2 * self.pow3[self.myK.pos]
            for p in self.myC:
                self.myPiece += self.pow3[p.pos]

            self.enPiece = 2 * self.pow3[self.enK.pos]
            for p in self.enC:
                self.enPiece += self.pow3[p.pos]

        def position(self, myPiece=None, enPiece=None):
            if myPiece is None:
                myPiece = self.myPiece
            if enPiece is None:
                enPiece = self.enPiece

            myCpos, myKpos, enCpos, enKpos = [], -1, [], -1  #自分/敵の子駒の座標のリスト/王駒の座標
            p = myPiece
            for i in range(self.FIELD_SIZE):
                if p % 3 == 1:
                    myCpos.append(i)
                if p % 3 == 2:
                    myKpos = i
                p = p // 3
            q = enPiece
            for i in range(self.FIELD_SIZE):
                if q % 3 == 1:
                    enCpos.append(i)
                if q % 3 == 2:
                    enKpos = i
                q = q // 3
            return myKpos, myCpos, enKpos, enCpos

        @abstractmethod
        def legal_actions(self):  #現在の状態からの合法手を返す
            pass

        def lose(self):  #敗北していればTrue
            return self.enPiece == self.parent.DEFAULT_PIECE  #相手の駒が自分の初期位置にいるかどうか

        def draw(self):  #引き分けならTrue
            return (not self.lose()) and (not self.legal_actions())  #負けていないがそもそも動けない

        def end(self):  #ゲームが終わっているか
            return self.lose() or self.draw()

        def winner(self):
            if self.lose():
                winner = -self.all_pieces.ox
                return winner
            if self.draw():
                return 0

        @abstractmethod
        def next(self, action, real_flag=True):  #現在の状態からactionの手を打った後の状態
            def reverse(x):  #ハッシュ値xの3進法表示を反転
                res = 0
                for i in range(self.FIELD_SIZE):
                    res += x % 3 * self.pow3[self.FIELD_SIZE - 1 - i]
                    x = x // 3
                return res

            #手番が交代するので、自分と敵の座標を交換、目線も入れ替え(ハッシュ値の3進法表示を逆順にする)
            #action=(from, to, k)をすると自駒の配置のハッシュ値は k * (3^to - 3^from)が加算される
            nextMyPiece = reverse(self.enPiece)
            nextEnPiece = reverse(self.myPiece + action[2] * (self.pow3[action[1]] - self.pow3[action[0]]))
            nextMyKpos, nextMyCpos, nextEnKpos, nextEnCpos = self.position(nextMyPiece, nextEnPiece)
            nextMyK = Game.Piece("king", nextMyKpos, self.FIELD_SIZE)
            nextEnK = Game.Piece("king", nextEnKpos, self.FIELD_SIZE)
            nextMyC = [Game.Piece("child", c, self.FIELD_SIZE) for c in nextMyCpos]
            nextEnC = [Game.Piece("child", c, self.FIELD_SIZE) for c in nextEnCpos]

            if real_flag:
                self.old_pieces = self.all_pieces.reverse()
                self.parent.start_time = time.perf_counter()
            return Game.AllPieces(nextMyK, nextEnK, nextMyC, nextEnC, -self.all_pieces.ox), self.old_pieces

    class Piece:
        def __init__(self, roll, pos, FIELD_SIZE):
            self.roll = roll
            self.pos = pos
            self.FIELD_SIZE = FIELD_SIZE

        def change(self):
            self.pos = -1 - self.pos

        def __lt__(self, other):
            return self.pos % self.FIELD_SIZE < other.pos % self.FIELD_SIZE

        def __eq__(self, other):
            return self.roll == other.roll and self.pos % self.FIELD_SIZE == other.pos % self.FIELD_SIZE

        def __str__(self):
            return self.roll + " " + str(self.pos)

    class AllPieces:
        def __init__(self, myK, enK, myC, enC, ox, sort_flag=True):
            self.ox = ox
            self.myK = myK
            self.enK = enK
            self.myC = sorted(myC) if sort_flag else myC
            self.enC = sorted(enC, reverse=True) if sort_flag else enC

        def each_piece(self):
            return self.myK, self.enK, self.myC, self.enC

        def get_positions(self):
            return self.myK.pos, self.enK.pos, [p.pos for p in self.myC], [p.pos for p in self.enC]

        def reverse(self):
            myK, enK, myC, enC = self.each_piece()
            enK.change()
            myK.change()
            for i in range(len(enC)):
                enC[i].change()
            for i in range(len(myC)):
                myC[i].change()
            return Game.AllPieces(enK, myK, enC, myC, -self.ox)

        def difference(self, other):
            if self.myK != other.myK:
                return self.myK, other.myK

            if self.enK != other.enK:
                return self.enK, other.enK

            difSelf, difOther = self.myK, self.enK
            for Cs in [(self.myC, other.myC), (self.enC, other.enC)]:
                for selfP in Cs[0]:
                    flag = False
                    for otherP in Cs[1]:
                        if selfP == otherP:
                            flag = True
                            break
                    if not flag:
                        difSelf = deepcopy(selfP)

            for Cs in [(other.myC, self.myC), (other.enC, self.enC)]:
                for otherP in Cs[0]:
                    flag = False
                    for selfP in Cs[1]:
                        if otherP == selfP:
                            flag = True
                            break
                    if not flag:
                        difOther = deepcopy(otherP)

            if difSelf == self.myK:
                return False
            return difSelf, difOther

        def pick_dif(self, other):
            dif = deepcopy(self.difference(other))

            if not dif:
                return self

            difSelf, difOther = dif
            resMyK, resEnK = deepcopy(self.each_piece())[:2]

            if resMyK == difSelf:
                resMyK = difOther
            if resEnK == difSelf:
                resEnK = difOther

            resMyC = []
            for c in deepcopy(self.myC):
                if c == difSelf:
                    resMyC.append(difOther)
                else:
                    resMyC.append(c)

            resEnC = []
            for c in deepcopy(self.enC):
                if c == difSelf:
                    resEnC.append(difOther)
                else:
                    resEnC.append(c)

            res = Game.AllPieces(resMyK, resEnK, resMyC, resEnC, self.ox, sort_flag=False)
            return res

        def __str__(self):
            res = str(self.myK.pos) + ","
            for p in self.myC:
                res += str(p.pos) + ","
            res += str(self.enK.pos) + ","
            for p in self.enC:
                res += str(p.pos) + ","
            return res