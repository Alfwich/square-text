import pygame, sys, os, math, random, time

# If we are running in the executable dist then make sure that python is
# using the executable path as the orgin for file requests.
if not "__file__" in locals():
    newPath = "\\".join(str(sys.executable).split("\\")[:-1])
    os.chdir(newPath)

from source.awgl.modules import *
from source.awgl.objs import *
from source.game import *

TITLE = "Test Game"

images.addToGlobalLoadList([
])

sounds.addToGlobalLoadList([
])

# Inits pygame and various components
def initScreen():
    return pygame.display.set_mode(SCREEN_SIZE, SCREEN_FLAGS)

def init():
    [mod.init() for mod in [pygame, images, fonts, joysticks, display, clock]]

def main():
    init()
    mainRenderList = RenderList.RenderList("main")
    mainCamera = Camera.Camera()

    infoText = TInfoText.TInfoText()
    mainRenderList.addObject(infoText)

    events.bindQuitEvent(sys.exit)

    while True:
        # Limit framerate to the desired FPS
        delta = clock.tick()

        # Handle game events through the event queue and tick all game constructs
        events.handleEvents()
        events.tick(delta)

        # Draw screen
        screen = display.getScreen()
        screen.fill(colors.BLACK)
        mainRenderList.render(screen, mainCamera)
        pygame.display.update()

if __name__ == "__main__":
    main()
