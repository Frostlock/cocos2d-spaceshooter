import unittest

from cocos.director import director
from cocos.audio.pygame import mixer
from pyglet import clock

from cocos.scene import Scene
from cocos.layer import Layer
import cocos.euclid as eu

from spaceshooter.sprites import Projectile

class TestProjectile(unittest.TestCase):

    def setUp(self):
        # Minimal setup of cocos2d director and audio
        director.init()
        mixer.init()
        
    def test_default_constructor(self):
        self.default_projectile = Projectile()
        self.assertIsInstance(self.default_projectile, Projectile)

    def test_specific_constructors(self):
        bullet_1 = Projectile(projectile_type="bullet",level=1,bounce_count=0)
        self.assertIsInstance(bullet_1, Projectile)
        bullet_1_b = Projectile(projectile_type="bullet", level=1, bounce_count=1)
        self.assertIsInstance(bullet_1_b, Projectile)
        bullet_2 = Projectile(projectile_type="bullet", level=2, bounce_count=0)
        self.assertIsInstance(bullet_2, Projectile)
        bullet_2_b = Projectile(projectile_type="bullet", level=2, bounce_count=1)
        self.assertIsInstance(bullet_2_b, Projectile)
        bullet_3 = Projectile(projectile_type="bullet", level=3, bounce_count=0)
        self.assertIsInstance(bullet_3, Projectile)
        bullet_3_b = Projectile(projectile_type="bullet", level=3, bounce_count=1)
        self.assertIsInstance(bullet_3_b, Projectile)
        bullet_4 = Projectile(projectile_type="bullet", level=4, bounce_count=0)
        self.assertIsInstance(bullet_4, Projectile)
        bullet_4_b = Projectile(projectile_type="bullet", level=4, bounce_count=1)
        self.assertIsInstance(bullet_4_b, Projectile)
        bomb_1 = Projectile(projectile_type="bomb", level=1, bounce_count=0)
        self.assertIsInstance(bomb_1, Projectile)
        bomb_1_b = Projectile(projectile_type="bomb", level=1, bounce_count=1)
        self.assertIsInstance(bomb_1_b, Projectile)
        bomb_2 = Projectile(projectile_type="bomb", level=2, bounce_count=0)
        self.assertIsInstance(bomb_2, Projectile)
        bomb_2_b = Projectile(projectile_type="bomb", level=2, bounce_count=1)
        self.assertIsInstance(bomb_2_b, Projectile)
        bomb_3 = Projectile(projectile_type="bomb", level=3, bounce_count=0)
        self.assertIsInstance(bomb_3, Projectile)
        bomb_3_b = Projectile(projectile_type="bomb", level=3, bounce_count=1)
        self.assertIsInstance(bomb_3_b, Projectile)
        bomb_4 = Projectile(projectile_type="bomb", level=4, bounce_count=0)
        self.assertIsInstance(bomb_4, Projectile)
        bomb_4_b = Projectile(projectile_type="bomb", level=4, bounce_count=1)
        self.assertIsInstance(bomb_4_b, Projectile)

    def test_error_constructors(self):
        self.assertRaises(ValueError, Projectile, "wrongtype")

    def test_run_animations(self):
        layer = Layer()

        bullet = Projectile(projectile_type="bullet",level=1,bounce_count=0)
        bullet.update_center(eu.Vector2(10, 10))
        layer.add(bullet)
        bullet = Projectile(projectile_type="bullet", level=2, bounce_count=0)
        bullet.update_center(eu.Vector2(10, 30))
        layer.add(bullet)
        bullet = Projectile(projectile_type="bullet", level=3, bounce_count=0)
        bullet.update_center(eu.Vector2(10, 50))
        layer.add(bullet)
        bullet = Projectile(projectile_type="bullet", level=4, bounce_count=0)
        bullet.update_center(eu.Vector2(10, 70))
        layer.add(bullet)

        bullet = Projectile(projectile_type="bullet", level=1, bounce_count=1)
        bullet.update_center(eu.Vector2(30, 10))
        layer.add(bullet)
        bullet = Projectile(projectile_type="bullet", level=2, bounce_count=1)
        bullet.update_center(eu.Vector2(30, 30))
        layer.add(bullet)
        bullet = Projectile(projectile_type="bullet", level=3, bounce_count=1)
        bullet.update_center(eu.Vector2(30, 50))
        layer.add(bullet)
        bullet = Projectile(projectile_type="bullet", level=4, bounce_count=1)
        bullet.update_center(eu.Vector2(30, 70))
        layer.add(bullet)

        bomb = Projectile(projectile_type="bomb", level=1, bounce_count=0)
        bomb.update_center(eu.Vector2(50, 10))
        layer.add(bomb)
        bomb = Projectile(projectile_type="bomb", level=2, bounce_count=0)
        bomb.update_center(eu.Vector2(50, 30))
        layer.add(bomb)
        bomb = Projectile(projectile_type="bomb", level=3, bounce_count=0)
        bomb.update_center(eu.Vector2(50, 50))
        layer.add(bomb)
        bomb = Projectile(projectile_type="bomb", level=4, bounce_count=0)
        bomb.update_center(eu.Vector2(50, 70))
        layer.add(bomb)

        bomb = Projectile(projectile_type="bomb", level=1, bounce_count=1)
        bomb.update_center(eu.Vector2(70, 10))
        layer.add(bomb)
        bomb = Projectile(projectile_type="bomb", level=2, bounce_count=1)
        bomb.update_center(eu.Vector2(70, 30))
        layer.add(bomb)
        bomb = Projectile(projectile_type="bomb", level=3, bounce_count=1)
        bomb.update_center(eu.Vector2(70, 50))
        layer.add(bomb)
        bomb = Projectile(projectile_type="bomb", level=4, bounce_count=1)
        bomb.update_center(eu.Vector2(70, 70))
        layer.add(bomb)

        clock.schedule_once(self.end_director, 10)
        scene = Scene(layer)
        director.run(scene)

    def end_director(self, dt):
        director.scene.end(None)

    def tearDown(self):
        pass

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProjectile)
    unittest.TextTestRunner(verbosity=2).run(suite)