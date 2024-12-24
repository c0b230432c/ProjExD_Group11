import math
import os
import random
import sys
import time
import pygame as pg


WIDTH = 600  # ゲームウィンドウの幅
HEIGHT = 700  # ゲームウィンドウの高さ
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# #### 小林担当部分 画面脇に湧く敵性オブジェクト
# class GutterLaser(pg.sprite.Sprite):
#     """
#     GutterEnemyクラスで生成されるlaserの当たり判定を担う。
#     どうやらpygameでは細長い画像を斜めにしてcolliderectすると、
#     細長い画像を対角線とした長方形/正方形を当たり判定として使ってしまうらしい。
#     その対策として、小さな正方形の当たり判定をlaserの画像上に並べればよい。
#     """
#     def __init__(self, xspawn, yspawn, colsize):
#         self.laser_colid = pg.transform.scale(pg.image.load("fig/miyasui_gazou.png"), (colsize, colsize))
#         self.xyspawn = (xspawn, yspawn)
#         self.laser_colid_rct = self.laser_colid.get_rect()
#         self.laser_colid_rct.center = self.xyspawn
#         print(9999999999999)


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
        select_x = spawn_x[random.randint(0,1)]
        select_y = spawn_y[random.randint(0,2)]
        self.sideFlag = "none"
        self.laser_size = 500   # レーザーの大きさを調整できる
        self.colsize = 10  # 当たり判定の正方形のサイズ
        self.laser_divide = 20  # レーザーの当たり判定を何個の正方形に置き換えるか
        self.lasercolid_xyspawns = []
        self.colist = []
        self.collideList = []
        self.spawn_xy = tuple([select_x, select_y])
        self.ge_img = pg.image.load("fig/miyasui_gazou2.png")  # 後ほど画像変更
        self.ge_img.convert_alpha()  # ピクセル単位で透明度を有効

        if self.spawn_xy[0] == WIDTH-20:
            self.ge_img = pg.transform.scale(pg.transform.flip(pg.transform.rotate(self.ge_img, 45), True, False), (100, 100))
            # 右側に湧く敵を中央へ向くように斜めにして縮小する
            self.sideFlag = "right"
        else:
            self.ge_img = pg.transform.scale(pg.transform.rotate(self.ge_img, 45), (100, 100))
            # 左側に湧く敵を中央へ向くように斜めにして縮小する
            self.sideFlag = "left"

        self.ge_rct = self.ge_img.get_rect()
        self.ge_rct.center = self.spawn_xy

        # 攻撃処理に関するゾーン
        self.fireing = False  # 発砲中フラグ
        self.fire_time = 190 # random.randint(15, self.life-30)  # 発砲タイミングの設定(生後15~(寿命-30))

        self.yokoyari_img = pg.transform.scale(pg.image.load("fig/clear_pic.png"), (self.laser_size, self.laser_size))
        # self.yokoyari_img.convert_alpha()
        # self.flare_rct = self.flare_img.get_rect()
        self.yokoyari_rct = self.yokoyari_img.get_rect()

        self.calc_xyspawns(self.sideFlag, self.colsize)

        # 攻撃描写に関するゾーン
        # self.flare_img = pg.transform.scale(pg.image.load("fig/flare_cross.png"), (20, 20))
        # self.flare_img.convert_alpha()
        

        # self.d_angle = [3, 20, 45, 60, 20, 5, 1]
        # self.num = 0
    
    def calc_xyspawns(self, sideFlag, colsize):
        side = sideFlag
        num = self.laser_divide
        if side == "right":
            bottomleft = self.yokoyari_rct.bottomleft
            # 下から1個目の四角
            temp = bottomleft[0], bottomleft[1]
            x = temp[0] + colsize/2
            y = temp[1] - colsize/2
            temp = x, y
            self.lasercolid_xyspawns.append((x, y))
            # 下から2個目以降、右上へ続く四角たち
            for i in range(num-1):
                x = temp[0] + colsize/2
                y = temp[1] - colsize/2
                temp = (x, y)
                self.lasercolid_xyspawns.append((x, y))
            
            
        elif side == "left":
            bottomright = self.yokoyari_rct.bottomright
            # 下から1個目の四角
            temp = bottomright[0], bottomright[1]
            x = temp[0] - colsize/2
            y = temp[1] - colsize/2
            temp = x, y
            self.lasercolid_xyspawns.append((x, y))
            # 下から2個目以降、左上へ続く四角たち
            for i in range(num-1):
                x = temp[0] - colsize/2
                y = temp[1] - colsize/2
                temp = (x, y)
                self.lasercolid_xyspawns.append((x, y))
            
    def createCol(self, xspawn, yspawn, colsize):
        self.laser_colid = pg.transform.scale(pg.image.load("fig/miyasui_gazou.png"), (colsize, colsize))
        self.xyspawn = (xspawn, yspawn)
        self.laser_colid_rct = self.laser_colid.get_rect()
        self.laser_colid_rct.center = self.xyspawn

        return self.laser_colid_rct

    # def getCollisionList(self):
    #     return self.colist
        
    def update(self, screen):
        screen.blit(self.ge_img, self.ge_rct)  # 敵性オブジェクトの描画
        if self.fire_time == self.life:  # 攻撃時間と寿命カウントが同じだったら
            self.fireing = True  # 発砲中をTrueにする

        if self.fireing:  # 
            # print(11111111111)
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


# class Score:
#     """
#     打ち落とした爆弾，敵機の数をスコアとして表示するクラス
#     爆弾：1点
#     敵機：10点
#     """
#     def __init__(self):
#         self.font = pg.font.Font(None, 50)
#         self.color = (0, 0, 255)
#         self.value = 0
#         self.image = self.font.render(f"Score: {self.value}", 0, self.color)
#         self.rect = self.image.get_rect()
#         self.rect.center = 100, HEIGHT-50

#     def update(self, screen: pg.Surface):
#         self.image = self.font.render(f"Score: {self.value}", 0, self.color)
#         screen.blit(self.image, self.rect)


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
        self.value.width = self.width * (self.hp / self.max)
        if self.hp <= 0:
            self.victory=True

    def hp_draw(self, screen):
        """
        HPバーを表示する関数
        引数：screen
        """ 
        if not self.victory:
            color = (0, 255, 0)
            if self.hp / self.max <= 0.1:
                color = (255, 0, 0)
            elif self.hp / self.max <= 0.5:
                color = (255, 255, 0)
            pg.draw.rect(screen, (255, 255, 255), self.frame)
            pg.draw.rect(screen, (0, 0, 0), self.bar)
            pg.draw.rect(screen, color, self.value)
            screen.blit(self.label, (self.x, self.y))


def main():
    pg.display.set_caption("真！こうかとん無双")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load(f"fig/background01.png")  # デフォルトではpb_bg.jpg
    # score = Score()

    bird = Bird(3, (WIDTH/2, HEIGHT-100))  # こうかとん出現場所
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gutters = pg.sprite.Group() # 小林担当部分
    glasers = pg.sprite.Group()
    max_hp = 200  #敵機の最大HP
    hp=max_hp  #現在の敵機のHP
    

    tmr = 1 
    # print(len(gutters),471)
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

        if tmr == 200:  # 200フレームに敵を出現させる
            emys.add(Enemy())

        if tmr % 200 == 0:  # 小林担当部分 # 541フレーム間隔で敵を出現させる
            gutters.add(GutterEnemy())

        for gutter in gutters:
            if gutter.fireing:
                # print("Fireing")
                for j in range(len(gutter.collideList)):
                    # print("collideList Cycle")
                    if gutter.collideList[j].colliderect(bird):
                        # print("COLLIDED")
                        bird.change_img(8, screen)  # こうかとん悲しみエフェクト
                        # score.update(screen)
                        pg.display.update()
                        time.sleep(2)
                        return
        

        # for glaser_colid in glaser_colids:  # こうかとんと衝突したGutterEnemyリスト
        #     if glaser_colid.colliderect(bird):
        #         bird.change_img(8, screen)  # こうかとん悲しみエフェクト
        #         # score.update(screen)
        #         pg.display.update()
        #         time.sleep(2)
        #         return
        

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bullet(emy, bird))

        for emy in pg.sprite.groupcollide(emys, beams, False, True).keys():  # ビームと衝突した敵機リスト
            # exps.add(Explosion(emy, 100))  # 爆発エフェクト
            # score.value += 10  # 10点アップ
            hp -= 10
            if hp <= 0:
                hp_bar.victory = True
            bird.change_img(6, screen)  # こうかとん喜びエフェクト

        # for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():  # ビームと衝突した爆弾リスト
        #     exps.add(Explosion(bomb, 50))  # 爆発エフェクト
        #     score.value += 1  # 1点アップ
        #コメントアウト理由:弾幕は消さない仕様にするため

        for bomb in pg.sprite.spritecollide(bird, bombs, True):  # こうかとんと衝突した爆弾リスト
            bird.change_img(8, screen)  # こうかとん悲しみエフェクト
            # score.update(screen)
            pg.display.update()
            time.sleep(2)
            return
        
        if hp_bar.victory:#HPが0の時
            bird.change_img(6, screen)  # こうかとん悲しみエフェクト
            # score.update(screen)
            pg.display.update()
            time.sleep(2)
            return

        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        bombs.update()
        bombs.draw(screen)
        exps.update()
        exps.draw(screen)
        # score.update(screen)
        hp_bar.hp_draw(screen)
        if len(gutters) >= 1: # 小林部分
            gutters.update(screen)

        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
