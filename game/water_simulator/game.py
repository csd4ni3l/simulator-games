import arcade, arcade.gui, pyglet.gl, array, random, os, json

from utils.constants import WATER_ROWS, WATER_COLS

from game.water_simulator.shader import create_shader
from game.base import BaseGame

class Game(BaseGame):
    def __init__(self, pypresence_client):
        super().__init__(pypresence_client, "Water Simulator", "water_simulator", {
                "splash_strength": 0.1,
                "splash_radius": 3,
                "wave_speed": 1,
                "damping": 0.02
        })
        
        self.splash_row = 0
        self.splash_col = 0
        self.current_splash_strength = 0
        
        self.splash_strength = self.settings["water_simulator"].get("splash_strength", 0.1)
        self.splash_radius = self.settings["water_simulator"].get("splash_radius", 3)
        
        self.wave_speed = self.settings["water_simulator"].get("wave_speed", 1)
        self.damping = self.settings["water_simulator"].get("damping", 0.02)

    def on_show_view(self):
        super().on_show_view()

        self.add_setting("Splash Strength: {value}", 0.1, 2.0, 0.1, "splash_strength")
        self.add_setting("Splash Radius: {value}", 0.5, 10, 0.5, "splash_radius")

        self.settings_box.add(arcade.gui.UISpace(height=self.window.height / 50))

        self.advanced_label = self.settings_box.add(arcade.gui.UILabel("Advanced Settings", font_size=18, multiline=True))

        self.settings_box.add(arcade.gui.UISpace(height=self.window.height / 75))

        self.add_setting("Wave Speed: {value}", 0.1, 1.25, 0.05, "wave_speed")
        self.add_setting("Damping: {value}", 0.005, 0.05, 0.001, "damping")
        self.setup_game()

    def on_update(self, delta_time):
        with self.shader_program:
            self.shader_program["rows"] = WATER_ROWS
            self.shader_program["cols"] = WATER_COLS
            
            self.shader_program["splash_row"] = self.splash_row
            self.shader_program["splash_col"] = self.splash_col
            self.shader_program["splash_strength"] = self.current_splash_strength
            self.shader_program["splash_radius"] = self.splash_radius

            self.shader_program["wave_speed"] = self.wave_speed
            self.shader_program["damping"] = self.damping
            
            self.shader_program.dispatch(self.water_image.width, self.water_image.height, 1, barrier=pyglet.gl.GL_ALL_BARRIER_BITS)

        self.current_splash_strength = 0

    def setup_game(self):
        self.shader_program, self.water_image, self.previous_heights_ssbo, self.current_heights_ssbo = create_shader() 

        self.image_sprite = pyglet.sprite.Sprite(img=self.water_image)

        scale_x = (self.window.width * 0.8) / self.image_sprite.width
        scale_y = self.window.height / self.image_sprite.height

        self.image_sprite.scale_x = scale_x
        self.image_sprite.scale_y = scale_y

        grid = array.array('f', [random.uniform(-0.1, 0.1) for _ in range(WATER_ROWS * WATER_COLS)])

        self.previous_heights_ssbo.set_data(grid.tobytes())
        self.current_heights_ssbo.set_data(grid.tobytes())

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE: # overwrite to remove shader program and SSBOs
            self.shader_program.delete()
            self.previous_heights_ssbo.delete()
            self.current_heights_ssbo.delete()

            with open("data.json", "w") as file:
                file.write(json.dumps(self.settings, indent=4))
            
            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))

    def on_mouse_press(self, x, y, button, modifiers):        
        col = int(x / (self.window.width * 0.8) * WATER_COLS)
        row = int(y / self.window.height * WATER_ROWS)

        self.splash_row = row
        self.splash_col = col
        self.current_splash_strength = self.splash_strength

    def on_draw(self):
        super().on_draw()

        self.image_sprite.draw()