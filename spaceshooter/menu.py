from cocos.director import director
from cocos.menu import *
from cocos.scene import Scene
from cocos.layer import MultiplexLayer, ColorLayer
from cocos.sprite import Sprite

import pyglet

from cocos.audio.pygame.mixer import Sound

from config import CONFIG


def init_layout(menu):
    # init fonts
    menu.font_title['font_name'] = CONFIG["view"]["font_name"]
    menu.font_title['font_size'] = 64
    menu.font_item['font_name'] = CONFIG["view"]["font_name"]
    menu.font_item['font_size'] = 28
    menu.font_item_selected['font_name'] = CONFIG["view"]["font_name"]
    menu.font_item_selected['font_size'] = 32
    menu.font_item_selected['color'] = (212, 175, 55, 255)
    # align menu
    menu.menu_valign = CENTER
    menu.menu_halign = RIGHT
    # Sound on activation of menu item
    menu.activate_sound = Sound(CONFIG["sounds"]["menu_select"])

class MainMenu(Menu):

    def __init__(self, new_game_func):

        # call superclass with the title
        super(MainMenu, self).__init__("Torvec")

        init_layout(self)

        items = []
        items.append(MenuItem('New Game', new_game_func))
        items.append(MenuItem('Options', self.on_options))
        items.append(MenuItem('Scores', self.on_scores))
        items.append(MenuItem('Quit', self.on_quit))
        self.create_menu(items, zoom_in(), zoom_out())

    # Callbacks
    def on_options(self):
        self.parent.switch_to(1)

    def on_scores(self):
        self.parent.switch_to(2)

    def on_quit(self):
        director.pop()


class OptionMenu(Menu):

    def __init__(self):
        super(OptionMenu, self).__init__("Options")

        init_layout(self)

        items = []

        items.append(ToggleMenuItem('Fullscreen: ', self.on_fullscreen, False))

        items.append(ToggleMenuItem('Show FPS: ', self.on_show_fps, False))

        self.volumes = ['Off', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', 'Max']
        items.append(MultipleMenuItem('Sounds: ', self.on_sound_volume, self.volumes, 8))
        items.append(MultipleMenuItem('Music: ', self.on_music_volume, self.volumes, 3))

        items.append(MenuItem('Back', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())
        #self.create_menu(items, shake(), shake_back())

    # Callbacks
    def on_fullscreen(self, value):
        director.window.set_fullscreen(value)

    def on_show_fps(self, value):
        director.show_FPS = value

    def on_sound_volume(self, value):
        print value
        #TODO: store in config file

    def on_music_volume(self, value):
        print value
        #TODO: store in config file

    def on_quit(self):
        self.parent.switch_to(0)


class ScoreMenu(Menu):

    def __init__(self):
        super(ScoreMenu, self).__init__("Scores")

        init_layout(self)

        items = []

        items.append(MenuItem('Nothing yet!', self.do_nothing))
        items.append(MenuItem('Back', self.on_quit))

        self.create_menu(items, zoom_in(), zoom_out())

    def do_nothing(self):
        pass

    def on_quit(self):
        self.parent.switch_to(0)


class MenuScene(Scene):

    def __init__(self, new_game_func):
        super(MenuScene, self).__init__()

        # Prepare main menu
        menulayer = MultiplexLayer(MainMenu(new_game_func), OptionMenu(), ScoreMenu())
        self.add(ColorLayer(0, 0, 0, 255), z=-1)
        # Animated shield
        shield_anim = pyglet.image.load_animation(CONFIG["graphics"]["rotating_shield"])
        shield_sprite = Sprite(shield_anim)
        shield_sprite.x = shield_sprite.width / 2 - 30
        shield_sprite.y = shield_sprite.height / 2
        self.add(shield_sprite, z=0)
        self.add(menulayer, z=1)

        # The scene class actually has music functionality but so far I have been unable to make it work.
        # Instead I have overloaded the on_enter and on_ext functions to deal with music.
        self.music = Sound(CONFIG["music"]["menu"])
        self.music.set_volume(CONFIG["music"]["volume"])

    def on_enter(self):
        super(MenuScene, self).on_enter()
        # Start Music
        self.music.play(-1)

    def on_exit(self):
        super(MenuScene, self).on_exit()
        # Stop Music
        self.music.stop()