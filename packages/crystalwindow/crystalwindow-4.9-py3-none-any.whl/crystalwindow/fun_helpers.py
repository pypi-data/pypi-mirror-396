import random

# random color helpers
def random_color():
    return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

def random_palette(n=5):
    return [random_color() for _ in range(n)]

# random name generator
def random_name():
    syllables = ["ka","zi","lo","ra","mi","to","na","ve"]
    return "".join(random.choice(syllables) for _ in range(3))

#Choose a random number
def random_number(min_val, max_val):
    return random.randint(min_val, max_val)

# tween helper
def lerp(a, b, t):
    return a + (b - a) * t

# debug overlay
class DebugOverlay:
    def __init__(self):
        self.active = True

    def draw(self, win, fps=60):
        if self.active:
            win.draw_text(f"FPS: {fps}", pos=(10,10))
            mx,my = win.mouse_pos
            win.draw_text(f"Mouse: {mx},{my}", pos=(10,30))
