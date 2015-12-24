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
    hudRenderList = RenderList.RenderList("hud")
    mainCamera = Camera.Camera()

    infoText = TInfoText.TInfoText()
    #hudRenderList.addObject(infoText)

    events.bindQuitEvent(sys.exit)
    events.bindKeyDownEvent("q", sys.exit)

    joysticks.updateJoysticks()

    class playerCharacter(GameObject.GameObject):
        def __init__(self):
            super(playerCharacter, self).__init__()
            self.setSize(100, 100)
            self.velocity = [0, 0]
            self.maxSpeed = 100

            events.bindJoystickAxisMotionEvent(0, 0, self.moveRight)
            events.bindJoystickAxisMotionEvent(0, 1, self.moveDown)

        def draw(self, screen, offset=None):
            position = self.getPosition()
            if not offset is None:
                position[0] += offset[0]
                position[1] += offset[1]

            points = map( lambda x: ((x[0]*self.getWidth())+position[0], x[1]*self.getHeight()+position[1]), [(0, 0), (1, 0), (1, 1), (0, 1)])
            pygame.draw.polygon(screen, colors.RED, points)

        def moveRight(self, event, value):
            self.velocity[0] = value * self.maxSpeed

        def moveDown(self, event, value):
            self.velocity[1] = value * self.maxSpeed

        def tick(self, delta):
            self.setPosition(self.getPositionX() + self.velocity[0] * delta, self.getPositionY() + self.velocity[1] * delta)

    player = playerCharacter()
    #mainRenderList.addObject(player)


    class TextCycler(Text.Text):
        def __init__(self, textList):
            super(TextCycler, self).__init__(textList[0])
            self.textList = textList
            self.currentTextIndex = 0
            self.setPosition(display.getScreenWidth()/2, display.getScreenHeight()/2)
            events.bindTimer(self.updateText, 1000, -1)

        def updateText(self):
            self.currentTextIndex = (self.currentTextIndex+1) % len(self.textList)
            self.setText(self.textList[self.currentTextIndex])

    textToDisplay = ["Hi There", "Have we met yet?", "Press 'd' key"]
    textCycler = TextCycler(textToDisplay)
    #mainRenderList.addObject(textCycler)

    class BitmapThing(GameObject.GameObject):
        def __init__(self, width, height, zoom):
            super(BitmapThing, self).__init__()
            width /= zoom
            height /= zoom
            self.setAlignment(GameObject.alignment.TOP, GameObject.alignment.LEFT)
            self.bitmap = pygame.Surface((width, height))
            self._bitmap = self.bitmap.copy()
            self.zoom = zoom
            self.colorDelta = 64
            self.color = pygame.Color(255, 255, 255)
            self.cColor = colors.BLACK
            self.ignore = set()
            self.mouseCoords = [0, 0]
            events.bindMouseDownEvent(1, self.mouseLeftClicked)
            events.bindMouseMotionEvent(self.mouseMoved)
            events.bindKeyAxis(["j"], ["u"], self.modifyRed)
            events.bindKeyAxis(["k"], ["i"], self.modifyGreen)
            events.bindKeyAxis(["l"], ["o"], self.modifyBlue)
            events.bindKeyDownEvent("p", self.clearIgnored)

            """
            for i in range(size):
                self.ignore.add((i, i))
            """

            self.colorLabel = Text.Text()
            self.colorLabel.setAlignment(GameObject.alignment.TOP, GameObject.alignment.LEFT)
            self.children.append(self.colorLabel)

            events.bindTimer(self.diffuse, 100, -1)

        def clearIgnored(self, event):
            self.ignore = set()

        def modifyComponent(self, value, delta):
            return sorted([0, value + delta, 255])[1]

        def modifyRed(self, event, value):
            delta = value*self.colorDelta
            self.color.r = self.modifyComponent(self.color.r, delta)

        def modifyGreen(self, event, value):
            delta = value*self.colorDelta
            self.color.g = self.modifyComponent(self.color.g, delta)

        def modifyBlue(self, event, value):
            delta = value*self.colorDelta
            self.color.b = self.modifyComponent(self.color.b, delta)

        def _setupColorLabelText(self):
            self.colorLabel.setText("(%d, %d, %d), (%s, %s, %s)" % (self.color.r, self.color.g, self.color.b, self.cColor.r, self.cColor.g, self.cColor.b))

        def _computePixelDiffuse(self, x, y):
            redTotal = 0
            greenTotal = 0
            blueTotal = 0
            total = 0
            #print x, y
            ourPixel = self._bitmap.get_at((x, y))
            #ourPixelMag = sqrt(x*x + y*y, z*z)
            for xOffset in xrange(-1, 2):
                for yOffset in xrange(-1, 2):
                    candX = x + xOffset
                    candY = y + yOffset
                    if candX < x or candY > y or (yOffset == 0 and xOffset == 0) or (candX < 0 or candX >= self._bitmap.get_width()) or (candY < 0 or candY >= self._bitmap.get_height()):
                        continue
                    total += 1
                    srcPixel = self._bitmap.get_at((candX, candY))
                    #print "\t", candX, candY, srcPixel
                    redTotal += srcPixel.r
                    greenTotal += srcPixel.g
                    blueTotal += srcPixel.b
            #print red, total
            #finalColor = pygame.Color(int(red/float(total)), ourPixel.g , ourPixel.b)
            if total == 0:
                return colors.BLACK
            g = lambda x, y: int(x/float(y))
            finalColor = pygame.Color(g(redTotal, total), g(greenTotal, total), g(blueTotal, total))
            #print red, total, int(red/float(total)), finalColor
            return finalColor

        def mouseLeftClicked(self, event):
            if tuple(self.mouseCoords) in self.ignore:
                self.ignore.remove(tuple(self.mouseCoords))
            else:
                self.ignore.add(tuple(self.mouseCoords))
                self.bitmap.set_at(self.mouseCoords, self.color)

        def mouseMoved(self, event):
            self.mouseCoords = map(lambda x: x/self.zoom, event.pos)
            self.mouseCoords[0] = sorted([0, self.mouseCoords[0], self.bitmap.get_width()-1])[1]
            self.mouseCoords[1] = sorted([0, self.mouseCoords[1], self.bitmap.get_height()-1])[1]

        def _getNeighbors(self, x, y):
            neighbors = []
            for xDelta in range(-1, 2):
                modifiedX = x + xDelta
                modifiedY = y + 1
                if modifiedX >= 0 and modifiedX < self.bitmap.get_width() and modifiedY >= 0 and modifiedY < self.bitmap.get_height():
                    neighbors.append((modifiedX, modifiedY))

            return neighbors


        def _pushColors(self, x, y):
            currentColor = self.bitmap.get_at((x,y))
            amountToPush = currentColor / pygame.Color(2,2,2)
            neighbors = self._getNeighbors(x, y)
            perPixelPush = amountToPush / pygame.Color(len(neighbors), len(neighbors), len(neighbors))
            newMainColor = currentColor - amountToPush
            for neighbor in neighbors:
                if neighbor not in self.ignore:
                    neighborColor = self.bitmap.get_at(neighbor)
                    newColor = neighborColor+perPixelPush
                    self.bitmap.set_at(neighbor, newColor)
            if not (x, y) in self.ignore:
                self.bitmap.set_at((x,y), newMainColor)

        def diffuse(self):
            #print("Diffuse!")
            self._bitmap = self.bitmap.copy()
            for x in range(self._bitmap.get_height()):
                for y in range(self._bitmap.get_width()):
                    #if (x, y) in self.ignore: continue
                    self._pushColors(y, x)
                    """
                    pixel = self._computePixelDiffuse(x, y)
                    #print pixel
                    self.bitmap.set_at((x, y), pixel)
                    """

            #print("Should diffuse")

        def draw(self, screen, offset=None):
            position = self.getPosition()
            if not offset is None:
                position[0] += offset[0]
                position[1] += offset[1]

            largerImage = pygame.transform.scale(self.bitmap, map(lambda x: x*self.zoom, self.bitmap.get_size()))
            screen.blit(largerImage, position)

        def tick(self, delta):
            super(BitmapThing, self).tick(delta)
            self.cColor = self.bitmap.get_at(self.mouseCoords)
            self._setupColorLabelText()

    bitmapThing = BitmapThing(1280, 800, 30)
    mainRenderList.addObject(bitmapThing)
    events.bindKeyDownEvent("f", lambda e: display.toggleFullscreen())
    while True:
        # Limit framerate to the desired FPS
        delta = clock.tick()

        # Handle game events through the event queue and tick all game constructs
        events.handleEvents()
        events.tick(delta)

        #mainCamera.centerOnObject(bitmapThing)

        # Draw screen
        screen = display.getScreen()
        screen.fill(colors.BLACK)
        mainRenderList.render(screen, mainCamera)
        hudRenderList.render(screen)
        pygame.display.update()

if __name__ == "__main__":
    main()
