import pyglet, arcade, arcade.gui, os, json, numpy as np

from game.chladni_plate_simulator.shader import create_shader

from utils.preload import button_texture, button_hovered_texture
from utils.constants import button_style

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing a simulator", details="Chladni Plate Simulator")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.settings_box = self.anchor.add(arcade.gui.UIBoxLayout(align="center", size_hint=(0.2, 1)).with_background(color=arcade.color.GRAY), anchor_x="right", anchor_y="bottom")
        self.settings_label = self.settings_box.add(arcade.gui.UILabel(text="Settings", font_size=24))

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.settings = json.load(file)
        else:
            self.settings = {}

        if not "chladni_plate_simulator" in self.settings:
            self.settings["chladni_plate_simulator"] = {
                "k": 0.1
            }

        self.sources = np.empty((0, 2), dtype=np.float32)
        
        self.dragged_source = None
        self.needs_redraw = False

    def add_setting(self, text, min_value, max_value, step, settings_key):
        label = self.settings_box.add(arcade.gui.UILabel(text.format(value=self.settings["chladni_plate_simulator"][settings_key])))
        slider = self.settings_box.add(arcade.gui.UISlider(value=self.settings["chladni_plate_simulator"][settings_key], min_value=min_value, max_value=max_value, step=step))
        slider._render_steps = lambda surface: None

        slider.on_change = lambda event, label=label: self.change_value(label, text, settings_key, event.new_value)

    def change_value(self, label, text, settings_key, value):
        label.text = text.format(value=value)

        self.settings["chladni_plate_simulator"][settings_key] = value

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

        self.settings_box.add(arcade.gui.UISpace(height=self.window.height / 75))

        self.add_setting("k: {value}", 0.02, 0.5, 0.01, "k")

        self.add_source_button = self.settings_box.add(arcade.gui.UITextureButton(text="Add source", texture=button_texture, texture_hovered=button_hovered_texture, style=button_style, width=self.window.width * 0.2))
        self.add_source_button.on_click = lambda event: self.add_source()

        self.setup()

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.shader_program.delete()
            self.sources_ssbo.delete()

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))

        elif symbol == arcade.key.C:
            del self.sources
            self.sources = np.empty((0, 2), dtype=np.float32)

            self.needs_redraw = True

    def on_draw(self):
        super().on_draw()

        self.image_sprite.draw()

        for item in self.sources.reshape(-1, 2):
            arcade.draw_circle_filled(item[0], item[1], 10, arcade.color.GRAY)