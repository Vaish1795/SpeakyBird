import random
import yaml

from itertools import chain
from global_var import *
from supporter import *

phrase_y_segments = []


class BG(pg.sprite.Sprite):
    def __init__(self, group, bg_image, settings):
        super().__init__(group)
        self.settings = settings
        self.background = bg_image
        self.rect = self.background.get_rect()

        width_scale_factor = self.settings.game_screen_width / (3 * self.background.get_width())
        height_scale_factor = self.settings.game_screen_height / (self.background.get_height())

        scale_factor = max(width_scale_factor, height_scale_factor)
        self.bg = pg.transform.scale(self.background, (int(self.background.get_width() * scale_factor),
                                                       int(self.background.get_height() * scale_factor)))
        self.image = repeat_image(self.settings, self.bg)


class BaseImage(pg.sprite.Sprite):
    def __init__(self, settings, constants, group, base_image, x, y):
        super().__init__(group)
        self.settings = settings
        self.constants = constants
        self.base = base_image
        self.rect = self.base.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.ground_bg = pg.transform.scale(self.base, (int(self.base.get_width()), int(self.base.get_height())))
        self.scroll_speed = self.constants.scroll_speed
        self.ground_scroll = self.constants.ground_scroll
        self.update_image()

    def update(self, dt):
        self.ground_scroll -= self.scroll_speed * dt * self.constants.target_fps
        if abs(self.ground_scroll) > self.ground_bg.get_width():
            self.ground_scroll = 0
        self.update_image()

    def update_image(self):
        # Create a surface to hold the repeated images
        self.image = repeat_image(self.settings, self.ground_bg, self.ground_scroll)

class Bird(pg.sprite.Sprite):
    def __init__(self, settings, constants, group, images, ground, sounds, x=0, y=0):
        super().__init__(group)
        self.settings = settings
        self.constants = constants
        self.bird_images = images
        self.ground = ground
        self.sounds = sounds
        self.bird_index = 0
        self.image = self.bird_images[self.bird_index]
        self.rect = self.image.get_rect()
        self.bird_vel = self.constants.bird_vel
        self.bird_vel_y = 10
        self.counter = 0
        self.bird_flap = self.constants.bird_flap
        self.bird_alive = self.constants.bird_alive

        self.bird_x = y
        self.bird_y = x

        self.rect.center = (self.bird_x, self.bird_y)
        self.level_pipes = False
        self.level_fireball = False
        self.sound = global_var.level_settings.get_setting('sound')

        self.level_pipes = global_var.level_settings.get_setting('pipes')
        self.level_fireball = global_var.level_settings.get_setting('fireball')

    def jump(self, maybe_jump):
        if not self.level_pipes or not maybe_jump or self.bird_flap or self.rect.y <= 0 or not self.bird_alive:
            return
        self.bird_flap = True
        self.bird_vel = -6 #defines how high the bird jumps. The lower the value, the higher the bird jumps
        print(f'jump sound: {self.sound}')
        if self.sound:
            self.sounds['wing'].play()
        if self.rect.y < 0:
            self.rect.y = 0

    def movement(self, moving_up, moving_down, effective_screen_height):
        screen_height = effective_screen_height - 15
        bird_height = self.rect.height
        bird_movement_distance = 5

        if moving_up:
            self.bird_y -= bird_movement_distance
            if self.bird_y < bird_height // 2:
                self.bird_y = bird_height // 2
                # self.animate()

        if moving_down:
            self.bird_y += bird_movement_distance
            if self.bird_y > screen_height - bird_height // 2:
                self.bird_y = screen_height - bird_height // 2
                # self.animate()

        # Adjusting for moving up to the top of the screen
        if self.bird_y < bird_height // 2:
            self.bird_y = bird_height // 2

        self.animate()
        self.rect.y = self.bird_y

    def rotate_bird(self):
        self.image = pg.transform.rotate(self.bird_images[self.bird_index], self.bird_vel * -7)

    def gravity(self):
        self.bird_vel += 0.15
        if self.bird_vel > 2: #defines how fast the bird falls. The higher the value, the faster the bird falls
            self.bird_vel = 2
        if self.rect.bottom < self.ground.rect.top:
            self.rect.y += int(self.bird_vel)
        if self.bird_vel > -8:
            self.bird_flap = False

    def animate(self):
        # handle animation
        if self.bird_alive:
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.bird_index += 1
                if self.bird_index >= len(self.bird_images):
                    self.bird_index = 0
                self.image = self.bird_images[self.bird_index]

    def update(self, delta_time, user_input, flying):
        if self.level_pipes:
            # handle gravity
            if flying:
                self.gravity()
            # handle animation
            self.animate()
            self.rotate_bird()

        if self.level_fireball:
            self.animate()

class BirdWalk(pg.sprite.Sprite):
    def __init__(self, settings, constants, group, images, ground, sounds, x, y):
        super().__init__(group)
        self.settings = settings
        self.constants = constants
        self.bird_images = images
        self.ground = ground
        self.sounds = sounds
        self.index = 0
        self.counter = 0
        self.bird_x = x
        self.bird_y = y
        self.is_moving = False
        self.is_jumping = False
        self.jump_target = None
        self.jump_stage = 0  # 0: prepare to jump, 1: jump, 2: land, 3: end
        self.image = self.bird_images['start']
        print(f"bird height {self.image.get_height()}")
        print(f"bird rect height {self.image.get_rect().height}")
        self.rect = self.image.get_rect(center=(self.bird_x, self.bird_y))
        self.rect.center = (self.bird_x, self.bird_y)
        self.bird_vel_y = 20
        self.bird_vel_x = 3
        self.bird_vel = 5
        self.bird_alive = self.constants.bird_alive

        self.effective_height = self.settings.game_screen_height - self.ground.rect.height

        self.pause_duration = 100
        self.pause_start_time = 0
        self.current_stair_index = 0
        self.next_stair_index = 1
        self.paused = False
        self.jump_to_next_stair = False

        self.sound = global_var.level_settings.get_setting('sound')
        self.reached_stair = False
        self.is_sound_played = False
        self.is_running = False
    # Returns true if the bird completed jump from previous stair.
    def stair_jump_complete(self):
        if self.current_stair_index == self.next_stair_index:
            self.next_stair_index += 1
            return True
        else:
            return False

    def all_stairs_jumped(self):
        if self.current_stair_index == len(global_var.stairs):
            print("Jump complete")
            return True
        return False

    def update_position_bird_for_stairs(self, score_manager):
        current_time = pg.time.get_ticks()

        # Control horizontal running movement
        if self.is_moving and not self.is_jumping:
            if self.bird_x < global_var.stop_position:
                self.bird_x += self.bird_vel
                self.is_running = True  # Set running state when moving horizontally

                if self.bird_x >= global_var.stop_position:
                    # Reached stop point or stair
                    self.reached_stair = True
                    self.is_jumping = self.jump_to_next_stair  # Prepare for jump if needed
                    self.is_running = False  # Stop running
                    # self.is_moving = False  # Stop horizontal movement
                    self.sounds['running'].stop()  # Stop running sound
            else:
                self.is_jumping = self.jump_to_next_stair
                self.bird_vel_x = 3
                self.bird_vel_y = 20

        # Allow jumping logic to proceed independently of `is_running`
        if self.is_jumping:
            if self.sound and not self.is_sound_played:
                self.sounds['stairjump'].play()
                self.sounds['stairjump'].set_volume(0.5)
                self.is_sound_played = True

            elapsed_time = current_time - self.pause_start_time
            if elapsed_time >= self.pause_duration:
                # Move horizontally and vertically for jump
                self.bird_x += self.bird_vel_x
                self.bird_y -= self.bird_vel_y
                self.bird_vel_y -= 1  # Simulate gravity
                self.paused = False

                # Check collision with stairs
                if not self.paused:
                    self.reached_stair = False
                    stair_rect = global_var.stairs[self.current_stair_index]
                    if self.rect.colliderect(stair_rect):
                        # Collision with stair
                        score_manager.increment_score(5)
                        self.bird_y = stair_rect.top - (self.rect.height // 2)

                        self.bird_vel_y = 0
                        self.bird_vel_x = 0

                        # Reset for next jump
                        self.paused = True
                        self.pause_start_time = current_time
                        self.is_running = False  # Stop running after landing
                        if self.sound:
                            self.sounds['running'].stop()
                        self.is_moving = False
                        self.reached_stair = True
                        self.is_sound_played = False

                        if self.jump_to_next_stair:
                            if self.current_stair_index < len(global_var.stairs) - 1:
                                next_stair_start = global_var.stairs[self.current_stair_index + 1].left
                                if (next_stair_start - self.bird_x) > 50:
                                    self.is_jumping = False
                                    self.is_moving = True
                                    self.is_running = True
                                    self.reached_stair = False
                                    global_var.stop_position = global_var.stairs[self.current_stair_index + 1].left - 50
                            else:
                                self.is_jumping = False
                                self.is_moving = True
                                self.is_running = True
                                self.reached_stair = False
                                global_var.stop_position = self.settings.game_screen_width - (self.rect.width // 2)
                            self.current_stair_index += 1
                            self.jump_to_next_stair = False

        # Update rect position
        self.rect.topleft = (self.bird_x, self.bird_y)

    def animate(self):
        # Ensure 'run' images are available
        if not self.bird_images.get('run'):
            print("Error: 'run' images not found.")
            return

        # Play running animation only if `is_running` is True
        if self.is_running:
            self.counter += 1
            step_cooldown = 5

            # Change the image based on the counter
            if self.counter > step_cooldown:
                self.counter = 0  # Reset counter
                self.index = (self.index + 1) % len(self.bird_images['run'])
                self.image = self.bird_images['run'][self.index]
                if self.sound and not self.is_jumping and not self.reached_stair:
                    self.sounds['running'].play()
        else:
            # Set to static image if not running
            self.image = self.bird_images['start']
            self.index = 0  # Reset the index to the start image

        # Update the rect to match the new image position
        self.rect = self.image.get_rect(center=(self.bird_x, self.bird_y))

    def update(self, score_manager):
        self.update_position_bird_for_stairs(score_manager)
        self.animate()

class Pipe(pg.sprite.Sprite):
    def __init__(self, pipe_image, constants, x, y, position):
        super().__init__()
        self.position = position
        self.constants = constants
        self.entered = False
        self.exit = False
        self.passed = False
        self.image = pipe_image
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.pipe_position()

    def pipe_position(self):
        if self.position == 'upper':
            self.rect.bottomleft = [self.x, self.y - int(self.constants.pipe_gap / 2)]
        elif self.position == 'lower':
            self.rect.topleft = [self.x, self.y + int(self.constants.pipe_gap / 2)]

    def update(self, dt, score_manager):
        self.rect.x -= self.constants.target_fps * dt * self.constants.scroll_speed
        if self.rect.right < 0:
            self.kill()

        # score
        if self.position == 'lower':
            if self.constants.bird_start_x > self.rect.topleft[0] and not self.passed:
                self.entered = True
            if self.constants.bird_start_x > self.rect.topright[0] and not self.passed:
                self.exit = True
            if self.exit and self.entered and not self.passed:
                self.passed = True
                score_manager.increment_score()

        return score


class Fireball(pg.sprite.Sprite):
    def __init__(self, settings, constants, images, x, y, bird_sprites, sounds):
        super().__init__()
        self.settings = settings
        self.constants = constants
        self.bird_sprites = bird_sprites
        self.sounds = sounds
        self.fireball_images = images
        self.image = self.fireball_images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.fireball_index = 0
        self.counter = 0
        self.fireball_vel = self.constants.fireball_speed
        self.last_update = pg.time.get_ticks()
        self.animation_delay = 100

        self.mask = pg.mask.from_surface(self.image)

    def update(self, effective_screen_height):
        self.rect.x -= self.constants.scroll_speed
        now = pg.time.get_ticks()
        if now - self.last_update > self.animation_delay:
            self.fireball_index = (self.fireball_index + 1) % len(self.fireball_images)
            self.image = self.fireball_images[self.fireball_index]
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
            self.mask = pg.mask.from_surface(self.image)
            self.last_update = now

        # Ensure fireball stays within the effective screen height
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > effective_screen_height:
            self.rect.bottom = effective_screen_height - 100

        if self.rect.right < 0:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class RandomPhrase(pg.sprite.Sprite):
    def __init__(self, settings, constants, effective_screen_height, positive_phrase, negative_phrase):
        super().__init__()
        self.settings = settings
        self.constants = constants
        self.positive_sprites = positive_phrase
        self.negative_sprites = negative_phrase
        self.positive_phrases = []
        self.negative_phrases = []
        self.read_phrases_and_words()
        self.text = ''
        self.color = (255, 255, 255)
        self.create_random_phrase()
        self.image = self.settings.phrases_font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.settings.game_screen_width
        # self.rect.y = random.randint(100, effective_screen_height - 200)
        self.rect.y = get_new_phrase_y_coord(effective_screen_height, self)
        # self.rect.y = y_coord
        self.mask = pg.mask.from_surface(self.image)
        self.speed = -1.7
        self.positive_mask = None
        self.negative_mask = None

    def read_phrases_and_words(self):
        with open(self.settings.phrases_path, 'r') as file:
            phrases_data = yaml.safe_load(file)
        self.positive_phrases = phrases_data['positive']
        self.negative_phrases = phrases_data['negative']

    def create_random_phrase(self):
        self.color = get_random_color() # Update color for each new phrase
        if random.random() < 0.3:
            self.text = random.choice(self.positive_phrases)
            self.positive_sprites.add(self)  # Add self to positive_sprites
        else:
            self.text = random.choice(self.negative_phrases)
            self.negative_sprites.add(self)  # Add self to negative_sprites
        self.image = self.settings.phrases_font.render(self.text, True, self.color)
        self.rect = self.image.get_rect()
        self.rect.x = self.settings.game_screen_width

    def update(self, dt):
        self.rect.x += self.speed
        if self.rect.right < 0:
            self.kill()

        # Check for overlapping with other phrases and adjust position
        self.check_and_adjust_overlap()

    def check_and_adjust_overlap(self):
        # Check overlap with other positive phrases
        for sprite in chain(self.positive_sprites, self.negative_sprites):
            if sprite != self and self.rect.colliderect(sprite.rect):
                self.rect.y = max(self.rect.y, sprite.rect.bottom + 55)
        # for sprite in self.positive_sprites:
        #     if sprite != self and self.rect.colliderect(sprite.rect):
        #         self.rect.y = max(self.rect.y, sprite.rect.bottom + 55)
        #
        # # Check overlap with other negative phrases
        # for sprite in self.negative_sprites:
        #     if sprite != self and self.rect.colliderect(sprite.rect):
        #         self.rect.y = max(self.rect.y, sprite.rect.bottom + 55)


class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, image, settings, phrase_sprites, positive_sprites, negative_sprites, sounds, particles):
        super().__init__()
        self.settings = settings
        self.sounds = sounds
        self.particle = particles
        self.negative_sprites = negative_sprites
        self.positive_sprites = positive_sprites
        self.phrase_sprites = phrase_sprites
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.centery = y
        self.speed = 10

    def update(self, score_manager):
        self.rect.x += self.speed
        self.check_collision(score_manager)
        if self.rect.left > self.settings.game_screen_width:
            self.kill()

    def check_collision(self, score_manager):
        for negative_phrase in self.negative_sprites:
            if pg.sprite.collide_mask(self, negative_phrase):
                negative_phrase.kill()
                if global_var.level_settings.get_setting('sound'):
                    self.sounds['balloon_pop'].play()
                create_particles(negative_phrase.rect.center, self.particle)
                self.kill()  #kill bullet
                score_manager.increment_score()

        for positive_phrase in self.positive_sprites:
            if pg.sprite.collide_mask(self, positive_phrase):
                positive_phrase.kill()
                if global_var.level_settings.get_setting('sound'):
                    self.sounds['wrong'].play()
                self.kill()
                score_manager.decrement_score()


class Particle(pg.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.position = list(position)
        self.velocity = [random.uniform(-2, 2), random.uniform(-2, 2)]
        self.timer = random.randint(30, 60)
        # self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        self.color = get_random_color()

        self.image = pg.Surface((4, 4), pg.SRCALPHA)
        pg.draw.circle(self.image, self.color, (3, 3), 4)
        self.rect = self.image.get_rect(center=position)

    def update(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.rect.center = self.position
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Staircase(pg.sprite.Sprite):
    def __init__(self, group, settings, stair_image, base_image, num_steps):
        super().__init__(group)
        self.settings = settings
        self.num_steps = num_steps
        self.base_image = base_image
        base_image_width, base_image_height = base_image.get_size()
        self.stair_image = pg.transform.scale(stair_image, (base_image_width, base_image_height))
        stair_image_width, stair_image_height = self.stair_image.get_size()
        new_surface = pg.Surface((base_image_width, self.settings.game_screen_height))
        # Blit the first image at the top
        new_surface.blit(self.base_image, (0, 0))
        # Calculate the starting position for img2
        y_offset = base_image_height
        # Stack img2 vertically
        while y_offset < self.settings.game_screen_height:
            new_surface.blit(self.stair_image, (0, y_offset))
            y_offset += stair_image_height

        self.image = new_surface
        self.rect = self.image.get_rect()
        self.step_height = stair_image_height
        self.staircase = []

        # Fill the combined image with base images and stairs
        for step in range(self.num_steps):
            block_x = self.settings.game_screen_width - 200 * (self.num_steps - step)
            block_y = self.settings.game_screen_height - (1 + 0.5 * (step + 1)) * self.step_height
            self.staircase.append((block_x, block_y))
            stair_rect = pg.Rect(block_x, block_y, base_image_width, stair_image_height)
            global_var.stairs.append(stair_rect)  # Store positions in self.stairs
        global_var.stop_position = global_var.stairs[0].left - 50
        print(f"stop_position {global_var.stop_position}")

    def update(self, screen):
        for block_pos in self.staircase:
            self.rect.topleft = block_pos  # Update rect for each block position
            screen.blit(self.image, self.rect)  # Blit the image at the updated rect


class StarRing:
    def __init__(self, center, num_stars, radius_x, radius_y, tilt_angle, angle_increment, offset_angle):
        self.center = center
        self.num_stars = num_stars
        self.radius_x = radius_x
        self.radius_y = radius_y
        self.tilt_angle = tilt_angle
        self.angle_increment = angle_increment
        self.offset_angle = offset_angle
        self.angle = 0
        self.stars = []

    def update(self):
        self.angle += self.angle_increment
        self.angle %= 360
        self.stars = self.calculate_ellipse_points(self.center, self.radius_x, self.radius_y, self.angle,
                                                   self.tilt_angle, self.num_stars, self.offset_angle)

    def draw(self, surface):
        for star in self.stars:
            draw_star(surface, star[0], star[1])

    def calculate_ellipse_points(self, center, radius_x, radius_y, angle_offset, tilt_angle, num_points, offset_angle):
        points = []
        for i in range(num_points):
            theta = math.radians(i * (360 / num_points) + angle_offset + offset_angle)
            x = center[0] + radius_x * math.cos(theta) * math.cos(math.radians(tilt_angle))
            y = center[1] + radius_y * math.sin(theta) * math.sin(math.radians(tilt_angle))
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            points.append(((x, y), color))
        return points

# function to draw stars over head once the bird dies
def draw_star(surface, center, color, size=5):
    points = []
    for i in range(5):
        angle = i * 144  # Star points are 144 degrees apart
        radian = math.radians(angle)
        x = center[0] + size * math.cos(radian)
        y = center[1] + size * math.sin(radian)
        points.append((x, y))
    pg.draw.polygon(surface, color, points)


#function to create particles when the bullet hits the phrase in fireball mode
def create_particles(position, particles_sprites):
    for _ in range(20):
        particle = Particle(position)
        particles_sprites.add(particle)


def shoot(bird, bullet_sprites, bullet_image, settings, phrase_sprites, positive_sprites, negative_sprites, sounds,
          particles):
    bullet = Bullet(bird.rect.right, bird.rect.centery, bullet_image, settings, phrase_sprites, positive_sprites,
                    negative_sprites, sounds, particles)
    bullet_sprites.add(bullet)


def spawn_phrase(settings, constants, effective_screen_height, phrase_sprites, positive_sprites, negative_sprites):
    if len(phrase_sprites) < 3:
        # phrase_y_coord = get_new_phrase_y_coord(effective_screen_height)
        phrase = RandomPhrase(settings, constants, effective_screen_height, positive_sprites, negative_sprites)
        phrase_sprites.add(phrase)


def spawn_fireball(images, settings, constants, screen, fireball_sprites, bird_sprites, sounds):
    fireball = Fireball(settings, constants, images, screen.get_width(), random.randint(0, screen.get_height()),
                        bird_sprites, sounds)
    fireball_sprites.add(fireball)


def spawn_pipes(images, settings, constants, effective_screen_height, pipe_sprites):
    pipe_upper = images['pipe_upper']
    pipe_lower = images['pipe_lower']
    # Randomly determine the mid point of the upper and lower pipes
    mid_point = random.randint(constants.pipe_gap, effective_screen_height - constants.pipe_gap)

    # Create new pipes
    upper_pipe = Pipe(pipe_upper, constants, settings.screen.get_width(),
                      int(effective_screen_height) - mid_point, 'upper')
    lower_pipe = Pipe(pipe_lower, constants, settings.screen.get_width(),
                      int(effective_screen_height) - mid_point, 'lower')

    # Add pipes to the sprite group
    pipe_sprites.add(upper_pipe)
    pipe_sprites.add(lower_pipe)


def get_random_color():
    # Generate a random dark red or purple color
    if random.random() < 0.5:
        # Dark red shades
        return random.randint(100, 255), 0, 0
    else:
        # Dark purple shades
        return 100, 0, random.randint(200, 255)


def get_new_phrase_y_coord(effective_screen_height, phrase_sprite):
    phrase_height = phrase_sprite.rect.height
    print(phrase_height)
    effective_y_range = [phrase_height + 20, effective_screen_height - phrase_height - 20]
    y_segment_possibilities = np.arange(1, np.floor((effective_y_range[1] - effective_y_range[0]) / phrase_height))
    actual_possibilities = [i for i in y_segment_possibilities if i not in phrase_y_segments]
    y_segment_choice = random.choice(actual_possibilities)
    y_coord = random.randint(effective_y_range[0] * y_segment_choice, effective_y_range[0] * (y_segment_choice + 1))
    phrase_y_segments.append(y_segment_choice)
    if len(phrase_y_segments) > 3:
        phrase_y_segments.pop(0)
    return y_coord
