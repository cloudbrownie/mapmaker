#imports --------------------------------------------------------------------- #
import pygame, sys, json, math, time, base64, random, tkinter, threading
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

#grid toggle button, with different sizes
class GridButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        self.sizes = ['off','8x8','16x16','32x32']
        self.surfaces = {}
        for ele in self.sizes:
            self.surfaces[ele] = pygame.Surface(size)
            self.surfaces[ele].fill(color)
            textSize = font.size(ele, scale=3)
            font.render(self.surfaces[ele], ele, (self.width // 2 - textSize[0] // 2, 15), scale=3)
        self.surface = self.surfaces['off']
        self.index = 0

    def cycleSize(self):
        self.index += 1
        self.index %= len(self.sizes)
        self.surface = self.surfaces[self.sizes[self.index]]

    def getStatus(self):
        return self.sizes[self.index]

#map building tiles
class MapTiles:
    def __init__(self, coords, size):
        self.x = coords[0]
        self.y = coords[1]
        self.rect = pygame.Rect(self.x, self.y, size, size)
        self.surface = pygame.Surface((size, size))
        self.surfID = None

    def draw(self, surf):
        pygame.draw.rect(surf, (74, 71, 67), self.rect, 1)

#the tile area
class TileArea(Screen):
    def __init__(self, topLeft, size, color, resolution):
        super().__init__(topLeft, size, color)
        self.background = pygame.Surface(resolution)
        self.background.fill(color)
        self.surface = pygame.Surface(resolution)
        self.surface.fill((0, 0, 1))
        self.surface.set_colorkey((0, 0, 1))
        self.gridSurface = self.surface.copy()
        self.gridSurface.fill((0, 0, 0))
        self.gridSurface.set_colorkey((0, 0, 0))
        self.width = resolution[0]
        self.height = resolution[1]
        self.xScale = size[0] / resolution[0]
        self.yScale = size[1] / resolution[1]


    def draw(self, surf):
        surf.blit(pygame.transform.scale(self.background, self.rect.size), self.rect)
        surf.blit(pygame.transform.scale(self.surface, self.rect.size), self.rect)
        surf.blit(pygame.transform.scale(self.gridSurface, self.rect.size), self.rect)
        self.surface.fill((0, 0, 1))

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

    def draw(self, surf):
        self.surface.fill(self.color)
        if self.selected == self.tabs[0]:
            pygame.draw.rect(self.surface, self.color, self.tabRects[0])
            pygame.draw.rect(self.surface, (54, 51, 47), self.tabRects[1])
        elif self.selected == self.tabs[1]:
            pygame.draw.rect(self.surface, self.color, self.tabRects[1])
            pygame.draw.rect(self.surface, (54, 51, 47), self.tabRects[0])
        pygame.draw.rect(self.surface, self.searchBarColor, self.searchBar)
        font.render(self.surface, 'Menu', (63 - font.size('Menu', scale=3)[0] // 2, font.size('Menu', scale=3)[1] // 2), scale=3)
        font.render(self.surface, 'Options', (188 - font.size('Options', scale=3)[0] // 2, font.size('Options', scale=3)[1] // 2), scale=3)
        surf.blit(pygame.transform.scale(self.surface, self.rect.size), self.rect)

#save button
class SaveButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        textSize = font.size('Save', scale=3)
        font.render(self.surface, 'Save', (self.width // 2 - textSize[0] // 2, 15), scale=3)

#clear button
class ClearButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        textSize = font.size('Clear', scale=3)
        font.render(self.surface, 'Clear', (self.width // 2 - textSize[0] // 2, 15), scale=3)

#load map button
class LoadButton(Button):
    def __init__(self, topLeft, size, color, font):
        super().__init__(topLeft, size, color)
        textSize = font.size('Load', scale=3)
        font.render(self.surface, 'Load', (self.width // 2 - textSize[0] // 2, 15), scale=3)

#texture tile
class TextureTile:
    def __init__(self, coords, surface):
        self.x = coords[0]
        self.y = coords[1]
        self.size = (32, 32)
        self.rect = pygame.Rect((self.x, self.y), self.size)
        self.surface = pygame.Surface(self.size)
        self.surface.blit(pygame.transform.scale(surface, self.size), (0,0))

    def draw(self, surf):
        surf.blit(self.surface, self.rect)

#general functions ----------------------------------------------------------- #
def saveMap(currentTiles):
    """
    used to save the current map that was built. it saves each tile's rect, surface id,
    and size to a dictionary. also saves each unique surface to the dictionary as well.
    then saves the dictionary to a json file. the unique surfaces are saved as endocded byte strings.
    """
    data = {}
    tiles = [x for x in currentTiles]
    #save all unique surfaces as a string
    uniqueSurfaces = []
    [uniqueSurfaces.append(pygame.image.tostring(tile.surface, 'RGB')) for tile in tiles if pygame.image.tostring(tile.surface, 'RGB') not in uniqueSurfaces]
    #give each tile an id corresponding to its surfaces in the surface list
    for tile in tiles:
        tile.surfID = uniqueSurfaces.index(pygame.image.tostring(tile.surface, 'RGB'))
    #put the surfaces into the data dict
    savedSurfaces = []
    #json doesnt like converting byte objects, so we encode to ascii, which means when we try to load this byte obj later, we need to decode
    [savedSurfaces.append(base64.b64encode(surf).decode('ascii')) for surf in uniqueSurfaces]
    #put all the tile objs into the data dict
    savedTiles = []
    [savedTiles.append({'SurfID':tile.surfID, 'Coords':tile.rect.topleft, 'Size':tile.rect.w}) for tile in tiles]
    #write to a json file in output
    data['Surfaces'] = savedSurfaces
    data['Tiles'] = savedTiles
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

    #this code is used to decode the surfaces
    #testSurf = pygame.image.fromstring(base64.b64decode(data['Surface 0']), (8, 8), 'RGB')

#load up a map to display on the screen
def loadMap(path):
    global gui
    try:
        with open(path, 'r') as readFile:
            data = json.load(readFile)
        tiles = []
        for tile in data['Tiles']:
            tiles.append(MapTiles(tile['Coords'], tile['Size']))
            tiles[-1].surfID = tile['SurfID']
            print(tiles[-1].rect)
        print('-'*50)
        for tile in tiles:
            tile.surface = pygame.image.fromstring(base64.b64decode(data['Surfaces'][tile.surfID]), tile.rect.size, 'RGB')
            print(tile.rect)
        return tiles
    except Exception as e:
        print(e)

#window init ----------------------------------------------------------------- #
screen = pygame.display.set_mode(size=(1750, 1000))
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

tilearea = TileArea((250, 0), (1500, 1000), (37, 36, 34), (720, 480))

#mouse settings
xRatio = screen.get_width() / gui.get_width()
yRatio = screen.get_height() / gui.get_height()
currentTexture = None
currentRect = None

#load button used to load a map from a json
loadButton = LoadButton((25, 140), (200, 50), (37, 36, 34), font)

#button used to swap grid sizes
sizeButton = GridButton((25, 205), (200, 50), (37, 36, 34), font)
gridStyle = sizeButton.getStatus()
tiles = []
size = None

#save button used to save the current map
saveButton = SaveButton((25, 270), (200, 50), (37, 36, 34), font)

#clear button to clear the buildign area
clearButton = ClearButton((25, 335), (200, 50), (37, 36, 34), font)

#loading textures settings
loadedTextures = []

#time settings
prevTime = time.time()
time.sleep(.00001)

#building vars
placedTiles = []

#loop ------------------------------------------------------------------------ #
while True:

    #time -------------------------------------------------------------------- #
    dt = time.time() - prevTime
    prevTime = time.time()

    #update elements --------------------------------------------------------- #
    gui.fill((0, 0, 0))
    for tile in placedTiles:
        tilearea.surface.blit(tile.surface, tile.rect)
    tilearea.draw(gui)
    sidebar.draw(gui)
    if textureMenu:
        #i can hold backspace an it'll start deleting everything after a certain period
        if backspacing:
            backspaceTimer += dt
            if backspaceTimer >= .20:
                if len(textureSearchPath) > 0:
                    textureSearchPath = textureSearchPath[:len(textureSearchPath)-1]
        else:
            backspaceTimer = 0
        #gotta make sure that what is being put in the searchbar fits the searchbar
        renderedSearch = ''
        fit = False
        for i in range(len(textureSearchPath)):
            if not fit:
                renderedSearch += textureSearchPath[i]
                textureSearchPathSurfaceSize = font.size(renderedSearch, scale=2)
                #check if the render is too long, make the render a substring from the back of the textureSearchPath
                if textureSearchPathSurfaceSize[0] >= sidebar.searchBar.w - searchRenderOffset:
                    fit = True
                    renderedSearch = textureSearchPath[-len(renderedSearch):]
                    #trims the newly created render to make sure it still fits
                    textureSearchPathSurfaceSize = font.size(renderedSearch, scale=2)
                    while textureSearchPathSurfaceSize[0] >= sidebar.searchBar.w - searchRenderOffset:
                        renderedSearch = renderedSearch[-len(renderedSearch)+1:] #return the string without the first character
                        textureSearchPathSurfaceSize = font.size(renderedSearch, scale=2)
        #render the search on top of the searchbar, but render to gui since i already drew the sidebar
        font.render(gui, renderedSearch, (sidebar.searchBar.midleft[0] + searchRenderOffset, sidebar.searchBar.midleft[1] - 10), scale=2)
        for texture in loadedTextures:
            gui.blit(texture.surface, texture.rect)
    elif buttonMenu:
        #i can hold backspace an it'll start deleting everything after a certain period
        if backspacing:
            backspaceTimer += dt
            if backspaceTimer >= .20:
                if len(mapSearchPath) > 0:
                    mapSearchPath = mapSearchPath[:len(mapSearchPath)-1]
        else:
            backspaceTimer = 0
        #gotta make sure that what is being put in the searchbar fits the searchbar
        renderedSearch = ''
        fit = False
        for i in range(len(mapSearchPath)):
            if not fit:
                renderedSearch += mapSearchPath[i]
                mapSearchPathSurfaceSize = font.size(renderedSearch, scale=2)
                #check if the render is too long, make the render a substring from the back of the mapSearchPath
                if mapSearchPathSurfaceSize[0] >= sidebar.searchBar.w - searchRenderOffset:
                    fit = True
                    renderedSearch = mapSearchPath[-len(renderedSearch):]
                    #trims the newly created render to make sure it still fits
                    mapSearchPathSurfaceSize = font.size(renderedSearch, scale=2)
                    while mapSearchPathSurfaceSize[0] >= sidebar.searchBar.w - searchRenderOffset:
                        renderedSearch = renderedSearch[-len(renderedSearch)+1:] #return the string without the first character
                        mapSearchPathSurfaceSize = font.size(renderedSearch, scale=2)
        font.render(gui, renderedSearch, (sidebar.searchBar.midleft[0] + searchRenderOffset, sidebar.searchBar.midleft[1] - 10), scale=2)
        sizeButton.draw(gui)
        saveButton.draw(gui)
        clearButton.draw(gui)
    loadButton.draw(gui)
    if currentTexture:
        currentRect.center = pygame.mouse.get_pos()
        gui.blit(currentTexture, currentRect)

    #handle events ----------------------------------------------------------- #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            mousepos = mx / xRatio, my / yRatio
            if event.button == 1:
                #check if a tile was clicked and draw there
                if tilearea.rect.collidepoint(mousepos):
                    mousepos = (mousepos[0] - tilearea.rect.x) / tilearea.xScale, mousepos[1] / tilearea.yScale
                    for tile in tiles:
                        if tile.rect.collidepoint(mousepos):
                            if currentTexture:
                                tile.surface.blit(pygame.transform.scale(currentTexture, tile.rect.size), (0,0))
                                placedTiles.append(tile)
                elif sidebar.rect.collidepoint(mousepos):
                    if sidebar.tabRects[0].collidepoint(mousepos):
                        textureMenu = True
                        buttonMenu = False
                        sidebar.selected = sidebar.tabs[0]
                    elif sidebar.tabRects[1].collidepoint(mousepos):
                        textureMenu = False
                        buttonMenu = True
                        sidebar.selected = sidebar.tabs[1]
                        textureSearching = False
                    elif loadButton.rect.collidepoint(mousepos):
                        if buttonMenu:
                            loaded = (loadMap(mapSearchPath))
                            if loaded:
                                placedTiles.extend(loaded)
                        else:
                            print(textureSearchPath)
                            textures = loadTextures(textureSearchPath, colorkey=(0, 0, 0))
                            if textures:
                                loadedTextures = []
                                for i in range(len(textures)):
                                    loadedTextures.append(TextureTile((20, 205 + 65 * i), textures[i]))
                    if textureMenu:
                        if sidebar.searchBar.collidepoint(mousepos):
                            textureSearching = True
                        else:
                            for texture in loadedTextures:
                                if texture.rect.collidepoint(mousepos):
                                    currentTexture = texture.surface.copy()
                                    currentRect = texture.rect.copy()
                    elif buttonMenu:
                        if sidebar.searchBar.collidepoint(mousepos):
                            mapSearching = True
                        elif sizeButton.rect.collidepoint(mousepos):
                            sizeButton.cycleSize()
                            gridStyle = sizeButton.getStatus()
                            tilearea.gridSurface.fill((0, 0, 0))
                            tiles = []
                            if gridStyle != 'off':
                                size = int(gridStyle.split('x')[0])
                                xTiles = math.ceil(tilearea.width / size)
                                yTiles = math.ceil(tilearea.height / size)
                                for i in range(yTiles):
                                    for j in range(xTiles):
                                        tiles.append(MapTiles((j * size, i * size), size))
                            for tile in tiles:
                                tile.draw(tilearea.gridSurface)
                        elif saveButton.rect.collidepoint(mousepos):
                            saveMap(placedTiles)
                        elif clearButton.rect.collidepoint(mousepos):
                            placedTiles = []
            elif event.button == 3:
                currentTexture = None
                currentRect = None
                if tilearea.rect.collidepoint(mousepos):
                    mousepos = (mousepos[0] - tilearea.rect.x) / tilearea.xScale, mousepos[1] / tilearea.yScale
                    for tile in placedTiles:
                        if tile.rect.collidepoint(mousepos):
                            placedTiles.remove(tile)
            elif event.button == 2:
                if tilearea.rect.collidepoint(mousepos):
                    mousepos = (mousepos[0] - tilearea.rect.x) / tilearea.xScale, mousepos[1] / tilearea.yScale
                    for tile in placedTiles:
                        if tile.rect.collidepoint(mousepos):
                            currentTexture = tile.surface.copy()
                            currentRect = loadedTextures[0].rect.copy()
        elif event.type == KEYDOWN:
            if event.key == K_RETURN:
                textureSearching = False
            elif textureSearching:
                if event.key == K_BACKSPACE:
                    backspacing = True
                    if len(textureSearchPath) > 0:
                        textureSearchPath = textureSearchPath[:len(textureSearchPath)-1]
                elif event.key == K_LSHIFT or event.key == K_RSHIFT:
                    shiftCaps = True
                elif event.key == K_CAPSLOCK:
                    allCaps = not allCaps
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
                elif event.key == K_LSHIFT or event.key == K_RSHIFT:
                    shiftCaps = True
                elif event.key == K_CAPSLOCK:
                    allCaps = not allCaps
                else:
                    #if both shitft and caps are on, the text turns small again
                    try:
                        if (shiftCaps and not allCaps) or (not shiftCaps and allCaps):
                            mapSearchPath += chr(event.key).capitalize()
                        else:
                            mapSearchPath += chr(event.key)
                    except: pass #invalid characters
        elif event.type == KEYUP:
            if textureSearching or mapSearching:
                if event.key == K_BACKSPACE:
                    backspacing = False
                elif event.key == K_LSHIFT or event.key == K_RSHIFT:
                    shiftCaps = False

    #update window ----------------------------------------------------------- #
    screen.blit(pygame.transform.scale(gui, (screen.get_width(), screen.get_height())), (0 ,0))
    pygame.display.flip()
