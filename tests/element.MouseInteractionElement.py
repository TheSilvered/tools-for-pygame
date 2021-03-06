import pygame
import sys; sys.path.insert(0, "..")
import tools_for_pygame as pgt
pygame.init()

__test_name__ = "element.MouseInteractionElement"
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption(__test_name__)
clock = pygame.time.Clock()
fps = pgt.gui.Label(pos=0, font="consolas", text_size=20, color=pgt.WHITE)

image = pygame.Surface((100, 100))
image.fill(pgt.SALMON)

e = pgt.MouseInteractionElement(
    pos=(100, 100),
    size=(100, 100),
    image=image,
    pos_point=pgt.CC
)

prev_state = None

while True:
    clock.tick()
    fps.text = int(clock.get_fps())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(pgt.GRAY(50))
    fps.draw(screen)
    e.draw(screen)
    if (e.hovered, e.clicked) != prev_state:
        prev_state = (e.hovered, e.clicked)
        print(e.hovered, e.clicked)
    pygame.display.update()
