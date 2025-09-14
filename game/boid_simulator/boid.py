import arcade, arcade.math, random, math

class Boid(arcade.Sprite):
    def __init__(self, boid_num, x, y):
        super().__init__(arcade.load_texture("assets/graphics/boid.png"), center_x=x, center_y=y)

        random_angle = random.randint(0, 361)

        self.boid_num = boid_num
        self.direction = arcade.math.Vec2(math.cos(random_angle), math.sin(random_angle))
        
        self.velocity = 5
        self.radius = 10
        
        self.w_separation = 1.0
        self.w_cohesion = 1.0
        self.w_alignment = 1.0
        self.small_radius = 100
        self.large_radius = 250

    def calculate_separation(self, neighbours: list[int, arcade.math.Vec2, arcade.math.Vec2]):
        steeraway_vectors = [arcade.math.Vec2(*self.position) - neighbour[2] for neighbour in neighbours]

        if not steeraway_vectors:
            return self.direction

        return (sum(steeraway_vectors) / len(steeraway_vectors)).normalize()

    def calculate_alignment(self, neighbours: list[int, arcade.math.Vec2, arcade.math.Vec2]):
        directions = [neighbour[1] for neighbour in neighbours] 

        if not directions:
            return self.direction

        return (sum(directions) / len(directions)).normalize()
    
    def calculate_cohesion(self, neighbours: list[int, arcade.math.Vec2, arcade.math.Vec2]):
        positions = [neighbour[2] for neighbour in neighbours]

        if not positions:
            return self.direction

        return ((sum(positions) / len(positions)) - self.position).normalize()
    
    def update(self, window_width, window_height, boids):
        small_radius_neighbours, large_radius_neighbours = [], []
        for boid_data in boids:
            distance = boid_data[2].distance(arcade.math.Vec2(*self.position))
            if boid_data[0] == self.boid_num or distance > self.large_radius:
                continue
            
            if distance <= self.small_radius:
                small_radius_neighbours.append(boid_data)

            large_radius_neighbours.append(boid_data)

        self.direction = self.w_separation * self.calculate_separation(small_radius_neighbours) + self.w_alignment * self.calculate_alignment(large_radius_neighbours) + self.w_cohesion * self.calculate_cohesion(large_radius_neighbours)
        
        if self.direction.length() > 1:
            self.direction = self.direction.normalize()

        self.position += self.direction * self.velocity
        self.angle = 90 - math.degrees(self.direction.heading())

        if self.center_x <= self.radius:
            self.center_x = self.radius
            self.direction = self.direction.reflect(arcade.math.Vec2(1, 0))
        elif self.center_x >= (window_width * 0.8) - self.radius:
            self.center_x = (window_width * 0.8) - self.radius
            self.direction = self.direction.reflect(arcade.math.Vec2(-1, 0))

        if self.center_y <= self.radius:
            self.center_y = self.radius
            self.direction = self.direction.reflect(arcade.math.Vec2(0, 1))
        elif self.center_y >= window_height - self.radius:
            self.center_y = window_height - self.radius
            self.direction = self.direction.reflect(arcade.math.Vec2(0, -1))
