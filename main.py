import pygame
import random
import sys
import os
import pygame_menu
from pygame_menu import themes


width, height, fps = 600, 600, 90
result = 0

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("game!")
clock = pygame.time.Clock()


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, color_key=-1):
    fullname = os.path.join("data", name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print("Cannot load image", name)
        raise SystemExit(message)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def create_sound(name):
    fullname = os.path.join("music", name)
    sound = pygame.mixer.Sound(fullname)
    sound.set_volume(0.2)
    return sound


background = load_image("fom.jpg")
background_rect = background.get_rect()
font_name = pygame.font.match_font('Block Fonts')
player_mus = create_sound("bullet_music.mp3")
enemy_mus = create_sound("enemy_boom.mp3")
fun_music = create_sound("backround_music.mp3")


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, pygame.color.Color("Red"))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_lives(surf, x, y, lives):
    image = load_image("player_image.jpg")
    image = pygame.transform.scale(image, (30, 30))
    for i in range(lives):
        img_rect = image.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(image, img_rect)


def draw_health(surf, x, y, health):
    if health < 0:
        health = 0
    lenght_health = 100
    height_health = 20
    fill = (health / 100) * lenght_health
    outline_rect = pygame.Rect(x, y, lenght_health, height_health)
    fill_rect = pygame.Rect(x, y, fill, height_health)
    pygame.draw.rect(surf, pygame.Color("green"), fill_rect)
    pygame.draw.rect(surf, pygame.Color("white"), outline_rect, 2)


def gg_game():
    screen.blit(background, background_rect)
    draw_text(screen, "Game!", 64, width / 2, height / 6)
    draw_text(screen, "Press a key to begin", 64, width / 2, height * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


def set_difficulty(value, difficulty):
    f = open("data/dific.txt", "w", encoding="utf8")
    if difficulty == 2:
        print("+;-", file=f)
    else:
        print("-;+", file=f)
    print("1;5", file=f)
    print("3;8", file=f)
    f.close()


def start_the_game():
    mainmenu._open(loading)
    pygame.time.set_timer(update_loading, 30)


def level_menu():
    mainmenu._open(level)


mainmenu = pygame_menu.Menu('Welcome', width, height, theme=themes.THEME_SOLARIZED)
mainmenu.add.text_input('Name: ', default='username')
mainmenu.add.button('Play', start_the_game)
mainmenu.add.button('Levels', level_menu)
mainmenu.add.button('Quit', pygame_menu.events.EXIT)
level = pygame_menu.Menu('Select a Difficulty', width, height, theme=themes.THEME_BLUE)
level.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)
loading = pygame_menu.Menu('Loading the Game...', width, height, theme=themes.THEME_DARK)
loading.add.progress_bar("Progress", progressbar_id="1", default=0, width=200, )
arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))
update_loading = pygame.USEREVENT + 0


def start_menu():
    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == update_loading:
                progress = loading.get_widget("1")
                progress.set_value(progress.get_value() + 1)
                if progress.get_value() == 100:
                    pygame.time.set_timer(update_loading, 0)
                    running = False
            if event.type == pygame.QUIT:
                terminate()
        if mainmenu.is_enabled():
            mainmenu.update(events)
            mainmenu.draw(screen)
            if (mainmenu.get_current().get_selected_widget()):
                arrow.draw(screen, mainmenu.get_current().get_selected_widget())
        pygame.display.update()


class Player(pygame.sprite.Sprite):
    image = None

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        if Player.image is None:
            Player.image = load_image("player_image.jpg")
        self.image = pygame.transform.scale(Player.image, (50, 50))
        self.rect = self.image.get_rect()
        self.radius = 15
        self.rect.centerx = width / 3
        self.rect.bottom = height - 5
        self.speed = 0
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()

    def update(self):
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = width / 2
            self.rect.bottom = height - 10
        self.speed = 0
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            self.speed = -8
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            self.speed = 8
        self.rect.x += self.speed
        if self.rect.right > width:
            self.rect.right = width
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        player_mus.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (width / 2, height + 200)


class Enemy(pygame.sprite.Sprite):
    image = None

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        if Enemy.image is None:
            Enemy.image = load_image("enemy_image.jpg")
        self.copypasta = pygame.transform.scale(Enemy.image, (random.randint(30, 50), random.randint(20, 90)))
        self.image = self.copypasta.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2
        self.rect.x = random.randrange(width - self.rect.width)
        self.rect.y = random.randint(-110, -10)
        with open("data/dific.txt", encoding="utf8") as f:
            text = f.readlines()
            number = text[0].split(";")
            ind = 1
            for i, j in enumerate(number):
                if j[0] == "+":
                    ind = i + 1
                    break
            self.speed_y = random.randint(int(text[ind][0]), int(text[ind][2]))
        self.speed_x = random.randint(-1, 1)
        self.rotate = 0
        self.old = pygame.time.get_ticks()
        self.rotate_speed = random.randint(-1, 10)

    def update(self):
        self.povorot()
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > height or self.rect.right > width or self.rect.left < 0:
            self.rect.x = random.randrange(width - self.rect.width)
            self.rect.y = random.randint(-110, -10)
            self.speed_y = random.randint(1, 3)
            self.speed_x = random.randint(-1, 1)

    def povorot(self):
        now = pygame.time.get_ticks()
        if now - self.old > 35.7:
            self.old = now
            self.rotate = (self.rotate + self.rotate_speed) % 360
            new_image = pygame.transform.rotate(self.copypasta, self.rotate)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center


class Bullet(pygame.sprite.Sprite):
    image = None

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        if Bullet.image is None:
            Bullet.image = load_image("bullet_image.jpg")
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


start_menu()
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
for i in range(10):
    vrag = Enemy()
    enemies.add(vrag)
    all_sprites.add(vrag)
all_sprites.add(player)
fun_music.play(loops=-1)
game_over = False
running = True
while running:
    if game_over:
        gg_game()
        game_over = False
        all_sprites = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = Player()
        for i in range(10):
            vrag = Enemy()
            enemies.add(vrag)
            all_sprites.add(vrag)
        all_sprites.add(player)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player.shoot()
    all_sprites.update()
    otvetka = pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_circle)
    for odin in otvetka:
        player.health -= odin.radius
        odin.kill()
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        if player.health < 0:
            player.health = 100
            player.lives -= 1
            if player.lives == 0:
                game_over = True
    ydaril = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for ydarili in ydaril:
        result += 10
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
        enemy_mus.play()
    screen.fill(pygame.Color("Black"))
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(result), 18, width / 2, 10)
    draw_lives(screen, width - 100, 5, player.lives)
    draw_health(screen, 10, 10, player.health)
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()