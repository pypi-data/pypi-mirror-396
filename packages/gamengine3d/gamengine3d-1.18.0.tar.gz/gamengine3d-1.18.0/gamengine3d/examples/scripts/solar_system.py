from gamengine3d import *

class Planet:
    def __init__(self, context: Context, color, radius, pos, mass, name, initial_vel):
        self.context = context
        self.color = color
        self.radius = radius
        self.pos = pos
        self.velocity = initial_vel
        self.mass = mass
        self.name = name

    def draw(self):
        self.context.functions.draw_sphere(pos=self.pos, radius=self.radius, color=self.color)

    def update(self, dt, planets):
        for planet in planets:
            if planet.name != self.name:
                sqr_dst = (self.pos - planet.pos).sqr_magnitude
                force_dir = (planet.pos - self.pos).normalized
                force = force_dir * planet.mass * self.mass / sqr_dst
                acceleration = force / self.mass
                self.velocity += acceleration * dt

        self.pos += self.velocity * dt

class SolarSystem:
    def __init__(self, obj: Engine, context: Context):
        self.engine = obj
        self.context = context
        self.planets = [Planet(self.context, Color.light_yellow, 2, vector3d.zero, 50, "Sun", vector3d.zero),
                        Planet(self.context, Color.light_grey, .06, vector3d(-17, 0, 0), .07, "Moon", vector3d(0, 0, -3.5)),
                        Planet(self.context, Color.light_blue, .2, vector3d(-15, 0, 0), 5, "Earth", vector3d(0, 0, -2))]


    def update(self, dt):
        for planet in self.planets:
            planet.update(dt, self.planets)
            planet.draw()
