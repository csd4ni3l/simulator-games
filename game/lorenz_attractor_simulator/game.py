import pyglet, arcade, arcade.gui, os, json, time

from game.lorenz_attractor_simulator.shader import create_shader
from game.base import BaseGame

class Game(BaseGame):
    def __init__(self, pypresence_client):
        super().__init__(pypresence_client, "Lorenz Attractor Simulator", "lorenz_attractor_simulator", {
                "sigma": 10,
                "rho": 28,
                "beta": 2.66666666,
                "steps": 50,
                "decay_factor": 0.999,
                "speed": 1 
        })

        self.delta_time = 0
        self.should_clear = False

        self.last_update = time.perf_counter()

    def setup(self):
        self.shader_program, self.lorenz_image = create_shader(int(self.window.width * 0.8), self.window.height)

        self.image_sprite = pyglet.sprite.Sprite(self.lorenz_image)

    def on_show_view(self):
        super().on_show_view()

        self.add_setting("Sigma: {value}", 1, 50, 0.1, "sigma")
        self.add_setting("Rho: {value}", 1, 100, 0.1, "rho")
        self.add_setting("Beta: {value}", 0.1, 10, 0.01, "beta")
        self.add_setting("Steps: {value}", 50, 1000, 10, "steps")
        self.add_setting("Decay multiplier: {value}", 0.8, 1, 0.001, "decay_factor")
        self.add_setting("Speed: {value}", 0.1, 100, 0.1, "speed")

        self.setup()

    def change_value(self, label, text, settings_key, value):
        super().change_value(label, text, settings_key, value)

        self.should_clear = True

    def on_update(self, delta_time):
        if time.perf_counter() - self.last_update >= 1 / 15:
            if self.should_clear:
                self.should_clear = False
                self.delta_time = 0

                pyglet.gl.glClearTexImage(
                    self.lorenz_image.id, 0, 
                    pyglet.gl.GL_RGBA, pyglet.gl.GL_FLOAT, 
                    None
                )

            current_settings = self.settings["lorenz_attractor_simulator"]

            with self.shader_program:
                self.shader_program["sigma"] = current_settings["sigma"]
                self.shader_program["rho"] = current_settings["rho"]
                self.shader_program["beta"] = current_settings["beta"]
                self.shader_program["steps"] = int(current_settings["steps"])
                self.shader_program["dt"] = self.delta_time
                self.shader_program["resolution"] = (int(self.window.width * 0.8), self.window.height)
                self.shader_program["decay_factor"] = current_settings["decay_factor"]

                self.shader_program.dispatch(int(self.window.width * 0.8) // 32, self.window.height // 32)

                pyglet.gl.glMemoryBarrier(pyglet.gl.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)

            self.delta_time += (current_settings["speed"] * 0.00005)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE: # overwrite instead of super because deleting shader program is mandatory.
            self.shader_program.delete()

            with open("data.json", "w") as file:
                file.write(json.dumps(self.settings, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))

    def on_draw(self):
        super().on_draw()

        self.image_sprite.draw()