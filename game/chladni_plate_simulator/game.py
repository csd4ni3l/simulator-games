import pyglet, arcade, arcade.gui, os, json, numpy as np

from game.chladni_plate_simulator.shader import create_shader
from game.base import BaseGame

from utils.preload import button_texture, button_hovered_texture
from utils.constants import button_style

class Game(BaseGame):
    def __init__(self, pypresence_client):
        super().__init__(pypresence_client, "Chladni Plate Simulator", "chladni_plate_simulator", {
                "k": 0.1
        })

        self.sources = np.empty((0, 2), dtype=np.float32)
        
        self.dragged_source = None
        self.needs_redraw = False

    def change_value(self, label, text, settings_key, value):
        super().change_value(label, text, settings_key, value)

        self.needs_redraw = True

    def on_update(self, delta_time):
        if self.needs_redraw:
            self.needs_redraw = False

            self.sources_ssbo.set_data(self.sources.tobytes())

            with self.shader_program:
                self.shader_program["source_count"] = len(self.sources)
                self.shader_program["k"] = self.settings["chladni_plate_simulator"]["k"]
                self.shader_program.dispatch(int(self.plate_image.width / 32), int(self.plate_image.height / 32), 1)

    def setup(self):
        self.shader_program, self.plate_image, self.sources_ssbo = create_shader(int(self.window.width * 0.8), self.window.height)

        self.image_sprite = pyglet.sprite.Sprite(img=self.plate_image)
        
    def add_source(self):
        self.sources = np.vstack([self.sources, [self.window.width * 0.4, self.window.height / 2]]).astype(np.float32)

        self.needs_redraw = True
        
    def on_mouse_press(self, x, y, button, modifiers):
        if not self.dragged_source:
            for i, source in enumerate(self.sources.reshape(-1, 2)):
                if arcade.math.Vec2(x, y).distance(arcade.math.Vec2(*source)) <= 10:
                    self.dragged_source = i
                    break

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        if self.dragged_source is not None:
            self.sources[self.dragged_source] = [x, y]

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragged_source = None
        self.needs_redraw = True

    def on_show_view(self):
        super().on_show_view()

        self.add_setting("k: {value}", 0.02, 0.5, 0.01, "k")

        self.add_source_button = self.settings_box.add(arcade.gui.UITextureButton(text="Add source", texture=button_texture, texture_hovered=button_hovered_texture, style=button_style, width=self.window.width * 0.2))
        self.add_source_button.on_click = lambda event: self.add_source()

        self.setup()

    def on_key_press(self, symbol, modifiers):
        super().on_key_press(symbol, modifiers)
        
        if symbol == arcade.key.C:
            del self.sources
            self.sources = np.empty((0, 2), dtype=np.float32)

            self.needs_redraw = True

    def on_draw(self):
        super().on_draw()

        self.image_sprite.draw()

        for item in self.sources.reshape(-1, 2):
            arcade.draw_circle_filled(item[0], item[1], 10, arcade.color.GRAY)