import arcade, arcade.gui, math

class BodyInventory(arcade.gui.UIGridLayout):
    def __init__(self, window_width, window_height, selected, items):
        super().__init__(column_count=2, row_count=math.ceil(len(items) / 2), size_hint=(0.2, 0.1))

        self.items = items
        self.selected_item = selected
        self.buttons = {}
        self.window_width, self.window_height = window_width, window_height

        n = 0
        for name, image in items.items():
            self.buttons[name] = self.add(arcade.gui.UITextureButton(width=(window_width * 0.2) / 4, height=(window_width * 0.2) / 4).with_background(texture=arcade.load_texture(image), color=arcade.color.WHITE if name == self.selected_item else arcade.color.TRANSPARENT_BLACK), column=n % 2, row=n // 2)
            self.buttons[name].on_click = lambda event, name=name: self.change_to(name)
            
            n += 1

    def add_item(self, name, image):
        if not (len(self.items) + 1 <= (self.column_count * self.row_count)):
            self.row_count += 1

            self._update_size_hints()

        self.items[name] = image

        self.buttons[name] = self.add(arcade.gui.UITextureButton(width=(self.window_width * 0.2) / 2, height=(self.window_height * 0.1) / math.ceil(len(self.items) / 2), color=arcade.color.TRANSPARENT_BLACK).with_background(texture=image), column=len(self.items) % 2, row=len(self.items) // 2)
        self.buttons[name].on_click = lambda event, name=name: self.change_to(name)

    def change_to(self, name):
        self.buttons[self.selected_item] = self.buttons[self.selected_item].with_background(color=arcade.color.TRANSPARENT_BLACK)
        self.selected_item = name
        self.buttons[self.selected_item] = self.buttons[self.selected_item].with_background(color=arcade.color.WHITE)