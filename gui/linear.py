import global_value as g
from funcy import *
from pygame.locals import *
from game import Game

class LinearGame(Game):
    def __init__(self, field_len, child_num):
        super().__init__(field_len, child_num, field_len, 80, 10, 30, 220, 30, 20)
        self.state = self.LinearState(self)
        self.DEFAULT_PIECE = self.state.myPiece
        self.active = True

        self.CENTERS = [(self.START_X + (self.EDGE_LEN + self.INTERVAL) * i +
                         self.EDGE_LEN // 2, self.START_Y + self.EDGE_LEN // 2)
                        for i in range(self.LEN)]

        self.fields = [
            Rect(self.START_X + (self.EDGE_LEN + self.INTERVAL) * i,
                 self.START_Y, self.EDGE_LEN, self.EDGE_LEN)
            for i in range(self.LEN)
        ]

    def default_all_pieces(self):
        myK = self.Piece("king", 0, self.FIELD_SIZE)
        enK = self.Piece("king", -1, self.FIELD_SIZE)
        myC = [self.Piece("child", i + 1, self.FIELD_SIZE) for i in range(self.NUM)]
        enC = [self.Piece("child", -i - 2, self.FIELD_SIZE) for i in range(self.NUM)]
        return self.AllPieces(myK, enK, myC, enC, 1)

    class LinearState(Game.State):
        def __init__(self, parent, all_pieces=None, old_pieces=None):
            super().__init__(parent, all_pieces, old_pieces)

        def legal_actions(self):  #現在の状態からの合法手を返す
            myKpos, myCpos, enKpos, enCpos = self.position()
            exist = [0] * self.LEN  #i番目の点に駒があれば exist[i] = 1
            exist[myKpos] = 1
            for e in myCpos:
                exist[e] = 1
            exist[enKpos] = 1
            for e in enCpos:
                exist[e] = 1
            res = []  #res[i] = (from, to, k) で座標fromから座標toに駒 k (1or2)を移動
            for serv in myCpos:
                if serv < self.LEN - 1 and not exist[serv + 1]:  #子駒が右に一つ動く
                    res.append((serv, serv + 1, 1))
                e = serv
                while e < self.LEN - 2:  #子駒が1つ飛ばしを1回以上繰り返す
                    if exist[e +
                             1] and (not exist[e + 2]
                                     ) and myKpos != e + 1 and enKpos != e + 1:
                        res.append((serv, e + 2, 1))
                        e += 2
                    else:
                        break

            if myKpos < self.LEN - 1 and not exist[myKpos + 1]:  #王駒が右に一つ動く
                res.append((myKpos, myKpos + 1, 2))

            frm = myKpos  #王が1つ以上の駒を飛ばすのを1回以上繰り返す
            while frm < self.LEN - 1 and exist[frm + 1]:
                to = frm + 1
                while to < self.LEN and exist[to]:
                    to += 1
                if to < self.LEN:
                    res.append((myKpos, to, 2))
                    frm = to
                else:
                    break
            return res

        def next(self, action, real_flag=True):
            next_pieces, old_pieces= super().next(action, real_flag)
            return self.parent.LinearState(self.parent, all_pieces=next_pieces, old_pieces=old_pieces)

        def __str__(self):  #printで読んだ時の表示
            myKing, myServ, enKing, enServ = self.position()
            ch_ls = ['.'] * self.LEN
            res = ""
            myKch, mySch, enKch, enSch = 'O', 'o', 'X', 'x'
            if self.ox == 1:  #先手目線
                ch_ls[myKing] = myKch
                for e in myServ:
                    ch_ls[e] = mySch
                ch_ls[enKing] = enKch
                for e in enServ:
                    ch_ls[e] = enSch
                for character in ch_ls:
                    res += character
            else:  #後手目線
                ch_ls[myKing] = enKch
                for e in myServ:
                    ch_ls[e] = enSch
                ch_ls[enKing] = myKch
                for e in enServ:
                    ch_ls[e] = mySch
                for character in ch_ls:
                    res = character + res
            return res + "\n"