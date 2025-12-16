import unittest

from hieropy.options import Options
from hieropy.printables import PrintedPil, OrthogonalHull, Rectangle

@unittest.skip("Temporarily skipping this test class")
class TestHull(unittest.TestCase):
	def test_hull(self):
		ch1 = chr(0x13000)
		printed = PrintedPil(3, 3, 0, 0, Options())
		rect = Rectangle(1, 1, 1, 1)
		printed.add_sign(ch1, 1, 1, 1, 0, False, rect)
		hull = OrthogonalHull(printed.get_pil(), 5)
		# print(hull.x_mins.values(), hull.x_maxs.values(), hull.y_mins.values(), hull.y_maxs.values())
