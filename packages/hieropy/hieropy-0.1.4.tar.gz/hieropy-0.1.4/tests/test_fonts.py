import unittest

from hieropy.options import Options
from hieropy.uniconstants import Rectangle
from hieropy.printables import measure_glyph_pdf, measure_glyph_pil, \
	measure_glyph_pdf_memo, em_size_of, PrintedPdf
from hieropy.hieroparsing import UniParser

@unittest.skip("Temporarily skipping this test class")
class TestFonts(unittest.TestCase):
	def omit_test_measure(self):
		ch = chr(0x13000)
		# ch = chr(0x130B7) # flat
		# ch = chr(0x130C0) # tall
		fontsize = 40
		x_scale = 1
		y_scale = 1
		rotate = 180
		mirror = True
		meas = measure_glyph_pdf(ch, fontsize, x_scale, y_scale, rotate, mirror)
		# print(meas.x, meas.y, meas.w, meas.h)
		meas2 = measure_glyph_pdf_memo(ch, fontsize, x_scale, y_scale, rotate, mirror)
		# print(meas2.x, meas2.y, meas2.w, meas2.h)

	def test_measure_pil(self):
		ch = chr(0x13000)
		ch = chr(0x130B7) # flat
		# ch = chr(0x130C0) # tall
		fontsize = 40
		x_scale = 1.001
		y_scale = 1
		# rotate = 180
		rotate = 0
		mirror = False
		meas = measure_glyph_pil(ch, x_scale, y_scale, rotate, mirror)
		# print(meas)

	def omit_test_em_size(self):
		ch1 = chr(0x13000)
		ch2 = chr(0x130B7)
		fontsize = 40
		x_scale = 1
		y_scale = 1
		rotate = 180
		mirror = True
		# print(em_size_of(ch1, fontsize, x_scale, y_scale, rotate, mirror))
		# print(em_size_of(ch2, fontsize, x_scale, y_scale, rotate, mirror))
	
	def test_printed_pdf(self):
		ch1 = chr(0x13000)
		ch2 = chr(0x13005)
		scale = 1
		x_scale = 1
		y_scale = 1
		rotate = 0
		mirror = False
		printed = PrintedPdf(3, 3, 0, 0, Options())
		rect1 = Rectangle(0, 0, 5, 10)
		rect2 = Rectangle(0, 1, 5, 10)
		printed.add_sign(ch1, scale, x_scale, y_scale, rotate, mirror, rect1)
		printed.add_sign(ch2, scale, x_scale, y_scale, rotate, mirror, rect2)
		# im = printed.get_pil()
		# im.save("testimage.png")
		# with open('testimage.pdf', 'wb') as f:
			# f.write(printed.get_pdf())

	def omit_test_format(self):
		parser = UniParser()
		fragments = [\
			'𓃀𓐰𓈖𓈖𓐰𓆱𓐰𓐍𓐱𓏏𓀜𓏏𓏲𓆑𓀀𓅓𓋹𓍑𓋴𓅓𓎛𓎿𓋴𓀁𓇋𓏠𓐰𓈖𓅆',
			'𓈖𓐰𓄿𓇋𓇋𓏦𓐰𓎢𓂋𓐰𓍿𓀀𓐱𓁐𓐰𓏦𓏇𓇋𓐪𓂧𓐰𓏌𓏛𓐰𓏦𓐍𓐰𓂋𓊪𓏏𓐰𓂋',
			'𓇋𓆵𓁻𓆟𓂋𓐰𓈙𓏤𓆑𓐰𓄿𓀋𓂡𓅯𓄿𓇋𓇋𓋴𓏏',
			'𓊪𓏏𓐰𓂋𓇋𓆵𓁻𓂞𓏲𓈖𓐰𓎢𓈖𓐰𓄿𓃀𓂧𓐰𓏏𓐱𓏲']
		options = Options(fontsize=40, typ='pdf')
		for _ in range(50):
			for f in fragments:
				parsed = parser.parse(f)
				parsed.print(options).get_pil()
