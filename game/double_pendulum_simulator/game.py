import arcade, arcade.gui, json, os, math

from game.base import BaseGame

class Game(BaseGame):
    def __init__(self, pypresence_client):
        super().__init__(pypresence_client, "Double Pendulum Simulator", "double_pendulum_simulator", {
            "length_a": 200,
            "length_b": 200,
            "mass_a": 40,
            "mass_b": 40,
            "gravity": 9.81,
            "speed": 1.0,
            "trail_size": 500
        })

        self.theta_a, self.theta_b = math.pi / 2, math.pi / 2
        self.omega_a, self.omega_b = 0, 0
        self.origin_x, self.origin_y = self.window.width * 0.4, self.window.height / 2

        self.trace = []

    def on_show_view(self):
        super().on_show_view()

        self.add_setting("Length A: {value}", 5, 500, 5, "length_a")
        self.add_setting("Length B: {value}", 5, 500, 5, "length_b")
        self.add_setting("Mass A: {value}", 1, 100, 1, "mass_a")
        self.add_setting("Mass B: {value}", 1, 100, 1, "mass_b")
        self.add_setting("Gravity: {value}", 0, 25, 0.01, "gravity")
        self.add_setting("Speed: {value}", 1, 100, 1, "speed")
        self.add_setting("Trail Size: {value}", 0, 5000, 50, "trail_size")

    def on_draw(self):
        super().on_draw()

        current_settings = self.settings["double_pendulum_simulator"]
        L1, L2 = current_settings["length_a"], current_settings["length_b"]
        m1, m2 = current_settings["mass_a"], current_settings["mass_b"]

        x1 = self.origin_x + L1 * math.sin(self.theta_a)
        y1 = self.origin_y - L1 * math.cos(self.theta_a)

        x2 = x1 + L2 * math.sin(self.theta_b)
        y2 = y1 - L2 * math.cos(self.theta_b)

        arcade.draw_line(self.origin_x, self.origin_y, x1, y1, arcade.color.BLACK, 2)
        arcade.draw_line(x1, y1, x2, y2, arcade.color.BLACK, 2)

        arcade.draw_circle_filled(x1, y1, m1 / 2, arcade.color.RED)
        arcade.draw_circle_filled(x2, y2, m2 / 2, arcade.color.BLUE)

        arcade.draw_points(self.trace, arcade.color.GREEN, 2)

    def on_update(self, dt):
        for _ in range(int(self.settings["double_pendulum_simulator"]["speed"])):
            current_settings = self.settings["double_pendulum_simulator"]
            
            g = current_settings["gravity"]

            m1, m2 = current_settings["mass_a"], current_settings["mass_b"]
            L1, L2 = current_settings["length_a"], current_settings["length_b"]
            t1, t2 = self.theta_a, self.theta_b
            w1, w2 = self.omega_a, self.omega_b

            num1 = -g * (2 * m1 + m2) * math.sin(t1)
            num2 = -m2 * g * math.sin(t1 - 2 * t2)
            num3 = -2 * math.sin(t1 - t2) * m2 * (w2 ** 2 * L2 + w1 ** 2 * L1 * math.cos(t1 - t2))
            den = L1 * (2 * m1 + m2 - m2 * math.cos(2 * t1 - 2 * t2))
            a1 = (num1 + num2 + num3) / den

            num1 = 2 * math.sin(t1 - t2)
            num2 = w1 ** 2 * L1 * (m1 + m2)
            num3 = g * (m1 + m2) * math.cos(t1)
            num4 = w2 ** 2 * L2 * m2 * math.cos(t1 - t2)
            den = L2 * (2 * m1 + m2 - m2 * math.cos(2 * t1 - 2 * t2))
            a2 = (num1 * (num2 + num3 + num4)) / den

            self.omega_a += a1 * dt
            self.omega_b += a2 * dt

            self.theta_a += self.omega_a * dt
            self.theta_b += self.omega_b * dt

            x1 = self.origin_x + L1 * math.sin(self.theta_a)
            y1 = self.origin_y - L1 * math.cos(self.theta_a)

            x2 = x1 + L2 * math.sin(self.theta_b)
            y2 = y1 - L2 * math.cos(self.theta_b)

            if not current_settings["trail_size"] == 0:
                self.trace.append((x2, y2))

                if len(self.trace) > current_settings["trail_size"]:
                    self.trace = self.trace[-int(current_settings["trail_size"]):]
            else:
                self.trace = []