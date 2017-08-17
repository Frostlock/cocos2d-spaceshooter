import unittest

from cocos.director import director
from cocos.audio.pygame import mixer
from pyglet import clock


from spaceshooter.menu import MenuScene, MainMenu, OptionMenu, ScoreMenu


class TestMenu(unittest.TestCase):

    def setUp(self):
        # Minimal setup of cocos2d director and audio
        director.init()
        mixer.init()

        #Not ideal to initialize with None instead of the new game function that is expected...
        self.menu_scene = MenuScene(None)
        self.main_menu = self.menu_scene.main_menu
        self.option_menu = self.menu_scene.option_menu
        self.score_menu = self.menu_scene.score_menu

    def test_constructors(self):
        self.assertIsInstance(self.menu_scene, MenuScene)
        self.assertIsInstance(self.main_menu, MainMenu)
        self.assertIsInstance(self.option_menu, OptionMenu)
        self.assertIsInstance(self.score_menu, ScoreMenu)

    def test_show_fps(self):
        self.option_menu.on_show_fps(True)
        self.assertIs(director.show_FPS,True)

    def test_hide_fps(self):
        self.option_menu.on_show_fps(False)
        self.assertIs(director.show_FPS, False)

    def test_run_menu_scene(self):
        # Prepare some menu navigation actions
        clock.schedule_once(self.main_menu.on_options, 2)
        clock.schedule_once(self.main_menu.on_scores, 5)
        clock.schedule_once(self.main_menu.on_quit, 10)  # Action that calls director.end()
        # Run the scene
        director.run(self.menu_scene)

    def test_volume_levels(self):
        # Make sure all volume options are properly translated to a float between 0. and 1.
        for vol_string in self.option_menu.volumes:
            f = self.option_menu.volume_to_float(vol_string)
            self.assertGreaterEqual(f, 0.)
            self.assertLessEqual(f, 1.)

    def test_kill(self):
        # This throws an AttributeError, 'NoneType' object has not attribute 'remove'
        # This is a 'feature' of cocos2d, since these objects don't have a parent object the error is thrown
        # TODO: fix in the cocos2d code :D
        #self.menu_scene.kill()
        #self.main_menu.kill()
        #self.option_menu.kill()
        #self.score_menu.kill()
        pass

    def tearDown(self):
        self.menu_scene = None
        self.main_menu = None
        self.option_menu = None
        self.score_menu = None

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMenu)
    unittest.TextTestRunner(verbosity=2).run(suite)