import arcade, arcade.gui, json, os, math

from utils.constants import button_style
from utils.preload import button_texture, button_hovered_texture

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing a simulator", details="Spirograph Simulator")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.settings_box = self.anchor.add(arcade.gui.UIBoxLayout(align="center", size_hint=(0.2, 1)).with_background(color=arcade.color.GRAY), anchor_x="right", anchor_y="bottom")
        self.settings_label = self.settings_box.add(arcade.gui.UILabel(text="Settings", font_size=24))

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.settings = json.load(file)
        else:
            self.settings = {}

        if not "spirograph_simulator" in self.settings:
            self.settings["spirograph_simulator"] = {
                "big_radius": 220,
                "small_radius": 65,
                "pen_distance": 100,
                "step_size": 0.01,
                "trail_size": 2000,
                "mode": "inside"
            }

        self.center_points = [[self.window.width * 0.4, self.window.height / 2, 0, []]]

        self.running = True

    def on_show_view(self):
        super().on_show_view()

        self.settings_box.add(arcade.gui.UISpace(height=self.window.height / 75))

        self.add_setting("Big Radius: {value}", 10, 500, 10, "big_radius")
        self.add_setting("Small Radius: {value}", 5, 140, 5, "small_radius")
        self.add_setting("Pen Distance: {value}", 0, 250, 10, "pen_distance")
        self.add_setting("Step Size: {value}", 0.001, 0.1, 0.001, "step_size")
        self.add_setting("Trail Size: {value}", 250, 5000, 250, "trail_size")

        self.settings_box.add(arcade.gui.UISpace(height=self.window.height / 75))

        self.add_center_point_button = self.settings_box.add(arcade.gui.UITextureButton(width=self.window.width * 0.2, text="Add drawing point", texture=button_texture, texture_hovered=button_hovered_texture, style=button_style))
        self.add_center_point_button.on_click = lambda event: self.add_point()

        self.mode_button = self.settings_box.add(arcade.gui.UITextureButton(width=self.window.width * 0.2, text=f"Change to {'outside' if self.settings['spirograph_simulator']['mode'] == 'inside' else 'inside'} mode", texture=button_texture, texture_hovered=button_hovered_texture, style=button_style))
        self.mode_button.on_click = lambda event: self.change_mode()

    def add_point(self):
        self.center_points.append([self.window.width * 0.4, self.window.height / 2, 0, []])

    def change_mode(self):
        mode = self.settings["spirograph_simulator"]["mode"]
        self.settings["spirograph_simulator"]["mode"] = "outside" if mode == "inside" else "inside"

        self.mode_button.text = f"Change to {mode} mode"

    def add_setting(self, text, min_value, max_value, step, settings_key):
        label = self.settings_box.add(arcade.gui.UILabel(text.format(value=self.settings["spirograph_simulator"][settings_key])))
        slider = self.settings_box.add(arcade.gui.UISlider(value=self.settings["spirograph_simulator"][settings_key], min_value=min_value, max_value=max_value, step=step))
        slider._render_steps = lambda surface: None

        slider.on_change = lambda event, label=label: self.change_value(label, text, settings_key, event.new_value)

    def change_value(self, label, text, settings_key, value):
        label.text = text.format(value=value)

        self.settings["spirograph_simulator"][settings_key] = value

    def on_draw(self):
        super().on_draw()

        current_settings = self.settings["spirograph_simulator"]

        for center_point in self.center_points:
            x, y, t, points = center_point

            arcade.draw_circle_outline(x, y, current_settings["big_radius"], arcade.color.GRAY, 2)

            if points:
                arcade.draw_lines(points, arcade.color.WHITE, 2)

                if current_settings["mode"] == "inside":
                    cx = (current_settings["big_radius"] - current_settings["small_radius"]) * math.cos(t) + x
                    cy = (current_settings["big_radius"] - current_settings["small_radius"]) * math.sin(t) + y
                else:
                    cx = (current_settings["big_radius"] + current_settings["small_radius"]) * math.cos(t) + x
                    cy = (current_settings["big_radius"] + current_settings["small_radius"]) * math.sin(t) + y

                arcade.draw_circle_outline(int(cx), int(cy), current_settings["small_radius"], arcade.color.BLUE, 2)

                px, py = points[-1]
                arcade.draw_line(cx, cy, px, py, arcade.color.RED, 2)
                arcade.draw_circle_filled(px, py, 6, arcade.color.RED)

    def on_update(self, delta_time):
        if self.running:
            current_settings = self.settings["spirograph_simulator"]
            big_radius, small_radius = current_settings["big_radius"], current_settings["small_radius"]
            pen_distance = current_settings["pen_distance"]

            for n in range(len(self.center_points)):
                self.center_points[n][2] += current_settings["step_size"]

                if current_settings["mode"] == "inside":
                    x = (big_radius - small_radius) * math.cos(self.center_points[n][2]) + pen_distance * math.cos(((big_radius - small_radius) / small_radius) * self.center_points[n][2])
                    y = (big_radius - small_radius) * math.sin(self.center_points[n][2]) - pen_distance * math.sin(((big_radius - small_radius) / small_radius) * self.center_points[n][2])
                else:
                    x = (big_radius + small_radius) * math.cos(self.center_points[n][2]) - pen_distance * math.cos(((big_radius + small_radius) / small_radius) * self.center_points[n][2])
                    y = (big_radius + small_radius) * math.sin(self.center_points[n][2]) - pen_distance * math.sin(((big_radius + small_radius) / small_radius) * self.center_points[n][2])

                self.center_points[n][3].append((x + self.center_points[n][0], y + self.center_points[n][1]))

                if len(self.center_points[n][3]) > current_settings["trail_size"]:
                    self.center_points[n][3].pop(0)

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            with open("data.json", "w") as file:
                file.write(json.dumps(self.settings, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        
        elif symbol == arcade.key.C:
            self.center_points = [[self.window.width * 0.4, self.window.height / 2, 0, []]]

        elif symbol == arcade.key.SPACE:
            self.running = not self.running