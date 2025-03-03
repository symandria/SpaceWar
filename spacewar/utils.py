"""
Utility functions for SpaceWar
"""
import pygame

def hex_to_coords(row, column):
    """
    Convert hex grid coordinates to screen coordinates
    
    Args:
        row: Hex grid row
        column: Hex grid column
        
    Returns:
        tuple: (x, y) screen coordinates
    """
    return (14*column + ((row-1) % 2)*7 - 9, 8+10*row)


def coords_to_hex(pos):
    """
    Convert screen coordinates to hex grid coordinates
    
    Args:
        pos: (x, y) screen coordinates
        
    Returns:
        tuple: (row, column) hex grid coordinates or None if invalid
    """
    if pos[0] < 2 or pos[1] < 17 or pos[0] > 155 or pos[1] > 156:
        return None
    elif pos[0] < 9 and (pos[1] - 17) % 20 >= 10:
        return None
    elif (pos[1] - 17) % 20 < 10:
        return (pos[1] - 17) // 10 + 1, (pos[0] - 2) // 14 + 1
    else:
        return (pos[1] - 17) // 10 + 1, (pos[0] - 9) // 14 + 1


def hex_distance(hex1, hex2):
    """
    Calculate distance between two hex grid coordinates
    
    Args:
        hex1: First hex coordinates (row, column)
        hex2: Second hex coordinates (row, column)
        
    Returns:
        int: Distance in hex grid units
    """
    hex1 = hex1[0], hex1[1] - (hex1[0] + 1) // 2
    hex1 += 0 - hex1[0] - hex1[1],
    hex2 = hex2[0], hex2[1] - (hex2[0] + 1) // 2
    hex2 += 0 - hex2[0] - hex2[1],
    return max(abs(hex1[0] - hex2[0]), abs(hex1[1] - hex2[1]), abs(hex1[2] - hex2[2]))


def wordwrap_render(text, font, width, foreground=(0, 0, 0), background=(255, 255, 255)):
    """
    Render text with word wrapping
    
    Args:
        text: Text to render
        font: Font to use
        width: Maximum width in pixels
        foreground: Text color (default: black)
        background: Background color (default: white)
        
    Returns:
        pygame.Surface: Rendered text surface
    """
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
        elif temp.startswith("\$"):
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
            text.insert(line+1, ("$" if center else "") + " ".join(temp_words[result:]))
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