import pygame
import sys; sys.path.insert(0, "..")
import tools_for_pygame as pgt

pygame.init()

__test_name__ = "draw.odd_circle"
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption(__test_name__)
clock = pygame.time.Clock()
fps = pgt.gui.Label(pos=0, font="consolas", text_size=20, color=pgt.WHITE)

while True:
    clock.tick()
    fps.text = int(clock.get_fps())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pgt.draw.clear_cache(pgt.draw.ODD_CIRCLE_CACHE)

    screen.fill(pgt.GRAY(50))
    fps.draw(screen)
    pygame.draw.rect(screen, pgt.WHITE, pygame.Rect(100, 0, 200, 800))
    pgt.draw.odd_circle(screen, (100, 100), 50, pgt.SALMON, 10, pgt.GREEN[:3] + (100,))
    pygame.display.update()
