import arcade, arcade.gui, random, os, json

from game.boid_simulator.boid import Boid

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state='Playing a simulator', details='Boids simulator', start=self.pypresence_client.start_time)
        self.boid_sprites = arcade.SpriteList()
        self.current_boid_num = 1

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.settings = json.load(file)
        else:
            self.settings = {}

        if not "boid_simulator" in self.settings:
            self.settings["boid_simulator"] = {
                "w_separation": 1.0,
                "w_alignment": 1.0,
                "w_cohesion": 1.0,
                "small_radius": 100,
                "large_radius": 250
            }

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))

        self.settings_box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=5, align="center", size_hint=(0.2, 1)).with_background(color=arcade.color.GRAY), anchor_x="right", anchor_y="bottom")
        self.settings_label = self.settings_box.add(arcade.gui.UILabel(text="Settings", font_size=24))
        self.add_setting("Separation Weight: {value}", 0.1, 5, 0.1, "w_separation")
        self.add_setting("Alignment Weight: {value}", 0.1, 5, 0.1, "w_alignment")
        self.add_setting("Cohesion Weight: {value}", 0.1, 5, 0.1, "w_cohesion")
        self.add_setting("Small Radius: {value}", 25, 250, 25, "small_radius")
        self.add_setting("Large Radius: {value}", 50, 500, 50, "large_radius")

    def save_data(self):
        with open("data.json", "w") as file:
            file.write(json.dumps(self.settings, indent=4))

    def add_setting(self, text, min_value, max_value, step, boid_variable):
        label = self.settings_box.add(arcade.gui.UILabel(text.format(value=self.settings["boid_simulator"][boid_variable])))
        slider = self.settings_box.add(arcade.gui.UISlider(value=self.settings["boid_simulator"][boid_variable], min_value=min_value, max_value=max_value, step=step, size_hint=(1, 0.05)))
        slider._render_steps = lambda surface: None

        slider.on_change = lambda event, label=label: self.change_value(label, text, boid_variable, event.new_value)

    def change_value(self, label, text, boid_variable, value):
        label.text = text.format(value=value)

        self.settings["boid_simulator"][boid_variable] = value

        for boid in self.boid_sprites:
            setattr(boid, boid_variable, value)

    def create_boid(self, x, y):
        boid = Boid(self.current_boid_num, x, y)
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

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            self.save_data()

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))

    def on_draw(self):
        super().on_draw()
        self.boid_sprites.draw()