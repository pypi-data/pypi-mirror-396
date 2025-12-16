import unittest
import tkinter as tk

from hieropy.previewdrawing import TkPreview

@unittest.skip("Temporarily skipping this test class")
class TestPanel():
	def __init__(self):
		root = tk.Tk()
		frame = tk.Frame(root, bg="green", bd=0)
		frame.pack(fill="x")
		self.canvas = tk.Canvas(frame, bd=0, bg="white", width=600, height=400)
		# self.canvas.grid(row=0, column=0, sticky='nsew')
		self.canvas.grid(row=0, column=0, sticky='ne')
		scroll_v = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
		scroll_v.grid(row=0, column=1, sticky='ns')
		scroll_h = tk.Scrollbar(frame, orient="horizontal", command=self.canvas.xview)
		scroll_h.grid(row=1, column=0, sticky='ew')
		self.canvas.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)
		root.bind("<a>", lambda e: self.add_node())
		root.bind("<r>", lambda e: self.remove_node())
		root.bind("<f>", lambda e: self.incr_focus())
		root.bind("<d>", lambda e: self.decr_focus())

		self.preview = TkPreview(self.canvas, 30, 6)
		self.preview.dir = 'h'
		node1 = self.preview.create_node(0)
		node1.button.config(text="1")
		node2 = self.preview.create_node(1)
		node2.button.config(text="2")
		node3 = self.preview.create_node(0)
		node3.button.config(text="3")
		node4 = self.preview.create_node(1)
		node4.button.config(text="4")
		self.preview.refresh()
		root.mainloop()

	def add_node(self):
		node5 = self.preview.create_node(2)
		node5.button.config(text="5")
		self.preview.refresh()

	def remove_node(self):
		self.preview.remove_node(2)
		self.preview.refresh()

	def incr_focus(self):
		self.preview.focus += 1
		self.preview.refresh()

	def decr_focus(self):
		self.preview.focus -= 1
		self.preview.refresh()

class TestPreviewDraw(unittest.TestCase):
	def test_draw(self):
		# test = TestPanel()
		pass

if __name__ == '__main__':
	pass
	unittest.main()
