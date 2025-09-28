import arcade, random

from game.boid_simulator.boid import Boid
from game.base import BaseGame

class Game(BaseGame):
    def __init__(self, pypresence_client):
        super().__init__(pypresence_client, "Boid Simulator", "boid_simulator", {
                "w_separation": 1.0,
                "w_alignment": 1.0,
                "w_cohesion": 1.0,
                "small_radius": 100,
                "large_radius": 250
        })

        self.current_boid_num = 1
        self.boid_sprites = arcade.SpriteList()

        self.add_setting("Separation Weight: {value}", 0.1, 5, 0.1, "w_separation")
        self.add_setting("Alignment Weight: {value}", 0.1, 5, 0.1, "w_alignment")
        self.add_setting("Cohesion Weight: {value}", 0.1, 5, 0.1, "w_cohesion")
        self.add_setting("Small Radius: {value}", 25, 250, 25, "small_radius")
        self.add_setting("Large Radius: {value}", 50, 500, 50, "large_radius")

    def change_value(self, label, text, boid_variable, value):
        super().change_value(label, text, boid_variable, value)
  
        for boid in self.boid_sprites:
            setattr(boid, boid_variable, value)

    def create_boid(self, x, y):
        boid = Boid(self.current_boid_num, x, y)
        
        boid.w_alignment = self.settings["boid_simulator"]["w_alignment"]
        boid.w_separation = self.settings["boid_simulator"]["w_separation"]
        boid.w_cohesion = self.settings["boid_simulator"]["w_cohesion"]
        boid.large_radius = self.settings["boid_simulator"]["large_radius"]
        boid.small_radius = self.settings["boid_simulator"]["small_radius"]

        self.boid_sprites.append(boid)
        self.current_boid_num += 1

    def setup_boids(self):
        for i in range(25):
            self.create_boid(random.randint(self.window.width / 2 - 150, self.window.width / 2), random.randint(self.window.height / 2 - 150, self.window.height / 2))

    def on_show_view(self):
        super().on_show_view()
        self.setup_boids()

    def on_update(self, delta_time):
        boid_directions = [(boid.boid_num, boid.direction, arcade.math.Vec2(*boid.position)) for boid in self.boid_sprites]
        for boid in self.boid_sprites:
            boid.update(self.window.width, self.window.height, boid_directions)

        if self.window.mouse[arcade.MOUSE_BUTTON_LEFT]:
            self.create_boid(self.window.mouse.data["x"], self.window.mouse.data["y"])

    def on_draw(self):
        super().on_draw()
        self.boid_sprites.draw()