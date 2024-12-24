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
        self.dire = (+1, 0)
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


class Bullet(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
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
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

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
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
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
        self.speed = 6
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height//2
        self.speed = 6

    def update(self):
        """
        爆弾を計算した速度ベクトルself.resに基づき移動させる
        """
        self.rect.move_ip(self.speed*self.res[0], self.speed*self.res[1])
        if check_bound(self.rect) != (True, True):
            self.kill()


class Fall(pg.sprite.Sprite):
    """
    縦に振ってくる爆弾のクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    def __init__(self):
        """
        上から降ってくる爆弾を生成する関数
        """
        super().__init__()
        rad = 25  # 爆弾円の半径：25
        self.image = pg.Surface((2*rad, 2*rad))
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.vx, self.vy = 0,6
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


class Razer(pg.sprite.Sprite):
    def __init__(self, length=800, width=20, color=(255, 0, 0)):
        super().__init__()
        self.length = length
        self.width = width
        self.color = color
        self.image = pg.Surface((length, width), pg.SRCALPHA)
        pg.draw.rect(self.image, color, (0, 0, length, width))
        self.orig_image = self.image
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.angle = 0
        self.rotation_speed = 2
        self.timer = 0
        self.mask = pg.mask.from_surface(self.image)

    def update(self):
        self.angle += self.rotation_speed
        self.angle %= 360
        self.image = pg.transform.rotate(self.orig_image, -self.angle)
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.mask = pg.mask.from_surface(self.image)
        self.timer += 1
        if self.timer >= 50:  # 1秒間表示（50フレーム）
            self.kill()  # razerを消す



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
        self.vx, self.vy = bird.dire
        angle = math.degrees(math.atan2(-self.vy, self.vx))
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/beam.png"), angle, 1.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
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
        self.kawata = True
        if self.hp <= 0:
            self.victory = True
        # if self.hp / self.max <= 0.3:    #3割り切ったら河田担当
        #     self.kawata = True

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


def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/background01.png")
    bird = Bird(3, (WIDTH/2, HEIGHT-100))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    anbo = pg.sprite.Group()
    falls = pg.sprite.Group()
    razers = pg.sprite.Group()
    max_hp = 1000
    hp = max_hp

    tmr = 0
    clock = pg.time.Clock()
    while True:
        hp_bar = HP(WIDTH - 250, 20, 200, hp, max_hp)
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.add(Beam(bird))
        screen.blit(bg_img, [0, 0])

        if tmr == 0:
            emys.add(Enemy())

        for emy in emys:
            if emy.state == "stop" and tmr % emy.interval == 0:
                if hp_bar.kawata:
                    if random.random() < 0.025:
                        fall = Fall()
                        bombs.add(fall)
                    if random.random() < 0.5 and len(razers) == 0:  # 2%の確率でレーザーを生成（既存のレーザーがない場合）
                        razers.add(Razer())
                    for i in range(30):
                        bombs.add(AngleBomb(emy, bird, i*12))
                    bombs.add(Bullet(emy, bird))
                else:
                    bombs.add(Bullet(emy, bird))

        for emy in pg.sprite.groupcollide(emys, beams, False, True).keys():
            hp -= 10
            if hp <= 0:
                hp_bar.victory = True
            bird.change_img(6, screen)

        for razer in razers:
            if pg.sprite.collide_mask(bird, razer):  # マスクを使用した衝突判定
                bird.change_img(8, screen)
                exps.add(Explosion(bird, 50))
                pg.display.update()
                time.sleep(2)
                return

        for bomb in pg.sprite.spritecollide(bird, bombs, True):
            bird.change_img(8, screen)
            exps.add(Explosion(bird, 50))
            pg.display.update()
            time.sleep(2)
            return
        
        if pg.sprite.spritecollide(bird, razers, False):  # レーザーとの衝突判定
            bird.change_img(8, screen)
            exps.add(Explosion(bird, 50))
            pg.display.update()
            time.sleep(2)
            return

        if hp_bar.victory:
            bird.change_img(6, screen)
            pg.display.update()
            time.sleep(2)
            return

        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        hp_bar.hp_draw(screen)
        razers.update()
        razers.draw(screen)
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