import global_value as g
from funcy import *
from pygame.locals import *
from game import Game

class SquareGame(Game):
    def __init__(self, field_len, child_num):
        super().__init__(field_len, child_num, field_len**2, 55, 5, 300, 170, 18, 12)

        self.state = self.SquareState(self)
        self.DEFAULT_PIECE = self.state.myPiece
        self.active = True

        self.CENTERS = [(self.START_X + (self.EDGE_LEN + self.INTERVAL) * (i % self.LEN) + self.EDGE_LEN // 2, self.START_Y + (self.EDGE_LEN + self.INTERVAL) * (i // self.LEN) + self.EDGE_LEN // 2)
                        for i in range(self.LEN**2)]

        self.fields = [
            Rect(
                self.START_X + (self.EDGE_LEN + self.INTERVAL) *
                (i % self.LEN), self.START_Y +
                (self.EDGE_LEN + self.INTERVAL) * (i // self.LEN),
                self.EDGE_LEN, self.EDGE_LEN) for i in range(self.LEN**2)
        ]

    def default_all_pieces(self):
        myK = self.Piece("king", 0, self.FIELD_SIZE)
        enK = self.Piece("king", -1, self.FIELD_SIZE)
        myC = sum([[self.Piece("child", i + self.LEN * j, self.FIELD_SIZE) for j in range(self.NUM - i)] for i in range(self.NUM)], [])[1:]
        enC = sum([[self.Piece("child", -i - self.LEN * j - 1, self.FIELD_SIZE) for j in range(self.NUM - i)] for i in range(self.NUM)], [])[1:]
        return self.AllPieces(myK, enK, myC, enC, 1)

    class SquareState(Game.State):
        def __init__(self, parent, all_pieces=None, old_pieces=None):
            super().__init__(parent, all_pieces, old_pieces)

        def legal_actions(self):    #現在の状態からの合法手を返す
            myKpos, myCpos, enKpos, enCpos = self.position()
            exist = [0] * (self.LEN**2)       #i番目の点に駒があれば exist[i] = 1
            exist[myKpos] = 1
            for e in myCpos:
                exist[e] = 1
            exist[enKpos] = 1
            for e in enCpos:
                exist[e] = 1
            res = []    #res[i] = (from, to, k) で座標fromから座標toに駒 k (1or2)を移動
            for serv in myCpos:
                if serv % self.LEN < self.LEN - 1 and not exist[serv+1]:   #子駒が右に一つ動く
                    res.append((serv, serv+1, 1))
                if serv // self.LEN < self.LEN - 1 and not exist[serv+self.LEN]:   #子駒が下に一つ動く
                    res.append((serv, serv+self.LEN, 1))

                serv_goals = []
                def dfs_serv_skip(frm):
                    if frm % self.LEN < self.LEN-2 and exist[frm+1] and (not exist[frm+2]) and myKpos != frm+1 and enKpos !=frm+1:
                        serv_goals.append(frm+2)
                        dfs_serv_skip(frm+2)
                    if frm // self.LEN < (self.LEN-2) and exist[frm+self.LEN] and (not exist[frm+2*self.LEN]) and myKpos != frm+self.LEN and enKpos != frm+self.LEN:
                        serv_goals.append(frm+self.LEN*2)
                        dfs_serv_skip(frm+self.LEN*2)
                dfs_serv_skip(serv)
                for goal in list(set(serv_goals)):
                    res.append((serv, goal, 1))

            king_goals = []
            if myKpos % self.LEN < self.LEN - 1 and not exist[myKpos+1]:   #王駒が右に一つ動く
                king_goals.append(myKpos + 1)
            if myKpos // self.LEN < self.LEN - 1 and not exist[myKpos+self.LEN]:   #王駒が下に一つ動く
                king_goals.append(myKpos + self.LEN)

            def dfs_king_skip(frm):
                for add in range(2, self.LEN - frm % self.LEN ):
                    to = frm + add
                    if exist[to]:
                        continue
                    flag = True
                    for j in range(frm + 1, to):
                        if not exist[j]:
                            flag = False
                    if flag:
                        king_goals.append(to)
                        dfs_king_skip(to)
                for add in range(2, self.LEN - frm // self.LEN):
                    to = frm + add * self.LEN
                    if exist[to]:
                        continue
                    flag = True
                    for j in range(frm + self.LEN, to, self.LEN):
                        if not exist[j]:
                            flag = False
                    if flag:
                        king_goals.append(to)
                        dfs_king_skip(to)

            dfs_king_skip(myKpos)
            for goal in list(set(king_goals)):
                res.append((myKpos, goal, 2))
            return res

        def next(self, action, real_flag=True):
            next_pieces, old_pieces = super().next(action, real_flag)
            return self.parent.SquareState(self.parent, all_pieces=next_pieces, old_pieces=old_pieces)

        def __str__(self):  #printで読んだ時の表示
            myKing, myServ, enKing, enServ = self.position()
            ch_ls = ['.'] * (self.parent.FIELD_SIZE)
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
                    if res and (len(res)+1) % (self.LEN+1) == 0:
                        res += '\n'
                    res += character
            else:  #後手目線
                ch_ls[myKing] = enKch
                for e in myServ:
                    ch_ls[e] = enSch
                ch_ls[enKing] = myKch
                for e in enServ:
                    ch_ls[e] = mySch
                for character in ch_ls:
                    if res and (len(res)+1) % (self.LEN+1) == 0:
                        res = '\n' + res
                    res = character + res
            return res + "\n"