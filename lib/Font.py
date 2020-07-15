import pygame

def clip(surf, x, y, width, height):
    handleSurf = surf.copy()
    clipR = pygame.Rect(x, y, width, height)
    handleSurf.set_clip(clipR)
    image = surf.subsurface(handleSurf.get_clip())
    return image.copy()

class Font:
    def __init__(self, fontFilePath):
        fontSheet = pygame.image.load(fontFilePath).convert()
        chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p',
        'q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H',
        'I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
        '1','2','3','4','5','6','7','8','9','0','!','@','#','%','^','(',')','-',
        '_','+','=','[',']','{','}','/',':',';',"'",'"','.',',','<','>','?']
        self.characters = {}
        width = 0
        charIndex = 0
        for i in range(fontSheet.get_width()):
            if charIndex < len(chars):
                if fontSheet.get_at((i, 0)) == (255, 0, 0, 255):
                    charImg = clip(fontSheet, i - width, 0, width, fontSheet.get_height())
                    self.characters[chars[charIndex]] = charImg.copy()
                    charIndex += 1
                    width = 0
                else:
                    width += 1
        self.spaceWidth = self.characters['a'].get_width()
        self.spacing = 1
        for ele in self.characters:
            self.characters[ele].set_colorkey((0, 0, 0))


    def render(self, surf, text, loc, scale=1):
        """
        PARAMS: surf: surface to blit to, text: text being rendered,
        loc: top left coords of where to start blitting
        """
        xOff = 0
        for char in text:
            if char != ' ':
                surf.blit(pygame.transform.scale(self.characters[char], (int(self.characters[char].get_width()*scale), int(self.characters[char].get_height()*scale))), (loc[0] + xOff, loc[1]))
                xOff += int((self.characters[char].get_width() + self.spacing)*scale)
            else:
                xOff += int((self.spaceWidth + self.spacing)*scale)

    def size(self, text, scale=1):
        width = 0
        height = 0
        if text[0] != ' ':
            height = pygame.transform.scale(self.characters[text[0]], (int(self.characters[text[0]].get_width()*scale), int(self.characters[text[0]].get_height()*scale))).get_height()
        for char in text:
            if char != ' ':
                width += pygame.transform.scale(self.characters[char], (int(self.characters[char].get_width()*scale), int(self.characters[char].get_height()*scale))).get_width() + int(self.spacing*scale)
                height = max(pygame.transform.scale(self.characters[char], (int(self.characters[char].get_width()*scale), int(self.characters[char].get_height()*scale))).get_height(), height)
            else:
                width += int((self.spaceWidth + self.spacing)*scale)
        return width, height
