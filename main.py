import pygame
import sys

# Inicializando o Pygame
pygame.init()
player_walk = []
player_anim_frame = 1
playerpos_x, playerpos_y = 100, 650
player_anim_time = 0
gravity = 0.5
vel_y = 0
vel_x = 0.2
RunningCoolDown = 0
# Definindo o tamanho dos tiles e da tela
TILE_SIZE = 100
WIDTH = 1800
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Sem Nome')
fps = 60
timer = pygame.time.Clock()

def load():
    global bg,clock, rock, ground, platform, acid, blue_key, green_key, red_key, yellow_key, blue_door, green_door, red_door, yellow_door, tiles, level_map
    clock = pygame.time.Clock()
# Carregar imagens (Exemplo com tiles, adicione o caminho correto)
    bg = pygame.image.load('assets/images/space bg.png')

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
    for i in range (1,5):
        image = pygame.image.load("assets/images/astronaut/" + str(i) + ".png")
        # Redimensiona a imagem do personagem para um tamanho menor, como 50x50
        image = pygame.transform.scale(image, (50, 50))  # ajuste para o tamanho desejado
        player_walk.append(image)


def update(dt):
    global vel_y, vel_x, is_Running, RunningCoolDown, player_anim_frame, playerpos_x, playerpos_y, player_anim_time, old_x, old_y,  gravity
    old_x= playerpos_x
    keys = pygame.key.get_pressed()

    # Aplicar gravidade ao jogador
    vel_y += gravity
    RunningCoolDown += dt

    # Movimento lateral do jogador
    if keys[pygame.K_RIGHT]:
        playerpos_x += vel_x * dt
        player_anim_time += dt  # incrementa o tempo usando dt
        if player_anim_time > 100:  # quando acumular mais de 100 ms
            player_anim_frame += 1  # avança para o próximo frame
            if player_anim_frame > 3:  # loop da animação
                player_anim_frame = 0
            player_anim_time = 0  # reinicializa a contagem do tempo

# Função para desenhar o mapa
def draw_map(screen):
    for row in range(len(level_map)):
        for col in range(len(level_map[row])):
            tile_type = level_map[row][col]
            if tile_type != 0:
                tile_image = tiles[tile_type]
                if tile_image:  # Verifica se o tile não está vazio
                    x = col * TILE_SIZE
                    y = row * TILE_SIZE
                    
                    # Ajustar a posição do ácido
                    if tile_type == 4:  # 4 representa o ácido no seu mapa
                        y += TILE_SIZE - acid.get_height()  # Ajusta para alinhar embaixo
                    screen.blit(tile_image, (x, y))
    screen.blit(player_walk[player_anim_frame],(playerpos_x,playerpos_y))

# Função principal
def main(screen):
    global clock
    running = True
    while running:
        screen.fill('black')  # Limpa a tela com a cor preta
        
        # Desenha o fundo na tela
        screen.blit(bg, (0, 0))  # Desenha a imagem do fundo na posição (0, 0)
        clock.tick(60)
        dt = clock.get_time()
        update(dt)
        # Desenha o mapa com os tiles
        draw_map(screen)
        pygame.display.update()

        # Evento de fechar a janela
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pygame.display.flip()  # Atualiza a tela
        timer.tick(fps)  # Controla a taxa de frames

    pygame.quit()
    sys.exit()


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
load()
main(screen)
pygame.quit()