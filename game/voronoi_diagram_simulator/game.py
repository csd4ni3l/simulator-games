import pyglet, arcade, arcade.gui, os, json, numpy as np

from game.voronoi_diagram_simulator.shader import create_shader

from utils.constants import button_style
from utils.preload import button_texture, button_hovered_texture

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing a simulator", details="Voronoi Diagram Simulator")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.settings_box = self.anchor.add(arcade.gui.UIBoxLayout(align="center", size_hint=(0.2, 1)).with_background(color=arcade.color.GRAY), anchor_x="right", anchor_y="bottom")
        self.settings_label = self.settings_box.add(arcade.gui.UILabel(text="Settings", font_size=24))

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.settings = json.load(file)

        else:
            self.settings = {}

        if not "voronoi_diagram_simulator" in self.settings:
            self.settings["voronoi_diagram_simulator"] = {
                "edge_thickness": 0.01,
                "edge_smoothness": 0.005
            }

        self.points = np.empty((0, 2), dtype=np.float32)
        
        self.dragged_point = None
        self.needs_redraw = True

    def setup(self):
        self.shader_program, self.voronoi_image, self.points_sbbo = create_shader(int(self.window.width * 0.8), self.window.height)

        self.image_sprite = pyglet.sprite.Sprite(img=self.voronoi_image)

    def on_show_view(self):
        super().on_show_view()

        self.settings_box.add(arcade.gui.UISpace(height=self.window.height / 75))

        self.add_setting("Edge Thickness: {value}", 0, 0.1, 0.01, "edge_thickness")
        self.add_setting("Edge Smoothness: {value}", 0, 0.1, 0.01, "edge_smoothness")

        self.add_point_button = self.settings_box.add(arcade.gui.UITextureButton(text="Add point", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width * 0.2, style=button_style))
        self.add_point_button.on_click = lambda event: self.add_point()

        self.setup()

    def add_point(self):
        self.points = np.vstack([self.points, [self.window.width * 0.4, self.window.height / 2]]).astype(np.float32)

        self.needs_redraw = True

    def add_setting(self, text, min_value, max_value, step, settings_key):
        label = self.settings_box.add(arcade.gui.UILabel(text.format(value=self.settings["voronoi_diagram_simulator"][settings_key])))
        slider = self.settings_box.add(arcade.gui.UISlider(value=self.settings["voronoi_diagram_simulator"][settings_key], min_value=min_value, max_value=max_value, step=step))
        slider._render_steps = lambda surface: None

        slider.on_change = lambda event, label=label: self.change_value(label, text, settings_key, event.new_value)

    def change_value(self, label, text, settings_key, value):
        label.text = text.format(value=value)

        self.settings["voronoi_diagram_simulator"][settings_key] = value

        self.needs_redraw = True

    def on_update(self, delta_time):
        if self.needs_redraw:
            self.needs_redraw = False

            self.points_sbbo.set_data(self.points.tobytes())

            with self.shader_program:
                self.shader_program["point_count"] = len(self.points)
                self.shader_program["resolution"] = (int(self.window.width * 0.8), self.window.height)
                self.shader_program["edge_smoothness"] = self.settings["voronoi_diagram_simulator"]["edge_smoothness"]
                self.shader_program["edge_thickness"] = self.settings["voronoi_diagram_simulator"]["edge_thickness"]

                self.shader_program.dispatch(int(int(self.window.width * 0.8) / 32), int(self.window.height / 32))

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.dragged_point:
            for i, point in enumerate(self.points.reshape(-1, 2)):
                if arcade.math.Vec2(x, y).distance(arcade.math.Vec2(*point)) <= 10:
                    self.dragged_point = i
                    break

    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        if self.dragged_point is not None:
            self.points[self.dragged_point] = [x, y]

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragged_point = None
        self.needs_redraw = True

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.shader_program.delete()

            with open("data.json", "w") as file:
                file.write(json.dumps(self.settings, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        
        elif symbol == arcade.key.C:
            del self.points
            self.points = np.empty((0, 2), dtype=np.float32)

            self.needs_redraw = True

    def on_draw(self):
        super().on_draw()

        self.image_sprite.draw()

        for point in self.points.reshape(-1, 2):
            arcade.draw_circle_filled(point[0], point[1], 10, arcade.color.GRAY)