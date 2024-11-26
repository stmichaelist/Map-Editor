import pygame
from os import listdir
from os.path import join, isfile
import sys

# Inicializando o Pygame
pygame.init()
player_walk = []
player_anim_frame = 1
player_anim_time = 0
RunningCoolDown = 0
# Definindo o tamanho dos tiles e da tela
TILE_SIZE = 100
WIDTH = 1800
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Sem Nome')
fps = 60
PLAYER_VEL = 10
timer = pygame.time.Clock()

def flip(sprites):
    return [pygame.transform.flip(sprite,True,False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


# Classe do tile
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image, type):
        super().__init__()
        self.image = image
        self.type = type
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        #Implementar comportamentos do tile
        pass

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 5
    SPRITES = load_sprite_sheets("images", "astronaut", 32, 32, True)
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel_x = 0
        self.vel_y = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.key_count = 0
    
    def jump(self):
        self.vel_y = -self.GRAVITY * 2.3
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0


    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.vel_x = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0
    
    def move_right(self, vel):
        self.vel_x = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.vel_y += min(1,(self.fall_count/fps) * self.GRAVITY)
        self.move(self.vel_x, self.vel_y)

        self.fall_count += 1
        self.update_sprite()
    
    def landed(self):
        self.fall_count = 0
        self.vel_y = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.vel_y *= -1

    def update_sprite(self):
        sprite_sheet = "astronaut"
        if self.vel_y != 0:
            if self.jump_count == 1:
                sprite_sheet = "Jump"
        if self.vel_x != 0 and self.vel_y > 0:
            sprite_sheet ="Walk"

        sprite_sheet_name = sprite_sheet + "_"+ self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win):
        win.blit(self.sprite, (self.rect.x, self.rect.y))

def draw(screen, player):


    player.draw(screen)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    player.update()  # Garante que a máscara do jogador está atualizada

    for obj in objects:
        if not hasattr(obj, 'mask') or obj.mask is None:
            continue

        if pygame.sprite.collide_mask(player, obj):  # Verifica a colisão de máscara
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            
            collided_objects.append(obj)

            # Lógica para lidar com tiles do tipo "Key"
            if obj.type in [6, 7, 8, 9]:  # Tipos de Key
                player.key_count += 1
                objects.remove(obj)  # Remove o tile do grupo

                # Atualiza o level_map com 0 (vazio)
                level_map[obj.row][obj.col] = 0  
                print(f"Key coletada! Total de keys: {player.key_count}")
            elif obj.type in [10,11,12,13] and player.key_count > 0:
                player.key_count = player.key_count -1
                objects.remove(obj)  # Remove o tile do grupo

                # Atualiza o level_map com 0 (vazio)
                level_map[obj.row][obj.col] = 0  
                print(f"Key Gasta! Total de keys: {player.key_count}")

                #Inserir lógica para carregar próxima fase AQ E NO COLLIDE!!!


    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None

    for obj in objects:
        if not hasattr(obj, 'mask') or obj.mask is None:
            # Ignora objetos sem máscara
            continue
        
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            if obj.type in [6, 7, 8, 9]:  # Tipos de Key
                player.key_count += 1
                objects.remove(obj)  # Remove o tile do grupo

                # Atualiza o level_map com 0 (vazio)
                level_map[obj.row][obj.col] = 0  
                print(f"Key coletada! Total de keys: {player.key_count}")
            elif obj.type in [10,11,12,13] and player.key_count > 0:
                player.key_count = player.key_count -1
                objects.remove(obj)  # Remove o tile do grupo

                # Atualiza o level_map com 0 (vazio)
                level_map[obj.row][obj.col] = 0  
                print(f"Key Gasta! Total de keys: {player.key_count}")
                #Inserir lógica para carregar próxima fase AQ E NO HANDLE_VERTICAL_COLLISION!!!
            break
    
    player.move(-(1.3*dx),0)
    player.update()
    return collided_object
                
def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.vel_x = 0
    collide_left = collide(player, objects, -PLAYER_VEL)
    collide_right = collide(player, objects, PLAYER_VEL)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    handle_vertical_collision(player, objects, player.vel_y)

def load():
    global bg,clock, rock, ground, platform, acid, blue_key, green_key, red_key, yellow_key, blue_door, green_door, red_door, yellow_door, tiles, level_map,sys_font
    clock = pygame.time.Clock()
    tile_group = pygame.sprite.Group()

# Carregar imagens (Exemplo com tiles, adicione o caminho correto)
    bg = pygame.image.load('assets/images/space bg.png')
    sys_font = pygame.font.Font("assets/fonts/fonte.ttf", 30)
    rock = pygame.transform.scale(pygame.image.load('assets/images/tiles/rock.png'), (100, 100))
    ground = pygame.transform.scale(pygame.image.load('assets/images/tiles/ground.png'), (100, 100))
    platform = pygame.transform.scale(pygame.image.load('assets/images/tiles/platform.png'), (100, 50))
    acid = pygame.transform.scale(pygame.image.load('assets/images/tiles/acid2.png'), (100, 25))
    blue_key = pygame.transform.scale(pygame.image.load('assets/images/keycards/key_blue.png'), (60, 100))
    green_key = pygame.transform.scale(pygame.image.load('assets/images/keycards/key_green.png'), (60, 100))
    red_key = pygame.transform.scale(pygame.image.load('assets/images/keycards/key_red.png'), (60, 100))
    yellow_key = pygame.transform.scale(pygame.image.load('assets/images/keycards/key_yellow.png'), (60, 100))
    blue_door = pygame.transform.scale(pygame.image.load('assets/images/portals/blue.png'), (100, 100))
    green_door = pygame.transform.scale(pygame.image.load('assets/images/portals/green.png'), (100, 100))
    red_door = pygame.transform.scale(pygame.image.load('assets/images/portals/red.png'), (100, 100))
    yellow_door = pygame.transform.scale(pygame.image.load('assets/images/portals/yellow.png'), (100, 100))

    # Lista de tiles, incluindo as chaves e portas
    tiles = ['', rock, ground, platform, acid, '', blue_key, green_key, red_key, yellow_key, blue_door, green_door, red_door, yellow_door]

    # Definir o mapa do nível (copie do Level Editor)
    level_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 3, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 3, 0, 0, 1, 4, 4, 4, 0, 0, 0, 0, 0, 4, 4, 4, 11, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],

    ]

tile_group = pygame.sprite.Group()

# Somente pra verificação de Objetos Tiles
def print_tile_group(tile_group):
    print("Verificando os objetos no grupo de tiles:")
    for index, tile in enumerate(tile_group):
        tile_type = "Desconhecido"
        if tile.image == acid:
            tile_type = "Acid"
        elif tile.image == ground:
            tile_type = "Ground"
        elif tile.image == platform:
            tile_type = "Platform"
        elif tile.image == rock:
            tile_type = "Rock"
        elif tile.image in [blue_key, green_key, red_key, yellow_key]:
            tile_type = "Key"
        elif tile.image in [blue_door, green_door, red_door, yellow_door]:
            tile_type = "Door"
        
        print(f"Index: {index}, Tipo do Tile: {tile_type}, Posição: {tile.rect.topleft}")

# Função para desenhar o mapa
def draw_map(screen, tile_group):
    for row in range(len(level_map)):
        for col in range(len(level_map[row])):
            tile_type = level_map[row][col]
            if tile_type != 0:  # Ignora espaços vazios
                tile_image = tiles[tile_type]
                if tile_image:  # Verifica se o tile não está vazio
                    x = col * TILE_SIZE
                    y = row * TILE_SIZE
                    
                    # Ajustar a posição do ácido
                    if tile_type == 4:  # 4 representa o ácido no seu mapa
                        y += TILE_SIZE - acid.get_height()  # Ajusta para alinhar embaixo

                    # Verifica se o tile já foi criado
                    existing_tile = any(t.rect.x == x and t.rect.y == y for t in tile_group)
                    if not existing_tile:  # Adiciona somente se não existir
                        tile = Tile(x, y, tile_image, tile_type)
                        tile.row = row  # Salva a linha na matriz
                        tile.col = col  # Salva a coluna na matriz
                        tile_group.add(tile)
    tile_group.update()
    tile_group.draw(screen)

def draw_button(screen, text, x, y, width_button, height_button, color, hover_color):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width_button, height_button)


    if button_rect.collidepoint(mouse_x, mouse_y):
        color = hover_color  

    pygame.draw.rect(screen, color, button_rect, border_radius=10)
    
    start = sys_font.render(text, True, (255, 255,255 ))  
    text_rect = start.get_rect(center=button_rect.center)
    screen.blit(start, text_rect)

    return button_rect  


def show_start_screen(screen, tile_group):
    running = True
    while running:
        draw_map(screen, tile_group)

        button_rect = draw_button(screen, "Start", WIDTH // 2 - 150 // 2, 150,  150, 75, (25, 177, 76),(0, 255, 0))    

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Encerra o jogo
            elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                return True  # Começa o jogo

        pygame.display.update()

# Função principal
def main(screen):
    global clock
    running = True
    player = Player(250, 620, 50, 50)
    while running:
        screen.fill('black')  # Limpa a tela com a cor preta
        
        # Desenha o fundo na tela
        screen.blit(bg, (0, 0))  # Desenha a imagem do fundo na posição (0, 0)
        clock.tick(fps)
        dt = clock.get_time()

        player.loop(fps)
        handle_move(player, tile_group)

        # Desenha o mapa com os tiles
        draw_map(screen, tile_group)
        draw(screen, player)
        pygame.display.update()

        # Evento de fechar a janela
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and player.jump_count < 1:
                    player.jump()

        
        pygame.display.flip()  # Atualiza a tela
        timer.tick(fps)  # Controla a taxa de frames
    
    #VERIFICANDO OBJETOS POR MAPA
    print_tile_group(tile_group)
    
    pygame.quit()
    sys.exit()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
load()
if show_start_screen(screen, tile_group):  # Exibe a tela de início
    main(screen)
pygame.quit()