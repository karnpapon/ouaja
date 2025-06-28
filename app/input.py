import pygame

class Keyboard:
  def __init__(self):
    self.current_key_states = None
    self.previous_key_states = None

  def process_input(self):
    self.previous_key_states = self.current_key_states
    self.current_key_states = pygame.key.get_pressed()

  def is_key_down(self, keyCode):
    if self.current_key_states is None or self.previous_key_states is None:
      return False
    return self.current_key_states[keyCode] == True

  def is_key_pressed(self, keyCode):
    if self.current_key_states is None or self.previous_key_states is None:
      return False
    return self.current_key_states[keyCode] == True and self.previous_key_states[keyCode] == False

  def is_key_released(self, keyCode):
    if self.current_key_states is None or self.previous_key_states is None:
      return False
    return self.current_key_states[keyCode] == False and self.previous_key_states[keyCode] == True

class InputStream:
  def __init__(self):
    self.keyboard = Keyboard()

  def process_input(self):
    self.keyboard.process_input()
