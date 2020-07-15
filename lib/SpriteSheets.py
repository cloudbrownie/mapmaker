import pygame

def loadTextures(tileSheetPath, colorkey=None):
    """
    loads the textures in a list.
    """
    try:
        tileSheet = pygame.image.load(tileSheetPath)
        tiles = []
        for i in range(tileSheet.get_height()):
            for j in range(tileSheet.get_width()):
                if tileSheet.get_at((j, i)) == (255, 255, 255, 255):
                    xStop, yStop = 0, 0
                    for x in range(j, tileSheet.get_width()):
                        if xStop == 0:
                            if tileSheet.get_at((x, i)) == (0, 255, 0, 255): xStop = x
                    for y in range(i, tileSheet.get_height()):
                        if yStop == 0:
                            if tileSheet.get_at((xStop, y)) == (255, 0, 0, 255): yStop = y
                    tile = pygame.Surface((xStop - (j + 1), yStop - i))
                    tile.blit(tileSheet, (0, 0), (j + 1, i, xStop - j, yStop - i))
                    if colorkey != None:
                        tile.set_colorkey(colorkey)
                    tiles.append(tile)
        return tiles
    except:
        return None

def loadTextureTypes(tileSheetPath, types, colorkey=None):
    """
    loads the textures with each line being a different set of textures.
    can be used for animation, as tiles are in a dict.
    """
    try:
        tileSheet = pygame.image.load(tileSheetPath)
        tiles = {}
        typeIndex = 0
        for i in range(tileSheet.get_height()):
            if tileSheet.get_at((0, i)) == (255, 255, 255, 255):
                tiles[types[typeIndex]] = []
                typeIndex += 1
            for j in range(tileSheet.get_width()):
                if tileSheet.get_at((j, i)) == (255, 255, 255, 255):
                    xStop, yStop = 0, 0
                    for x in range(j, tileSheet.get_width()):
                        if xStop == 0:
                            if tileSheet.get_at((x, i)) == (0, 255, 0, 255): xStop = x
                    for y in range(i, tileSheet.get_height()):
                        if yStop == 0:
                            if tileSheet.get_at((xStop, y)) == (255, 0, 0, 255): yStop = y
                    tile = pygame.Surface((xStop - (j + 1), yStop - i))
                    tile.blit(tileSheet, (0, 0), (j + 1, i, xStop - j, yStop - i))
                    if colorkey != None:
                        tile.set_colorkey(colorkey)
                    tiles[types[typeIndex - 1]].append(tile)
        return tiles
    except:
        return None

def reverseTextures(textures):
    modified = []
    for texture in textures:
        modified.append(pygame.transform.flip(texture, True, False))
    return modified
