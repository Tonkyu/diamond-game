#参考 https://tail-island.github.io/programming/2018/06/19/monte-carlo-tree-search.html
from funcy import *
import actions
import state_linear
import state_square

def print_split():
    print("----------------------")

def game_choice():
    state_num = int(input("Which Game?\nLinear\t0\nSquare\t1\n"))
    if state_num != 0 and state_num != 1:
        print("##input error##")
        state_num = game_choice()
    return state_num

def game_settings():
    strategies = [('User',actions.User), ('Random', actions.Random), ('PureMCT', actions.PureMCT), ('UCT', actions.UCT)]
    strategy_question = ""
    for i in range(len(strategies)):
        strategy_question += str(i) + " : "
        strategy_question += strategies[i][0]
        strategy_question += "\n"
    first_num = int(input("First Player?\n" + strategy_question))
    second_num = int(input("Second Player?\n" + strategy_question))
    playtimes = int(input("How many plays?\n"))

    first_name = strategies[first_num][0]
    first_func = strategies[first_num][1]
    second_name = strategies[second_num][0]
    second_func = strategies[second_num][1]

    return first_name, second_name, first_func, second_func, playtimes

def first_player_point(ended_state):
    #勝利で+1, 引き分けで0、敗北で-1の報酬
    if ended_state.lose:
        return 1 if ended_state.ox == -1 else 0
    return 0.5

def test_algorithm(state_num, next_actions, playtimes):
    first_win = 0
    first_lose = 0
    first_draw = 0
    total_point = 0
    for _ in range(playtimes):
        state = state_linear.State() if state_num == 0 else state_square.State()
        for next_action in cat(repeat(next_actions)):   #交互にプレイ
            #戦況を観戦する際は次のコメントアウトを外す
            #print(state)
            if state.end:
                state.print_winner()
                if state.draw:
                    first_draw += 1
                elif state.ox == 1: 
                    first_lose += 1
                else:
                    first_win += 1
                break
            state = state.next(next_action(state))
        total_point += first_player_point(state)

    print_split()
    print("Win\t: ", first_win)
    print("Lose\t: ", first_lose)
    print("Draw\t: ", first_draw)
    print("Average point\t: ", total_point / playtimes)

def battle(state_num, first_name, second_name, first_func, second_func, playtimes):
    #2つの戦略の対戦
    print_split()
    print(first_name + " V.S. " + second_name)
    print_split()
    test_algorithm(state_num, (first_func, second_func), playtimes)

def main():
    state_num = game_choice()
    first_name, second_name, first_func, second_func, playtimes = game_settings()
    battle(state_num, first_name, second_name, first_func, second_func, playtimes)


if __name__ == '__main__':
    main()