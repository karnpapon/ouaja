import pygame
import numpy as np
from .sprite import FXSprite
from .line import GradientLine
from .const import BG_COLOR, TEXT_COLOR

def clamp(minimum, x, maximum):
  return max(minimum, min(x, maximum))

def replace_color(surface, old_color, new_color, tolerance=0):
  """
  Replace all pixels of a given color in a Pygame surface with a new color.

  Args:
      surface (pygame.Surface): The surface to process (must have per-pixel alpha).
      old_color (tuple): The RGB color to replace, e.g., (255, 0, 0).
      new_color (tuple): The RGB color to use as replacement, e.g., (255, 255, 255).
      tolerance (int): Optional tolerance for matching the old_color. Default is 0 (exact match).

  Returns:
      pygame.Surface: A new surface with the color replaced.
  """
  # Ensure the surface has per-pixel alpha
  surface = surface.convert_alpha()

  # Copy to avoid modifying the original surface
  new_surface = surface.copy()

  # Get pixel arrays
  rgb_array = pygame.surfarray.pixels3d(new_surface)
  alpha_array = pygame.surfarray.pixels_alpha(new_surface)

  # Build match mask
  r_match = np.abs(rgb_array[:, :, 0] - old_color[0]) <= tolerance
  g_match = np.abs(rgb_array[:, :, 1] - old_color[1]) <= tolerance
  b_match = np.abs(rgb_array[:, :, 2] - old_color[2]) <= tolerance
  match_mask = r_match & g_match & b_match

  # Replace color
  rgb_array[match_mask] = new_color

  # Unlock pixel arrays
  del rgb_array
  del alpha_array

  return new_surface

def tint_surface(surface: pygame.Surface, tint_color):
  """Apply a color tint to a white image with transparency."""
  tinted = surface.copy()
  tinted.fill(tint_color, special_flags=pygame.BLEND_RGBA_MULT)
  return tinted


def slice_nine(image: pygame.Surface, tile_size):
  return {
      "tl": image.subsurface((0, 0, tile_size, tile_size)),
      "t": image.subsurface((tile_size, 0, tile_size, tile_size)),
      "tr": image.subsurface((tile_size * 2, 0, tile_size, tile_size)),
      "l": image.subsurface((0, tile_size, tile_size, tile_size)),
      "c": image.subsurface((tile_size, tile_size, tile_size, tile_size)),
      "r": image.subsurface((tile_size * 2, tile_size, tile_size, tile_size)),
      "bl": image.subsurface((0, tile_size * 2, tile_size, tile_size)),
      "b": image.subsurface((tile_size, tile_size * 2, tile_size, tile_size)),
      "br": image.subsurface((tile_size * 2, tile_size * 2, tile_size, tile_size)),
  }

def draw_nine_slice_scaled(slices, surface: pygame.Surface, rect, tile_size, scale):
  x, y, w, h = rect
  s = tile_size * scale

  # Corners
  surface.blit(pygame.transform.scale(slices["tl"], (s, s)), (x, y))
  surface.blit(pygame.transform.scale(slices["tr"], (s, s)), (x + w - s, y))
  surface.blit(pygame.transform.scale(slices["bl"], (s, s)), (x, y + h - s))
  surface.blit(pygame.transform.scale(
      slices["br"], (s, s)), (x + w - s, y + h - s))

  # Top/Bottom
  for i in range(x + s, x + w - s, s):
    surface.blit(pygame.transform.scale(slices["t"], (s, s)), (i, y))
    surface.blit(pygame.transform.scale(slices["b"], (s, s)), (i, y + h - s))

  # Left/Right
  for j in range(y + s, y + h - s, s):
    surface.blit(pygame.transform.scale(slices["l"], (s, s)), (x, j))
    surface.blit(pygame.transform.scale(slices["r"], (s, s)), (x + w - s, j))

  # Center
  for i in range(x + s, x + w - s, s):
    for j in range(y + s, y + h - s, s):
      surface.blit(pygame.transform.scale(slices["c"], (s, s)), (i, j))

def wrap_text(text, font, max_width):
  words = text.split(" ")
  lines = []
  current_line = ""

  for word in words:
    test_line = current_line + word + " "
    if font.size(test_line)[0] <= max_width:
      current_line = test_line
    else:
      lines.append(current_line.strip())
      current_line = word + " "
  if current_line:
    lines.append(current_line.strip())

  return lines


def draw_text(surface, text, color, rect, font, aa=False, bkg=None):
  """
  draw some text into an area of a surface
  automatically wraps words
  returns any text that didn't get blitted
  https://www.pygame.org/wiki/TextWrap
  """
  rect = pygame.Rect(rect)
  y = rect.top
  lineSpacing = -2

  # get the height of the font
  fontHeight = font.size("Tg")[1]

  while text:
    i = 1

    # determine if the row of text will be outside our area
    if y + fontHeight > rect.bottom:
      break

    # determine maximum width of line
    while font.size(text[:i])[0] < rect.width and i < len(text):
      i += 1

    # if we've wrapped the text, then adjust the wrap to the last word
    if i < len(text):
      i = text.rfind(" ", 0, i) + 1

    # render the line and blit it to the surface
    if bkg:
      image = font.render(text[:i], 1, color, bkg)
      image.set_colorkey(bkg)
    else:
      image = font.render(text[:i], aa, color)

    surface.blit(image, (rect.left, y))
    y += fontHeight + lineSpacing

    # remove the text we just blitted
    text = text[i:]

  return text

def get_font(size):
  return pygame.font.Font("assets/fonts/NicerNightie.ttf", size)

def draw_border(screen: pygame.Surface, tile, screen_width, screen_height, tile_size):
  # Top and Bottom
  for x in range(0, screen_width, tile_size):
    screen.blit(tile, (x, 0))  # Top
    screen.blit(tile, (x, screen_height - tile_size))  # Bottom

  # Left and Right
  for y in range(0, screen_height, tile_size):
    screen.blit(tile, (0, y))  # Left
    screen.blit(tile, (screen_width - tile_size, y))  # Right

def get_center_position(surface: pygame.Surface, screen_size: tuple[int]):
  surface_rect = surface.get_rect()
  return (
      (surface_rect.width - screen_size[0]) // 2,
      (surface_rect.height - screen_size[1]) // 2
  )

def blend_color(start_color, end_color, t):
  return tuple(int(start + (end - start) * t) for start, end in zip(start_color, end_color))

def draw_line_with_signal(sc: pygame.Surface, start, end, progress, sprite: FXSprite, target_offset_pos):
  # pygame.draw.line(sc, (255, 255, 255), start, end + target_offset_pos, 4)
  if not sprite: 
    return
  if 0 <= progress <= 1:
    x = start[0] + (end[0] - start[0]) * progress
    y = start[1] + (end[1] - start[1]) * progress
    # sprite.position = (int(x - (sprite.image.get_width()/2 ) - 5), int(y - (sprite.image.get_height()/2 ) - 5))
    # pygame.draw.circle(sc, (255, 255, 255), (int(x), int(y)), 8)
    sc.blit(sprite.image, (int(x - (sprite.image.get_width()/2 )), int(y - (sprite.image.get_height()/2 ))))

def is_leave_node(node):
  return (len(node["right_nodes"]) == 0 or len(node["left_nodes"]) == 0)