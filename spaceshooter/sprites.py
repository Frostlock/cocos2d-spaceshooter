import random, math

import cocos
import cocos.collision_model as cm
import cocos.euclid as eu
import cocos.actions as ac

import pyglet

from cocos.audio.pygame.mixer import Sound

from config import CONFIG


class ConfiguredSprite(cocos.sprite.Sprite):

    """
    Specialised sprite
        Gets configuration from config JSON
        Supports still or animated images
        Is located in and scaled to worldspace
    """
    @property
    def type(self):
        return self._type

    @property
    def config(self):
        return self._config

    @property
    def hasCollisionShape(self):
        return False

    @property
    def world_scale(self):
        return self._world_scale

    def world_to_view(self, v):
        """world coords to view coords; v an eu.Vector2, returns (float, float)"""
        return v.x / self.world_scale, v.y / self.world_scale

    def __init__(self, type, config, cx=0., cy=0., scale=1.0):
        self._type = type
        self._config = config
        self._world_scale = CONFIG["game"]["scale"]

        # Load image or animation for sprite
        if "image" in config.keys():
            image = config["image"]
            super(ConfiguredSprite, self).__init__(image)
        elif "animation" in config.keys():
            if config["animation"].lower()[-4:] == ".gif":
                animation = pyglet.image.load_animation(config["image"])
            else:
                image_sheet = pyglet.image.load(config["animation"])
                r, c = config["grid"]
                image_seq = pyglet.image.ImageGrid(image_sheet, r, c)
                if config["loop"] == True:
                    animation = image_seq.get_animation(config["period"], loop=True)
                else:
                    animation = image_seq.get_animation(config["period"], loop=False)
            super(ConfiguredSprite, self).__init__(animation)
        else:
            print "WARNING: No image or animation found for sprite."
            super(ConfiguredSprite, self).__init__(None)

        # Init scale
        if "scale" in self.config.keys():
            self.scale = scale * self.config["scale"]
        elif "scale_min" in self.config.keys() and "scale_max" in self.config.keys():
            # Set random scale between min and max
            random_scale = random.uniform(self.config["scale_min"], self.config["scale_max"])
            self.scale = scale * random_scale
        else:
            print("WARNING: Actor type " + self.type + " has no scale defined in config.")
            self.scale = scale
        # Apply world scale
        self.scale = self.scale / self.world_scale

        # Init position
        self.x = cx
        self.y = cy

        if "spawn_sound" in self.config.keys():
            self.sound = Sound(self.config["spawn_sound"])
            self.sound.play()

        if "time_to_live" in self.config.keys():
            self.do(ac.Delay(self.config["time_to_live"]) + ac.CallFunc(self.kill))

class Effect(ConfiguredSprite):

    """
    Effect
        has no collision shape
        is stationary
        automatically destroys when animation finishes
    """

    def __init__(self, effect_type, cx, cy):
        config = CONFIG["effects"][effect_type]
        super(Effect, self).__init__(effect_type, config, cx, cy, scale=1.0)

        if config["loop"] == False:
            # This works better than the scheduled calling of kill(), scheduled call could happen after object is destroyed leading to error.
            # TODO: This will go wrong for an effect with an image instead of an animation.
            self.do(ac.Delay(self.image.get_duration()) + ac.CallFunc(self.kill))

class Actor(ConfiguredSprite):
    """
    Actor has 
        collision shape and logic
        potential movement
    """

    @property
    def impulse(self):
        return self._impulse
    @impulse.setter
    def impulse(self, impulse):
        self._impulse = impulse

    @property
    def direction(self):
        """ Vector representation of current rotation"""
        a = math.radians(self.rotation)
        return eu.Vector2(math.sin(a), math.cos(a))

    @property
    def hasCollisionShape(self):
        return True

    def __init__(self, actor_type, config=None, cx=0., cy=0., scale=1.0):
        if config is None:
            config = CONFIG["actors"][actor_type]
        super(Actor, self).__init__(actor_type, config, cx, cy)

        self._impulse = eu.Vector2(0.0, 0.0)

        # Collision shape is a circle
        # Estimate radius by using sprite width
        # Use factor 0.98 to make the collision shape slightly smaller in size then the visual shape
        collision_radius = (self.width / 2.0) * 0.98
        self.cshape = cm.CircleShape(eu.Vector2(cx, cy), collision_radius)
        self.update_center(self.cshape.center)

        self._collman = None

        if self.type == "asteroid":
            # Put random spin on asteroids
            angle = random.randrange(-360,360)
            duration = 1 #/ self.scale
            self.do(ac.Repeat(ac.RotateBy(angle, duration)))
            #self.velocity = eu.Vector2(0.0,10)

        self.schedule(self.update)

    def update_center(self, cshape_center):
        """cshape_center must be eu.Vector2"""
        #TODO: insted of calling this use position directly put collisionshape as child node.
        # note that the center of the cshape is used to easily keep track of the actor location
        # not possible to add as childnode since circleshape is not a complete cocos node...
        self.position = cshape_center
        self.cshape.center = cshape_center

    def set_collision_manager(self, collman):
        """ By setting a collision manager this actor will check for collisions with other actors."""
        self._collman = collman

    def update(self, dt):
        # Update location based on current vectors
        pos = self.cshape.center
        newPos = pos + dt * self.impulse
        self.update_center(newPos)

        # Handle collisions
        if self._collman is not None:
            for other in self._collman.iter_colliding(self):
                if self.type == "bullet":
                    if other.type == 'asteroid':
                        # Create impact effect
                        expl = Effect("impact", self.x, self.y)
                        self.parent.add(expl, z=20)
                        # Remove self
                        self.kill()


class Ship(Actor):

    """
    Ship
        has propulsion related attributes
        can shoot
    """
    @property
    def top_speed(self):
        return self._top_speed

    @property
    def angular_velocity(self):
        return self._angular_velocity

    @property
    def acceleration(self):
        return self._acceleration

    @property
    def rate_of_fire(self):
        return self._rate_of_fire

    def __init__(self, ship_type, config=None, cx=0., cy=0., scale=1.0):
        if config is None:
            config = CONFIG["ships"][ship_type]
        super(Ship, self).__init__(ship_type, config, cx, cy, scale)

        self._top_speed = self.config['top_speed']
        self._angular_velocity = self.config['angular_velocity']  # angular velocity is in degrees per second
        self._acceleration = self.config['acceleration']
        self._rate_of_fire = self.config['rate_of_fire']  # shots per second


class Player(Ship):
    """
    Player
        is controlled by player
        can pick up prizes
    """

    def __init__(self, cx=0., cy=0., scale=1.0):
        config = CONFIG["ships"]["player"]
        super(Player, self).__init__("player", config, cx, cy, scale)

    def pickup_prize(self):
        """Random (mostly) beneficial effect will be applied to the player."""
        prize = random.choice(["Top speed increased!",
                               "Turning speed increased!",
                               "Acceleration increased!",
                               "Rate of fire increased!",
                               "Nothing gained..."])
        if prize == "Top speed increased!":
            self._top_speed += self.config["top_speed_increment"]
        elif prize == "Turning speed increased!":
            self._angular_velocity += self.config["angular_velocity_increment"]
        elif prize == "Acceleration increased!":
            self._acceleration += self.config["acceleration_increment"]
        elif prize == "Rate of fire increased!":
            self._rate_of_fire += self.config["rate_of_fire_increment"]
        return prize

