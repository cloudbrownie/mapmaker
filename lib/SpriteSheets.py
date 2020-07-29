import pygame

def loadTextures(tileSheetPath, colorkey=None):
    try:
        tilesheet = pygame.image.load(tileSheetPath)
        tiles = []
        for i in range(tilesheet.get_height()):
            if tilesheet.get_at((0, i)) == (255, 0, 0, 255): # look for the red dots that indicate new rows
                row = []
                for j in range(tilesheet.get_width()):
                    if tilesheet.get_at((j, i)) == (255, 255, 255, 255): # look for the white dots that indicate new tetxures
                        width = 0
                        height = 0
                        for x in range(j, tilesheet.get_width()): # go right of the white dot
                            if tilesheet.get_at((x, i)) == (0, 255, 0, 255) and width == 0:
                                width = x - j - 1
                        for y in range(i, tilesheet.get_height()): # go down of the white dot
                            if tilesheet.get_at((j, y)) == (0, 255, 0, 255) and height == 0:
                                height = y - i - 1
                        texture = pygame.Surface((width, height))
                        texture.blit(tilesheet, (0, 0), (j + 1, i + 1, width, height))
                        if colorkey:
                            texture.set_colorkey(colorkey)
                        row.append(texture.copy())
                tiles.append(row)
        return tiles
    except Exception as e:
        print(e)


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
                            if tileSheet.get_at((xStop, y)) == (0, 255, 0, 255): yStop = y
                    tile = pygame.Surface((xStop - (j + 1), yStop - i))
                    tile.blit(tileSheet, (0, 0), (j + 1, i, xStop - j, yStop - i))
                    if colorkey != None:
                        tile.set_colorkey(colorkey)
                    tiles[types[typeIndex - 1]].append(tile)
        return tiles
    except Exception as e:
        print(e)
        return None

def reverseTextures(textures):
    modified = []
    for texture in textures:
        modified.append(pygame.transform.flip(texture, True, False))
    return modified
