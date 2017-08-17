from __future__ import division, unicode_literals

import random
import math

import pyglet
from pyglet.window import key
from pyglet.gl import *

import cocos
from cocos.director import director
import cocos.collision_model as cm
import cocos.euclid as eu
import cocos.actions as ac

from cocos.audio.pygame.mixer import Sound
from cocos.audio.pygame import mixer

from config import CONFIG
from sprites import Actor, Effect, Player
from menu import MenuScene
from menu import MainMenu, OptionMenu, ScoreMenu


class MessageLayer(cocos.layer.Layer):

    """
        Transitory messages appearing on the screen
    """

    log_messages = []

    def show_message(self, msg, callback=None):
        w, h = director.get_window_size()

        self.msg = cocos.text.Label(msg,
                                    font_size=52,
                                    font_name=CONFIG['view']['font_name'],
                                    anchor_y='center',
                                    anchor_x='center',
                                    width=w,
                                    multiline=True,
                                    align="center")
        self.msg.position = (w / 2.0, h)

        self.add(self.msg)

        actions = (
            ac.Show() + ac.Accelerate(ac.MoveBy((0, -h / 2.0), duration=0.5)) +
            ac.Delay(0.8) +
            ac.Accelerate(ac.MoveBy((0, -h / 2.0), duration=0.5)) +
            ac.Hide()
        )

        if callback:
            actions += ac.CallFunc(callback)

        self.msg.do(actions)

    def log_message(self, message):
        w, h = director.get_window_size()
        font_size = 10
        line_height = font_size + 4

        # Move previous messages up
        for pm in self.log_messages:
            pm.do(ac.MoveBy((0, line_height),0.5))

        #TODO: Might be good to clean up message history at some point.
        #Or making them visible by pressing a button (to look back at what happened)

        # Prepare new message
        lbl = cocos.text.Label(message,
                                    font_size=font_size,
                                    font_name=CONFIG['view']['font_name'],
                                    anchor_y='bottom',
                                    anchor_x='left',
                                    width=w,
                                    multiline=True,
                                    align="left")

        lbl.position = (10, 10 - line_height)
        self.add(lbl)
        self.log_messages.append(lbl)

        actions = (
            ac.Show() +
            ac.MoveBy((0, line_height), 0.5) +
            ac.Delay(8) +
            ac.FadeOut(0.5)
        )
        lbl.do(actions)


class KeyBoardControl(cocos.layer.Layer):

    """
    Keyboardcontroller for player
    """
    is_event_handler = True

    @property
    def player(self):
        return self._player

    def __init__(self, player):
        self._player = player

        # Initialize button dictionary to keep track of key presses
        self.bindings = CONFIG["game"]['bindings']
        self.buttons = {}
        for k, v in self.bindings.iteritems():
            self.buttons[v] = 0

        self.schedule(self.update)


class GameControl(cocos.layer.Layer):

    """
    Responsabilities:
        Generation: random generates a level
        Initial State: Set initial playststate
        Play: updates level state, by time and user input. Detection of
        end-of-level conditions.
        Level progression.
    """
    is_event_handler = True

    def __init__(self, message_layer):
        super(GameControl, self).__init__()
        self.message_layer = message_layer

        # Scale this world layer and position it correctly so that it fits the window
        self.width = CONFIG["window"]["width"] * CONFIG["game"]["scale"]
        self.height = CONFIG["window"]["height"] * CONFIG["game"]["scale"]
        self.scale = 1 / CONFIG["game"]["scale"]
        pos_x = (CONFIG["window"]["width"] - self.width) / 2 / CONFIG["game"]["scale"]
        pos_y = (CONFIG["window"]["height"] - self.height) / 2 / CONFIG["game"]["scale"]
        self.position = pos_x, pos_y

        # load sounds:
        sounds = {}
        sounds["start_game"] = Sound(CONFIG['sounds']['start_game'])
        sounds["pickup"] = Sound(CONFIG['sounds']['pickup'])
        self.sounds = sounds

        #todo: figure out a good way to set collision cell size?
        #cell_size = self.rPlayer * self.asteroid_scale_max * 2.0 * 1.25
        cell_size = 5.0
        self.collman = cm.CollisionManagerGrid(0.0, self.width,
                                               0.0, self.height,
                                               cell_size, cell_size)

        # Initialize button dictionary to keep track of key presses
        self.bindings = CONFIG["game"]['bindings']
        self.buttons = {}
        for k, v in self.bindings.iteritems():
            self.buttons[v] = 0

        self._time_since_last_shot = 0

        self.toRemove = set()
        self.schedule(self.update)
        self.ladder_begin()

    def ladder_begin(self):
        self.player = None
        self.level_num = 0
        self.empty_level()
        msg = 'Get ready!'
        self.sounds["start_game"].play()
        self.message_layer.show_message(msg, callback=self.level_launch)

    def level_launch(self):
        self.generate_random_level()
        msg = 'level %d' % self.level_num
        self.message_layer.show_message(msg, callback=self.level_start)

    def level_start(self):
        self.win_status = 'undecided'
        self.message_layer.log_message("Collect all upgrades to open the wormhole!")

    def level_conquered(self):
        self.player.do(ac.FadeOut(0.5))
        self.win_status = 'intermission'
        msg = 'level %d\ncomplete!' % self.level_num
        self.message_layer.show_message(msg, callback=self.level_next)

    def level_losed(self):
        self.win_status = 'losed'
        self.player = None
        msg = 'Game Over'
        self.message_layer.show_message(msg, callback=self.ladder_begin)

    def level_next(self):
        self.empty_level()
        self.level_num += 1
        self.level_launch()

    def empty_level(self):
        # del old actors, if any
        for node in self.get_children():
            if node is not self.player:
                self.remove(node)
        self.gate = None
        self.prize_cnt = 0
        self.toRemove.clear()
        self.win_status = 'intermission'  # | 'undecided' | 'conquered' | 'losed'

    def generate_random_level(self):
        # hardcoded params:
        prize_num = 1
        asteroid_num = 10
        z = 0

        # add player
        cx, cy = (0.5 * self.width, 0.5 * self.height)
        if self.player is None:
            self.player = Player(cx, cy)
            self.add(self.player, z=1000)
        else:
            self.player.update_center(eu.Vector2(cx, cy))
            self.player.impulse = eu.Vector2(0., 0.)
            self.player.do(ac.FadeIn(0.5))
        min_separation = self.player.width / 2.0
        self.collman.add(self.player)

        # add gate
        self.gate = Actor('gate', None, cx, cy)
        self.gate.color = CONFIG["game"]["palette"]["gate_closed"]
        cntTrys = 0
        while cntTrys < 100:
            cx = random.randrange(self.gate.width, self.width - self.gate.width)
            cy = random.randrange(self.gate.height, self.height - self.gate.height)
            self.gate.update_center(eu.Vector2(cx, cy))
            if not self.collman.they_collide(self.player, self.gate):
                break
            cntTrys += 1
        self.add(self.gate, z=z)
        z += 1
        self.collman.add(self.gate)

        # add prize
        self.cnt_prize = 0
        for i in range(prize_num):
            prize = Actor('prize', None, cx, cy)
            cntTrys = 0
            while cntTrys < 100:
                cx = random.randrange(prize.width, self.width - prize.width)
                cy = random.randrange(prize.height, self.height - prize.height)
                prize.update_center(eu.Vector2(cx, cy))
                if self.collman.any_near(prize, min_separation) is None:
                    self.cnt_prize += 1
                    self.add(prize, z=z)
                    z += 1
                    self.collman.add(prize)
                    break
                cntTrys += 1

        # add asteroids
        for i in range(asteroid_num):
            asteroid = Actor('asteroid', None, cx, cy)
            cntTrys = 0
            while cntTrys < 100:
                cx = random.randrange(asteroid.width, self.width - asteroid.width)
                cy = random.randrange(asteroid.height, self.height - asteroid.height)
                asteroid.update_center(eu.Vector2(cx, cy))
                if self.collman.any_near(asteroid, min_separation) is None:
                    self.add(asteroid, z=z)
                    z += 1
                    self.collman.add(asteroid)
                    break
                cntTrys += 1

    def update(self, dt):
        # if not playing dont update model
        if self.win_status != 'undecided':
            return

        # update collman
        self.collman.clear()
        for z, node in self.children:
            if node.hasCollisionShape:
                self.collman.add(node)

        # Handle player collisions
        # TODO: can we move this into the player?
        # Not so easy since these have impact on game progress
        for other in self.collman.iter_colliding(self.player):
            other_type = other.type
            if other_type == 'prize':
                self.toRemove.add(other)
                self.cnt_prize -= 1
                self.sounds["pickup"].play()
                prize_msg = self.player.pickup_prize()
                self.message_layer.log_message(prize_msg)
                if not self.cnt_prize:
                    self.open_gate()
            elif (other_type == 'asteroid' or
                  other_type == 'gate' and self.cnt_prize > 0):
                # Fade out player image and create explosion effect
                expl = Effect("player_explosion", self.player.x, self.player.y)
                self.message_layer.log_message("Asteroid collision!")
                self.player.do(ac.Hide())
                self.add(expl, z=20)
                self.level_losed()
            elif other_type == 'gate':
                self.level_conquered()

        # Handle keyboard events
        self.handle_keyboard_events(dt)

        if self.player is not None:
            # Player should bounce from window borders
            newPos = self.player.cshape.center
            r = self.player.cshape.r
            new_impulse = self.player.impulse
            if newPos.x < r:
                new_impulse = -self.reflection_y(new_impulse)
            if newPos.x > (self.width - r):
                new_impulse = -self.reflection_y(new_impulse)
            if newPos.y < r:
                new_impulse = self.reflection_y(new_impulse)
            if newPos.y > (self.height - r):
                new_impulse = self.reflection_y(new_impulse)
            self.player.impulse = new_impulse

        # at end of frame do removes
        for node in self.toRemove:
            self.remove(node)
        self.toRemove.clear()

    def handle_keyboard_events(self, dt):
        # Only update player when game is undecided
        if self.win_status == 'undecided':
            # Player rotation
            rot = self.buttons[self.bindings['right']] - self.buttons[self.bindings['left']]
            if rot != 0:
                self.player.rotation += rot * dt * self.player.angular_velocity
                # a = math.radians(self.player.rotation)
                # self.player.direction = eu.Vector2(math.sin(a), math.cos(a))

            # Player speed
            newVel = self.player.impulse
            mov = self.buttons[self.bindings['forward']] - self.buttons[self.bindings['backward']]
            if mov != 0:
                newVel += dt * mov * self.player.acceleration * self.player.direction
                nv = newVel.magnitude()
                if nv > self.player.top_speed:
                    newVel *= self.player.top_speed / nv
                exhaust_x = self.player.x - self.player.direction.x * 10
                exhaust_y = self.player.y - self.player.direction.y * 10
                exhaust = Effect("exhaust", exhaust_x, exhaust_y)
                self.add(exhaust, z=15)
            self.player.impulse = newVel

            # Shooting
            self._time_since_last_shot += dt
            if self.buttons[self.bindings['shoot']] == 1:
                if self._time_since_last_shot > 1 / self.player.rate_of_fire:
                    bullet_x = self.player.x + self.player.direction.x * 10
                    bullet_y = self.player.y + self.player.direction.y * 10
                    bullet = Actor("bullet", None, bullet_x, bullet_y)
                    bullet.set_collision_manager(self.collman)
                    bullet.rotation = self.player.rotation
                    #laser should take direction a shoot straight
                    bullet.impulse = 500 * eu.Vector2(self.player.direction.x, self.player.direction.y)
                    #bullet should take impulse
                    #bullet.impulse = 2 * eu.Vector2(self.player.impulse.x, self.player.impulse.y)
                    self.add(bullet, z=15)
                    self._time_since_last_shot = 0

    def reflection_y(self, a):
        assert isinstance(a, eu.Vector2)
        return eu.Vector2(a.x, -a.y)

    def open_gate(self):
        self.gate.color = CONFIG["game"]["palette"]["gate_open"]
        #TODO: for some reason this overlaps with the last prize pickup message, I think it is due to two messages being logged in the same frame/pyglet update
        self.message_layer.log_message("Wormhole open!")

    def on_key_press(self, k, m):
        if k in self.buttons.keys():
            self.buttons[k] = 1
            return True
        return False

    def on_key_release(self, k, m):
        if k in self.buttons.keys():
            self.buttons[k] = 0
            return True
        return False

class PrizeCollectorScene(cocos.scene.Scene):

    def __init__(self):
        super(PrizeCollectorScene, self).__init__()

        # Window background color
        r, g, b = CONFIG["game"]["palette"]["background"]
        #bg = cocos.layer.ColorLayer(r, g, b, 255, int(self.width), int(self.height))
        self.add(cocos.layer.ColorLayer(r, g, b, 255), z=-1)
        # Message layer
        message_layer = MessageLayer()
        self.add(message_layer, z=1)
        # Animation layer
        playview = GameControl(message_layer)
        self.add(playview, z=0)

        # Music
        self.music = Sound(CONFIG["music"]["level"])
        self.music.set_volume(CONFIG["music"]["volume"])

    def on_enter(self):
        super(PrizeCollectorScene, self).on_enter()
        # Start Music
        self.music.play(-1)

    def on_exit(self):
        super(PrizeCollectorScene, self).on_exit()
        # Stop Music
        self.music.stop()

class SpaceShooterGame(object):

    def __init__(self):
        # Initialize pyglet
        pyglet.font.add_file(CONFIG["view"]["font_file"])

        # Initialize audio mixer
        mixer.init()
        #self.music = None

        # Initialize cocos2d director
        director.init(**CONFIG['window'])

        # Prepare main menu
        self.menu_scene = MenuScene(self.new_game)

    def main_menu(self):
        director.run(self.menu_scene)

    def new_game(self):
        #scene = cocos.scene.Scene()

        # # Window background color
        # scene.add(cocos.layer.ColorLayer(0, 65, 133, 255), z=-1)
        # # Message layer
        # message_layer = MessageLayer()
        # scene.add(message_layer, z=1)
        # # Animation layer
        # playview = Worldview(fn_show_message=message_layer.show_message)
        # scene.add(playview, z=0)

        # #Music
        # #TODO: move to on_enter
        # if self.music is not None: self.music.stop()
        # self.music = Sound(CONFIG["music"]["level"])
        # self.music.play(-1)
        # self.music.set_volume(CONFIG["music"]["volume"])

        scene = PrizeCollectorScene()
        director.push(scene)

        #director.run(self.menu_scene)


#
# if __name__ == "__main__":
#     ssg = SpaceShooterGame()
#     ssg.main_menu()
#     #ssg.new_game()