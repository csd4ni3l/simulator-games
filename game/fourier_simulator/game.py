import arcade, arcade.gui, os, json, numpy as np

from scipy.interpolate import interp1d

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing a simulator", details="Fourier Simulator")

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.settings_box = self.anchor.add(arcade.gui.UIBoxLayout(align="center", size_hint=(0.2, 1)).with_background(color=arcade.color.GRAY), anchor_x="right", anchor_y="bottom")
        self.settings_label = self.settings_box.add(arcade.gui.UILabel(text="Settings", font_size=24))

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.settings = json.load(file)
        else:
            self.settings = {}

        if not "fourier_simulator" in self.settings:
            self.settings["fourier_simulator"] = {
                "max_coefficients": 1000,
                "speed": 1.0,
                "tail_size": 1000,
                "resampling_size": 512
            }

        self.path_points = []
        
        self.drawing_done = False
        
        self.fourier_coefficients = []
        self.drawing_trail = []

        self.time = 0.0

    def on_show_view(self):
        super().on_show_view()

        self.settings_box.add(arcade.gui.UISpace(height=self.window.height / 75))

        self.add_setting("Max Coefficients: {value}", 1, 10000, 1, "max_coefficients")
        self.add_setting("Speed: {value}", 0.1, 1.5, 0.1, "speed")
        self.add_setting("Tail Size: {value}", 10, 1000, 10, "tail_size")
        self.add_setting("Resampling Size: {value}", 128, 8192, 128, "resampling_size")

    def add_setting(self, text, min_value, max_value, step, settings_key):
        label = self.settings_box.add(arcade.gui.UILabel(text.format(value=self.settings["fourier_simulator"][settings_key])))
        slider = self.settings_box.add(arcade.gui.UISlider(value=self.settings["fourier_simulator"][settings_key], min_value=min_value, max_value=max_value, step=step))
        slider._render_steps = lambda surface: None

        slider.on_change = lambda event, label=label: self.change_value(label, text, settings_key, event.new_value)

    def change_value(self, label, text, settings_key, value):
        label.text = text.format(value=value)

        self.settings["fourier_simulator"][settings_key] = value

    def main_exit(self):
        with open("data.json", "w") as file:
            file.write(json.dumps(self.settings, indent=4))

        from menus.main import Main
        self.window.show_view(Main(self.pypresence_client))

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.main_exit()

    def on_mouse_press(self, x, y, button, modifiers):
        self.path_points = []
        self.drawing_trail.clear()
        self.drawing_done = False
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.drawing_done = True
        self.calculate_fourier_coefficients()

    def calculate_drawing_point(self, t):
        pos = 0j
        
        for i, c in enumerate(self.fourier_coefficients):
            k = i - (len(self.fourier_coefficients) // 2)
            angle = 2 * np.pi * k * t
            pos += c * np.exp(1j * angle)

        return float(pos.real), float(pos.imag)
    
    def resample_path(self, path_points, N):
        t = np.linspace(0, 1, len(path_points))

        fx = interp1d(t, path_points.real, kind='linear')
        fy = interp1d(t, path_points.imag, kind='linear')

        t_uniform = np.linspace(0, 1, N)

        return fx(t_uniform) + 1j * fy(t_uniform)

    def calculate_fourier_coefficients(self):
        if not self.path_points:
            return
        
        c_points = np.array(self.path_points)
        
        c_points = self.resample_path(c_points, int(self.settings["fourier_simulator"]["resampling_size"]))

        coeffs = np.fft.fftshift(np.fft.fft(c_points) / len(c_points))

        self.fourier_coefficients = np.array(coeffs[:int(self.settings["fourier_simulator"]["max_coefficients"])], dtype=np.complex64)
    
    def on_mouse_drag(self, x, y, dx, dy, _buttons, _modifiers):
        if not self.drawing_done:
            self.path_points.append(complex(x / self.window.width, y / self.window.height))

    def on_update(self, delta_time):
        self.time += delta_time

        if self.drawing_done:
            t_normalized = (self.time * self.settings["fourier_simulator"]["speed"]) % 1.0
            x, y = self.calculate_drawing_point(t_normalized)

            pixel_x = x * self.window.width
            pixel_y = y * self.window.height

            self.drawing_trail.append((pixel_x, pixel_y))

            if len(self.drawing_trail) > self.settings["fourier_simulator"]["tail_size"]:
                self.drawing_trail.pop(0)

    def on_draw(self):
        super().on_draw()

        if len(self.drawing_trail) > 1:
            arcade.draw_line_strip(
                self.drawing_trail,
                color=arcade.color.WHITE,
                line_width=2
            )