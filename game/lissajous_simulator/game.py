import pyglet, arcade, arcade.gui, os, json

from game.lissajous_simulator.shader import create_shader
from game.base import BaseGame

class Game(BaseGame):
    def __init__(self, pypresence_client):
        super().__init__(pypresence_client, "Lissajous Simulator", "lissajous_simulator", {
                "amplitude_x": 0.8,
                "amplitude_y": 0.8,
                "frequency_x": 3.0,
                "frequency_y": 2.0,
                "thickness": 0.005,
                "samples": 50,
                "phase_shift": 6.283
        })

        self.time = 0

    def on_show_view(self):
        super().on_show_view()

        self.add_setting("X Amplitude: {value}", 0, 1.5, 0.1, "amplitude_x")
        self.add_setting("Y Amplitude: {value}", 0, 1.5, 0.1, "amplitude_y")
        
        self.add_setting("X Frequency: {value}", 1, 10, 1, "frequency_x")
        self.add_setting("Y Frequency: {value}", 1, 10, 1, "frequency_y")

        self.add_setting("Phase Shift: {value}", 0, 6.283, 0.001, "phase_shift")

        self.add_setting("Thickness: {value}", 0.001, 0.05, 0.001, "thickness")
        self.add_setting("Samples: {value}", 1, 1000, 25, "samples")

        self.setup()

    def setup(self):
        self.shader_program, self.lissajous_image = create_shader(int(self.window.width * 0.8), self.window.height)

        self.image_sprite = pyglet.sprite.Sprite(img=self.lissajous_image)

    def on_update(self, delta_time):
        self.time += delta_time

        current_settings = self.settings["lissajous_simulator"]

        with self.shader_program:
            self.shader_program["x_amp"] = current_settings["amplitude_x"]
            self.shader_program["y_amp"] = current_settings["amplitude_y"]
            
            self.shader_program["x_freq"] = current_settings["frequency_x"]
            self.shader_program["y_freq"] = current_settings["frequency_y"]

            self.shader_program["thickness"] = current_settings["thickness"]
            self.shader_program["samples"] = int(current_settings["samples"])
            self.shader_program["phase_shift"] = current_settings["phase_shift"]

            self.shader_program["resolution"] = (int(self.window.width * 0.8), self.window.height)

            self.shader_program["time"] = self.time

            self.shader_program.dispatch(int(self.lissajous_image.width / 32), int(self.lissajous_image.height / 32), 1)
    
    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE: # overwrite and no super because shader program needs to be deleted.
            self.shader_program.delete()

            with open("data.json", "w") as file:
                file.write(json.dumps(self.settings, indent=4))

            from menus.main import Main

            self.window.show_view(Main(self.pypresence_client))

    def on_draw(self):
        super().on_draw()

        self.image_sprite.draw()