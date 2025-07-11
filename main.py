import pygame
import sys
import os

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 800, 600
TILE_SIZE = 40
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -16
PLAYER_SPEED = 5
INVINCIBILITY_TIME = 3000

# --- Screen ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2-Player Platformer")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)

# --- Asset Loading ---
def load_image(name, size=(TILE_SIZE, TILE_SIZE)):
    return pygame.transform.scale(pygame.image.load(os.path.join("assets", name)), size)

images = {
    "tile": load_image("tile.png"),
    "player1": load_image("player1.png"),
    "player2": load_image("player2.png"),
    "enemy": load_image("enemy.png"),
    "coin": load_image("coin.png", (20, 20)),
    "invincible": load_image("invincible.png", (30, 30)),
    "goal": load_image("goal.png", (20, 20)),
}

# --- Background and Music ---
background_img = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.png")), (WIDTH, HEIGHT))
pygame.mixer.music.load(os.path.join("assets", "music.mp3"))
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# --- Sound Effects ---
coin_sound = pygame.mixer.Sound(os.path.join("assets", "coin.mp3"))
coin_sound.set_volume(0.6)

# --- Level Map ---
LEVELS = [
    [
        "                                                                     ",
        "                                                                     ",
        "                                                                     ",
        "      c                    g                                         ",
        "                ^                                                    ",
        "                                                                     ",
        "      %                                                              ",
        "                                                                     ",
        "        ===                                                          ",
        "p       =q=                                                          ",
        "===========     =====================================================",
    ],
    [
        "                             ",
        "                             ",
        "                             ",
        "                           g ",
        "                ^     =====  ",
        "                             ",
        "      c             =        ",
        "   =======       ======      ",
        "                             ",
        "p        q                   ",
        "=============================",
    ],
    [
        "                             ",
        "                             ",
        "                             ",
        "                           g ",
        "                ^     =====  ",
        "                             ",
        "      c             =        ",
        "   =======       ======      ",
        "                             ",
        "p        q                   ",
        "=============================",
    ],
    [
        "                             ",
        "                             ",
        "                             ",
        "                           g ",
        "                ^     =====  ",
        "                             ",
        "      c             =        ",
        "   =======       ======      ",
        "                             ",
        "p        q                   ",
        "=============================",
    ],
]

# --- Classes ---
class Entity(pygame.sprite.Sprite):
    def __init__(self, image, x, y, w=TILE_SIZE, h=TILE_SIZE):
        super().__init__()
        self.image = pygame.transform.scale(image, (w, h))
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(Entity):
    def __init__(self, image, x, y, controls):
        super().__init__(image, x, y)
        self.original_image = self.image.copy()
        self.vel_y = 0
        self.on_ground = False
        self.invincible = False
        self.invincibility_timer = 0
        self.controls = controls

    def update(self, tiles):
        keys = pygame.key.get_pressed()
        dx = 0
        dy = self.vel_y

        if keys[self.controls['left']]:
            dx -= PLAYER_SPEED
        if keys[self.controls['right']]:
            dx += PLAYER_SPEED
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = JUMP_STRENGTH

        self.vel_y += GRAVITY

        self.rect.x += dx
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if dx > 0:
                    self.rect.right = tile.rect.left
                if dx < 0:
                    self.rect.left = tile.rect.right

        self.rect.y += dy
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if dy > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0

        if self.invincible and pygame.time.get_ticks() - self.invincibility_timer > INVINCIBILITY_TIME:
            self.invincible = False
            self.image = self.original_image

    def set_invincible(self):
        self.invincible = True
        self.invincibility_timer = pygame.time.get_ticks()
        self.image = pygame.transform.scale(images["invincible"], (TILE_SIZE, TILE_SIZE))

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__(images["enemy"], x, y)
        self.direction = 1
        self.speed = 2

    def update(self):
        self.rect.x += self.direction * self.speed
        if self.rect.left <= 0 or self.rect.right >= WIDTH * 2:
            self.direction *= -1

class InvincibilityBlock(Entity):
    def __init__(self, x, y):
        super().__init__(images["invincible"], x + 5, y + 5, 30, 30)

class Goal(Entity):
    def __init__(self, x, y):
        super().__init__(images["goal"], x + 10, y + 10, 20, 20)

# --- Level Loader ---
def load_level(level_map):
    global player1, player2, tiles, enemies, coins, goal, prizes, level_width, level_height

    tiles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    goal = pygame.sprite.Group()
    prizes = pygame.sprite.Group()

    player1 = None
    player2 = None

    for row_index, row in enumerate(level_map):
        for col_index, char in enumerate(row):
            x, y = col_index * TILE_SIZE, row_index * TILE_SIZE
            if char == "=":
                tiles.add(Entity(images["tile"], x, y))
            elif char == "p":
                player1 = Player(images["player1"], x, y, {'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'jump': pygame.K_SPACE})
            elif char == "q":
                player2 = Player(images["player2"], x, y, {'left': pygame.K_a, 'right': pygame.K_d, 'jump': pygame.K_w})
            elif char == "^":
                enemies.add(Enemy(x, y))
            elif char == "c":
                coins.add(Entity(images["coin"], x + 10, y + 10, 20, 20))
            elif char == "g":
                goal.add(Goal(x, y))
            elif char == "%":
                prizes.add(InvincibilityBlock(x, y))

    level_width = len(level_map[0]) * TILE_SIZE
    level_height = len(level_map) * TILE_SIZE

# --- Game State ---
level_index = 0
score = 0
game_state = "play"
camera_offset = pygame.Vector2(0, 0)

load_level(LEVELS[level_index])

def draw_group(group):
    for sprite in group:
        screen.blit(sprite.image, sprite.rect.topleft - camera_offset)

# --- Main Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state in ["gameover", "win"] and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                level_index = 0
                score = 0
                load_level(LEVELS[level_index])
                game_state = "play"
                camera_offset = pygame.Vector2(0, 0)

    if game_state == "play":
        player1.update(tiles)
        player2.update(tiles)
        enemies.update()

        for player in [player1, player2]:
            for coin in pygame.sprite.spritecollide(player, coins, True):
                score += 1
                coin_sound.play()

            for block in pygame.sprite.spritecollide(player, prizes, True):
                player.set_invincible()

            for enemy in pygame.sprite.spritecollide(player, enemies, False):
                if player.invincible:
                    enemies.remove(enemy)
                else:
                    game_state = "gameover"

            if pygame.sprite.spritecollideany(player, goal):
                level_index += 1
                if level_index < len(LEVELS):
                    load_level(LEVELS[level_index])
                else:
                    game_state = "win"

            if player.rect.top > HEIGHT:
                game_state = "gameover"

        # Camera follows player1
        camera_offset.x = player1.rect.centerx - WIDTH // 2
        camera_offset.y = player1.rect.centery - HEIGHT // 2
        camera_offset.x = max(0, min(camera_offset.x, level_width - WIDTH))
        camera_offset.y = max(0, min(camera_offset.y, level_height - HEIGHT))

        draw_group(tiles)
        draw_group(enemies)
        draw_group(coins)
        draw_group(prizes)
        draw_group(goal)
        screen.blit(player1.image, player1.rect.topleft - camera_offset)
        screen.blit(player2.image, player2.rect.topleft - camera_offset)

        screen.blit(font.render(f"Coins: {score}", True, (255, 255, 255)), (20, 20))
        if player1.invincible:
            screen.blit(font.render("P1 INVINCIBLE!", True, (0, 255, 255)), (WIDTH - 250, 20))
        if player2.invincible:
            screen.blit(font.render("P2 INVINCIBLE!", True, (0, 255, 255)), (WIDTH - 250, 60))

    elif game_state == "gameover":
        screen.blit(font.render("Game Over! Press R to restart", True, (255, 0, 0)), (WIDTH // 2 - 220, HEIGHT // 2))

    elif game_state == "win":
        screen.blit(font.render("You Win! Press R to play again", True, (0, 255, 0)), (WIDTH // 2 - 210, HEIGHT // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()
