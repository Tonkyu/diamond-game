import global_value as g
import sys
import pygame
from pygame.locals import *
from linear import LinearGame
from square import SquareGame
import actions
import time

g.WINDOW_X = 1410
g.WINDOW_Y = 600
pygame.init()
screen = pygame.display.set_mode((g.WINDOW_X, g.WINDOW_Y))
font = pygame.font.Font(None, 55)

white = (255, 255, 255)
black = (0, 0, 0)
yellow_green = (124, 252, 0)
red = (240, 128, 128)

LINEAR_FIELD_LEN = 15
LINEAR_CHILD_NUM = 2
SQUARE_FIELD_LEN = 5
SQUARE_CHILD_NUM = 3

RND = (actions.Random, "Random")
MCT = (actions.PureMCT, "PureMCT")
UCT = (actions.UCT, "UCT")

def main():
    FIELD_LEN = LINEAR_FIELD_LEN
    CHILD_NUM = LINEAR_CHILD_NUM
    Game = LinearGame
    strategy = [UCT, RND]
    global ox
    ox = 1
    def reset_game():
        global ox
        ox = 1
        return Game(FIELD_LEN, CHILD_NUM)

    G = reset_game()  #ゲーム起動

    pygame.display.set_caption('Simple Diamond Game')
    guide_content = "Press Space Key to move forward"
    guide_text = font.render(guide_content, True, black)

    change_mode_content = "Play Square version"
    change_mode_button = pygame.Rect(700, 40, 430, 80)
    change_mode_text = font.render(change_mode_content, True, black)

    reset_button = pygame.Rect(1170, 40, 145, 80)
    reset_text = font.render("Reset", True, black)

    fRND_btn = pygame.Rect(910, 420, 140, 70)
    fMCT_btn = pygame.Rect(1070, 420, 140, 70)
    fUCT_btn = pygame.Rect(1230, 420, 140, 70)
    sRND_btn = pygame.Rect(910, 510, 140, 70)
    sMCT_btn = pygame.Rect(1070, 510, 140, 70)
    sUCT_btn = pygame.Rect(1230, 510, 140, 70)

    fRND_text = font.render("RND", True, black)
    fMCT_text = font.render("MCT", True, black)
    fUCT_text = font.render("UCT", True, black)
    sRND_text = font.render("RND", True, black)
    sMCT_text = font.render("MCT", True, black)
    sUCT_text = font.render("UCT", True, black)

    MOVE_TIME_LIMIT = 2
    move_status = 0
    start_time = time.perf_counter()

    while True:
        screen.fill(white) # 背景
        G.set_field(screen)
        move_status = (time.perf_counter() - start_time) / MOVE_TIME_LIMIT
        G.set_pieces(screen, move_status)

        screen.blit(guide_text, [40, 500])

        vs_text = font.render(strategy[0][1] + " V.S. " + strategy[1][1], True, black)
        screen.blit(vs_text, [20, 40])

        pygame.draw.rect(screen, yellow_green, reset_button)
        screen.blit(reset_text, [1190, 63])

        pygame.draw.rect(screen, yellow_green, change_mode_button)
        screen.blit(change_mode_text, [730, 63])

        select_mode_text = font.render("Select strategies below", True, black)
        screen.blit(select_mode_text, [750, 370])

        first_mode_text = font.render("First", True, G.myKColor)
        screen.blit(first_mode_text, [770, 440])

        second_mode_text = font.render("Second", True, G.enKColor)
        screen.blit(second_mode_text, [750, 530])

        if strategy[0] == RND:
            pygame.draw.rect(screen, red, fRND_btn)
        else:
            pygame.draw.rect(screen, yellow_green, fRND_btn)

        if strategy[0] == MCT:
            pygame.draw.rect(screen, red, fMCT_btn)
        else:
            pygame.draw.rect(screen, yellow_green, fMCT_btn)

        if strategy[0] == UCT:
            pygame.draw.rect(screen, red, fUCT_btn)
        else:
            pygame.draw.rect(screen, yellow_green, fUCT_btn)

        if strategy[1] == RND:
            pygame.draw.rect(screen, red, sRND_btn)
        else:
            pygame.draw.rect(screen, yellow_green, sRND_btn)

        if strategy[1] == MCT:
            pygame.draw.rect(screen, red, sMCT_btn)
        else:
            pygame.draw.rect(screen, yellow_green, sMCT_btn)

        if strategy[1] == UCT:
            pygame.draw.rect(screen, red, sUCT_btn)
        else:
            pygame.draw.rect(screen, yellow_green, sUCT_btn)

        screen.blit(fRND_text, [940, 440])
        screen.blit(fMCT_text, [1100, 440])
        screen.blit(fUCT_text, [1260, 440])
        screen.blit(sRND_text, [940, 530])
        screen.blit(sMCT_text, [1100, 530])
        screen.blit(sUCT_text, [1260, 530])

        if G.state.end():
            winner = G.state.winner()
            if winner == 1:
                result_content = "WIN : First"
                result_color = G.myKColor
            elif winner == -1:
                result_content = "WIN : Second"
                result_color = G.enKColor
            else:
                result_content = "Draw"
                result_color = black
            result_text = font.render(result_content, True, result_color)
            screen.blit(result_text, [100, 120])

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    start_time = time.perf_counter()
                    if not G.state.end():
                        if ox == 1:
                            G.next(strategy[0][0])
                        else:
                            G.next(strategy[1][0])
                        ox = -ox
            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button.collidepoint(event.pos):
                    G = reset_game()

                if change_mode_button.collidepoint(event.pos):
                    old_type = type(G)
                    if old_type is LinearGame:
                        Game = SquareGame
                        FIELD_LEN = SQUARE_FIELD_LEN
                        CHILD_NUM = SQUARE_CHILD_NUM
                        change_mode_content = "Play Linear version"
                    elif old_type is SquareGame:
                        Game = LinearGame
                        FIELD_LEN = LINEAR_FIELD_LEN
                        CHILD_NUM = LINEAR_CHILD_NUM
                        change_mode_content = "Play Square version"
                    G = reset_game()

                if fRND_btn.collidepoint(event.pos):
                    strategy[0] = RND
                if fMCT_btn.collidepoint(event.pos):
                    strategy[0] = MCT
                if fUCT_btn.collidepoint(event.pos):
                    strategy[0] = UCT
                if sRND_btn.collidepoint(event.pos):
                    strategy[1] = RND
                if sMCT_btn.collidepoint(event.pos):
                    strategy[1] = MCT
                if sUCT_btn.collidepoint(event.pos):
                    strategy[1] = UCT


        # 画面を更新
        pygame.display.update()

if __name__ == '__main__':
    main()