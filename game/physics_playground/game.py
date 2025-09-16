import arcade, arcade.gui, pymunk, pymunk.util, math, time, os, io, json, random

from PIL import Image

from arcade.gui.experimental.scroll_area import UIScrollArea, UIScrollBar

from pymunk.autogeometry import convex_decomposition

from svgpathtools import svg2paths

from game.physics_playground.body_inventory import BodyInventory

from utils.constants import menu_background_color, button_style
from utils.preload import button_texture, button_hovered_texture

class FakeShape():
    def __init__(self, body):
        self.body = body

class CustomPhysics(arcade.Sprite):
    def __init__(self, pymunk_obj, filename):
        super().__init__(filename, center_x=pymunk_obj.body.position.x, center_y=pymunk_obj.body.position.y)
        self.pymunk_obj = pymunk_obj
        
class SpritePhysics(arcade.Sprite):
    def __init__(self, pymunk_obj, filename):
        super().__init__(filename, center_x=pymunk_obj.body.position.x, center_y=pymunk_obj.body.position.y)
        self.pymunk_obj = pymunk_obj
class PhysicsCoin(SpritePhysics):
    def __init__(self, pymunk_obj, filename):
        super().__init__(pymunk_obj, filename)
        self.width = pymunk_obj.radius * 2
        self.height = pymunk_obj.radius * 2

class PhysicsCrate(SpritePhysics):
    def __init__(self, pymunk_obj, filename, width, height):
        super().__init__(pymunk_obj, filename)
        self.width = width
        self.height = height

class Game(arcade.gui.UIView):
    def __init__(self, pypresence_client):
        super().__init__()

        self.pypresence_client = pypresence_client
        self.pypresence_client.update(state='Playing a simulator', details='Physics Playground', start=self.pypresence_client.start_time)

        arcade.set_background_color(arcade.color.WHITE)

        if os.path.exists("data.json"):
            with open("data.json", "r") as file:
                self.settings = json.load(file)
        else:
            self.settings = {}

        if not "physics_playground" in self.settings:
            self.settings["physics_playground"] = {
                "iterations": 50,
                "gravity_x": 0,
                "gravity_y": -930,

                "crate_elasticity": 0.5,
                "crate_friction": 0.9,
                "crate_mass": 1,

                "coin_elasticity": 0.5,
                "coin_friction": 0.9,
                "coin_mass": 1,

                "custom_elasticity": 0.5,
                "custom_friction": 0.9,
                "custom_mass": 1
            }

        self.space = pymunk.Space()

        self.spritelist: arcade.SpriteList[SpritePhysics] = arcade.SpriteList()
        self.walls = []
        self.custom_bodies = []

        self.custom_pymunk_objs = {}

        self.dragged_shape = None
        self.last_mouse_position = 0, 0
        self.last_processing_time_update = time.perf_counter()

        self.iterations = self.settings["physics_playground"].get("iterations", 35)
        self.space.iterations = self.iterations

        self.gravity_x = self.settings["physics_playground"].get("gravity_x", 0)
        self.gravity_y = self.settings["physics_playground"].get("gravity_y", -930)
        self.space.gravity = (self.gravity_x, self.gravity_y)

        self.crate_elasticity = self.settings["physics_playground"].get("crate_elasticity", 0.5)
        self.crate_friction = self.settings["physics_playground"].get("crate_friction", 0.9)
        self.crate_mass = self.settings["physics_playground"].get("crate_mass", 1)

        self.coin_elasticity = self.settings["physics_playground"].get("coin_elasticity", 0.5)
        self.coin_friction = self.settings["physics_playground"].get("coin_friction", 0.9)
        self.coin_mass = self.settings["physics_playground"].get("coin_mass", 1)

        self.custom_elasticity = self.settings["physics_playground"].get("custom_elasticity", 0.5)
        self.custom_friction = self.settings["physics_playground"].get("custom_friction", 0.9)
        self.custom_mass = self.settings["physics_playground"].get("custom_mass", 1)

        self.anchor = self.add_widget(arcade.gui.UIAnchorLayout(size_hint=(1, 1)))
        
        self.info_box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=3, align="left"), anchor_x="left", anchor_y="top")
        self.fps_label = self.info_box.add(arcade.gui.UILabel(text="FPS: 60", text_color=arcade.color.BLACK))
        self.object_count_label = self.info_box.add(arcade.gui.UILabel(text="Object count: 0", text_color=arcade.color.BLACK))
        self.processing_time_label = self.info_box.add(arcade.gui.UILabel(text="Processing time: 0 ms", text_color=arcade.color.BLACK))

        self.settings_box = self.anchor.add(arcade.gui.UIBoxLayout(align="center", size_hint=(0.2, 1)).with_background(color=arcade.color.GRAY), anchor_x="right", anchor_y="bottom")
        self.settings_title_label = self.settings_box.add(arcade.gui.UILabel(text="Settings", font_size=24))

        self.settings_box.add(arcade.gui.UISpace(size_hint=(0, 0.025)))

        self.add_setting("Crate Elasticity: {value}", 0, 3, 0.1, "crate_elasticity", "elasticity", PhysicsCrate)
        self.add_setting("Coin Elasticity: {value}", 0, 3, 0.1, "coin_elasticity", "elasticity", PhysicsCoin)
        self.add_setting("Custom Elasticity: {value}", 0, 3, 0.1, "custom_elasticity", "elasticity", CustomPhysics)
        
        self.add_setting("Crate Friction: {value}", 0, 10, 0.1, "crate_friction", "friction", PhysicsCrate)
        self.add_setting("Coin Friction: {value}", 0, 10, 0.1, "coin_friction", "friction", PhysicsCoin)
        self.add_setting("Custom Friction: {value}", 0, 10, 0.1, "custom_friction", "friction", CustomPhysics)

        self.add_setting("Crate Mass: {value}kg", 1, 100, 1, "crate_mass", "mass", PhysicsCrate)
        self.add_setting("Coin Mass: {value}kg", 1, 100, 1, "coin_mass", "mass", PhysicsCoin)
        self.add_setting("Custom Mass: {value}kg", 1, 100, 1, "custom_mass", "mass", CustomPhysics)

        self.add_setting("Gravity X: {value}", -900, 900, 100, "gravity_x", on_change=lambda label, value: self.change_gravity(label, value, "x"))
        self.add_setting("Gravity Y: {value}", -1800, 1800, 100, "gravity_y", on_change=lambda label, value: self.change_gravity(label, value, "y"))
        self.add_setting("Pymunk Iterations: {value}", 1, 200, 1, "iterations", on_change=lambda label, value: self.change_iterations(label, value))

        self.settings_box.add(arcade.gui.UILabel("Inventory", font_size=18))

        self.inventory_grid = self.settings_box.add(BodyInventory(self.window.width, self.window.height, "crate", {"crate": ":resources:images/tiles/boxCrate_double.png", "coin": ":resources:images/items/coinGold.png"}))
        if os.name != "nt":
            self.add_custom_body_button = self.settings_box.add(arcade.gui.UITextureButton(text="Add custom body from SVG", size_hint=(1, 0.1), width=self.window.width * 0.2, height=self.window.height * 0.1))
                
            self.add_custom_body_button.on_click = lambda event: self.custom_body_ui()

    def save_data(self):
        with open("data.json", "w") as file:
            file.write(json.dumps(self.settings, indent=4))

    def change_iterations(self, label, value):
        self.iterations = int(value)
        self.space.iterations = self.iterations
        label.text = f"Pymunk Iterations: {self.iterations}"

    def change_gravity(self, label, value, gravity_type):
        if gravity_type == "x":
            self.gravity_x = value
        else:
            self.gravity_y = value

        self.space.gravity = pymunk.Vec2d(self.gravity_x, self.gravity_y)
        label.text = f"Gravity {gravity_type.capitalize()}: {value}"

    def add_setting(self, text, min_value, max_value, step, local_variable, pymunk_variable=None, instance=None, on_change=None):
        label = self.settings_box.add(arcade.gui.UILabel(text.format(value=getattr(self, local_variable))))
        slider = self.settings_box.add(arcade.gui.UISlider(value=getattr(self, local_variable), min_value=min_value, max_value=max_value, step=step, size_hint=(1, 0.05)))
        slider._render_steps = lambda surface: None

        if pymunk_variable:
            slider.on_change = lambda event, label=label: self.change_value(label, text, local_variable, event.new_value, pymunk_variable, instance)
        elif on_change:
            slider.on_change = lambda event, label=label: on_change(label, event.new_value)
        else:
            slider.on_change = lambda event, label=label: self.change_value(label, text, local_variable, event.new_value)

    def change_value(self, label, text, local_variable, value, pymunk_variable=None, instance=None):
        label.text = text.format(value=value)

        setattr(self, local_variable, value)

        self.settings["physics_playground"][local_variable] = value

        if pymunk_variable:
            for sprite in self.spritelist:
                if isinstance(sprite, instance):
                    setattr(sprite.pymunk_obj, pymunk_variable, value)

    def create_wall(self, width, height, x, y):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pymunk.Vec2d(x, y)
        pymunk_obj = pymunk.Segment(body, [0, height], [width, height], 0.0)
        pymunk_obj.friction = 10
        self.space.add(pymunk_obj, body)
        self.walls.append(pymunk_obj)

    def create_crate(self, x, y, size, mass):
        pymunk_moment = pymunk.moment_for_box(1.0, (size, size))
        
        pymunk_body = pymunk.Body(mass, pymunk_moment)
        pymunk_body.position = pymunk.Vec2d(x, y)
        
        pymunk_shape = pymunk.Poly.create_box(pymunk_body, (size, size))
        pymunk_shape.elasticity = self.crate_elasticity
        pymunk_shape.friction = self.crate_friction
        
        self.space.add(pymunk_body, pymunk_shape)

        sprite = PhysicsCrate(pymunk_shape, ":resources:images/tiles/boxCrate_double.png", width=size, height=size)
        self.spritelist.append(sprite)

    def create_coin(self, x, y, radius, mass):
        inertia = pymunk.moment_for_circle(1.0, 0, radius, (0, 0))
        
        body = pymunk.Body(mass, inertia)
        body.position = x, y
        body.velocity = 0, 0
        
        shape = pymunk.Circle(body, radius, pymunk.Vec2d(0, 0))
        shape.friction = self.coin_friction
        shape.elasticity = self.coin_elasticity
        
        self.space.add(body, shape)

        sprite = PhysicsCoin(shape, ":resources:images/items/coinGold.png")
        self.spritelist.append(sprite)

    def on_draw(self):
        super().on_draw()

        self.spritelist.draw()

        for wall in self.walls:
            body = wall.body
            pv1 = body.position + wall.a.rotated(body.angle)
            pv2 = body.position + wall.b.rotated(body.angle)

            arcade.draw_line(pv1.x, pv1.y, pv2.x, pv2.y, arcade.color.BLACK, 2)

        for body in self.custom_bodies:
            for shape in body.shapes:
                if isinstance(shape, pymunk.Poly):
                    verts = [v.rotated(body.angle) + body.position for v in shape.get_vertices()]
                    arcade.draw_polygon_filled(verts, arcade.color.BLACK)
                    
    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.last_mouse_position = x, y

            shape_list = self.space.point_query((x, y), 1, pymunk.ShapeFilter())

            if len(shape_list) > 0:
                self.dragged_shape = shape_list[0]

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragged_shape = None

    def on_mouse_motion(self, x, y, dx, dy):
        if self.dragged_shape is not None:
            self.last_mouse_position = x, y

            self.dragged_shape.shape.body.position = self.last_mouse_position
            self.dragged_shape.shape.body.velocity = dx * 50, dy * 50
    
    def clear_custom_body_ui(self):
        if hasattr(self, "custom_body_ui_box"):
            self.anchor.remove(self.custom_body_ui_box)
            self.custom_body_ui_box.clear()
            del self.custom_body_ui_box
        
        if hasattr(self, "file_manager_ui_box"):
            self.anchor.remove(self.file_manager_ui_box)
            self.file_manager_ui_box.clear()
            del self.file_manager_ui_box

        if hasattr(self, "scrollbar"):
            self.anchor.remove(self.scrollbar)
            del self.scrollbar

    def sample_path(self, path, segments=50):
        pts = []

        for i in range(segments + 1):
            point = path.point(i / segments)
            pts.append((point.real, point.imag))

        return pts

    def add_custom_body(self, file_path):
        import cairosvg
        paths, _ = svg2paths(file_path)

        pts = self.sample_path(paths[0], 64)

        png_bytes = cairosvg.svg2png(url=file_path, scale=1.0)
        original_image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        original_width, _ = original_image.size

        desired_width = 32
        scale_factor = desired_width / original_width

        pts = [(x * scale_factor, y * scale_factor) for x, y in pts]
        
        try:
            convex_parts = convex_decomposition(pts, 0.1)
        except AssertionError:
            convex_parts = [pymunk.util.convex_hull(pts)]

        total_moment = sum(pymunk.moment_for_poly(1.0, part) for part in convex_parts)

        png_bytes = cairosvg.svg2png(url=file_path, scale=scale_factor)
        image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        texture = arcade.Texture(image)

        self.custom_pymunk_objs[file_path] = (convex_parts, total_moment, texture)
        self.inventory_grid.add_item(file_path, texture)

        self.clear_custom_body_ui()

    def create_custom_body(self, file_path, x, y, mass):
        convex_parts, moment, image = self.custom_pymunk_objs[file_path]

        body = pymunk.Body(mass, moment)
        body.position = pymunk.Vec2d(x, y)

        self.space.add(body)

        for part in convex_parts:
            shape = pymunk.Poly(body, part)
            self.space.add(shape)
        
        sprite = CustomPhysics(FakeShape(body), image)

        self.spritelist.append(sprite)

    def get_directory_content(self, directory):
        try:
            entries = os.listdir(directory)
        except PermissionError:
            return None

        filtered = [
            entry for entry in entries
            if (os.path.isdir(os.path.join(directory, entry)) and not "." in entry) or
            os.path.splitext(entry)[1].lower() == ".svg"
        ]

        sorted_entries = sorted(
            filtered,
            key=lambda x: (0 if os.path.isdir(os.path.join(directory, x)) else 1, x.lower())
        )

        return sorted_entries

    def file_manager(self, current_directory=None):
        self.clear_custom_body_ui()

        if not current_directory:
            current_directory = os.getcwd()

        self.scroll_area = UIScrollArea(size_hint=(0.5, 0.5)) # center on screen
        self.scroll_area.scroll_speed = -50
        self.anchor.add(self.scroll_area, anchor_x="center", anchor_y="center")

        self.scrollbar = UIScrollBar(self.scroll_area)
        self.scrollbar.size_hint = (0.02, 0.5)
        self.anchor.add(self.scrollbar, anchor_x="center", anchor_y="center", align_x=self.window.width / 4)

        self.file_manager_ui_box = self.scroll_area.add(arcade.gui.UIBoxLayout(space_between=10).with_background(color=arcade.color.GRAY))
        self.file_manager_ui_box.add(arcade.gui.UILabel(f"File Manager ({current_directory})", font_size=16))

        go_up_button = self.file_manager_ui_box.add(arcade.gui.UITextureButton(text="Go up", texture=button_texture, texture_hovered=button_hovered_texture, style=button_style, width=self.window.width / 2, height=self.window.height / 10))
        go_up_button.on_click = lambda event, current_directory=current_directory: self.file_manager(os.path.dirname(current_directory))

        for file in self.get_directory_content(current_directory):
            if os.path.isfile(f"{current_directory}/{file}"):
                file_button = self.file_manager_ui_box.add(arcade.gui.UITextureButton(text=file, texture=button_texture, texture_hovered=button_hovered_texture, style=button_style, width=self.window.width / 2, height=self.window.height / 10))
                file_button.on_click = lambda event, file=file: self.custom_body_ui(f"{current_directory}/{file}")
            else:
                file_button = self.file_manager_ui_box.add(arcade.gui.UITextureButton(text=file, texture=button_texture, texture_hovered=button_hovered_texture, style=button_style, width=self.window.width / 2, height=self.window.height / 10))
                file_button.on_click = lambda event, file=file: self.file_manager(f"{current_directory}/{file}")

    def custom_body_ui(self, file_selected=None):
        self.clear_custom_body_ui()
        
        self.custom_body_ui_box = self.anchor.add(arcade.gui.UIBoxLayout(space_between=10, size_hint=(0.5, 0.5)).with_background(color=arcade.color.GRAY), anchor_x="center")
        self.custom_body_ui_box.add(arcade.gui.UILabel("Add Custom Body from SVG File", font_size=24))

        select_file_button = self.custom_body_ui_box.add(arcade.gui.UITextureButton(text=f"Select File ({file_selected})", texture=button_texture, texture_hovered=button_hovered_texture, style=button_style, width=self.window.width / 2, height=self.window.height / 10))
        select_file_button.on_click = lambda event: self.file_manager()

        add_button = self.custom_body_ui_box.add(arcade.gui.UITextureButton(text="Add Body", texture=button_texture, texture_hovered=button_hovered_texture, style=button_style, width=self.window.width / 2, height=self.window.height / 10))
        
        if file_selected:
            add_button.on_click = lambda event, file_selected=file_selected: self.add_custom_body(file_selected)

    def on_update(self, delta_time):
        if self.window.keyboard[arcade.key.W]:
            if self.inventory_grid.selected_item == "crate":
                self.create_crate(self.window.mouse.data['x'], self.window.mouse.data['y'], 32, self.crate_mass)
            elif self.inventory_grid.selected_item == "coin":
                self.create_coin(self.window.mouse.data['x'], self.window.mouse.data['y'], 10, self.coin_mass)
            else:
                self.create_custom_body(self.inventory_grid.selected_item, self.window.mouse.data['x'], self.window.mouse.data['y'], self.custom_mass)

        for sprite in self.spritelist:
            x, y = sprite.pymunk_obj.body.position

            if x < 0 or x > self.window.width * 0.775 or y < 0:
                if not isinstance(sprite.pymunk_obj, FakeShape):
                    sprite.remove_from_sprite_lists()
                    self.space.remove(sprite.pymunk_obj, sprite.pymunk_obj.body)
                else:
                    sprite.remove_from_sprite_lists()
                    for shape in sprite.pymunk_obj.body.shapes:
                        self.space.remove(shape)
                    self.space.remove(sprite.pymunk_obj.body)

        start = time.perf_counter()
        self.space.step(self.window._draw_rate)

        if self.dragged_shape is not None:
            self.dragged_shape.shape.body.position = self.last_mouse_position
            self.dragged_shape.shape.body.velocity = 0, 0

        for sprite in self.spritelist:
            sprite.position = sprite.pymunk_obj.body.position
            sprite.angle = -math.degrees(sprite.pymunk_obj.body.angle)

        self.object_count_label.text = f"Object count: {len(self.spritelist)}"

        current_time = time.perf_counter()
        if current_time - self.last_processing_time_update > 0.2: 
            self.last_processing_time_update = current_time
            self.processing_time_label.text = f"Processing time: {round((current_time - start) * 1000, 2)} ms"

    def on_key_press(self, symbol, modifiers):
        if symbol == arcade.key.ESCAPE:
            arcade.set_background_color(menu_background_color)
            
            self.save_data()

            from menus.main import Main
            self.window.show_view(Main(self.pypresence_client))
        elif symbol == arcade.key.D:
            self.create_wall((self.window.width * 0.8) / 10, 80, self.window.mouse.data["x"] - (self.window.width * 0.8) / 20, self.window.mouse.data["y"] - 80)
        elif symbol == arcade.key.C:
            for sprite in self.spritelist:
                if not isinstance(sprite.pymunk_obj, FakeShape):
                    self.space.remove(sprite.pymunk_obj, sprite.pymunk_obj.body)
                else:
                    for shape in sprite.pymunk_obj.body.shapes:
                        self.space.remove(shape)
                    self.space.remove(sprite.pymunk_obj.body)


            self.spritelist.clear()

    def on_show_view(self):
        super().on_show_view()

        self.create_wall((self.window.width * 0.8), 80, 0, 0)
