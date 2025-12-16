from VertexEngine.scenes import Scene

class PhysicsObject:
    def __init__(self, x, y, width, height, mass=1, solid=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mass = mass
        self.solid = solid
        self.on_ground = False

    def apply_force(self, fx, fy):
        self.ax = fx / self.mass
        self.ay = fy / self.mass

    def update(self, dt, world_width, world_height):
        self.vx += self.ax * dt
        self.vy += self.ay * dt

        self.ax = 0
        self.ay = 0

        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.solid:
            if self.x < 0:
                self.x = 0
                self.vx *= -0.5
            elif self.x + self.width > world_width:
                self.x = world_width - self.width
                self.vx *= -0.5

            if self.y < 0:
                self.y = 0
                self.yx *= -0.5
            elif self.y + self.height > world_height:
                self.y = world_height - self.height
                self.vy *= -0.5
                self.on_ground = True
            else:
                self.on_ground = False