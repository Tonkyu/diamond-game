myCh, enCh = 'O', 'X'
LEN = 5 #フィールドの長さ
NUM = 3 #いっぺんに並べる子駒の数
pow3 = [3 ** i for i in range(LEN**2)] #3の累乗

def reverse(x):         #ハッシュ値xの3進法表示を反転
    res = 0
    for i in range(LEN**2):
        res += x % 3 * pow3[LEN**2 - 1 - i]
        x = x // 3
    return res

#自分・敵の駒の座標を [0, 3^LEN**2)のハッシュ値で保存
#左からi番目の点に置かれている駒は、3進法表示でi桁目が...
#0なら何も置かれていない, 1なら子駒, 2なら王駒

default_pieces = 1
for i in range(NUM):
    for j in range(NUM-i):
        default_pieces += pow3[i + LEN * j]
default_enemy_pieces = reverse(default_pieces)

# ゲームの状態
class State:
    def __init__(self, pieces=default_pieces, enemy_pieces=default_enemy_pieces, ox=1):
        self.pieces       = pieces          #自駒
        self.enemy_pieces = enemy_pieces    #敵駒
        self.ox = ox        #手番 1で先手, -1で後手

    @property   #現在の状態の各駒の座標を返す
    def position(self):
        myServ,myKing,enServ,enKing = [],-1,[],-1   #自分/敵の子駒の座標のリスト/王駒の座標
        p = self.pieces
        for i in range(LEN**2):
            if p % 3 == 1 :
                myServ.append(i)
            if p % 3 == 2:
                myKing = i
            p = p // 3
        q = self.enemy_pieces
        for i in range(LEN**2):
            if q % 3 == 1 :
                enServ.append(i)
            if q % 3 == 2:
                enKing = i
            q = q // 3
        return myKing, myServ, enKing, enServ

    @property
    def legal_actions(self):    #現在の状態からの合法手を返す
        myKing, myServ, enKing, enServ = self.position
        exist = [0] * (LEN**2) #i番目の点に駒があれば exist[i] = 1
        exist[myKing] = 1
        for e in myServ:
            exist[e] = 1
        exist[enKing] = 1
        for e in enServ:
            exist[e] = 1
        res = []    #res[i] = (from, to, k) で座標fromから座標toに駒 k (1or2)を移動
        for serv in myServ:
            if serv%LEN < LEN - 1 and not exist[serv+1]:   #子駒が右に一つ動く
                res.append((serv, serv+1, 1))
            if serv//LEN < LEN - 1 and not exist[serv+LEN]:   #子駒が下に一つ動く
                res.append((serv, serv+LEN, 1))
            #if serv_j < LEN - 1 and serv_i < LEN - 1 and not exist[serv+LEN+1]:   #子駒が右下に一つ動く
            #    res.append((serv, serv+LEN+1, 1))

            serv_goals = []

            def dfs_serv_skip(frm):
                if frm % LEN < LEN-2 and exist[frm+1] and (not exist[frm+2]) and myKing != frm+1 and enKing !=frm+1:
                    serv_goals.append(frm+2)
                    dfs_serv_skip(frm+2)
                if frm // LEN < (LEN-2) and exist[frm+LEN] and (not exist[frm+2*LEN]) and myKing != frm+LEN and enKing !=frm+LEN:
                    serv_goals.append(frm+LEN*2)
                    dfs_serv_skip(frm+LEN*2)

            dfs_serv_skip(serv)
            for goal in list(set(serv_goals)):
                res.append((serv, goal, 1))

        king_goals = []
        if myKing % LEN < LEN - 1 and not exist[myKing+1]:   #王駒が右に一つ動く
            king_goals.append(myKing + 1)
        if myKing // LEN <  LEN - 1 and not exist[myKing+LEN]:   #王駒が下に一つ動く
            king_goals.append(myKing + LEN)

        def dfs_king_skip(frm):
            for add in range(2, LEN - frm % LEN ):
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
            for add in range(2, LEN - frm // LEN):
                to = frm + add * LEN
                if exist[to]:
                    continue
                flag = True
                for j in range(frm + LEN, to, LEN):
                    if not exist[j]:
                        flag = False
                if flag:
                    king_goals.append(to)
                    dfs_king_skip(to)

        dfs_king_skip(myKing)
        for goal in list(set(king_goals)):
            res.append((myKing, goal, 2))
        return res

    @property
    def lose(self):     #敗北していればTrue
        return self.enemy_pieces == default_pieces  #相手の駒が自分の初期位置にいるかどうか

    @property
    def draw(self):     #引き分けならTrue
        return (not self.lose) and (not self.legal_actions) #負けていないがそもそも動けない

    @property
    def end(self):      #ゲームが終わっているか
        return self.lose or self.draw

    def print_winner(self):
        if self.lose:
            winner = enCh if self.ox > 0 else myCh
            print("Win: ", winner)
        if self.draw:
            print("Draw")

    def print_legal_actions(self):  #合法手の表示
        print("Legal Actions")
        actions = self.legal_actions
        for i in range(len(actions)):
            piece = 'Serv' if actions[i][2] == 1 else 'King'
            print('['+str(i)+'] : move',piece,'from',actions[i][0],'to',actions[i][1])

    def next(self, action):     #現在の状態からactionの手を打った後の状態
        #手番が交代するので、自分と敵の座標を交換、目線も入れ替え(ハッシュ値の3進法表示を逆順にする)
        #action=(from, to, k)をすると自駒の配置のハッシュ値は k * (3^to - 3^from)が加算される
        next_pieces = reverse(self.enemy_pieces)
        next_enemy = reverse(self.pieces+action[2]*(pow3[action[1]]-pow3[action[0]]))
        return State(next_pieces, next_enemy, -self.ox)

    def __str__(self):      #printで読んだ時の表示
        myKing, myServ, enKing, enServ = self.position
        ch_ls = ['.'] * (LEN**2)
        res = ""
        myKch, mySch, enKch, enSch = 'O', 'o', 'X', 'x'
        if self.ox == 1:    #先手目線
            ch_ls[myKing] = myKch
            for e in myServ:
                ch_ls[e] = mySch
            ch_ls[enKing] = enKch
            for e in enServ:
                ch_ls[e] = enSch
            for character in ch_ls:
                if res and (len(res)+1) % (LEN+1) == 0:
                    res += '\n'
                res += character
        else:               #後手目線
            ch_ls[myKing] = enKch
            for e in myServ:
                ch_ls[e] = enSch
            ch_ls[enKing] = myKch
            for e in enServ:
                ch_ls[e] = mySch
            for character in ch_ls:
                if res and (len(res)+1) % (LEN+1) == 0:
                    res = '\n' + res
                res = character + res
        return res + '\n'
