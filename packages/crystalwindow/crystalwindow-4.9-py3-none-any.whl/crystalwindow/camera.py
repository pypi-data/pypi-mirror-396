class Camera:
    def __init__(self, target, speed=0.1):
        self.target = target  # sprite or obj w/ x,y
        self.offset_x = 0
        self.offset_y = 0
        self.speed = speed  # smoothness

    def update(self, win_width, win_height):
        # camera aims for target center
        target_x = self.target.x - win_width // 2
        target_y = self.target.y - win_height // 2

        # smooth lerp follow
        self.offset_x += (target_x - self.offset_x) * self.speed
        self.offset_y += (target_y - self.offset_y) * self.speed

    def apply(self, obj):
        # shift object's draw position by camera offset
        return obj.x - self.offset_x, obj.y - self.offset_y
