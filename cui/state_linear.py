myCh, enCh = 'O', 'X'
LEN = 15 #フィールドの長さ
NUM = 2 #子駒の数
pow3 = [3 ** i for i in range(LEN)] #3の累乗

#自分・敵の駒の座標を [0, 3^LEN)のハッシュ値で保存
#左からi番目の点に置かれている駒は、3進法表示でi桁目が...
#0なら何も置かれていない, 1なら子駒, 2なら王駒

default_pieces = 2
default_enemy_pieces = 2 * pow3[-1]
for i in range(NUM):
    default_pieces += pow3[i+1]
    default_enemy_pieces += pow3[-2-i]

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
        for i in range(LEN):
            if p % 3 == 1 :
                myServ.append(i)
            if p % 3 == 2:
                myKing = i
            p = p // 3
        q = self.enemy_pieces
        for i in range(LEN):
            if q % 3 == 1 :
                enServ.append(i)
            if q % 3 == 2:
                enKing = i
            q = q // 3
        return myKing, myServ, enKing, enServ
        
    @property
    def legal_actions(self):    #現在の状態からの合法手を返す
        myKing, myServ, enKing, enServ = self.position
        exist = [0] * LEN       #i番目の点に駒があれば exist[i] = 1
        exist[myKing] = 1
        for e in myServ:
            exist[e] = 1
        exist[enKing] = 1
        for e in enServ:
            exist[e] = 1
        res = []    #res[i] = (from, to, k) で座標fromから座標toに駒 k (1or2)を移動
        for serv in myServ:
            if serv < LEN - 1 and not exist[serv+1]:   #子駒が右に一つ動く
                res.append((serv, serv+1, 1))
            e = serv
            while e < LEN-2:    #子駒が1つ飛ばしを1回以上繰り返す
                if exist[e+1] and (not exist[e+2]) and myKing!=e+1 and enKing!=e+1:
                    res.append((serv, e+2, 1))
                    e += 2
                else:
                    break

        if myKing < LEN - 1 and not exist[myKing+1]:   #王駒が右に一つ動く
            res.append((myKing, myKing+1, 2))

        frm = myKing    #王が1つ以上の駒を飛ばすのを1回以上繰り返す
        while frm < LEN - 1 and exist[frm+1]: 
            to = frm + 1
            while to < LEN and exist[to]:
                to += 1
            if to < LEN :
                res.append((myKing, to, 2))
                frm = to
            else:
                break
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
        def reverse(x):         #ハッシュ値xの3進法表示を反転
            res = 0
            for i in range(LEN):
                res += x % 3 * pow3[LEN - 1 - i]
                x = x // 3
            return res
        #手番が交代するので、自分と敵の座標を交換、目線も入れ替え(ハッシュ値の3進法表示を逆順にする)
        #action=(from, to, k)をすると自駒の配置のハッシュ値は k * (3^to - 3^from)が加算される
        next_pieces = reverse(self.enemy_pieces)
        next_enemy = reverse(self.pieces+action[2]*(pow3[action[1]]-pow3[action[0]]))
        return State(next_pieces, next_enemy, -self.ox)

    def __str__(self):      #printで読んだ時の表示
        myKing, myServ, enKing, enServ = self.position
        ch_ls = ['.'] * LEN
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
                res += character
        else:               #後手目線
            ch_ls[myKing] = enKch
            for e in myServ:
                ch_ls[e] = enSch
            ch_ls[enKing] = myKch
            for e in enServ:
                ch_ls[e] = mySch
            for character in ch_ls:
                res = character + res
        return res