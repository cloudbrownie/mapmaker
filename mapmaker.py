#imports --------------------------------------------------------------------- #
import pygame, sys, json, math, time, base64
from pygame.locals import *
from lib.Font import Font
from lib.SpriteSheets import loadTextures, reverseTextures

#classes --------------------------------------------------------------------- #
#screen tiles
class Screen:
    def __init__(self, topLeft, size, color):
        self.surface = pygame.Surface(size)
        self.surface.fill(color)
        self.rect = pygame.Rect(topLeft, size)
        self.width = size[0]
        self.height = size[1]
        self.color = color

    def draw(self, surf):
        surf.blit(pygame.transform.scale(self.surface, self.rect.size), self.rect)

#default button
class Button:
    def __init__(self, topLeft, size, color):
        self.surface = pygame.Surface(size)
        self.surface.fill(color)
        self.rect = pygame.Rect(topLeft, size)
        self.width = size[0]
        self.height = size[1]

    def draw(self, surf):
        surf.blit(self.surface, self.rect)

#the tile area
class TileArea(Screen):
    def __init__(self, topLeft, size, color, resolution):
        super().__init__(topLeft, size, color)
        self.background = pygame.Surface(resolution)
        self.background.fill(color)
        self.color = color
        self.gridSurfaces = {'off':pygame.Surface(resolution), '8x8':pygame.Surface(resolution), '16x16':pygame.Surface(resolution), '32x32':pygame.Surface(resolution)}
        for surf in self.gridSurfaces:
            self.gridSurfaces[surf].set_colorkey((0, 0, 0))
            if surf != 'off':
                curSize = int(surf.split('x')[0])
                for i in range(math.ceil(resolution[0] / curSize)):
                    pygame.draw.line(self.gridSurfaces[surf], (74, 71, 67), (curSize * i, 0), (curSize * i, resolution[1]), 1)
                for i in range(math.ceil(resolution[1] / curSize)):
                    pygame.draw.line(self.gridSurfaces[surf], (74, 71, 67), (0, curSize * i), (resolution[0], curSize * i), 1)
        self.gridSurface = self.gridSurfaces['off']
        self.width = resolution[0]
        self.height = resolution[1]
        self.xScale = size[0] / resolution[0]
        self.yScale = size[1] / resolution[1]
        self.curSize = 1

    def draw(self, surf, layers):
        self.background.fill(self.color)
        self.background.blit(self.gridSurface, (0, 0))
        for layer in layers:
            if layers[layer].show:
                for tile in layers[layer].tiles:
                    self.background.blit(tile.surface, tile.rect)
        surf.blit(self.background, (0, 0))

    def changeGrid(self, newSize):
        self.gridSurface = self.gridSurfaces[newSize]
        if newSize != 'off':
            self.curSize = int(newSize.split('x')[0])
        else:
            self.curSize = 1

    def getCurSize(self):
        return self.curSize

#side bar
class Sidebar(Screen):
    def __init__(self, topLeft, size, color):
        super().__init__(topLeft, size, color)
        self.color = color
        self.texturePath = ''
        self.searchBar = pygame.Rect(25, 75, 200, 50)
        self.searchBarColor = 37, 36, 34
        self.tabs = 'Menu', 'Options'
        self.tabRects = pygame.Rect(0, 0, 125, 50), pygame.Rect(125, 0, 125, 50)
        self.selected = self.tabs[0]
        self.separators = []

    def draw(self, surf):
        self.surface.fill(self.color)
        if self.selected == self.tabs[0]:
            pygame.draw.rect(self.surface, self.color, self.tabRects[0])
            pygame.draw.rect(self.surface, (54, 51, 47), self.tabRects[1])
            for separator in self.separators:
                pygame.draw.line(self.surface, (54, 51, 47), separator[0], separator[1], 2)
        elif self.selected == self.tabs[1]:
            pygame.draw.rect(self.surface, self.color, self.tabRects[1])
            pygame.draw.rect(self.surface, (54, 51, 47), self.tabRects[0])
        pygame.draw.rect(self.surface, self.searchBarColor, self.searchBar)
        font.render(self.surface, 'Menu', (63 - font.size('Menu', scale=3)[0] // 2, font.size('Menu', scale=3)[1] // 2), scale=3)
        font.render(self.surface, 'Options', (188 - font.size('Options', scale=3)[0] // 2, font.size('Options', scale=3)[1] // 2), scale=3)
        surf.blit(pygame.transform.scale(self.surface, self.rect.size), self.rect)

    def createSeparator(self, y):
        self.separators.append(((5, y), (self.rect.w - 5, y)))

    def clearSeparators(self):
        self.separators = []

#grid toggle button, with different sizes
class GridButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        self.sizes = ['off','8x8','16x16','32x32']
        self.surfaces = {}
        for ele in self.sizes:
            self.surfaces[ele] = pygame.Surface(size)
            self.surfaces[ele].fill(color)
            textSize = font.size(ele, scale=2)
            font.render(self.surfaces[ele], ele, (self.width // 2 - textSize[0] // 2, 7), scale=2)
        self.surface = self.surfaces['off']
        self.index = 0

    def cycleSize(self):
        self.index += 1
        self.index %= len(self.sizes)
        self.surface = self.surfaces[self.sizes[self.index]]

    def getStatus(self):
        return self.sizes[self.index]

#save button
class SaveButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        textSize = font.size('Save', scale=2)
        font.render(self.surface, 'Save', (self.width // 2 - textSize[0] // 2, 7), scale=2)

#clear button
class ClearButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        textSize = font.size('Clear', scale=2)
        font.render(self.surface, 'Clear', (self.width // 2 - textSize[0] // 2, 7), scale=2)

class ClearAllButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        textSize = font.size('Clear All', scale=2)
        font.render(self.surface, 'Clear All', (self.width // 2 - textSize[0] // 2, 7), scale=2)

#load map button
class LoadButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        textSize = font.size('Load', scale=2)
        font.render(self.surface, 'Load', (self.width // 2 - textSize[0] // 2, 7), scale=2)

#texture tile in sidebar that shows the current loaded textures
class TextureTile:
    def __init__(self, coords, surface):
        self.x = coords[0]
        self.y = coords[1]
        self.size = (surface.get_width(), surface.get_height())
        self.rect = pygame.Rect((self.x, self.y), self.size)
        self.textureRect = pygame.Rect((self.x, self.y), (surface.get_size()))
        self.origSurface = pygame.Surface(surface.get_size())
        self.origSurface.blit(surface, (0,0))
        self.surface = pygame.Surface(self.size)
        self.surface.blit(pygame.transform.scale(surface, self.size), (0,0))

    def draw(self, surf):
        surf.blit(self.surface, self.rect)

#current texture holding
class CurrentTexture:
    def __init__(self, surface):
        self.rect = pygame.Rect((0, 0), surface.get_size())
        self.surface = surface.copy()
        self.colorkey = (0, 0, 0)
        self.surface.set_colorkey(self.colorkey)

    def draw(self, surf):
        tempSurf = self.surface.copy()
        self.surface.fill(self.colorkey)
        self.surface.blit(tempSurf, (0, 0))
        surf.blit(self.surface, self.rect)

    def rotateSurface(self, direction):
        if direction == K_q:
            self.surface.blit(pygame.transform.rotate(self.surface, 90.0), (0,0))
        else:
            self.surface.blit(pygame.transform.rotate(self.surface, -90.0), (0,0))

    def update(self, surf, mousepos, scales):
        self.rect.centerx = mousepos[0] / scales[0]
        self.rect.centery = mousepos[1] / scales[1]
        self.draw(surf)

    def show(self, surf):
        surf.blit(pygame.transform.scale(self.surface, (100, 100)), (75, 225))

#drawn tile to the screen
class DrawnTile:
    def __init__(self, coords, surface):
        self.x = coords[0]
        self.y = coords[1]
        self.rect = pygame.Rect((self.x, self.y), surface.get_size())
        self.surface = surface.copy()
        self.colorkey = (0, 0, 0)
        self.surface.set_colorkey(self.colorkey)

    def draw(self, surf):
        tempSurf = self.surface.copy()
        self.surface.fill(self.colorkey)
        self.surface.blit(tempSurf, (0, 0))
        surf.blit(self.surface, self.rect)

#layer container
class BuildLayer:
    def __init__(self, layerNum, font):
        #interactable vars
        self.id = layerNum
        self.tiles = []
        self.show = True
        self.current = False
        self.icon = pygame.Surface((100, 20))
        self.curIcon = pygame.Surface((100, 20))
        self.rect = pygame.Rect(0, 0, 100, 20)
        self.icon.fill((47, 46, 44))
        self.curIcon.fill((37, 36, 34))
        self.color = (47, 46, 44)
        self.font = font
        self.renderId(f'Layer {self.id}')
        self.activeRect = pygame.Rect(0, 0, 20, 20)
        self.typeRect = pygame.Rect(0, 0, 20, 20)
        #layer quality vars
        self.types = ['solid', 'platform', 'decoration']
        self.typeColors = [(0, 255, 0), (255, 255, 0), (255, 0, 0)]
        self.index = 0
        self.type = self.types[self.index]

    def renderId(self, id):
        self.icon.fill(self.color)
        self.font.render(self.icon, id, (self.rect.w // 2 - self.font.size(id)[0] // 2, self.rect.h // 2 - self.font.size(id)[1] // 2))
        self.curIcon.fill((37, 36, 34))
        self.font.render(self.curIcon, id, (self.rect.w // 2 - self.font.size(id)[0] // 2, self.rect.h // 2 - self.font.size(id)[1] // 2))

    def reposition(self, centerloc):
        self.rect.center = centerloc
        self.activeRect.center = centerloc[0] - 65, centerloc[1]
        self.typeRect.center = centerloc[0] + 65, centerloc[1]

    def cycleType(self):
        self.index += 1
        self.index %= len(self.types)
        self.type = self.types[self.index]

    def setType(self, type):
        self.index = self.types.index(type)
        self.type = self.types[self.index]

    def drawIcon(self, surf):
        if self.current:
            surf.blit(self.curIcon, self.rect)
        else:
            surf.blit(self.icon, self.rect)
        pygame.draw.rect(surf, self.color, self.activeRect)
        if self.show:
            pygame.draw.rect(surf, (255, 255, 255), (self.rect.x - 22, self.rect.y + 3, self.rect.h - 6, self.rect.h - 6))
        pygame.draw.rect(surf, self.color, self.typeRect)
        pygame.draw.rect(surf, self.typeColors[self.index], (self.typeRect.x + 3, self.rect.y + 3, self.rect.h - 6, self.rect.h - 6))

#general functions ----------------------------------------------------------- #
def saveMap(currentTiles):
    """
    used to save the current map that was built. it saves each tile's rect, surface id,
    and size to a dictionary. also saves each unique surface to the dictionary as well.
    then saves the dictionary to a json file. the unique surfaces are saved as endocded byte strings.
    """


    data = {'Layers':[], 'Surfaces':[]}
    surfaces = []
    for layer in layers:
        #save all unique surfaces to a string
        [surfaces.append(pygame.image.tostring(tile.surface, 'RGB')) for tile in layers[layer].tiles if pygame.image.tostring(tile.surface, 'RGB') not in surfaces]
        #give all tiles their surface id
        for tile in layers[layer].tiles:
            tile.surfID = surfaces.index(pygame.image.tostring(tile.surface, 'RGB'))
        #save all tiles as a dict
        layerRects = []
        [layerRects.append({'SurfID':tile.surfID, 'Coords':tile.rect.topleft, 'Size':tile.rect.size, 'Type':layers[layer].type}) for tile in layers[layer].tiles]
        data['Layers'].append(layerRects)
    #json doesnt like converting byte objects, so we encode to ascii, which means when we try to load this byte obj later, we need to decode
    for i in range(len(surfaces)):
        surfaces[i] = base64.b64encode(surfaces[i]).decode('ascii')
    #save the surfaces
    data['Surfaces'] = surfaces
    timeString = time.ctime(time.time())
    timeString = timeString[-16:]
    timeString = list(timeString)
    timeStamp = ''
    for i in range(len(timeString)):
        if timeString[i] == ' ' or timeString[i] == ':':
            timeString[i] = '.'
        timeStamp += timeString[i]
    with open(f'output/{timeStamp}.json','w+') as writeFile:
        json.dump(data, writeFile)

#load up a map to display on the screen
def loadMap(path):
    try:
        #load the map from the json given the path
        with open(path, 'r') as readFile:
            data = json.load(readFile)
        #layers are stored in dict
        layers = {}
        for i in range(len(data['Layers'])): #this iterates through every layer
            type = data['Layers'][i][0]['Type'] #this grabs the type of the first tile in the current layer
            newLayer = BuildLayer(i, font) #this creates a build layer object for the current layer
            newLayer.setType(type)
            for tile in data['Layers'][i]: #this iterates through every tile in the current layer
                surface = pygame.image.fromstring(base64.b64decode(data['Surfaces'][tile['SurfID']]), tile['Size'], 'RGB') #creates a surface using the current tile's info
                newLayer.tiles.append(DrawnTile(tile['Coords'], surface.copy())) #creates a new tile obj with the current tile's info and surface
            layers[i] = newLayer #adds the new layer to the layers dict
        return layers
    except Exception as e:
        print(e)

#clean up tiles when there is more than one on the same exact spot
def cleanUp(tiles, newTile):
    for tile in tiles:
        if tile.rect.topleft == newTile.rect.topleft and tile.rect.bottomright == newTile.rect.bottomright:
            tiles.remove(tile)
    tiles.append(newTile)

#window init ----------------------------------------------------------------- #
pygame.init()
screen = pygame.display.set_mode(size=(1920, 1050))
pygame.display.set_caption('Tile Map Maker')

#setup ----------------------------------------------------------------------- #
font = Font('lib/font.png')

gui = pygame.Surface((1750, 1000))
gui.set_colorkey((0, 0, 0))

#setting up the sidebar menu
sidebar = Sidebar((0,0), (250, 1000), (64, 61, 57))
textureSearching = False
textureSearchPath = ''
mapSearching = False
mapSearchPath = ''
textureMenu = True
buttonMenu = False

#search settings
backspacing = False
backspaceTimer = 0
shiftCaps = False
allCaps = False
searchRenderOffset = 5

res = (1080, 720)
tilearea = TileArea((250, 0), (1500, 1000), (37, 36, 34), (2880, 1920))

#mouse settings
xRatio = screen.get_width() / gui.get_width()
yRatio = screen.get_height() / gui.get_height()
currentTexture = None

#load button used to load a map from a json
loadButton = LoadButton((35, 140), (180, 30), (37, 36, 34), font)

#button used to swap grid sizes
sizeButton = GridButton((35, 185), (180, 30), (37, 36, 34), font)
gridStyle = sizeButton.getStatus()
tiles = []
size = None

#save button used to save the current map
saveButton = SaveButton((35, 230), (180, 30), (37, 36, 34), font)

#clear button to clear the buildign area
clearButton = ClearButton((35, 275), (180, 30), (37, 36, 34), font)
clearAllButton = ClearAllButton((35, 320), (180, 30), (37, 36, 34), font)

#loading textures settings
loadedTextures = []

#time settings
prevTime = time.time()
time.sleep(.00001)

#building vars
layers = {0:BuildLayer(0, font)}
layers[0].reposition((125, 365))
layerIndex = 0
mapDrag = False
dragOrig = (0, 0)
placing = False
removing = False
cameraRect = pygame.Rect((0, 0), res)
buildSurface = pygame.Surface(tilearea.background.get_size())

#loop ------------------------------------------------------------------------ #
while True:

    #time -------------------------------------------------------------------- #
    dt = time.time() - prevTime
    prevTime = time.time()

    #update elements --------------------------------------------------------- #
    gui.fill((0, 0, 0))
    tilearea.draw(buildSurface, layers)
    #cut out camera surface from build surface
    if mapDrag and pygame.mouse.get_pressed()[0]:
        xOff, yOff = pygame.mouse.get_rel()
        cameraRect.x -= xOff / (tilearea.rect.w / cameraRect.w)
        cameraRect.y -= yOff / (tilearea.rect.h / cameraRect.h)
    #this makes sure that the canera is within range of the build surface
    cameraRect.w = min(cameraRect.w, res[0])
    cameraRect.h = min(cameraRect.h, res[1])
    cameraRect.top = max(cameraRect.top, 0)
    cameraRect.bottom = min(cameraRect.bottom, buildSurface.get_height())
    cameraRect.left = max(cameraRect.left, 0)
    cameraRect.right = min(cameraRect.right, buildSurface.get_width())
    cameraSurface = buildSurface.subsurface(cameraRect)
    #stretch camera surface to match build area size
    gui.blit(pygame.transform.scale(cameraSurface, (1500, 1000)), (250, 0))

    sidebar.draw(gui)
    if textureMenu:
        #i can hold backspace an it'll start deleting everything after a certain period
        if backspacing and textureSearchPath != '':
            backspaceTimer += dt
            if backspaceTimer >= .20:
                textureSearchPath = textureSearchPath[:len(textureSearchPath)-1]
        else:
            backspaceTimer = 0
        #gotta make sure that what is being put in the searchbar fits the searchbar
        renderedSearch = textureSearchPath
        if renderedSearch != '':
            while font.size(renderedSearch, scale=2)[0] >= sidebar.searchBar.w - searchRenderOffset:
                renderedSearch = renderedSearch[-len(renderedSearch)+1:]
        #render the search on top of the searchbar, but render to gui since i already drew the sidebar
        font.render(gui, renderedSearch, (sidebar.searchBar.midleft[0] + searchRenderOffset, sidebar.searchBar.midleft[1] - 10), scale=2)
        for texture in loadedTextures:
            gui.blit(texture.surface, texture.rect)
        #display the texture currently held
        font.render(gui, 'Current Texture', (sidebar.rect.w // 2 - font.size('Current Texture', scale=2.5)[0] // 2, 190), scale=2.5)
        if currentTexture:
            currentTexture.show(gui)

    elif buttonMenu:
        #i can hold backspace an it'll start deleting everything after a certain period
        if backspacing and mapSearchPath != '':
            backspaceTimer += dt
            if backspaceTimer >= .20:
                mapSearchPath = mapSearchPath[:len(mapSearchPath)-1]
        else:
            backspaceTimer = 0
        #gotta make sure that what is being put in the searchbar fits the searchbar
        renderedSearch = mapSearchPath
        if renderedSearch != '':
            while font.size(renderedSearch, scale=2)[0] >= sidebar.searchBar.w - searchRenderOffset:
                renderedSearch = renderedSearch[-len(renderedSearch)+1:]
        font.render(gui, renderedSearch, (sidebar.searchBar.midleft[0] + searchRenderOffset, sidebar.searchBar.midleft[1] - 10), scale=2)
        sizeButton.draw(gui)
        saveButton.draw(gui)
        clearButton.draw(gui)
        clearAllButton.draw(gui)
        for layer in layers:
            layers[layer].drawIcon(gui)
    loadButton.draw(gui)
    if currentTexture:
        currentTexture.update(gui, pygame.mouse.get_pos(), (xRatio, yRatio))

    mx, my = pygame.mouse.get_pos()
    mousepos = mx / xRatio, my / yRatio
    if placing:
        #drag drawing
        mousepos = cameraRect.x + ((mousepos[0] - tilearea.rect.x) / (tilearea.rect.w / cameraRect.w)), cameraRect.y + (mousepos[1] / (tilearea.rect.h / cameraRect.h))
        if tilearea.getCurSize() > 1:
            newTile = DrawnTile((mousepos[0] - mousepos[0] % tilearea.getCurSize(), mousepos[1] - mousepos[1] % tilearea.getCurSize()), currentTexture.surface)
        else:
            newTile = DrawnTile((mousepos[0] - currentTexture.surface.get_width() // 2, mousepos[1] - currentTexture.surface.get_height() // 2), currentTexture.surface)
        cleanUp(layers[layerIndex].tiles, newTile)
    elif removing:
        #drag deleting
        mousepos = cameraRect.x + ((mousepos[0] - tilearea.rect.x) / (tilearea.rect.w / cameraRect.w)), cameraRect.y + (mousepos[1] / (tilearea.rect.h / cameraRect.h))
        for tile in layers[layerIndex].tiles:
            if tile.rect.collidepoint(mousepos):
                layers[layerIndex].tiles.remove(tile)
                break

    #handle events ----------------------------------------------------------- #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEWHEEL:
            if tilearea.rect.collidepoint(mousepos):
                wMult = 75 * (res[0] / cameraRect.w)
                hMult = 50 * (res[1] / cameraRect.h)
                if cameraRect.w - event.y * wMult > 0 and cameraRect.h - event.y * hMult > 0: #zoom the map based on zoom already
                    cameraRect.w -= event.y * wMult
                    cameraRect.h -= event.y * hMult
                    cameraRect.center = cameraRect.x + ((mousepos[0] - tilearea.rect.x) / (tilearea.rect.w / cameraRect.w)), cameraRect.y + (mousepos[1] / (tilearea.rect.h / cameraRect.h))
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                #draw at a position in the grid
                if tilearea.rect.collidepoint(mousepos):
                    if not mapDrag and currentTexture:
                        placing = True
                        removing = False
                    elif mapDrag:
                        dragOrig = pygame.mouse.get_rel()
                elif sidebar.rect.collidepoint(mousepos):
                    #swap sidebar tabs
                    if sidebar.tabRects[0].collidepoint(mousepos):
                        textureMenu = True
                        buttonMenu = False
                        sidebar.selected = sidebar.tabs[0]
                    elif sidebar.tabRects[1].collidepoint(mousepos):
                        textureMenu = False
                        buttonMenu = True
                        sidebar.selected = sidebar.tabs[1]
                        textureSearching = False
                    #works with the searchbar
                    elif loadButton.rect.collidepoint(mousepos):
                        mapSearching = False
                        textureSearching = False
                        if buttonMenu:
                            loaded = (loadMap(mapSearchPath))
                            if loaded:
                                for layer in loaded:
                                    layers[len(layers)] = loaded[layer]
                                    layers[len(layers) - 1].reposition((125, 340 + 25 * len(layers)))
                        else:
                            textures = loadTextures(textureSearchPath, colorkey=(0, 0, 0))
                            if textures:
                                sidebar.clearSeparators()
                                loadedTextures = []
                                sidebar.createSeparator(340)
                                y = 344
                                for row in textures: # each row
                                    if len(row) > 0:
                                        x = 10
                                        height = []
                                        for texture in row: # each texture in row
                                            if x >= sidebar.rect.w - texture.get_width():
                                                x = 10
                                                y += max(height) + 8
                                            loadedTextures.append(TextureTile((x, y), texture))
                                            x += texture.get_width() + 4
                                            height.append(texture.get_height())
                                        y += max(height) + 8
                                        sidebar.createSeparator(y - 4)
                    if textureMenu:
                        #buttons for the texture menu
                        if sidebar.searchBar.collidepoint(mousepos):
                            textureSearching = True
                        else:
                            for texture in loadedTextures:
                                if texture.rect.collidepoint(mousepos):
                                    currentTexture = CurrentTexture(texture.origSurface)
                    elif buttonMenu:
                        #buttons for the button menu
                        if sidebar.searchBar.collidepoint(mousepos):
                            mapSearching = True
                        elif sizeButton.rect.collidepoint(mousepos):
                            sizeButton.cycleSize()
                            gridStyle = sizeButton.getStatus()
                            tilearea.changeGrid(gridStyle)
                        elif saveButton.rect.collidepoint(mousepos):
                            saveMap(layers)
                        elif clearButton.rect.collidepoint(mousepos):
                            layers[layerIndex].tiles = []
                        elif clearAllButton.rect.collidepoint(mousepos):
                            for layer in layers:
                                layers[layer].tiles = []
                        else:
                            for layer in layers:
                                if layers[layer].rect.collidepoint(mousepos):
                                    layers[layerIndex].current = False
                                    layerIndex = layers[layer].id
                                    layers[layerIndex].current = True
                                elif layers[layer].activeRect.collidepoint(mousepos):
                                    layers[layer].show = not layers[layer].show
                                elif layers[layer].typeRect.collidepoint(mousepos):
                                    layers[layer].cycleType()
            elif event.button == 3:
                #for deleting
                currentTexture = None
                if tilearea.rect.collidepoint(mousepos):
                    removing = True
                    placing = False
            elif event.button == 2:
                #if you're hovering over a placed tile, make the current texture to that tile
                if tilearea.rect.collidepoint(mousepos):
                    mousepos = cameraRect.x + ((mousepos[0] - tilearea.rect.x) / (tilearea.rect.w / cameraRect.w)), cameraRect.y + (mousepos[1] / (tilearea.rect.h / cameraRect.h))
                    for tile in layers[layerIndex].tiles:
                        if tile.rect.collidepoint(mousepos):
                            currentTexture = CurrentTexture(tile.surface)
        elif event.type == MOUSEBUTTONUP:
            #stop buildign or removing
            if event.button == 1:
                placing = False
            elif event.button == 3:
                removing = False
        elif event.type == KEYDOWN:
            if not textureSearching and not mapSearching:
                #rotate the current texture
                if (event.key == K_q or event.key == K_e) and currentTexture:
                    currentTexture.rotateSurface(event.key)
                #change layers
                elif event.key == K_w:
                    if layerIndex - 1 > -1:
                        layers[layerIndex].current = False
                        layerIndex -= 1
                        layers[layerIndex].current = True
                elif event.key == K_s:
                    if layerIndex + 1 < 26:
                        layers[layerIndex].current = False
                        layerIndex += 1
                        if layerIndex not in layers:
                            layers[layerIndex] = BuildLayer(layerIndex, font)
                            layers[len(layers) - 1].reposition((125, 340 + 25 * len(layers)))
                        layers[layerIndex].current = True
            #map dragging
            if event.key == K_LCTRL:
                mapDrag = True
            #get rid of the current tile
            elif event.key == K_ESCAPE:
                currentTexture = None
            #enter key
            elif event.key == K_RETURN:
                textureSearching = False
                mapSearching = False
                if buttonMenu:
                    loaded = (loadMap(mapSearchPath))
                    if loaded:
                        for layer in loaded:
                            layers[len(layers)] = loaded[layer]
                            layers[len(layers) - 1].reposition((125, 340 + 25 * len(layers)))
                else:
                    textures = loadTextures(textureSearchPath, colorkey=(0, 0, 0))
                    if textures:
                        sidebar.clearSeparators()
                        loadedTextures = []
                        sidebar.createSeparator(340)
                        y = 344
                        for row in textures: # each row
                            if len(row) > 0:
                                x = 10
                                height = []
                                for texture in row: # each texture in row
                                    if x >= sidebar.rect.w - texture.get_width():
                                        x = 10
                                        y += max(height) + 8
                                    loadedTextures.append(TextureTile((x, y), texture))
                                    x += texture.get_width() + 4
                                    height.append(texture.get_height())
                                y += max(height) + 8
                                sidebar.createSeparator(y - 4)
                shiftCaps = True
            #caps
            elif event.key == K_CAPSLOCK:
                allCaps = not allCaps
            #next two ifs are for the search bar
            elif textureSearching:
                if event.key == K_BACKSPACE:
                    backspacing = True
                    if len(textureSearchPath) > 0:
                        textureSearchPath = textureSearchPath[:len(textureSearchPath)-1]
                else:
                    #if both shitft and caps are on, the text turns small again
                    try:
                        if (shiftCaps and not allCaps) or (not shiftCaps and allCaps):
                            textureSearchPath += chr(event.key).capitalize()
                        else:
                            textureSearchPath += chr(event.key)
                    except: pass #invalid characters
            elif mapSearching:
                if event.key == K_BACKSPACE:
                    backspacing = True
                    if len(mapSearchPath) > 0:
                        mapSearchPath = mapSearchPath[:len(mapSearchPath)-1]
                else:
                    #if both shitft and caps are on, the text turns small again
                    try:
                        if (shiftCaps and not allCaps) or (not shiftCaps and allCaps):
                            mapSearchPath += chr(event.key).capitalize()
                        else:
                            mapSearchPath += chr(event.key)
                    except: pass #invalid characters
        elif event.type == KEYUP:
            if mapDrag:
                mapDrag = False
            if textureSearching or mapSearching:
                if event.key == K_BACKSPACE:
                    backspacing = False
                elif event.key == K_LSHIFT or event.key == K_RSHIFT:
                    shiftCaps = False

    #update window ----------------------------------------------------------- #
    screen.blit(pygame.transform.scale(gui, (screen.get_width(), screen.get_height())), (0,0))
    pygame.display.flip()
