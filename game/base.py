import arcade, arcade.gui, os, json

class BaseGame(arcade.gui.UIView):
    def __init__(self, pypresence_client, game_name, game_key, game_dict):
        super().__init__()

        self.game_name = game_name
        self.game_key = game_key
        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state="Playing a simulator", details=game_name)

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        self.settings_box = self.anchor.add(arcade.gui.UIBoxLayout(align="center", size_hint=(0.2, 1)).with_background(color=arcade.color.GRAY), anchor_x="right", anchor_y="bottom")
        self.settings_label = self.settings_box.add(arcade.gui.UILabel(text="Settings", font_size=24))
        self.settings_space = self.settings_box.add(arcade.gui.UISpace(height=self.window.height / 75))

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.settings = json.load(file)

        else:
            self.settings = {}

        if not game_key in self.settings:
            self.settings[game_key] = game_dict

    def add_setting(self, text, min_value, max_value, step, settings_key):
        label = self.settings_box.add(arcade.gui.UILabel(text.format(value=self.settings[self.game_key][settings_key])))
        slider = self.settings_box.add(arcade.gui.UISlider(value=self.settings[self.game_key][settings_key], min_value=min_value, max_value=max_value, step=step))
        slider._render_steps = lambda surface: None

        slider.on_change = lambda event, label=label: self.change_value(label, text, settings_key, event.new_value)

    def change_value(self, label, text, settings_key, value):
        label.text = text.format(value=value)

        self.settings[self.game_key][settings_key] = value

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            with open("data.json", "w") as file:
                file.write(json.dumps(self.settings, indent=4))

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))