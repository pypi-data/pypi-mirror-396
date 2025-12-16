import unittest
import tkinter as tk

from hieropy.treedrawing import TkTreeNode, TkTrees

@unittest.skip("Temporarily skipping this test class")
class TestPanel():
	def __init__(self):
		root = tk.Tk()
		frame = tk.Frame(root, bg="white", bd=0, width=600, height=700)
		frame.pack(fill="x")
		self.canvas = tk.Canvas(frame, bd=0, bg="green", width=300, height=400)
		# self.canvas.grid(row=0, column=0, sticky='nsew')
		self.canvas.grid(row=0, column=0, sticky='e')
		scroll_v = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
		scroll_v.grid(row=0, column=1, sticky='ns')
		scroll_h = tk.Scrollbar(frame, orient="horizontal", command=self.canvas.xview)
		scroll_h.grid(row=1, column=0, sticky='ew')
		self.canvas.configure(yscrollcommand=scroll_v.set, xscrollcommand=scroll_h.set)
		frame.grid_rowconfigure(0, weight=1)
		frame.grid_columnconfigure(0, weight=1)
		root.bind("<a>", lambda e: self.add_root())
		root.bind("<r>", lambda e: self.remove_root())

		self.trees = TkTrees(self.canvas)
		node1 = self.trees.create_node()
		node1.button.config(text="1")
		node2 = self.trees.create_node()
		node2.button.config(text="2")
		node3 = self.trees.create_node()
		node3.button.config(text="3")
		node4 = self.trees.create_node()
		node4.button.config(text="4")
		self.trees.append_child(node1)
		node1.append_child(node2)
		node2.append_child(node3)
		node3.append_child(node4)
		self.trees.refresh()
		root.mainloop()

	def add_root(self):
		node5 = self.trees.create_node()
		node5.button.config(text="5")
		self.trees.append_child(node5)
		self.trees.refresh()

	def remove_root(self):
		some_root = self.trees.trees[5]
		self.trees.remove_child(some_root)
		self.trees.refresh()

@unittest.skip("Temporarily skipping this test class")
class TestTreeDraw(unittest.TestCase):
	def test_draw(self):
		# test = TestPanel()
		pass

if __name__ == '__main__':
	unittest.main()
