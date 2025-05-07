import pygame
import random
import sys

pygame.init()
pygame.mixer.init()
title_music = 'WindSound.wav'
gameplay_music = 'StickerbrushSymphony.mp3'

collision_sound = pygame.mixer.Sound("collisionwav.wav")

screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Avian Evasion")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Calibri', 36)
font_large = pygame.font.SysFont('Calibri', 48)

sprite_sheet = pygame.image.load("Bird Spritesheet.png").convert_alpha()
frame_width = 16
frame_height = 16
bird_frames = []

for i in range(8):
    rect = pygame.Rect(i * frame_width, 16, frame_width, frame_height)
    frame = sprite_sheet.subsurface(rect).copy()
    scaled_frame = pygame.transform.scale(frame, (frame_width * 3, frame_height * 3))
    flipped_frame = pygame.transform.flip(scaled_frame, True, False)
    bird_frames.append(flipped_frame)

cloud_imgs = [
    pygame.image.load("Cloud2.png").convert_alpha(),
    pygame.image.load("Cloud3.png").convert_alpha(),
    pygame.image.load("Cloud4.png").convert_alpha()]

cloud_imgs = [pygame.transform.scale(cloud, (cloud.get_width()*2, cloud.get_height()*2)) for cloud in cloud_imgs]

gnat_image = pygame.image.load("Dragonfly.png").convert_alpha()
gnat_image = pygame.transform.scale(gnat_image, (20, 20)).copy()
gnat_image = pygame.transform.rotate(gnat_image, 90)

feather_image = pygame.image.load("feather.png").convert_alpha()
feather_image = pygame.transform.scale(feather_image, (26, 26))

stick_image = pygame.image.load("stick.png").convert_alpha()
stick_image = pygame.transform.scale(stick_image, (96, 96))

stone_image = pygame.image.load("Stone.png").convert_alpha()
stone_image = pygame.transform.scale(stone_image, (96, 96))

obstacle_images = [stick_image, stone_image]

def show_title_screen():
    pygame.mixer.music.load(title_music)
    pygame.mixer.music.play(-1)
    showing = True
    while showing:
        screen.fill((135, 206, 235))
        title_text = font_large.render("Avian Evasion", True, (0, 0, 0))
        prompt_text = font.render("Press SPACE to Start", True, (0, 0, 0))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 180))
        screen.blit(prompt_text, (screen_width // 2 - prompt_text.get_width() // 2, 240))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            showing = False

def show_instructions_screen():
    pygame.mixer.music.stop()
    showing = True
    while showing:
        screen.fill((230, 240, 255))

        title = font_large.render("How to Play", True, (0, 0, 0))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 60))

        movement = font.render("Movement: Arrow Keys", True, (0, 0, 0))
        screen.blit(movement, (screen_width // 2 - movement.get_width() // 2, 130))

        powerups_header = font.render("Powerups:", True, (0, 100, 0))
        feather_line = font.render("• Feather - Slows obstacles", True, (0, 0, 0))
        gnat_line = font.render("• Dragonfly - Energy Boost!", True, (0, 0, 0))

        screen.blit(powerups_header, (screen_width // 2 - powerups_header.get_width() // 2, 190))
        screen.blit(feather_line, (screen_width // 2 - feather_line.get_width() // 2, 230))
        screen.blit(gnat_line, (screen_width // 2 - gnat_line.get_width() // 2, 270))

        avoid = font.render("Avoid: Sticks and Stones", True, (150, 0, 0))
        screen.blit(avoid, (screen_width // 2 - avoid.get_width() // 2, 330))

        prompt = font.render("Press ENTER to Begin", True, (0, 0, 0))
        screen.blit(prompt, (screen_width // 2 - prompt.get_width() // 2, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN]:
                showing = False

def show_pause_screen():
    pause_text = font_large.render("Paused", True, (0, 0, 0))
    screen.blit(pause_text, (screen_width // 2 - pause_text.get_width() // 2, screen_height // 2))
    pygame.display.flip()

def game_loop():
    bird_x = 100
    bird_y = 300
    bird_radius = 20
    bird_speed = 5

    bird_frame_index = 0
    bird_frame_timer = 0
    bird_frame_delay = 100

    clouds = []
    for i in range(5):
        img = random.choice(cloud_imgs)
        x = random.randint(0, screen_width)
        y = random.randint(20, 150)
        speed = random.uniform(0.5, 1.5)
        clouds.append({"img": img, "x": x, "y": y, "speed": speed})

    obstacle_width = 40
    obstacle_height = 40
    obstacle_speed = 5
    base_obstacle_speed = 5
    obstacles = []
    for i in range(2):
        x = screen_width + i * 300
        y = random.randint(0, screen_height - 40)
        img = random.choice(obstacle_images)
        obstacles.append({"x": x, "y": y, "img": img})
        
    gnat_radius = 10
    gnat_x = screen_width + random.randint(100, 300)
    gnat_y = random.randint(50, screen_height - 50)
    gnat_active = True
    gnat_timer = pygame.time.get_ticks()
    gnat_cooldown = 5000
    boost_duration = 3000
    boost_active = False
    boost_start_time = 0

    feather_radius = 10
    feather_x = screen_width + random.randint(300, 600)
    feather_y = random.randint(50, screen_height - 50)
    feather_active = True
    feather_timer = pygame.time.get_ticks()
    feather_cooldown = 8000
    slow_duration = 3000
    slow_active = False
    slow_start_time = 0

    timer = 0
    timer_start_time = pygame.time.get_ticks()
    paused = False
    running = True

    pygame.mixer.music.load(gameplay_music)
    pygame.mixer.music.play(-1)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused

        if paused:
            show_pause_screen()
            continue

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            bird_x -= bird_speed
        if keys[pygame.K_RIGHT]:
            bird_x += bird_speed
        if keys[pygame.K_UP]:
            bird_y -= bird_speed
        if keys[pygame.K_DOWN]:
            bird_y += bird_speed

        bird_x = max(bird_radius, min(bird_x, screen_width - bird_radius))
        bird_y = max(bird_radius, min(bird_y, screen_height - bird_radius))

        for obstacle in obstacles:
            obstacle["x"] -= obstacle_speed
            if obstacle["x"] < -obstacle_width:
                obstacle["x"] = screen_width
                obstacle["y"] = random.randint(0, screen_height - obstacle_height)
                obstacle["img"] = random.choice(obstacle_images)
                if timer % 10 == 0:
                    obstacle_speed += 0.5
                    base_obstacle_speed = obstacle_speed
                    if len(obstacles) < 5:
                        new_x = screen_width + random.randint(100, 300)
                        new_y = random.randint(0, screen_height - obstacle_height)
                        obstacles.append({"x": new_x, "y": new_y, "img": random.choice(obstacle_images)})

        for obstacle in obstacles:
            if (bird_x + bird_radius > obstacle["x"] and 
                bird_x - bird_radius < obstacle["x"] + obstacle_width and 
                bird_y + bird_radius > obstacle["y"] and 
                bird_y - bird_radius < obstacle["y"] + obstacle_height):
                collision_sound.play()
                elapsed_time = (pygame.time.get_ticks() - timer_start_time) // 1000
                show_game_over(elapsed_time)
                return

        if gnat_active:
            gnat_x -= obstacle_speed
            if gnat_x < -gnat_radius:
                gnat_active = False

        if gnat_active:
            distance = ((bird_x - gnat_x) ** 2 + (bird_y - gnat_y) ** 2) ** 0.5
            if distance < bird_radius + gnat_radius:
                boost_active = True
                boost_start_time = pygame.time.get_ticks()
                bird_speed = 8
                gnat_active = False

        if boost_active and pygame.time.get_ticks() - boost_start_time > boost_duration:
            bird_speed = 5
            boost_active = False

        if not gnat_active and pygame.time.get_ticks() - gnat_timer > gnat_cooldown:
            gnat_x = screen_width + random.randint(100, 300)
            gnat_y = random.randint(50, screen_height - 50)
            gnat_active = True
            gnat_timer = pygame.time.get_ticks()

        if feather_active:
            feather_x -= obstacle_speed
            if feather_x < -feather_radius:
                feather_active = False

        if feather_active:
            distance = ((bird_x - feather_x) ** 2 + (bird_y - feather_y) ** 2) ** 0.5
            if distance < bird_radius + feather_radius:
                slow_active = True
                slow_start_time = pygame.time.get_ticks()
                obstacle_speed = max(3, obstacle_speed - 2)
                feather_active = False

        if slow_active and pygame.time.get_ticks() - slow_start_time > slow_duration:
            obstacle_speed = base_obstacle_speed
            slow_active = False

        if not feather_active and pygame.time.get_ticks() - feather_timer > feather_cooldown:
            feather_x = screen_width + random.randint(300, 600)
            feather_y = random.randint(50, screen_height - 50)
            feather_active = True
            feather_timer = pygame.time.get_ticks()

        bird_frame_timer += clock.get_time()
        if bird_frame_timer > bird_frame_delay:
            bird_frame_index = (bird_frame_index + 1) % len(bird_frames)
            bird_frame_timer = 0

        for cloud in clouds:
            cloud["x"] -= cloud["speed"]
            if cloud["x"] < -cloud["img"].get_width():
                cloud["x"] = screen_width + random.randint(20, 100)
                cloud["y"] = random.randint(20, 150)
                cloud["img"] = random.choice(cloud_imgs)
                cloud["speed"] = random.uniform(0.5, 1.5)

        screen.fill((135, 206, 235))

        for cloud in clouds:
            screen.blit(cloud["img"], (cloud["x"], cloud["y"]))

        for obstacle in obstacles:
            screen.blit(obstacle["img"], (obstacle["x"], obstacle["y"]))

        bird_image = bird_frames[bird_frame_index]
        bird_rect = bird_image.get_rect(center=(int(bird_x), int(bird_y)))
        screen.blit(bird_image, bird_rect)

        elapsed_time = (pygame.time.get_ticks() - timer_start_time) // 1000
        timer_text = font.render("Time: " + str(elapsed_time), True, (0, 0, 0))
        screen.blit(timer_text, (10, 10))

        if gnat_active:
            gnat_rect = gnat_image.get_rect(center=(int(gnat_x), int(gnat_y)))
            screen.blit(gnat_image, gnat_rect)

        if feather_active:
            feather_rect = feather_image.get_rect(center=(int(feather_x), int(feather_y)))
            screen.blit(feather_image, feather_rect)

        pygame.display.flip()
        timer += 1
        clock.tick(60)

def show_game_over(timer):
    pygame.mixer.music.stop()
    screen.fill((135, 206, 235))
    game_over_text = font_large.render("Game Over", True, (0, 0, 0))
    score_text = font.render(f"Final Time: {timer} seconds", True, (0, 0, 0))
    retry_text = font.render("Press R to Retry or Q to Quit", True, (0, 0, 0))
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, 150))
    screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, 220))
    screen.blit(retry_text, (screen_width // 2 - retry_text.get_width() // 2, 260))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                waiting = False
                game_loop()
            elif keys[pygame.K_q]:
                pygame.quit()
                sys.exit()

show_title_screen()
show_instructions_screen()
game_loop()
