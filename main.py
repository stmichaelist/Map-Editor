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
pygame.display.set_caption('Astronaut Adventures')
fps = 60
PLAYER_VEL = 10
timer = pygame.time.Clock()
global level, path
level = 1

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
    LIVES=3

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.vel_x = 0
        self.vel_y = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.keys = []
        self.key_counts = {
            'blue': 0,
            'green': 0,
            'red': 0,
            'yellow': 0
        }
        self.openned_doors = []
        self.lives = self.LIVES  # Inicializa o número de vidas
        self.dead = False  # Flag para verificar se o jogador morreu
        
    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.dead = True  # O jogador morre quando as vidas chegam a 0
    
    def reset_position(self, x, y):
        self.rect.x = x
        self.rect.y = y
        self.lives = self.LIVES  # Restaura as vidas ao reiniciar
        self.dead = False  # O jogador revive
        
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
        
    def collect_key(self, key_type):
        # Mapeia os tipos de chaves para suas cores
        key_map = {
            6: 'blue',
            7: 'green',
            8: 'red',
            9: 'yellow'
        }

        if key_type in key_map:
            key_color = key_map[key_type]
            self.key_counts[key_color] += 1  # Incrementa o contador
            print(f"Chave {key_color.capitalize()} coletada!")
            print(f"Inventário de chaves: {self.key_counts}")

    
    def open_doors(self, door_type, tile):
        global level, path, level_map, tile_group

        # Mapeia os tipos de porta com suas respectivas chaves
        key_map = {
            10: 'blue',
            11: 'green',
            12: 'red',
            13: 'yellow'
        }

        # Verifica se o tipo de porta é válido e se ainda não foi aberta
        if door_type in key_map:
            key_color = key_map[door_type]

            # Verifica se há chaves disponíveis para a porta
            if self.key_counts[key_color] > 0:
                self.key_counts[key_color] -= 1  # Remove uma chave do inventário
                self.openned_doors.append(door_type)  # Marca a porta como aberta
                tile_group.remove(tile)  # Remove a porta do grupo
                level_map[tile.row][tile.col] = 0  # Remove a porta do mapa
                print(f"Porta {key_color.capitalize()} aberta! Chaves restantes: {self.key_counts}")

                # Carregar o próximo nível
                if level < 5:  # Se ainda houver níveis disponíveis
                    level += 1
                    path = f'level{level}.txt'
                    print(f"Carregando {path}...")

                    # Recarregar o mapa
                    level_map = load_level_from_file(path)

                    # Reconfigurar o grupo de tiles
                    tile_group.empty()  # Limpa o grupo existente
                    draw_map(screen, tile_group)  # Recarrega o grupo de tiles no novo nível

                    # Reposicionar o jogador
                    self.rect.x, self.rect.y = 230, 620
                    print(f"Jogador transportado para ({self.rect.x}, {self.rect.y})")

                else:
                    # Caso seja o último nível, exibir tela final
                    screen.fill((0, 0, 0))  # Limpa a tela
                    show_end_screen(screen)
                    pygame.quit()
                    sys.exit()

            else:
                print(f"Sem chaves {key_color.capitalize()} para abrir a porta!")


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
            # Ignora objetos sem máscara
            continue

        if pygame.sprite.collide_mask(player, obj):  # Verifica a colisão de máscara
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
            if obj.image == acid:  
                player.lives=0
                player.lose_life()
            collided_objects.append(obj)

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
    
def load_level_from_file(file_path):
    level_map = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Converte a linha para uma lista de inteiros
                row = [int(value) for value in line.strip().strip('[],').split(',')]
                level_map.append(row)
    except FileNotFoundError:
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
    except ValueError:
        print("Erro: O arquivo contém valores inválidos.")
    return level_map


def load():
    global bg,clock, rock, ground, platform, acid, blue_key, green_key, red_key, yellow_key, blue_door, green_door, red_door, yellow_door, tiles, level_map,sys_font, level, path
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
    path = f'level{level}.txt'
    print(path)
    level_map = load_level_from_file(path)

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

def check_collectibles(player, tile_group, proximity_threshold=20):
    player.update()  # Atualiza a máscara do jogador
    player_rect = player.rect  # Retângulo que representa a posição do jogador
    
    for tile in tile_group:
        if tile.type in [6, 7, 8, 9]:  # Tipos das chaves
            tile_rect = tile.rect  # Retângulo do item
            if pygame.sprite.collide_mask(player, tile):
                print(f"Coletando chave {tile.type}")
                player.collect_key(tile.type)  # Adiciona ao inventário do jogador
                tile_group.remove(tile)  # Remove o keycard do grupo
                level_map[tile.row][tile.col] = 0  # Remove do mapa
                continue

            # Verifica proximidade: se o jogador está dentro do raio de proximidade do item
            if player_rect.colliderect(tile_rect.inflate(proximity_threshold, proximity_threshold)):
                # Aproxime a detecção, se o jogador estiver perto do item, colete-o
                player.collect_key(tile.type)  # Adiciona ao inventário do jogador
                tile_group.remove(tile)  # Remove o keycard do grupo
                level_map[tile.row][tile.col] = 0  # Remove do mapa


def check_doors(player, tile_group, proximity_threshold=20):
    player.update()  # Atualiza a máscara do jogador
    player_rect = player.rect  # Retângulo que representa a posição do jogador
    for tile in tile_group:
        if tile.type in [10, 11, 12, 13]:  # Tipos das chaves
            tile_rect = tile.rect  # Retângulo do item
            if pygame.sprite.collide_mask(player, tile):
                print(f"Abrindo porta {tile.type}")
                player.open_doors(tile.type, tile)  # Adiciona ao inventário do jogador
                continue

            # Verifica proximidade: se o jogador está dentro do raio de proximidade do item
            if player_rect.colliderect(tile_rect.inflate(proximity_threshold, proximity_threshold)):
                # Aproxime a detecção, se o jogador estiver perto do item, colete-o
                player.open_doors(tile.type, tile)  # Adiciona ao inventário do jogador

                
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


def draw_lives(screen, lives, font):
    lives_text = font.render(f'Vidas: {lives}', True, (255, 255, 255))
    screen.blit(lives_text, (10, 10))  # Desenha o texto no canto superior esquerdo

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

def show_end_screen(screen):
    running = True
    while running:
        screen.fill((0, 0, 0))  # Preenche o fundo de preto

        # Configuração do texto
        font = pygame.font.Font(None, 74)  # Fonte e tamanho
        text = font.render("Parabéns! Você completou o jogo!", True, (255, 255, 255))  # Texto branco
        text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))  # Centraliza

        # Desenha o texto
        screen.blit(text, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Encerra o jogo

        pygame.display.update()


# Função principal
def main(screen):
    global clock,level,level_map 
    running = True
    player = Player(230, 620, 50, 50)
    while running:
        screen.fill('black')  # Limpa a tela com a cor preta
        
        # Desenha o fundo na tela
        screen.blit(bg, (0, 0))  # Desenha a imagem do fundo na posição (0, 0)
        clock.tick(fps)
        dt = clock.get_time()

        player.loop(fps)
        handle_move(player, tile_group)
        
        # Verificar coleta de itens
        check_collectibles(player, tile_group)

        check_doors(player, tile_group)
        if player.dead or player.rect.right < 0 or player.rect.left > 1800:
        # Mostra uma mensagem de "Game Over" e reinicia o jogo
            game_over_text = sys_font.render("Game Over", True, (255, 0, 0))
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(2000)  # Espera 2 segundos antes de reiniciar
            player.reset_position(100, 10)  # Reseta o jogador para a posição inicial
            player.lives=3
            level=1 

            path = f'level{level}.txt'
            print(f"Carregando {path}...")

            # Recarregar o mapa
            level_map = load_level_from_file(path)

            tile_group.empty()  
            screen.fill((0, 0, 0))
            if show_start_screen(screen, tile_group):  # Exibe a tela de início
                main(screen)
        # Desenha o mapa com os tiles
        draw_map(screen, tile_group)
        draw(screen, player)

        draw_lives(screen, player.lives, sys_font)
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
    
    pygame.quit()
    sys.exit()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
load()
if show_start_screen(screen, tile_group):  # Exibe a tela de início
    main(screen)
pygame.quit()