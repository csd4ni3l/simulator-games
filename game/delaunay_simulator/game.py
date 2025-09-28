import arcade, arcade.gui, numpy as np, random, math

from scipy.spatial import Delaunay

from game.base import BaseGame

from utils.constants import button_style
from utils.preload import button_texture, button_hovered_texture

class Game(BaseGame):
    def __init__(self, pypresence_client):
        super().__init__(pypresence_client, "Delaunay Triangulation", "delaunay_simulator", {})

        self.points = []

        [self.add_point() for _ in range(4)]
        
        self.fixed_points = [(0, 0), (0, self.window.height), (self.window.width * 0.8, 0), (self.window.width * 0.8, self.window.height)]

        self.triangles = None
        self.dragged_point = None

        self.needs_recalc = True

    def fract(self, x):
        return x - math.floor(x)

    def hash3(self, p: float) -> arcade.math.Vec3:
        p3 = arcade.math.Vec3(p * 127.1, p * 311.7, p * 74.7)
        return arcade.math.Vec3(
            int(self.fract(math.sin(p3.x) * 43758.5453123) * 255),
            int(self.fract(math.sin(p3.y) * 43758.5453123) * 255),
            int(self.fract(math.sin(p3.z) * 43758.5453123) * 255)
        )
    
    def on_show_view(self):
        super().on_show_view()

        self.add_point_button = self.settings_box.add(arcade.gui.UITextureButton(width=self.window.width * 0.2, text="Add Point", texture=button_texture, texture_hovered=button_hovered_texture, style=button_style))
        self.add_point_button.on_click = lambda event: self.add_point()

    def change_value(self, label, text, settings_key, value):
        super().change_value(label, text, settings_key, value)

        self.needs_recalc = True

    def add_point(self):
        self.points.append((random.randint(0, (self.window.width * 0.8)), random.randint(0, self.window.height - 0)))

        self.needs_recalc = True

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.dragged_point:
            for i, point in enumerate(self.points):
                if arcade.math.Vec2(x, y).distance(arcade.math.Vec2(*point)) <= 10:
                    self.dragged_point = i
                    break

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        if self.dragged_point is not None:
            self.points[self.dragged_point] = [x, y]
            self.needs_recalc = True

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragged_point = None
        self.needs_recalc = True

    def on_draw(self):
        super().on_draw()

        if self.triangles is not None:
            for n, simplex in enumerate(self.triangles):
                points = self.points + self.fixed_points
                p1 = points[simplex[0]]
                p2 = points[simplex[1]]
                p3 = points[simplex[2]]

                arcade.draw_triangle_filled(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], self.hash3(n))

        for point in self.points + self.fixed_points:
            arcade.draw_circle_filled(point[0] + 5, point[1] + 5, 10, arcade.color.GRAY)

    def on_update(self, delta_time):
        if self.needs_recalc:
            self.needs_recalc = False

            self.triangles = Delaunay(np.array(self.points + self.fixed_points)).simplices