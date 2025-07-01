import pygame

def clamp(point):
  """ Ensure the point is inside the window """
  x, y = point
  x = max(0, x)
  x = min(pygame.display.get_window_size()[0]-1, x)
  y = max(0, y)
  y = min(pygame.display.get_window_size()[1]-1, y)
  return x, y


def getLinePath(start_pos, end_pos):
  """ Using Bresenham's Line algorithm, get a list of all the points
      along a straight-line path from the start to the end (inclusive).
      Note that this includes diagonal movement """

  # clamp range to window
  x0, y0 = clamp(start_pos)
  x1, y1 = clamp(end_pos)
  points = []

  # ref: https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm#Algorithm_for_integer_arithmetic
  dx = abs(x1 - x0)
  if x0 < x1:
    sx = 1
  else:
    sx = -1
  dy = -abs(y1 - y0)
  if y0 < y1:
    sy = 1
  else:
    sy = -1
  error = dx + dy

  while True:
    points.append((x0, y0))
    if x0 == x1 and y0 == y1:
      break
    e2 = 2 * error
    if e2 >= dy:
      if x0 == x1:
        break
      error = error + dy
      x0 = x0 + sx
    if e2 <= dx:
      if y0 == y1:
        break
      error = error + dx
      y0 = y0 + sy

  return points


class GradientLine:
  def __init__(self, start_point, end_point, start_colour, end_colour, thickness: int = 1):
    self.lines = []
    self.width = thickness

    line_pixels = getLinePath(start_point, end_point)
    pixel_count = float(len(line_pixels))
    red_step = float(end_colour[0] - start_colour[0]) / pixel_count
    green_step = float(end_colour[1] - start_colour[1]) / pixel_count
    blue_step = float(end_colour[2] - start_colour[2]) / pixel_count

    red = float(start_colour[0])
    green = float(start_colour[1])
    blue = float(start_colour[2])

    # It is too inefficient to continually draw a huge whack of pixels
    # So Identify a bunch of line-segments that are the same colour
    start_point = None
    for pixel in line_pixels:
      if (start_point == None):
        start_point = pixel
        start_red, start_green, start_blue = (red, green, blue)
      else:
        # calculate the next colour
        # if that colour significantly different, output a line segment
        if (abs(start_red - red) > 1.0 or
            abs(start_green - green) > 1.0 or
                abs(start_blue - blue) > 1.0):
          colour = (int(start_red), int(start_green), int(start_blue))
          self.lines.append((start_point, pixel, colour))
          start_point = None

      # crawl the gradient
      red += red_step
      green += green_step
      blue += blue_step

  def draw(self, surface: pygame.Surface):
    """ Draw a line from start to end, changing colour along the way """
    for segment in self.lines:
      point_a, point_b, colour = segment
      pygame.draw.line(surface, colour, point_a, point_b, self.width)
