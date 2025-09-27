import arcade, arcade.gui, asyncio, pypresence, time, copy, json
from utils.preload import button_texture, button_hovered_texture
from utils.constants import big_button_style, discord_presence_id
from utils.utils import FakePyPresence

class Main(arcade.gui.UIView):
    def __init__(self, pypresence_client=None):
        super().__init__()

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout())
        self.box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=10), anchor_x='center', anchor_y='center')

        self.pypresence_client = pypresence_client

        with open("settings.json", "r") as file:
            self.settings_dict = json.load(file)

        if self.settings_dict.get('discord_rpc', True):
            if self.pypresence_client == None: # Game has started
                try:
                    asyncio.get_event_loop()
                except:
                    asyncio.set_event_loop(asyncio.new_event_loop())
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.start_time = time.time()
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = time.time()

            elif isinstance(self.pypresence_client, FakePyPresence): # the user has enabled RPC in the settings in this session.
                # get start time from old object
                start_time = copy.deepcopy(self.pypresence_client.start_time)
                try:
                    self.pypresence_client = pypresence.Presence(discord_presence_id)
                    self.pypresence_client.connect()
                    self.pypresence_client.start_time = start_time
                except:
                    self.pypresence_client = FakePyPresence()
                    self.pypresence_client.start_time = start_time

            self.pypresence_client.update(state='In Menu', details='In Main Menu', start=self.pypresence_client.start_time)
        else: # game has started, but the user has disabled RPC in the settings.
            self.pypresence_client = FakePyPresence()
            self.pypresence_client.start_time = time.time()

        self.pypresence_client.update(state='In Menu', details='In Main Menu', start=self.pypresence_client.start_time)

    def on_show_view(self):
        super().on_show_view()

        self.title_label = self.box.add(arcade.gui.UILabel(text="Simulator Games", font_name="Roboto", font_size=48))

        self.boid_simulator_button = self.box.add(arcade.gui.UITextureButton(text="Boid Simulator", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.boid_simulator_button.on_click = lambda event: self.boid_simulator()

        self.water_simulator_button = self.box.add(arcade.gui.UITextureButton(text="Water Splash Simulator", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.water_simulator_button.on_click = lambda event: self.water_simulator()

        self.physics_playground_button = self.box.add(arcade.gui.UITextureButton(text="Physics Playground", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.physics_playground_button.on_click = lambda event: self.physics_playground()

        self.fourier_simulator_button = self.box.add(arcade.gui.UITextureButton(text="Fourier Drawing Simulator", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.fourier_simulator_button.on_click = lambda event: self.fourier_simulator()

        self.chladni_plate_simulator_button = self.box.add(arcade.gui.UITextureButton(text="Chladni Plate Simulator", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.chladni_plate_simulator_button.on_click = lambda event: self.chladni_plate_simulator()

        self.lissajous_simulator_button = self.box.add(arcade.gui.UITextureButton(text="Lissajous Simulator", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.lissajous_simulator_button.on_click = lambda event: self.lissajous_simulator()

        self.voronoi_diagram_simulator_button = self.box.add(arcade.gui.UITextureButton(text="Voronoi Diagram Simulator", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.voronoi_diagram_simulator_button.on_click = lambda event: self.voronoi_diagram_simulator()

        self.lorenz_attractor_simulator_button = self.box.add(arcade.gui.UITextureButton(text="Lorenz Attractor Simulator", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.lorenz_attractor_simulator_button.on_click = lambda event: self.lorenz_attractor_simulator()

        self.spirograph_simulator_button = self.box.add(arcade.gui.UITextureButton(text="Spirograph Simulator", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.spirograph_simulator_button.on_click = lambda event: self.spirograph_simulator()

        self.settings_button = self.box.add(arcade.gui.UITextureButton(text="Settings", texture=button_texture, texture_hovered=button_hovered_texture, width=self.window.width / 2, height=self.window.height / 14, style=big_button_style))
        self.settings_button.on_click = lambda event: self.settings()

    def physics_playground(self):
        from game.physics_playground.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def boid_simulator(self):
        from game.boid_simulator.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def water_simulator(self):
        from game.water_simulator.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def fourier_simulator(self):
        from game.fourier_simulator.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def chladni_plate_simulator(self):
        from game.chladni_plate_simulator.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def lissajous_simulator(self):
        from game.lissajous_simulator.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def voronoi_diagram_simulator(self):
        from game.voronoi_diagram_simulator.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def lorenz_attractor_simulator(self):
        from game.lorenz_attractor_simulator.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def spirograph_simulator(self):
        from game.spirograph_simulator.game import Game
        self.window.show_view(Game(self.pypresence_client))

    def settings(self):
        from menus.settings import Settings
        self.window.show_view(Settings(self.pypresence_client))
