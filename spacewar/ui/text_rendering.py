import pygame


def wordwrap_render(text, font, width, foreground, background):
    surfaces = []
    text = text.split("\n")
    line = 0
    final_width = 0
    final_height = 0
    while line < len(text):
        center = False
        temp = text[line]
        if temp.startswith("$"):
            center = True
            temp = temp[1:]
        elif temp.startswith("\\$"):
            temp = temp[1:]
        temp_words = temp.split(" ")
        result = 1
        cur = " ".join(temp_words[:result])
        while "\t" in cur:
            idx = cur.index("\t")
            spaces = " " * (8 - idx % 8)
            cur = spaces.join(cur.partition("\t")[::2])
        temp_surf = font.render(cur, True, foreground)
        while temp_surf.get_width() < width and result < len(temp_words):
            result += 1
            cur = " ".join(temp_words[:result])
            while "\t" in cur:
                idx = cur.index("\t")
                spaces = " " * (8 - idx % 8)
                cur = spaces.join(cur.partition("\t")[::2])
            temp_surf = font.render(cur, True, foreground)
        if temp_surf.get_width() >= width:
            result -= 1
            cur = " ".join(temp_words[:result])
            while "\t" in cur:
                idx = cur.index("\t")
                spaces = " " * (8 - idx % 8)
                cur = spaces.join(cur.partition("\t")[::2])
            temp_surf = font.render(cur, True, foreground)
            text.insert(line + 1, ("$" if center else "") + " ".join(temp_words[result:]))
        surfaces.append((temp_surf, center))
        if temp_surf.get_width() > final_width:
            final_width = temp_surf.get_width()
        final_height += temp_surf.get_height()
        line += 1
    final_surf = pygame.Surface((final_width, final_height))
    final_surf.fill(background)
    final_surf.set_colorkey(background)
    y = 0
    for surf, center in surfaces:
        if center:
            rect = surf.get_rect()
            rect.top = y
            rect.centerx = final_width // 2
            final_surf.blit(surf, rect)
        else:
            final_surf.blit(surf, (0, y))
        y += surf.get_height()
    return final_surf


def render_button(text, font, foreground, background):
    text_surf = font.render(text, True, foreground)
    frame = pygame.Surface((text_surf.get_width() + 4, text_surf.get_height() + 4))
    rect = frame.get_rect()
    frame.fill(background)
    pygame.draw.rect(frame, foreground, rect, 1)
    frame.blit(text_surf, (2, 2))
    return frame, rect
