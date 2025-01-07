import cv2
import math
import numpy as np
import os
import random
import sys
import time
import pygame as pg


WIDTH = 600  # ゲームウィンドウの幅
HEIGHT = 700  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class GutterEnemy(pg.sprite.Sprite):
    """
    端にスポーンする敵性オブジェクトの描画と攻撃
    """
    
    def __init__(self):
        """
        敵性オブジェクトのスポーンに伴う処理と描画
        """
        super().__init__()
        spawn_x = [20, WIDTH-20]
        spawn_y = [50, 130, 200]
        self.life = 200  
        self.select_x = spawn_x[random.randint(0,1)]
        self.select_y = spawn_y[random.randint(0,2)]
        self.sideFlag = "none"
        self.laser_size = 400   # レーザーの大きさを調整できる
        self.colsize = 42  # 当たり判定の正方形のサイズ
        self.laser_divide = 9  # レーザーの当たり判定を何個の正方形に置き換えるか
        self.lasercolid_xyspawns = []
        self.collideList = []
        self.spawn_xy = tuple([self.select_x, self.select_y])
        self.ge_img = pg.image.load("fig/miyasui_gazou2.png")  # 後ほど画像変更
        self.ge_img.convert_alpha()  # ピクセル単位で透明度を有効

        if self.spawn_xy[0] == WIDTH-20:
            self.ge_img = pg.transform.scale(pg.transform.flip(pg.transform.rotate(self.ge_img, -45), True, False), (100, 100))
            # 右側に湧く敵を中央へ向くように斜めにして縮小する
            self.sideFlag = "right"
        else:
            self.ge_img = pg.transform.scale(pg.transform.rotate(self.ge_img, -45), (100, 100))
            # 左側に湧く敵を中央へ向くように斜めにして縮小する
            self.sideFlag = "left"

        self.ge_rct = self.ge_img.get_rect()
        self.ge_rct.center = self.spawn_xy

        # 攻撃処理に関するゾーン
        self.fireing = False  # 発砲中フラグ
        self.fire_time = random.randint(15, self.life-50)  # 発砲タイミングの設定(生後15~(寿命-50))

        self.yokoyari_img = pg.transform.scale(pg.image.load("fig/clear_pic.png"), (self.laser_size, self.laser_size))
        # self.yokoyari_img.convert_alpha()
        self.yokoyari_rct = self.yokoyari_img.get_rect()

        self.calc_xyspawns(self.sideFlag, self.spawn_xy, self.colsize)
    
    def calc_xyspawns(self, sideFlag, spawn_xy, colsize):
        side = sideFlag
        spawn_x = spawn_xy[0]
        spawn_y = spawn_xy[1]
        size = colsize
        if side == "right":
            for i in range(self.laser_divide):
                spawn_x -= size
                spawn_y += size
                self.lasercolid_xyspawns.append((spawn_x, spawn_y))
        elif side == "left":
            for i in range(self.laser_divide):
                spawn_x += size
                spawn_y += size
                self.lasercolid_xyspawns.append((spawn_x, spawn_y))
            
    def createCol(self, xspawn, yspawn, colsize):
        self.laser_colid = pg.transform.scale(pg.image.load("fig/miyasui_gazou.png"), (colsize, colsize))
        self.xyspawn = (xspawn, yspawn)
        self.laser_colid_rct = self.laser_colid.get_rect()
        self.laser_colid_rct.center = self.xyspawn

        return self.laser_colid_rct
        
    def update(self, screen):
        screen.blit(self.ge_img, self.ge_rct)  # 敵性オブジェクトの描画
        if self.fire_time == self.life:  # 攻撃時間と寿命カウントが同じだったら
            self.fireing = True  # 発砲中をTrueにする

        if self.fireing:  # 今、発砲中である場合に
            if self.sideFlag == "right":  # 画像の左右反転など
                self.yokoyari_img = pg.transform.rotate(pg.image.load("fig/simplelaser.png"), 45)   # 攻撃の画像を設定
            elif self.sideFlag == "left":
                self.yokoyari_img = pg.transform.rotate(pg.image.load("fig/simplelaser.png"), 135)  # 攻撃の画像を設定
            self.yokoyari_img = pg.transform.scale(self.yokoyari_img, (self.laser_size, self.laser_size))
            self.yokoyari_rct = self.yokoyari_img.get_rect()
            self.yokoyari_img.convert_alpha()

            # laserの当たり判定を生成
            for i in range(self.laser_divide):
                self.collideList.append(self.createCol(self.lasercolid_xyspawns[i][0], self.lasercolid_xyspawns[i][1], self.colsize))
                
        if self.sideFlag == "right":
            self.yokoyari_rct.center = tuple([self.spawn_xy[0]-self.laser_size/2-20, self.spawn_xy[1]+self.laser_size/2+20])
        elif self.sideFlag == "left":
            self.yokoyari_rct.center = tuple([self.spawn_xy[0]+self.laser_size/2+20, self.spawn_xy[1]+self.laser_size/2+20])

        if self.fireing:
            screen.blit(self.yokoyari_img, self.yokoyari_rct)  # 光線
        self.life -= 1
        if self.life <= 0:  # 消滅処理
            # print("Gutter Enemy killed")
            self.kill()



#### 小林担当部分 画面脇に湧く敵性オブジェクト

def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書 WASD式
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 0.9),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 0.9),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 0.9),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 0.9),  # 右下
        }
        self.dire = (1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(self.speed*sum_mv[0], self.speed*sum_mv[1])
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-self.speed*sum_mv[0], -self.speed*sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        screen.blit(self.image, self.rect)

class Bird_Collide(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）の当たり判定に関するクラス
    """
    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとんの当たり判定Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        rad = 10  # 当たり判定の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = (255, 0, 0)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_alpha(128)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

    def update(self, screen: pg.Surface, bird: Bird):
        """
        当たり判定の位置を更新する
        引数1 screen：画面Surface
        引数2 bird：こうかとん
        """
        self.rect.center = bird.rect.center
        screen.blit(self.image, self.rect)


class Bullet(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = (0, 255, 0)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class AngleBomb(pg.sprite.Sprite):
    """
    角度付き爆弾のクラス
    """
    def __init__(self, emy: "Enemy", bird: Bird, angle: int):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        引数3 angle：爆弾の角度
        """
        super().__init__()
        rad = 10  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = (0, 255, 255)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)
        vector = np.array([self.vx,self.vy])
        radi=np.deg2rad(angle)
        rot = np.array([[math.cos(radi), -math.sin(radi)],
                    [math.sin(radi), math.cos(radi)]])
        self.res = np.dot(rot, vector) 
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.vx, self.vy = self.res
        self.speed = 6

    def update(self):
        """
        爆弾を計算した速度ベクトルself.resに基づき移動させる
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Fall(pg.sprite.Sprite):
    """
    縦に振ってくる爆弾のクラス
    """
    def __init__(self):
        """
        上から降ってくる爆弾を生成する関数
        """
        super().__init__()
        rad = 5    # 爆弾円の半径：20
        self.image = pg.Surface((2*rad, 2*rad))
        color = (255, 255, 0)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.vx, self.vy = random.randint(-6, 6),6
        self.rect.centerx = random.randint(rad, WIDTH - rad)
        self.rect.top = 0
        self.speed = 6

    def update(self):
        """
        爆弾を計算した速度self.vyに基づき移動させる
        """
        self.rect.move_ip(self.vx, self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class FreeBullet(pg.sprite.Sprite):
    """
    弾幕に関するクラス
    """
    def __init__(self, x: int, y: int, vector: tuple, color: tuple, rad: int):
        """
        弾幕円Surfaceを生成する
        引数1 x座標
        引数2 y座標
        引数3 動かしたい方向ベクトル
        引数4 色（RGB）
        引数5 円の半径
        """
        super().__init__()
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = vector
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 6
        self.wait_time = 0

    def set_wait_time(self, time: int):
        self.wait_time = time

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        super().__init__()
        self.vx, self.vy = (0, -1)
        # angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), 90, 1.0)
        # self.vx = math.cos(math.radians(angle))
        # self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(self.speed*self.vx, self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bullet|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBulletまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load(f"fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    def __init__(self):
        super().__init__()
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/E_2.png"), 0, 0.2)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH//2, 0
        self.vx, self.vy = 0, +6
        self.bound = HEIGHT//4-50 # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.move_ip(self.vx, self.vy)


class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


class Zanki:
    """
    残機を表示するクラス
    """
    def __init__(self, zanki :int):
        """
        残機数を表示する関数
        """
        self.font = pg.font.Font(None, 40)
        self.color = (0, 255, 255)
        self.value = zanki
        self.image = self.font.render(f"machine:{'◆'*self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT - 50

    def update(self, screen: pg.Surface):
        """
        残機数を更新する関数
        """
        self.image = self.font.render(f"machine:{'◆'*self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


class HP(pg.sprite.Sprite):
    """
    HPバーの処理
    """
    def __init__(self, x, y, width, now, max):
        """
        hpバーを表示するための設定を行う関数
        引数：(x座標,y座標,HPバーの幅,今のHP,最大HP)
        """
        self.x = x
        self.y = y
        self.width = width
        self.max = max # 最大HP
        self.hp = now # HP
        self.victory = False
        self.mark = int((self.width - 4) / self.max) # HPバーの1目盛り
        self.font = pg.font.SysFont(None, 28)
        self.label = self.font.render("HP", True, (255, 255, 255))
        self.frame = pg.Rect(self.x + 2 + self.label.get_width(), self.y, self.width, self.label.get_height())
        self.bar = pg.Rect(self.x + 4 + self.label.get_width(), self.y + 2, self.width - 4, self.label.get_height() - 4)
        self.value = pg.Rect(self.x + 4 + self.label.get_width(), self.y + 2, self.width - 4, self.label.get_height() - 4)
        self.value.width = (self.width - 4) * (self.hp / self.max)
        self.kawata = False
        if self.hp <= 0:
            self.victory = True
        if self.hp / self.max <= 0.3:    #3割り切ったら河田担当
            self.kawata = True

    def hp_draw(self, screen):
        """
        HPバーを表示する関数
        引数：screen
        """ 
        if not self.victory:
            color = (0, 255, 0)
            self.kawata = False
            if self.hp / self.max <= 0.3:  #3割以下なら赤
                self.kawata = True
                color = (255, 0, 0)
            elif self.hp / self.max <= 0.6:  #6割以下なら黄色
                color = (255, 255, 0)
            pg.draw.rect(screen, (255, 255, 255), self.frame)
            pg.draw.rect(screen, (0, 0, 0), self.bar)
            pg.draw.rect(screen, color, self.value)
            screen.blit(self.label, (self.x, self.y))


class Special:
    """
    必殺技に関するクラス
    """
    def __init__(self):
        SPECIAL_LIVES = 3
        self.lives = SPECIAL_LIVES # 必殺技の初期残機数
        self.font = pg.font.Font(None, 50)
        self.color = (255, 0, 0)
        self.image = self.font.render(f"SPECIAL: {self.lives}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = WIDTH - 100, HEIGHT - 50

    def update(self, screen: pg.Surface):
        """
        必殺技残機数を画面に表示
        """
        self.image = self.font.render(f"SPECIAL: {self.lives}", 0, self.color) # 残機更新のため必要
        screen.blit(self.image, self.rect)

    def use(self, bombs: pg.sprite.Group,free_bullets: pg.sprite.Group, screen: pg.Surface):
        """
        必殺技を使用し、爆弾をすべて消去
        """
        if self.lives > 0: # 必殺技残機が残っているなら
            self.lives -= 1 # 必殺技残機を1減らす
            self.play_video(screen) # ゲーム停止と動画再生
            bombs.empty() # 爆弾をすべて消去
            free_bullets.empty() # 弾幕をすべて消去
            
    def play_video(self, screen: pg.Surface):
        """
        ゲームを一時停止し、動画を再生
        """
        video_path = "fig/proen_kari.mp4" # 動画パス
        cap = cv2.VideoCapture(video_path) # cv2の動画を読み込むメソッド
        while cap.isOpened(): # 動画が再生されている間
            ret, frame = cap.read() # 1フレームごとに動画を読み込み(frame=1フレームごとの画像データ)
            if not ret: # フレームが読み込めなかったら
                break # 動画が終了した際にフレームが読み込めなくなるのでWhileから出ないとエラーが起きる
            # OpenCVのBGR形式をPygameのSurface形式に変換
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.transpose(frame) # 画像データの回転-->surfaceに変換するのに必要
            frame = pg.surfarray.make_surface(frame)
            screen.blit(frame, (0, 250))
            pg.display.update()
            pg.time.delay(int(500 / 30)) # 30FPS
        cap.release() #動画ファイルを閉じる
    time.sleep(3) # ゲーム停止時間


def main():
    pg.display.set_caption("こうかとん弾幕ゲーム【難～爆】")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/background01.png")  # デフォルトではpb_bg.jpg
    special = Special()  # 必殺技管理クラス

    bird = Bird(3, (WIDTH/2, HEIGHT-100))  # こうかとん出現場所
    collider = Bird_Collide(3, (WIDTH/2, HEIGHT-100))
    bombs = pg.sprite.Group()
    free_bullets = pg.sprite.Group()  #弾幕のグループ
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    anbo = pg.sprite.Group()
    falls = pg.sprite.Group()
    max_hp = 2000  #敵機の最大HP
    hp=max_hp  #現在の敵機のHP
    zanki = 3  #残機
    gutters = pg.sprite.Group() # 両脇に出てくる敵機のグループ # 小林担当部
    max_hp = 200  #敵機の最大HP
    hp=max_hp  #現在の敵機のHP
    
    tmr = 1 
    anbo = pg.sprite.Group()
    falls = pg.sprite.Group()
    max_hp = 2000  #敵機の最大HP
    hp=max_hp  #現在の敵機のHP
    zanki = 3  #残機

    second_tmr = 0  #第二フェーズのタイマー
    tmr = 0
    clock = pg.time.Clock()
    while True:
        hp_bar = HP(WIDTH - 250, 20, 200, hp, max_hp)
        key_lst = pg.key.get_pressed()
        zankis = Zanki(zanki)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.add(Beam(bird))
            if event.type == pg.KEYDOWN and event.key == pg.K_b and special.lives > 0: # Bキーで必殺技発動
                special.use(bombs, free_bullets, screen)
            if event.type == pg.KEYDOWN and event.key == pg.K_n:
                bird.speed = 5
            if event.type == pg.KEYDOWN and event.key == pg.K_m:
                bird.speed = 10

        screen.blit(bg_img, [0, 0])

        if tmr == 200:  # 200フレームに敵を出現させる
            emys.add(Enemy())

        if tmr == 500:  # 500の時、初めてgutterenemyを呼び出す。
            gutters.add(GutterEnemy())
        if tmr % 741 == 0 and tmr != 0:  # 小林担当部分 # 741間隔で敵を出現させる
            gutters.add(GutterEnemy())

        for gutter in gutters:  # gutter
            if gutter.fireing:
                for j in range(len(gutter.collideList)):  # 当たり判定リストの要素数の回数だけfor
                    if gutter.fireing == False:
                        continue
                    if gutter.collideList[j].colliderect(collider):  # こうかとんとlaserの衝突判定
                        zanki -= 1
                        if zanki <= 0:
                            bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                            pg.display.update()
                            time.sleep(2)
                            return
                        gutter.fireing = False
         
        if 0.3 < hp / max_hp <= 0.6:
            #時間経過で出現する弾幕
            if second_tmr == 0:
                for i in range(0, 250, 50):
                    free_bullets.add(FreeBullet(25+i , 50, (+0, +0.5), (255, 255, 255), 25))
                    free_bullets.add(FreeBullet(WIDTH-25-i, 50, (-0, +0.5), (255, 255, 255), 25))
            elif second_tmr == 60:
                for i in range(0, 400, 50):
                    free_bullets.add(FreeBullet(125+i , 50, (+0, +0.5), (255, 255, 255), 25))
            elif second_tmr == 120:
                for i in range(0, 250, 50):
                    free_bullets.add(FreeBullet(25+i , 50, (+0, +0.5), (255, 255, 255), 25))
                    free_bullets.add(FreeBullet(WIDTH-25-i, 50, (-0, +0.5), (255, 255, 255), 25))
            elif second_tmr == 240:
                free_bullets.add(FreeBullet(25, 500, (+0.5, +0), (255, 255, 255), 25))
                free_bullets.add(FreeBullet(WIDTH-25, 600, (-0.5, -0), (255, 255, 255), 25))
            elif second_tmr == 300:
                free_bullets.add(FreeBullet(25, 600, (+0.5, +0), (255, 255, 255), 25))
                free_bullets.add(FreeBullet(WIDTH-25, 500, (-0.5, -0), (255, 255, 255), 25))
            elif second_tmr == 360:
                free_bullets.add(FreeBullet(25, 450, (+0.5, +0), (255, 255, 255), 25))
                free_bullets.add(FreeBullet(WIDTH-25, 450, (-0.5, -0), (255, 255, 255), 25))
            elif second_tmr == 420:
                free_bullets.add(FreeBullet(25, 650, (+0.5, +0), (255, 255, 255), 25))
                free_bullets.add(FreeBullet(WIDTH-25, 550, (-0.5, -0), (255, 255, 255), 25))
            
            #繰り返し放つ弾幕
            if 120 <= second_tmr and (second_tmr-120)%20 == 0:
                free_bullets.add(FreeBullet(25 , 25, (+0, +0.5), (255, 255, 255), 25))
                free_bullets.add(FreeBullet(WIDTH-25, 25, (-0, +0.5), (255, 255, 255), 25))
            if 180 <= second_tmr < 480 and (second_tmr-180)%30 == 0:
                # 8方位のベクトルを計算
                direction_vectors_8 = [(math.cos(angle), math.sin(angle))  # x = cos(θ), y = sin(θ)
                    for angle in [i * math.pi / 4 for i in range(8)]]  # 0, π/4, π/2, ..., 7π/4
                for vector in direction_vectors_8:
                    free_bullets.add(FreeBullet(150 , 150, vector, (255, 255, 255), 10))
                    free_bullets.add(FreeBullet(WIDTH-150 , 150, vector, (255, 255, 255), 10))
            if 480 <= second_tmr and (second_tmr-480)%30 == 0:
                # 16方位のベクトルを計算
                direction_vectors_16 = [(math.cos(angle), math.sin(angle))  # x = cos(θ), y = sin(θ)
                    for angle in [i * math.pi / 8 for i in range(16)]]  # 0, π/8, 2π/8, ..., 15π/8
                angle_step = 5 * math.pi / 180  # 5度をラジアンに変換
                rotation_angle = second_tmr-480//30 * angle_step  #時間に比例して増加する
                sin_theta = math.sin(rotation_angle)
                cos_theta = math.cos(rotation_angle)
                direction_vectors_16 = [(
                                        cos_theta * x + sin_theta * y,  # x' = cos(θ) * x + sin(θ) * y
                                        -sin_theta * x + cos_theta * y  # y' = -sin(θ) * x + cos(θ) * y
                                        )
                                        for x, y in direction_vectors_16]
                for vector in direction_vectors_16:
                    free_bullets.add(FreeBullet(150 , 150, vector, (255, 255, 255), 5))
                    free_bullets.add(FreeBullet(WIDTH-150 , 150, vector, (255, 255, 255), 5))
            second_tmr += 1

        for emy in emys:
            if hp_bar.kawata:
                    if random.random() < 0.3:
                        fall = Fall()  # 縦に降ってくる弾
                        bombs.add(fall)  # bombsグループに追加
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                if hp_bar.kawata:
                    for i in range(36):
                        bombs.add(AngleBomb(emy, collider, i*10))
                    bombs.add(Bullet(emy, collider))
                else:
                    bombs.add(Bullet(emy, collider))

        for emy in pg.sprite.groupcollide(emys, beams, False, True).keys():  # ビームと衝突した敵機リスト
            hp -= 10
            if hp <= 0:
                hp_bar.victory = True

        for bomb in pg.sprite.spritecollide(collider, bombs, True):  # こうかとんと衝突した弾幕リスト
            zanki -= 1
            if zanki <= 0:
                bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                pg.display.update()
                time.sleep(2)
                return

        for bomb in pg.sprite.spritecollide(collider, free_bullets, True):  # こうかとんと衝突した弾幕リスト
            zanki -= 1
            if zanki <= 0:
                bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                pg.display.update()
                time.sleep(2)
                return
        
        if hp_bar.victory:#HPが0の時
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
            bg_image = pg.Surface((WIDTH, HEIGHT))  #空のSurfaceの生成
            pg.draw.rect(bg_image, (0, 0, 0), (0, 0, WIDTH, HEIGHT))  #黒い矩形をdrawする
            bg_image.set_alpha(200)  #半透明にする
            bg_rect = bg_image.get_rect()
            clear_font = pg.font.Font(None, 50)
            clear_image = clear_font.render(f"clear! death: {3-zanki}, use bomb:{3-special.lives}", 0, (255, 0, 0))
            clear_rect = clear_image.get_rect()
            clear_rect.center = WIDTH/2, HEIGHT/2
            screen.blit(bg_image, bg_rect)
            screen.blit(clear_image, clear_rect)
            pg.display.update()
            time.sleep(5)
            return

        bird.update(key_lst, screen)
        collider.update(screen, bird)
        beams.update()
        beams.draw(screen)
        bombs.update()
        bombs.draw(screen)
        free_bullets.update()
        free_bullets.draw(screen)
        if len(gutters) >= 1:  # gutterが存在しない状況下でupdateがエラーを吐くため。
            gutters.update(screen)
        exps.update()
        exps.draw(screen)
        special.update(screen)
        zankis.update(screen)
        hp_bar.hp_draw(screen)
        anbo.update()
        anbo.draw(screen)
        falls.update()
        falls.draw(screen)
        emys.update()
        emys.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)
        
if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()