import pygame
import data

class GobjectGroup(pygame.sprite.RenderPlain):
    def __init__(self, sprite=None):
        if sprite is not None:
            pygame.sprite.RenderPlain.__init__(self, sprite)
        else:
            pygame.sprite.RenderPlain.__init__(self)

    def draw_to_mask(self, surface):
        for sprite in self.sprites():
            if not sprite.clicked and sprite.rect.top > 50 and sprite.moved_once:
                surface.blit(sprite.image, sprite.rect.topleft, ((0, 0), (sprite.rect.size)))

    def handle_click(self, dragging):
        for sprite in self.sprites():
            sprite.handle_click(pygame.mouse.get_pos(), dragging)
            if sprite.clicked:
                break
