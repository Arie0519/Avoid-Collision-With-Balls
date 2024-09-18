#モジュールのインポート
import pygame
from pygame.locals import *
import sys
import math
import random
import sqlite3



#定数
WIDTH = 1280           #画面横サイズ
HEIGHT = 720           #画面縦サイズ
PLAYER_SIZE = 20       #プレイヤー半径
PLAYER_DOT = 20        #プレイヤーの移動ドット
BALL_SIZE = 20         #ボール半径
BALL_DOT = 2           #ボールの移動ドット(縦横同じ)
BALL_TIME = 10         #待ち時間
THRESHOLD = 3          #増殖値
ELIPSE_WIDTH = 250     #楕円の長径
ELIPSE_HEIGHT = 160    #楕円の短径

#色
black = (0,0,0)        
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
yellow = (255,255,0)



#Scoreクラス(初期化,加点,スコア表示)
class Score:
    
    #初期化
    def __init__(self):         
        self.score = 0
        
    #加点
    def plus(self):             
        self.score += 1
        
    #スコア表示
    def draw(self, screen):    
        font = pygame.font.Font(None, 60)
        text = font.render("Score: {:d} pts".format(self.score), True, green)
        text_rect = text.get_rect(center=(int(WIDTH/2), int(HEIGHT/8)))
        screen.blit(text,text_rect)



#Playerクラス(初期化,描画,キー入力)
class Player():
    
    #初期化
    def __init__(self):
        self.x = int(WIDTH/2) - PLAYER_SIZE
        self.y = int(HEIGHT/2) - PLAYER_SIZE
    
    #描画
    def draw(self, screen):
        pygame.draw.circle(screen, white, (self.x,self.y),PLAYER_SIZE)   #円
    
    #キー入力
    def move(self, event):
        if event.key == K_a or event.key == K_LEFT:
            if self.x > PLAYER_SIZE * 2:
                self.x -= PLAYER_DOT
            else:
                self.x = PLAYER_SIZE
                
        if event.key == K_d or event.key == K_RIGHT:
            if self.x < WIDTH - PLAYER_SIZE * 2:
                self.x += PLAYER_DOT
            else:
                self.x = WIDTH - PLAYER_SIZE
                
        if event.key == K_w or event.key == K_UP:
            if self.y > PLAYER_SIZE * 2:
                self.y -= PLAYER_DOT
            else:
                self.y = PLAYER_SIZE
                
        if event.key == K_s or event.key == K_DOWN:
            if self.y < HEIGHT - PLAYER_SIZE * 2:
                self.y += PLAYER_DOT
            else:
                self.y = HEIGHT - PLAYER_SIZE
    
    
    
#ボールクラス(初期化,描画,壁との衝突判定)
class Ball(Player, Score):
    #初期化
    def __init__(self):
        self.x = random.randint(BALL_SIZE*2,WIDTH-BALL_SIZE*2)
        self.y = random.randint(BALL_SIZE*2,HEIGHT-BALL_SIZE*2)
        self.x_flg = 0
        self.y_flg = 0
        self.score_flg = 0
        
    #描画
    def draw(self, screen):
        pygame.draw.circle(screen, red, (self.x,self.y), BALL_SIZE) #画面,RGB値,座標,半径
    
    #壁との衝突判定
    def collision(self, Score):
        
        #加点する関数
        def plus_score():
            self.score_flg = 1
            Score.plus()
            self.score_flg = 0
            
        #横座標設定
        if self.x < BALL_SIZE:
            self.x_flg = 0
            plus_score()
        elif self.x > WIDTH - BALL_SIZE:
            self.x_flg = 1
            plus_score()
        
        if self.x_flg == 0:
            self.x += BALL_DOT
        else:
            self.x -= BALL_DOT
            
        #縦座標設定
        if self.y < BALL_SIZE:
            self.y_flg = 0
            plus_score()
        elif self.y > HEIGHT - BALL_SIZE:
            self.y_flg = 1
            plus_score()
        
        if self.y_flg == 0:
            self.y += BALL_DOT
        else:
            self.y -= BALL_DOT
            
    #プレイヤーとの衝突判定
    def conflict(self, Player):
        distance = math.sqrt((Player.x-self.x)**2+(Player.y-self.y)**2)
        if distance <= (PLAYER_SIZE + BALL_SIZE):
            return 1
        else:   
            return 0



#タイトル画面の描画
def make_title(screen, db_curs):
    font = pygame.font.Font(None, 100)
    text1 = font.render("GAME START", True, yellow)
    text1_rect = text1.get_rect(center=(int(WIDTH/2), int(HEIGHT/4)-30))
    screen.blit(text1,text1_rect)
            
    font = pygame.font.Font(None, 60)
    text2 = font.render("push SPACE to start", True, white)
    text2_rect = text2.get_rect(center=(int(WIDTH/2), int(HEIGHT*4/5)+30))
    screen.blit(text2,text2_rect)
    
    db_curs.execute("select count(*) from items")
    items_len = db_curs.fetchall()
    db_curs.execute("select * from items order by score desc limit 10")
    result = db_curs.fetchall()
    for i in range(min(items_len[0][0],5)):
        font = pygame.font.Font(None, 60)
        text3 = font.render("No.{:d}  :  {:d} pts".format((i+1),result[i][0]), True, green)
        text3_rect = text3.get_rect(center=(int(WIDTH/3)+40, int(HEIGHT/3)+60*i+20))
        screen.blit(text3,text3_rect)
    if items_len[0][0] > 5:
        for i in range(min(items_len[0][0]-5,5)):
            font = pygame.font.Font(None, 60)
            text3 = font.render("No.{:d}  :  {:d} pts".format((i+6),result[i][0]), True, green)
            text3_rect = text3.get_rect(center=(int(WIDTH*2/3)-40, int(HEIGHT/3)+60*i+20))
            screen.blit(text3,text3_rect)
     
        
        
#GO画面の描画
def make_gameover(screen, score):
    font = pygame.font.Font(None, 100)
    text = font.render("GAME OVER", True, red)
    text_rect = text.get_rect(center=(int(WIDTH/2), int(HEIGHT/4)-30))
    screen.blit(text,text_rect)
    
    font = pygame.font.Font(None, 60)
    text2 = font.render("Your Score: {:d} pts".format(score.score), True, green)
    text2_rect = text2.get_rect(center=(int(WIDTH/2), int(HEIGHT*2/5)))
    screen.blit(text2,text2_rect)
    
    
    
    font = pygame.font.Font(None, 60)
    text3 = font.render("Retry", True, black)
    text3_rect = text3.get_rect(center=(int(WIDTH*7/20), int(HEIGHT*13/20)))
    screen.blit(text3,text3_rect)
    
    
    font = pygame.font.Font(None, 60)
    text4 = font.render("Exit", True, black)
    text4_rect = text4.get_rect(center=(int(WIDTH*13/20), int(HEIGHT*13/20)))
    screen.blit(text4,text4_rect)
    
    font = pygame.font.Font(None, 60)
    text5 = font.render("select event and push SPACE", True, white)
    text5_rect = text5.get_rect(center=(int(WIDTH/2), int(HEIGHT*17/20)))
    screen.blit(text5,text5_rect)


    
#メイン関数
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(u"Game")
    db_connect = sqlite3.connect('a.db')
    db_curs = db_connect.cursor()
    db_curs.execute("CREATE TABLE IF NOT EXISTS items(score)")

    game_state = 0
    action_flg = 0
    
    while True:
        
        #初期化とゲームシステム
        
        #タイトル画面,変数とフラグの初期化
        if game_state == 0:
            score = Score()
            player = Player()
            balls = [Ball()]
            conflict_flg = 0
            add_count = 0
            
            
        #ゲーム画面,ゲームシステムとスコア計算
        if game_state == 1:
            if conflict_flg == 0:           #ゲーム中
                for ball in balls:          #ボールを動かす
                    ball.collision(score)
                    conflict_flg += ball.conflict(player)
                
                if score.score % THRESHOLD == 1:
                    add_count = 0
            
                if score.score != 0 and score.score % THRESHOLD == 0:
                    add_count += 1
        
                if add_count == 1:
                    balls.append(Ball())
                
            if conflict_flg >= 1:           #ゲームオーバー
                db_curs.execute('insert into items values({:d})'.format(score.score))
                db_connect.commit()    
                game_state = 2
                
        #描画
        screen.fill(black)                  #背景の設定(黒)
        
        if game_state == 0:                 #タイトル画面の描画
            make_title(screen,db_curs)
            
        if game_state == 1:                 #ゲーム画面の描画
            score.draw(screen)
            player.draw(screen)
            for ball in balls:
                ball.draw(screen)
                
            pygame.time.wait(BALL_TIME)
            
        if game_state == 2:                 #GO画面の描画
            if action_flg == 0:
                pygame.draw.ellipse(screen, yellow, (int(WIDTH*7/20)-ELIPSE_WIDTH/2, int(HEIGHT*13/20)-ELIPSE_HEIGHT/2,ELIPSE_WIDTH,ELIPSE_HEIGHT))
                pygame.draw.ellipse(screen, white, (int(WIDTH*13/20)-ELIPSE_WIDTH/2, int(HEIGHT*13/20)-ELIPSE_HEIGHT/2,ELIPSE_WIDTH,ELIPSE_HEIGHT))
            elif action_flg == 1:
                pygame.draw.ellipse(screen, white, (int(WIDTH*7/20)-ELIPSE_WIDTH/2, int(HEIGHT*13/20)-ELIPSE_HEIGHT/2,ELIPSE_WIDTH,ELIPSE_HEIGHT))
                pygame.draw.ellipse(screen, yellow, (int(WIDTH*13/20)-ELIPSE_WIDTH/2, int(HEIGHT*13/20)-ELIPSE_HEIGHT/2,ELIPSE_WIDTH,ELIPSE_HEIGHT))
            make_gameover(screen,score)
            
        
        #イベント取得
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
                #状態1:タイトル画面
                if game_state == 0:
                    if event.key == K_SPACE:
                        game_state = 1
                        
                #状態2:ゲーム画面
                elif game_state == 1:
                    player.move(event)
                        
                #状態3:ゲームオーバー画面
                elif game_state == 2:
                    if event.key == K_a or event.key == K_LEFT:
                        action_flg = 0
                    if event.key == K_d or event.key == K_RIGHT:
                        action_flg = 1
                        
                    if action_flg == 0:
                        if event.key == K_SPACE:
                            game_state = 0
                            
                    if action_flg == 1:
                        if event.key == K_SPACE:
                            pygame.quit()
                            sys.exit()
                        
        pygame.display.update()
                        
    db_connect.close()

#メイン関数呼び出し
if __name__ == "__main__":
    main()
    