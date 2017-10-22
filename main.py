#!/usr/bin/env python3

from gi.repository import Gtk
import subprocess, os
from bs4 import BeautifulSoup

import faulthandler # degugging library
faulthandler.enable()

class xkcdViewer(Gtk.Window):
	def __init__(self):

		Gtk.Window.__init__(self, title="XKCD Viewer")
     	
        # set the default window values
		self.set_default_size(900, 750)


def main():
		try:
			subprocess.call("wget google.com")
		except:
			badName_dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
						Gtk.ButtonsType.CLOSE, "You need internet to run this program!")
			errorNoInternet.run()
			errorNoInternet.destroy()

		home = os.environ["HOME"]
		os.chdir(home)

		try:
			os.mkdir(".xkcdViewer")
		except:
			if os.path.isdir(".xkcdViewer"):
				pass

		os.chdir(".xkcdViewer")

		if os.path.isfile("index.html"):
			subprocess.call("rm -rf index.html")
			subprocess.call("wget http://xkcd.com", shell=True)
		else:
			subprocess.call("wget http://xkcd.com", shell=True)

		soup = BeautifulSoup(open("index.html"))
		element = soup.select("#comic img")
	
		imgCode = str(element[0])

		with open("img.html", "w") as imgFile:
			imgFile.write(imgCode)
       	
       	
window = xkcdViewer()
window.show_all()
window.connect("delete-event", Gtk.main_quit)
Gtk.main()
