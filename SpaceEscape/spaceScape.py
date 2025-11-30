##############################################################
###               S P A C E     E S C A P E                ###
##############################################################
###                  versao Alpha 1.2                      ###
##############################################################
### Objetivo: desviar dos meteoros que caem.                ###
### Cada colisão tira uma vida. Sobreviva o máximo que puder###
### Agora com fundo rolante, 3 fases e ranking!             ###
### Meteoros especiais que tiram 2 vidas!                   ###
### Power-up Buraco Negro - Teleporte + Invenc!             ###
### Trilha sonora diferente para cada fase!                 ###
### Meteoro Coração - Ganha +2 vidas!                       ###
### Sistema de tiros! Destrua os meteoros!                  ###
### Tela inicial estilo Arcade "Insert Coin"!               ###
##############################################################
### Prof. Filipo Novo Mor - github.com/ProfessorFilipo     ###
##############################################################
import pygame
import random
import os
import json
import math

pygame.init()


# SISTEMA DE HIGH SCORES

HIGHSCORE_FILE = "highscores.json"


def load_highscores():
    """Carrega os high scores do arquivo JSON"""
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_highscores(scores):
    """Salva os high scores no arquivo JSON"""
    try:
        with open(HIGHSCORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except:
        pass


def add_highscore(name, score, phase):
    """Adiciona um novo high score e mantém apenas os top 10"""
    scores = load_highscores()
    scores.append({
        "name": name,
        "score": score,
        "phase": phase
    })
    # Ordena por pontuação (decrescente) e mantém top 10
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:10]
    save_highscores(scores)
    return scores


highscores = load_highscores()


#  CONFIGURAÇÕES GERAIS DO JOGO

WIDTH, HEIGHT = 800, 600
FPS = 60
pygame.display.set_caption("🚀 Space Escape - Multiplayer")


#  SEÇÃO DE ASSETS (os alunos podem trocar os arquivos aqui)

ASSETS = {
    "background": "ceu.png",
    "player": "nave001.png",
    "meteor": "meteoro001.png",
    "neutron_star": "neutron-star_spritesheet_medium.png",
    "black_hole": "buraco_negro_spritesheet.png",
    "heart_meteor": "heart-meteor_spritesheet_medium.png",
    "projectile": "projetil.png",
    "sound_point": "classic-game-action-positive-5-224402.mp3",
    "sound_hit": "stab-f-01-brvhrtz-224599.mp3",
    "sound_critical": "stab-f-01-brvhrtz-224599.mp3",
    "sound_shoot": "som_projetil.mp3",
    "music_fase1": "game-gaming-background-music-385611.mp3",
    "music_fase2": "musicaFase2.mp3",
    "music_fase3": "musicaFase3.mp3"
}


#  CARREGAMENTO DE IMAGENS E SONS

WHITE = (255, 255, 255)
RED = (255, 60, 60)
BLUE = (60, 100, 255)
GREEN = (60, 255, 100)
YELLOW = (255, 255, 60)
ORANGE = (255, 140, 0)
CYAN = (0, 255, 255)
PURPLE = (200, 0, 255)
PINK = (255, 100, 150)

screen = pygame.display.set_mode((WIDTH, HEIGHT))


def load_image(filename, fallback_color, size=None):
    if os.path.exists(filename):
        img = pygame.image.load(filename).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    else:
        surf = pygame.Surface(size or (50, 50), pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf


background = load_image(ASSETS["background"], (10, 10, 30), (WIDTH, HEIGHT))
player1_img = load_image(ASSETS["player"], BLUE, (80, 60))
player2_img = load_image(ASSETS["player"], GREEN, (80, 60))
meteor_img = load_image(ASSETS["meteor"], RED, (40, 40))

# Carregar imagem do projétil
projectile_img = load_image(ASSETS["projectile"], YELLOW, (10, 20))

# Carregar spritesheet da estrela de nêutrons
neutron_star_spritesheet = load_image(ASSETS["neutron_star"], CYAN, (256, 128))

# Carregar spritesheet do buraco negro
black_hole_spritesheet = load_image(ASSETS["black_hole"], PURPLE, (128, 64))


# Função para extrair frames do spritesheet
def get_frame(spritesheet, frame_num, frame_width=64, frame_height=64, cols=4):
    col = frame_num % cols
    row = frame_num // cols
    x = col * frame_width
    y = row * frame_height

    frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
    frame.blit(spritesheet, (0, 0), (x, y, frame_width, frame_height))
    return frame


# Carregar todos os frames da estrela de nêutrons
neutron_star_frames = []
for i in range(8):
    neutron_star_frames.append(get_frame(neutron_star_spritesheet, i))

# Carregar todos os frames do buraco negro (8 frames de 16x32)
black_hole_frames = []
for i in range(8):
    black_hole_frames.append(get_frame(black_hole_spritesheet, i, frame_width=16, frame_height=32, cols=8))

# Carregar spritesheet do meteoro coração
heart_meteor_spritesheet = load_image(ASSETS["heart_meteor"], (255, 100, 150), (256, 128))

# Carregar todos os frames do meteoro coração (8 frames: 2 linhas x 4 colunas)
heart_meteor_frames = []
for i in range(8):
    heart_meteor_frames.append(get_frame(heart_meteor_spritesheet, i, frame_width=64, frame_height=64, cols=4))


def load_sound(filename):
    if os.path.exists(filename):
        return pygame.mixer.Sound(filename)
    return None


sound_point = load_sound(ASSETS["sound_point"])
sound_hit = load_sound(ASSETS["sound_hit"])
sound_critical = load_sound(ASSETS["sound_critical"])
sound_shoot = load_sound(ASSETS["sound_shoot"])


# SISTEMA DE MÚSICA POR FASE

current_music_phase = 0  # Controla qual música está tocando


def play_phase_music(phase):

    global current_music_phase

    # Só troca se a fase mudou
    if phase == current_music_phase:
        return

    # Define qual arquivo de música usar
    if phase == 1:
        music_file = ASSETS["music_fase1"]
    elif phase == 2:
        music_file = ASSETS["music_fase2"]
    elif phase == 3:
        music_file = ASSETS["music_fase3"]
    else:
        return

    # Verifica se o arquivo existe e toca
    if os.path.exists(music_file):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)  # -1 = loop infinito
        current_music_phase = phase
        print(f"🎵 Tocando música da Fase {phase}: {music_file}")
    else:
        print(f"⚠️ Arquivo de música não encontrado: {music_file}")


# Inicia com a música da fase 1
play_phase_music(1)


#  SISTEMA DE ROLAGEM DE FUNDO

bg_y1 = 0
bg_y2 = -HEIGHT
bg_scroll_speed = 2


#  SISTEMA DE FASES

current_phase = 1
phase_thresholds = [0, 100, 300]
phase_colors = [
    (100, 150, 255),
    (255, 200, 100),
    (255, 100, 100)
]
phase_bg_speeds = [2, 4, 6]
phase_meteor_speeds = [5, 7, 9]


#  VARIÁVEIS DE JOGO

font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()


#  VARIÁVEIS PARA TELA ARCADE "INSERT COIN"

arcade_timer = 0  # Timer para animações
stars_bg = []  # Estrelas do fundo animado
for _ in range(100):
    stars_bg.append({
        'x': random.randint(0, WIDTH),
        'y': random.randint(0, HEIGHT),
        'speed': random.uniform(0.5, 3),
        'size': random.randint(1, 3),
        'brightness': random.randint(100, 255)
    })

# Cores estilo arcade
NEON_PINK = (255, 0, 128)
NEON_BLUE = (0, 255, 255)
NEON_GREEN = (0, 255, 128)
NEON_YELLOW = (255, 255, 0)
NEON_ORANGE = (255, 128, 0)

game_mode = 1
use_mouse = True

player1_rect = player1_img.get_rect(center=(WIDTH // 3, HEIGHT - 60))
player1_x = float(player1_rect.centerx)
player1_y = float(player1_rect.centery)
player1_speed = 7
player1_score = 0
player1_lives = 5
player1_invulnerable = 0

player2_rect = player2_img.get_rect(center=(2 * WIDTH // 3, HEIGHT - 60))
player2_x = float(player2_rect.centerx)
player2_y = float(player2_rect.centery)
player2_speed = 7
player2_score = 0
player2_lives = 5
player2_invulnerable = 0



# SISTEMA DE PROJÉTEIS

class Projectile:
    def __init__(self, x, y, owner=1):
        self.rect = pygame.Rect(x - 5, y - 10, 10, 20)
        self.speed = 12
        self.owner = owner  # 1 = Player 1, 2 = Player 2

    def update(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        surface.blit(projectile_img, self.rect)


# Lista de projéteis
projectile_list = []

# Cooldown de tiro (evita tiro contínuo)
player1_shoot_cooldown = 0
player2_shoot_cooldown = 0
SHOOT_COOLDOWN = 15  # frames entre cada tiro (0.25 segundos a 60 FPS)


# Sistema de meteoros especiais
class SpecialMeteor:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 64, 64)
        self.frame = 0
        self.frame_timer = 0
        self.damage = 2

    def update(self, speed):
        self.rect.y += speed
        self.frame_timer += 1
        if self.frame_timer >= 5:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 8

    def draw(self, surface):
        surface.blit(neutron_star_frames[self.frame], self.rect)


# Sistema de Power-up Buraco Negro
class BlackHolePowerup:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 32)
        self.frame = 0
        self.frame_timer = 0
        self.speed = 3
        # Movimento sinusoidal
        self.x_offset = 0
        self.original_x = x

    def update(self):
        self.rect.y += self.speed

        # Movimento em onda
        self.x_offset += 0.1
        self.rect.x = self.original_x + int(math.sin(self.x_offset) * 30)

        # Animar
        self.frame_timer += 1
        if self.frame_timer >= 5:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 8

    def draw(self, surface):
        surface.blit(black_hole_frames[self.frame], self.rect)

        # Efeito de brilho ao redor
        glow_surface = pygame.Surface((40, 50), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (200, 0, 255, 30), (20, 25), 20)
        surface.blit(glow_surface, (self.rect.x - 12, self.rect.y - 9))


# Sistema de Meteoro Coração (+2 vidas)
class HeartMeteor:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 64, 64)
        self.frame = 0
        self.frame_timer = 0
        self.speed = 4
        self.bonus_lives = 2

    def update(self, speed):
        self.rect.y += speed
        self.frame_timer += 1
        if self.frame_timer >= 5:
            self.frame_timer = 0
            self.frame = (self.frame + 1) % 8

    def draw(self, surface):
        surface.blit(heart_meteor_frames[self.frame], self.rect)

        # Efeito de brilho rosa ao redor
        glow_surface = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (255, 100, 150, 40), (40, 40), 35)
        surface.blit(glow_surface, (self.rect.x - 8, self.rect.y - 8))


# Meteoros normais
meteor_list = []
for _ in range(8):
    x = random.randint(0, WIDTH - 40)
    y = random.randint(-500, -40)
    meteor_list.append(pygame.Rect(x, y, 40, 40))

# Lista de meteoros especiais
special_meteor_list = []

#  Lista de power-ups
black_hole_powerups = []

#  Lista de meteoros coração
heart_meteor_list = []

meteor_speed = 5

running = True
game_started = False
phase_change_timer = 0
entering_name = False
player_name = ""
name_input_active = False

special_meteor_warning = 0



# FUNÇÃO DE MOVIMENTO SUAVE COM MOUSE

def move_to_mouse(current_x, current_y, target_x, target_y, speed):
    dx = target_x - current_x
    dy = target_y - current_y
    dist = (dx ** 2 + dy ** 2) ** 0.5

    if dist > speed:
        current_x += (dx / dist) * speed
        current_y += (dy / dist) * speed
    else:
        current_x = target_x
        current_y = target_y

    return current_x, current_y



# FUNÇÃO PARA DISPARAR PROJÉTIL

def shoot_projectile(player_rect, owner=1):
    """Cria um novo projétil na posição do jogador"""
    projectile = Projectile(player_rect.centerx, player_rect.top, owner)
    projectile_list.append(projectile)
    if sound_shoot:
        sound_shoot.play()



# FUNÇÃO PARA ATUALIZAR FASE

def update_phase(score):
    global current_phase, bg_scroll_speed, meteor_speed, phase_change_timer

    new_phase = 1
    if score >= phase_thresholds[2]:
        new_phase = 3
    elif score >= phase_thresholds[1]:
        new_phase = 2

    if new_phase != current_phase:
        current_phase = new_phase
        bg_scroll_speed = phase_bg_speeds[current_phase - 1]
        meteor_speed = phase_meteor_speeds[current_phase - 1]
        phase_change_timer = 120

        # NOVO: Troca a música quando muda de fase
        play_phase_music(current_phase)

    return current_phase


#  MENU INICIAL - ESTILO ARCADE "INSERT COIN"

def draw_arcade_stars(surface):
    """Desenha e anima as estrelas do fundo"""
    for star in stars_bg:
        star['y'] += star['speed']
        if star['y'] > HEIGHT:
            star['y'] = 0
            star['x'] = random.randint(0, WIDTH)

        brightness = star['brightness'] + int(math.sin(arcade_timer * 0.1 + star['x']) * 30)
        brightness = max(50, min(255, brightness))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(surface, color, (int(star['x']), int(star['y'])), star['size'])


def draw_blinking_text(surface, text, font_obj, x, y, color, speed=0.1):
    """Desenha texto piscando centralizado"""
    if int(arcade_timer * speed) % 2 == 0:
        text_surf = font_obj.render(text, True, color)
        rect = text_surf.get_rect(center=(x, y))
        surface.blit(text_surf, rect)


def draw_rainbow_title(surface, text, font_obj, center_x, y):
    """Desenha título com cores alternando"""
    colors = [NEON_PINK, NEON_ORANGE, NEON_YELLOW, NEON_GREEN, NEON_BLUE, PURPLE]

    # Renderizar para calcular largura total
    full_render = font_obj.render(text, True, WHITE)
    total_width = full_render.get_width()
    start_x = center_x - total_width // 2

    current_x = start_x
    for i, char in enumerate(text):
        color_index = int((arcade_timer * 0.05 + i * 0.5)) % len(colors)
        color = colors[color_index]
        char_surf = font_obj.render(char, True, color)
        surface.blit(char_surf, (current_x, y))
        current_x += char_surf.get_width()


def show_menu():
    global arcade_timer
    arcade_timer += 1

    # Fundo
    screen.fill((8, 8, 20))
    draw_arcade_stars(screen)

    # Borda arcade
    border_color = NEON_BLUE if int(arcade_timer * 0.05) % 2 == 0 else NEON_PINK
    pygame.draw.rect(screen, border_color, (4, 4, WIDTH - 8, HEIGHT - 8), 3)

    # ===== TÍTULO =====
    title_font = pygame.font.Font(None, 72)
    title_y = 35 + int(math.sin(arcade_timer * 0.05) * 3)

    # Sombra
    shadow = title_font.render("SPACE ESCAPE", True, (30, 30, 30))
    shadow_rect = shadow.get_rect(center=(WIDTH // 2 + 2, title_y + 2))
    screen.blit(shadow, shadow_rect)

    # Título colorido
    draw_rainbow_title(screen, "SPACE ESCAPE", title_font, WIDTH // 2, title_y - 15)

    # Subtítulo
    sub_font = pygame.font.Font(None, 22)
    sub_text = sub_font.render("ARCADE EDITION", True, NEON_YELLOW)
    sub_rect = sub_text.get_rect(center=(WIDTH // 2, title_y + 30))
    screen.blit(sub_text, sub_rect)

    # ===== PRESS START =====
    start_font = pygame.font.Font(None, 32)
    draw_blinking_text(screen, "- PRESS 1, 2 OR 3 TO START -", start_font, WIDTH // 2, 105, NEON_GREEN, 0.06)

    # ===== MODOS DE JOGO =====
    mode_font = pygame.font.Font(None, 30)
    modes_y = 135

    # Caixa dos modos
    pygame.draw.rect(screen, (15, 15, 30), (WIDTH // 2 - 180, modes_y - 5, 360, 90))
    pygame.draw.rect(screen, NEON_BLUE, (WIDTH // 2 - 180, modes_y - 5, 360, 90), 2)

    modes = [
        ("[1]", "UM JOGADOR - MOUSE", NEON_PINK),
        ("[2]", "UM JOGADOR - TECLADO", NEON_GREEN),
        ("[3]", "DOIS JOGADORES", NEON_YELLOW)
    ]

    for i, (key, text, color) in enumerate(modes):
        y = modes_y + 8 + i * 26
        key_surf = mode_font.render(key, True, color)
        text_surf = mode_font.render(text, True, WHITE)
        screen.blit(key_surf, (WIDTH // 2 - 165, y))
        screen.blit(text_surf, (WIDTH // 2 - 115, y))

    # ===== CONTROLES =====
    ctrl_font = pygame.font.Font(None, 24)
    ctrl_y = 240

    # Caixa controles
    pygame.draw.rect(screen, (15, 15, 30), (WIDTH // 2 - 180, ctrl_y - 5, 360, 55))
    pygame.draw.rect(screen, CYAN, (WIDTH // 2 - 180, ctrl_y - 5, 360, 55), 1)

    # Título
    ctrl_title = ctrl_font.render("CONTROLES", True, CYAN)
    ctrl_title_rect = ctrl_title.get_rect(center=(WIDTH // 2, ctrl_y + 8))
    screen.blit(ctrl_title, ctrl_title_rect)

    # Linhas de controle
    ctrl_info = pygame.font.Font(None, 20)
    line1 = ctrl_info.render("MOVER: Mouse ou WASD/Setas", True, WHITE)
    line2 = ctrl_info.render("ATIRAR: Clique ou Espaco/Ctrl", True, WHITE)
    screen.blit(line1, (WIDTH // 2 - 165, ctrl_y + 22))
    screen.blit(line2, (WIDTH // 2 - 165, ctrl_y + 36))

    # ===== POWER-UPS =====
    pu_font = pygame.font.Font(None, 24)
    pu_y = 310

    # Caixa power-ups
    pygame.draw.rect(screen, (15, 15, 30), (WIDTH // 2 - 180, pu_y - 5, 360, 75))
    pygame.draw.rect(screen, PURPLE, (WIDTH // 2 - 180, pu_y - 5, 360, 75), 1)

    # Título
    pu_title = pu_font.render("POWER-UPS", True, NEON_YELLOW)
    pu_title_rect = pu_title.get_rect(center=(WIDTH // 2, pu_y + 8))
    screen.blit(pu_title, pu_title_rect)

    # Power-ups em grade
    pu_info = pygame.font.Font(None, 19)
    powerups = [
        ("Meteoro Azul: -2 Vidas", CYAN, WIDTH // 2 - 165),
        ("Meteoro Rosa: +2 Vidas", PINK, WIDTH // 2 + 10),
        ("Buraco Negro: Escudo", PURPLE, WIDTH // 2 - 165),
        ("3 Fases: 0-99/100-299/300+", ORANGE, WIDTH // 2 + 10)
    ]

    for i, (text, color, x) in enumerate(powerups):
        y = pu_y + 24 + (i // 2) * 18
        pu_surf = pu_info.render(text, True, color)
        screen.blit(pu_surf, (x, y))

    # ===== HIGH SCORES =====
    hs_y = 400

    # Caixa
    pygame.draw.rect(screen, (15, 15, 30), (WIDTH // 2 - 150, hs_y - 5, 300, 95))
    pygame.draw.rect(screen, NEON_YELLOW, (WIDTH // 2 - 150, hs_y - 5, 300, 95), 2)

    # Título
    hs_font = pygame.font.Font(None, 26)
    hs_color = NEON_YELLOW if int(arcade_timer * 0.1) % 2 == 0 else NEON_ORANGE
    hs_title = hs_font.render("HIGH SCORES", True, hs_color)
    hs_rect = hs_title.get_rect(center=(WIDTH // 2, hs_y + 10))
    screen.blit(hs_title, hs_rect)

    # Scores
    scores = load_highscores()
    score_font = pygame.font.Font(None, 18)

    if scores:
        for i, entry in enumerate(scores[:5]):
            y = hs_y + 28 + i * 13

            if i == 0:
                color = NEON_YELLOW
            elif i == 1:
                color = (200, 200, 200)
            elif i == 2:
                color = (205, 140, 80)
            else:
                color = (180, 180, 180)

            line = f"{i + 1}. {entry['name'][:8]:<8}  {entry['score']:>5} pts  Fase {entry['phase']}"
            line_surf = score_font.render(line, True, color)
            line_rect = line_surf.get_rect(center=(WIDTH // 2, y))
            screen.blit(line_surf, line_rect)
    else:
        no_surf = score_font.render("Nenhum score ainda!", True, NEON_PINK)
        no_rect = no_surf.get_rect(center=(WIDTH // 2, hs_y + 50))
        screen.blit(no_surf, no_rect)

    # ===== RODAPÉ =====
    footer_font = pygame.font.Font(None, 16)
    footer = footer_font.render("Everton Tarelli - github.com/TarelliEverton", True, (70, 70, 100))
    footer_rect = footer.get_rect(center=(WIDTH // 2, HEIGHT - 12))
    screen.blit(footer, footer_rect)

    pygame.display.flip()



#  TELA DE ENTRADA DE NOME

def show_name_input():
    screen.blit(background, (0, 0))

    title_font = pygame.font.Font(None, 60)
    title = title_font.render("Digite seu nome:", True, YELLOW)
    screen.blit(title, (WIDTH // 2 - 200, 200))

    input_box = pygame.Rect(WIDTH // 2 - 150, 280, 300, 50)
    pygame.draw.rect(screen, WHITE, input_box, 3)

    name_surface = pygame.font.Font(None, 48).render(player_name, True, WHITE)
    screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))

    hint = small_font.render("Pressione ENTER para continuar", True, WHITE)
    screen.blit(hint, (WIDTH // 2 - 160, 360))

    hint2 = small_font.render("(Máximo 20 caracteres)", True, WHITE)
    screen.blit(hint2, (WIDTH // 2 - 120, 390))

    pygame.display.flip()



#  LOOP PRINCIPAL

while running:
    clock.tick(FPS)

    # Atualizar cooldown de tiro
    if player1_shoot_cooldown > 0:
        player1_shoot_cooldown -= 1
    if player2_shoot_cooldown > 0:
        player2_shoot_cooldown -= 1

    # ENTRADA DE NOME
    if name_input_active:
        show_name_input()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                name_input_active = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if player_name.strip():
                        name_input_active = False
                        game_started = True
                    else:
                        player_name = "Jogador"
                        name_input_active = False
                        game_started = True
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    name_input_active = False
                    entering_name = False
                    player_name = ""
                else:
                    if len(player_name) < 20 and event.unicode.isprintable():
                        player_name += event.unicode
        continue

    # MENU INICIAL
    if not game_started:
        show_menu()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_mode = 1
                    use_mouse = True
                    name_input_active = True
                    entering_name = True
                elif event.key == pygame.K_2:
                    game_mode = 1
                    use_mouse = False
                    name_input_active = True
                    entering_name = True
                elif event.key == pygame.K_3:
                    game_mode = 2
                    player_name = "Multiplayer"
                    game_started = True
        continue

    # JOGO EM ANDAMENTO

    # --- Atualiza rolagem do fundo ---
    bg_y1 += bg_scroll_speed
    bg_y2 += bg_scroll_speed

    if bg_y1 >= HEIGHT:
        bg_y1 = bg_y2 - HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = bg_y1 - HEIGHT

    # Desenha o fundo rolante
    screen.blit(background, (0, bg_y1))
    screen.blit(background, (0, bg_y2))

    # Bordas coloridas da fase
    border_thickness = 10
    border_color = phase_colors[current_phase - 1]

    pygame.draw.rect(screen, border_color, (0, 0, WIDTH, border_thickness))
    pygame.draw.rect(screen, border_color, (0, HEIGHT - border_thickness, WIDTH, border_thickness))
    pygame.draw.rect(screen, border_color, (0, 0, border_thickness, HEIGHT))
    pygame.draw.rect(screen, border_color, (WIDTH - border_thickness, 0, border_thickness, HEIGHT))

    # --- Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_started = False
                # Reset
                player1_score = 0
                player1_lives = 5
                player1_invulnerable = 0
                player2_score = 0
                player2_lives = 5
                player2_invulnerable = 0
                current_phase = 1
                bg_scroll_speed = phase_bg_speeds[0]
                meteor_speed = phase_meteor_speeds[0]
                bg_y1 = 0
                bg_y2 = -HEIGHT
                player1_rect.center = (WIDTH // 3, HEIGHT - 60)
                player2_rect.center = (2 * WIDTH // 3, HEIGHT - 60)
                player1_x = float(player1_rect.centerx)
                player1_y = float(player1_rect.centery)
                player2_x = float(player2_rect.centerx)
                player2_y = float(player2_rect.centery)
                special_meteor_list.clear()
                black_hole_powerups.clear()
                heart_meteor_list.clear()
                projectile_list.clear()
                # Reinicia a música para fase 1
                current_music_phase = 0
                play_phase_music(1)

            # Tiro com ESPAÇO (para modo teclado)
            if event.key == pygame.K_SPACE and game_mode == 1 and not use_mouse:
                if player1_shoot_cooldown == 0:
                    shoot_projectile(player1_rect, 1)
                    player1_shoot_cooldown = SHOOT_COOLDOWN

        #  Tiro com clique do mouse (para modo mouse)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and game_mode == 1 and use_mouse:  # Botão esquerdo
                if player1_shoot_cooldown == 0:
                    shoot_projectile(player1_rect, 1)
                    player1_shoot_cooldown = SHOOT_COOLDOWN

    # --- Movimento do Jogador 1 ---
    if game_mode == 1:
        if use_mouse:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player1_x, player1_y = move_to_mouse(player1_x, player1_y, mouse_x, mouse_y, player1_speed)
        else:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] and player1_rect.left > 0:
                player1_x -= player1_speed
            if keys[pygame.K_d] and player1_rect.right < WIDTH:
                player1_x += player1_speed
            if keys[pygame.K_w] and player1_rect.top > 0:
                player1_y -= player1_speed
            if keys[pygame.K_s] and player1_rect.bottom < HEIGHT:
                player1_y += player1_speed

        player1_rect.centerx = int(player1_x)
        player1_rect.centery = int(player1_y)
        player1_rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        player1_x = float(player1_rect.centerx)
        player1_y = float(player1_rect.centery)

    # --- Movimento dos 2 Jogadores no Multiplayer ---
    if game_mode == 2:
        keys = pygame.key.get_pressed()

        # Player 1 - WASD + ESPAÇO para atirar
        if keys[pygame.K_a] and player1_rect.left > 0:
            player1_x -= player1_speed
        if keys[pygame.K_d] and player1_rect.right < WIDTH:
            player1_x += player1_speed
        if keys[pygame.K_w] and player1_rect.top > 0:
            player1_y -= player1_speed
        if keys[pygame.K_s] and player1_rect.bottom < HEIGHT:
            player1_y += player1_speed

        # Player 1 atira com ESPAÇO
        if keys[pygame.K_SPACE] and player1_shoot_cooldown == 0:
            shoot_projectile(player1_rect, 1)
            player1_shoot_cooldown = SHOOT_COOLDOWN

        player1_rect.centerx = int(player1_x)
        player1_rect.centery = int(player1_y)
        player1_rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        player1_x = float(player1_rect.centerx)
        player1_y = float(player1_rect.centery)

        # Player 2 - Setas + ENTER para atirar
        if keys[pygame.K_LEFT] and player2_rect.left > 0:
            player2_x -= player2_speed
        if keys[pygame.K_RIGHT] and player2_rect.right < WIDTH:
            player2_x += player2_speed
        if keys[pygame.K_UP] and player2_rect.top > 0:
            player2_y -= player2_speed
        if keys[pygame.K_DOWN] and player2_rect.bottom < HEIGHT:
            player2_y += player2_speed

        # Player 2 atira com ENTER ou RSHIFT ou CTRL
        if (keys[pygame.K_RETURN] or keys[pygame.K_RSHIFT] or keys[pygame.K_RCTRL] or keys[
            pygame.K_LCTRL]) and player2_shoot_cooldown == 0:
            shoot_projectile(player2_rect, 2)
            player2_shoot_cooldown = SHOOT_COOLDOWN

        player2_rect.centerx = int(player2_x)
        player2_rect.centery = int(player2_y)
        player2_rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        player2_x = float(player2_rect.centerx)
        player2_y = float(player2_rect.centery)

    # Atualizar invulnerabilidade
    if player1_invulnerable > 0:
        player1_invulnerable -= 1
    if player2_invulnerable > 0:
        player2_invulnerable -= 1

    # --- Atualiza fase baseado na pontuação ---
    if game_mode == 1:
        update_phase(player1_score)
    else:
        update_phase(max(player1_score, player2_score))

    # --- Atualizar projéteis ---
    for projectile in projectile_list[:]:
        projectile.update()

        # Remove projétil se sair da tela
        if projectile.rect.bottom < 0:
            projectile_list.remove(projectile)
            continue

        # Colisão com meteoros normais
        for meteor in meteor_list:
            if projectile.rect.colliderect(meteor):
                # Reposiciona o meteoro
                meteor.y = random.randint(-100, -40)
                meteor.x = random.randint(0, WIDTH - meteor.width)

                # Adiciona pontos ao jogador que atirou
                if projectile.owner == 1:
                    player1_score += 5  #
                else:
                    player2_score += 5

                if projectile in projectile_list:
                    projectile_list.remove(projectile)
                if sound_hit:
                    sound_hit.play()
                break

        # Colisão com meteoros especiais
        for special_meteor in special_meteor_list[:]:
            if projectile.rect.colliderect(special_meteor.rect):
                special_meteor_list.remove(special_meteor)

                # Adiciona pontos ao jogador que atirou
                if projectile.owner == 1:
                    player1_score += 10  # Bonus maior por destruir especial
                else:
                    player2_score += 10

                if projectile in projectile_list:
                    projectile_list.remove(projectile)
                if sound_critical:
                    sound_critical.play()
                break

    # Atualizar power-ups
    for powerup in black_hole_powerups[:]:
        powerup.update()

        # Saiu da tela
        if powerup.rect.y > HEIGHT:
            black_hole_powerups.remove(powerup)
            continue

        # Colisão com Player 1 - TELEPORTA A NAVE!
        if powerup.rect.colliderect(player1_rect):
            # Teletransporta para posição aleatória
            player1_x = float(random.randint(50, WIDTH - 50))
            player1_y = float(random.randint(50, HEIGHT - 50))
            player1_rect.centerx = int(player1_x)
            player1_rect.centery = int(player1_y)

            # Fica invulnerável por 4 segundos (240 frames a 60 FPS)
            player1_invulnerable = 240

            black_hole_powerups.remove(powerup)
            if sound_point:
                sound_point.play()

        # Colisão com Player 2 - TELEPORTA A NAVE!
        elif game_mode == 2 and powerup.rect.colliderect(player2_rect):
            # Teletransporta para posição aleatória
            player2_x = float(random.randint(50, WIDTH - 50))
            player2_y = float(random.randint(50, HEIGHT - 50))
            player2_rect.centerx = int(player2_x)
            player2_rect.centery = int(player2_y)

            # Fica invulnerável por 4 segundos (240 frames a 60 FPS)
            player2_invulnerable = 240

            black_hole_powerups.remove(powerup)
            if sound_point:
                sound_point.play()

    # --- Movimento dos meteoros normais ---
    for meteor in meteor_list:
        meteor.y += meteor_speed

        # Saiu da tela
        if meteor.y > HEIGHT:
            meteor.y = random.randint(-100, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)

            # 1 a cada 50 meteoros spawna um buraco negro (2% de chance)
            if random.random() < 0.02:
                powerup_x = random.randint(50, WIDTH - 50)
                powerup_y = random.randint(-300, -100)
                black_hole_powerups.append(BlackHolePowerup(powerup_x, powerup_y))

            # 5% de chance de spawnar meteoro especial
            if random.random() < 0.05:
                special_x = random.randint(0, WIDTH - 64)
                special_y = random.randint(-300, -64)
                special_meteor_list.append(SpecialMeteor(special_x, special_y))
                special_meteor_warning = 60

            # 2% de chance de spawnar meteoro coração (+2 vidas)
            if random.random() < 0.02:
                heart_x = random.randint(0, WIDTH - 64)
                heart_y = random.randint(-300, -64)
                heart_meteor_list.append(HeartMeteor(heart_x, heart_y))

            if game_mode == 1:
                player1_score += 1
            else:
                player1_score += 1
                player2_score += 1

            if sound_point:
                sound_point.play()

        # Colisão com Player 1 (só se não estiver invulnerável)
        if meteor.colliderect(player1_rect) and player1_invulnerable == 0:
            player1_lives -= 1
            meteor.y = random.randint(-100, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)
            if sound_hit:
                sound_hit.play()
            if player1_lives <= 0:
                running = False

        # Colisão com Player 2 (só se não estiver invulnerável)
        if game_mode == 2 and meteor.colliderect(player2_rect) and player2_invulnerable == 0:
            player2_lives -= 1
            meteor.y = random.randint(-100, -40)
            meteor.x = random.randint(0, WIDTH - meteor.width)
            if sound_hit:
                sound_hit.play()
            if player2_lives <= 0:
                running = False

    # Movimento e colisão dos meteoros especiais
    for special_meteor in special_meteor_list[:]:
        special_meteor.update(meteor_speed * 0.8)

        if special_meteor.rect.y > HEIGHT:
            special_meteor_list.remove(special_meteor)
            continue

        # Colisão com Player 1 (só se não estiver invulnerável)
        if special_meteor.rect.colliderect(player1_rect) and player1_invulnerable == 0:
            player1_lives -= special_meteor.damage
            special_meteor_list.remove(special_meteor)
            if sound_critical:
                sound_critical.play()
            special_meteor_warning = 30

            if player1_lives <= 0:
                running = False

        # Colisão com Player 2 (só se não estiver invulnerável)
        if game_mode == 2 and special_meteor.rect.colliderect(player2_rect) and player2_invulnerable == 0:
            player2_lives -= special_meteor.damage
            special_meteor_list.remove(special_meteor)
            if sound_critical:
                sound_critical.play()
            special_meteor_warning = 30

            if player2_lives <= 0:
                running = False

    # Movimento e colisão dos meteoros coração (+2 vidas)
    for heart_meteor in heart_meteor_list[:]:
        heart_meteor.update(meteor_speed * 0.7)

        # Saiu da tela
        if heart_meteor.rect.y > HEIGHT:
            heart_meteor_list.remove(heart_meteor)
            continue

        # Colisão com Player 1 - GANHA 2 VIDAS!
        if heart_meteor.rect.colliderect(player1_rect):
            player1_lives += heart_meteor.bonus_lives
            heart_meteor_list.remove(heart_meteor)
            if sound_point:
                sound_point.play()
            continue

        # Colisão com Player 2 - GANHA 2 VIDAS!
        if game_mode == 2 and heart_meteor.rect.colliderect(player2_rect):
            player2_lives += heart_meteor.bonus_lives
            heart_meteor_list.remove(heart_meteor)
            if sound_point:
                sound_point.play()

    # --- Desenha tudo ---

    #  Desenhar projéteis
    for projectile in projectile_list:
        projectile.draw(screen)

    # Desenhar com efeito piscante se invulnerável
    if player1_invulnerable == 0 or (player1_invulnerable // 5) % 2 == 0:
        screen.blit(player1_img, player1_rect)

    if game_mode == 2:
        if player2_invulnerable == 0 or (player2_invulnerable // 5) % 2 == 0:
            screen.blit(player2_img, player2_rect)

    # Efeito de escudo ao redor da nave quando invulnerável
    if player1_invulnerable > 0:
        shield_radius = 50 + int(math.sin(player1_invulnerable * 0.2) * 5)
        pygame.draw.circle(screen, PURPLE, player1_rect.center, shield_radius, 3)
        pygame.draw.circle(screen, (200, 0, 255, 100), player1_rect.center, shield_radius - 5, 2)

    if game_mode == 2 and player2_invulnerable > 0:
        shield_radius = 50 + int(math.sin(player2_invulnerable * 0.2) * 5)
        pygame.draw.circle(screen, PURPLE, player2_rect.center, shield_radius, 3)
        pygame.draw.circle(screen, (200, 0, 255, 100), player2_rect.center, shield_radius - 5, 2)

    for meteor in meteor_list:
        screen.blit(meteor_img, meteor)

    # Desenhar meteoros especiais
    for special_meteor in special_meteor_list:
        special_meteor.draw(screen)

    # Desenhar power-ups
    for powerup in black_hole_powerups:
        powerup.draw(screen)

    # Desenhar meteoros coração
    for heart_meteor in heart_meteor_list:
        heart_meteor.draw(screen)

    # --- Exibe Pontos e Fase ---
    if game_mode == 1:
        text = font.render(f"Pontos: {player1_score}   Vidas: {player1_lives}", True, WHITE)
        screen.blit(text, (10, 10))

        mode = "MOUSE (Clique=Tiro)" if use_mouse else "WASD (Espaço=Tiro)"
        control_text = small_font.render(f"Controle: {mode} | ESC = Menu", True, WHITE)
        screen.blit(control_text, (10, 50))

        # Indicador de invulnerabilidade
        if player1_invulnerable > 0:
            invuln_text = font.render(f"⚡ INVULNERÁVEL: {player1_invulnerable // 60 + 1}s ⚡", True, CYAN)
            screen.blit(invuln_text, (10, 80))

        phase_text = small_font.render(f"FASE {current_phase}", True, phase_colors[current_phase - 1])
        screen.blit(phase_text, (WIDTH - 120, 10))
    else:
        # Pontos para 2 jogadores
        p1_text = font.render(f"P1: {player1_score} pts | {player1_lives} vidas", True, BLUE)
        p2_text = font.render(f"P2: {player2_score} pts | {player2_lives} vidas", True, GREEN)
        screen.blit(p1_text, (10, 10))
        screen.blit(p2_text, (10, 50))

        control_text = small_font.render("P1: WASD+Espaco | P2: Setas+Ctrl | ESC = Menu", True, WHITE)
        screen.blit(control_text, (10, 90))

        # Indicadores de invulnerabilidade
        y_pos = 120
        if player1_invulnerable > 0:
            p1_invuln = small_font.render(f"⚡ P1 Invulnerável: {player1_invulnerable // 60 + 1}s", True, CYAN)
            screen.blit(p1_invuln, (10, y_pos))
            y_pos += 30
        if player2_invulnerable > 0:
            p2_invuln = small_font.render(f"⚡ P2 Invulnerável: {player2_invulnerable // 60 + 1}s", True, CYAN)
            screen.blit(p2_invuln, (10, y_pos))

        phase_text = small_font.render(f"FASE {current_phase}", True, phase_colors[current_phase - 1])
        screen.blit(phase_text, (WIDTH - 120, 10))

    # --- Aviso de mudança de fase ---
    if phase_change_timer > 0:
        phase_change_timer -= 1
        big_font = pygame.font.Font(None, 64)
        phase_alert = big_font.render(f"FASE {current_phase}!", True, YELLOW)
        alert_rect = phase_alert.get_rect(center=(WIDTH // 2, HEIGHT // 2))

        alert_bg = pygame.Surface((300, 100))
        alert_bg.fill((0, 0, 0))
        alert_bg.set_alpha(150)
        screen.blit(alert_bg, (WIDTH // 2 - 150, HEIGHT // 2 - 50))

        screen.blit(phase_alert, alert_rect)

        # Indicador de música nova
        music_alert = small_font.render("🎵 Nova trilha sonora! 🎵", True, GREEN)
        music_rect = music_alert.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        screen.blit(music_alert, music_rect)

    # Aviso de meteoro especial
    if special_meteor_warning > 0:
        special_meteor_warning -= 1
        warning_font = pygame.font.Font(None, 48)
        warning_text = warning_font.render("⚡ CUIDADO! -2 VIDAS ⚡", True, CYAN)
        warning_rect = warning_text.get_rect(center=(WIDTH // 2, 80))

        alpha = int((special_meteor_warning % 10) * 25.5)
        warning_bg = pygame.Surface((400, 60))
        warning_bg.fill((0, 50, 100))
        warning_bg.set_alpha(alpha)
        screen.blit(warning_bg, (WIDTH // 2 - 200, 50))

        screen.blit(warning_text, warning_rect)

    pygame.display.flip()


#  TELA DE FIM DE JOGO - ESTILO ARCADE

pygame.mixer.music.stop()

# Salvar high score apenas para modo single player
if game_mode == 1 and player_name:
    add_highscore(player_name, player1_score, current_phase)

# Determinar vencedor no multiplayer
if game_mode == 2:
    # Vencedor é quem ainda tem vidas (ou mais pontos em caso de empate de vidas)
    if player1_lives > 0 and player2_lives <= 0:
        winner = 1
        winner_color = BLUE
    elif player2_lives > 0 and player1_lives <= 0:
        winner = 2
        winner_color = GREEN
    elif player1_lives <= 0 and player2_lives <= 0:
        # Ambos morreram ao mesmo tempo - decide por pontos
        if player1_score > player2_score:
            winner = 1
            winner_color = BLUE
        elif player2_score > player1_score:
            winner = 2
            winner_color = GREEN
        else:
            winner = 0  # Empate
            winner_color = NEON_YELLOW
    else:
        # Ambos vivos (não deveria acontecer)
        winner = 0
        winner_color = NEON_YELLOW

# Timer para animações
end_timer = 0

# Loop da tela de fim
end_screen = True
while end_screen:
    clock.tick(FPS)
    end_timer += 1

    # Fundo com estrelas
    screen.fill((8, 8, 20))
    draw_arcade_stars(screen)

    # Borda arcade pulsante
    border_color = NEON_PINK if int(end_timer * 0.08) % 2 == 0 else NEON_BLUE
    pygame.draw.rect(screen, border_color, (4, 4, WIDTH - 8, HEIGHT - 8), 3)

    if game_mode == 1:
        # ===== TELA SINGLE PLAYER =====

        # GAME OVER texto grande
        go_font = pygame.font.Font(None, 80)
        go_color = RED if int(end_timer * 0.1) % 2 == 0 else NEON_ORANGE
        go_text = go_font.render("GAME OVER", True, go_color)
        go_rect = go_text.get_rect(center=(WIDTH // 2, 80))

        # Sombra
        go_shadow = go_font.render("GAME OVER", True, (50, 20, 20))
        screen.blit(go_shadow, (go_rect.x + 3, go_rect.y + 3))
        screen.blit(go_text, go_rect)

        # Caixa de resultado
        result_box = pygame.Rect(WIDTH // 2 - 200, 130, 400, 150)
        pygame.draw.rect(screen, (15, 15, 35), result_box)
        pygame.draw.rect(screen, NEON_YELLOW, result_box, 2)

        # Nome do jogador
        name_font = pygame.font.Font(None, 32)
        name_text = name_font.render(f"JOGADOR: {player_name}", True, NEON_YELLOW)
        name_rect = name_text.get_rect(center=(WIDTH // 2, 160))
        screen.blit(name_text, name_rect)

        # Pontuação final (animada)
        score_font = pygame.font.Font(None, 50)
        score_color = NEON_GREEN if int(end_timer * 0.15) % 2 == 0 else WHITE
        score_text = score_font.render(f"{player1_score} PTS", True, score_color)
        score_rect = score_text.get_rect(center=(WIDTH // 2, 205))
        screen.blit(score_text, score_rect)

        # Fase alcançada
        phase_font = pygame.font.Font(None, 36)
        phase_color = phase_colors[current_phase - 1]
        phase_text = phase_font.render(f"FASE {current_phase} ALCANCADA", True, phase_color)
        phase_rect = phase_text.get_rect(center=(WIDTH // 2, 250))
        screen.blit(phase_text, phase_rect)

        # HIGH SCORES
        hs_box = pygame.Rect(WIDTH // 2 - 160, 300, 320, 130)
        pygame.draw.rect(screen, (15, 15, 35), hs_box)
        pygame.draw.rect(screen, NEON_YELLOW, hs_box, 2)

        hs_font = pygame.font.Font(None, 30)
        hs_color = NEON_YELLOW if int(end_timer * 0.1) % 2 == 0 else NEON_ORANGE
        hs_title = hs_font.render("HIGH SCORES", True, hs_color)
        hs_rect = hs_title.get_rect(center=(WIDTH // 2, 320))
        screen.blit(hs_title, hs_rect)

        scores = load_highscores()
        score_list_font = pygame.font.Font(None, 20)

        for i, entry in enumerate(scores[:5]):
            y = 345 + i * 16
            if i == 0:
                color = NEON_YELLOW
            elif i == 1:
                color = (200, 200, 200)
            elif i == 2:
                color = (205, 140, 80)
            else:
                color = (150, 150, 150)

            line = f"{i + 1}. {entry['name'][:10]:<10}  {entry['score']:>5} pts  F{entry['phase']}"
            line_surf = score_list_font.render(line, True, color)
            line_rect = line_surf.get_rect(center=(WIDTH // 2, y))
            screen.blit(line_surf, line_rect)

    else:
        # ===== TELA MULTIPLAYER - VITÓRIA =====

        if winner == 0:
            # EMPATE
            title_font = pygame.font.Font(None, 70)
            title_color = NEON_YELLOW if int(end_timer * 0.1) % 2 == 0 else WHITE
            title_text = title_font.render("EMPATE!", True, title_color)
            title_rect = title_text.get_rect(center=(WIDTH // 2, 70))

            shadow = title_font.render("EMPATE!", True, (50, 50, 20))
            screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
            screen.blit(title_text, title_rect)
        else:
            # VITÓRIA
            # Texto "WINNER" grande
            win_font = pygame.font.Font(None, 60)
            win_text = win_font.render("WINNER!", True, NEON_YELLOW)
            win_rect = win_text.get_rect(center=(WIDTH // 2, 50))

            shadow = win_font.render("WINNER!", True, (50, 50, 20))
            screen.blit(shadow, (win_rect.x + 3, win_rect.y + 3))
            screen.blit(win_text, win_rect)

            # Player vencedor com efeito
            player_font = pygame.font.Font(None, 90)
            pulse = abs(math.sin(end_timer * 0.1)) * 20
            player_color = winner_color

            player_text = player_font.render(f"PLAYER {winner}", True, player_color)
            player_rect = player_text.get_rect(center=(WIDTH // 2, 120))

            # Brilho ao redor
            glow_surf = player_font.render(f"PLAYER {winner}", True, WHITE)
            glow_surf.set_alpha(50 + int(pulse * 2))
            screen.blit(glow_surf, (player_rect.x - 2, player_rect.y - 2))
            screen.blit(glow_surf, (player_rect.x + 2, player_rect.y + 2))
            screen.blit(player_text, player_rect)

            # Estrelas decorativas animadas ao redor do vencedor
            for i in range(8):
                angle = (end_timer * 0.03) + (i * math.pi / 4)
                radius = 120 + math.sin(end_timer * 0.1 + i) * 10
                star_x = WIDTH // 2 + math.cos(angle) * radius
                star_y = 120 + math.sin(angle) * 50
                star_color = NEON_YELLOW if i % 2 == 0 else winner_color
                pygame.draw.circle(screen, star_color, (int(star_x), int(star_y)), 4)

            # Motivo da vitória
            loser = 2 if winner == 1 else 1
            reason_font = pygame.font.Font(None, 26)
            reason_color = RED if int(end_timer * 0.1) % 2 == 0 else NEON_ORANGE
            reason_text = reason_font.render(f"PLAYER {loser} FOI ELIMINADO!", True, reason_color)
            reason_rect = reason_text.get_rect(center=(WIDTH // 2, 170))
            screen.blit(reason_text, reason_rect)

        # Caixa de placar
        score_box = pygame.Rect(WIDTH // 2 - 180, 200, 360, 120)
        pygame.draw.rect(screen, (15, 15, 35), score_box)
        pygame.draw.rect(screen, CYAN, score_box, 2)

        # Título placar
        placar_font = pygame.font.Font(None, 28)
        placar_title = placar_font.render("PLACAR FINAL", True, CYAN)
        placar_rect = placar_title.get_rect(center=(WIDTH // 2, 220))
        screen.blit(placar_title, placar_rect)

        # Player 1
        p1_font = pygame.font.Font(None, 36)
        p1_color = NEON_YELLOW if winner == 1 else BLUE
        p1_status = f"P1: {player1_score} PTS"
        if player1_lives <= 0:
            p1_status += " [ELIMINADO]"
        p1_text = p1_font.render(p1_status, True, p1_color)
        p1_rect = p1_text.get_rect(center=(WIDTH // 2, 255))
        screen.blit(p1_text, p1_rect)

        # Player 2
        p2_color = NEON_YELLOW if winner == 2 else GREEN
        p2_status = f"P2: {player2_score} PTS"
        if player2_lives <= 0:
            p2_status += " [ELIMINADO]"
        p2_text = p1_font.render(p2_status, True, p2_color)
        p2_rect = p2_text.get_rect(center=(WIDTH // 2, 295))
        screen.blit(p2_text, p2_rect)

        # Estatísticas
        stats_box = pygame.Rect(WIDTH // 2 - 150, 340, 300, 80)
        pygame.draw.rect(screen, (15, 15, 35), stats_box)
        pygame.draw.rect(screen, PURPLE, stats_box, 1)

        stats_font = pygame.font.Font(None, 22)
        stats_title = stats_font.render("ESTATISTICAS", True, PURPLE)
        stats_rect = stats_title.get_rect(center=(WIDTH // 2, 355))
        screen.blit(stats_title, stats_rect)

        diff = abs(player1_score - player2_score)
        diff_text = stats_font.render(f"Diferenca: {diff} pts", True, WHITE)
        diff_rect = diff_text.get_rect(center=(WIDTH // 2, 380))
        screen.blit(diff_text, diff_rect)

        phase_text = stats_font.render(f"Fase alcancada: {current_phase}", True, phase_colors[current_phase - 1])
        phase_rect = phase_text.get_rect(center=(WIDTH // 2, 400))
        screen.blit(phase_text, phase_rect)

    # ===== PRESS ANY KEY (ambos os modos) =====
    press_font = pygame.font.Font(None, 28)
    if int(end_timer * 0.06) % 2 == 0:
        press_text = press_font.render("PRESSIONE QUALQUER TECLA", True, WHITE)
        press_rect = press_text.get_rect(center=(WIDTH // 2, 470))
        screen.blit(press_text, press_rect)

    # Créditos
    credit_font = pygame.font.Font(None, 16)
    credit = credit_font.render("Everton Tarelli - github.com/TarelliEverton", True, (60, 60, 90))
    credit_rect = credit.get_rect(center=(WIDTH // 2, HEIGHT - 15))
    screen.blit(credit, credit_rect)

    pygame.display.flip()

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            end_screen = False
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            end_screen = False

pygame.quit()