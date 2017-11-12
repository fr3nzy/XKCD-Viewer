#! python3

import gi
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, Gdk, Gio, WebKit, Notify
import os, requests, bs4, urllib.request, time

# dependencies: gir1.2-webkit-3.0, notify

class App(Gtk.Window):
	def __init__(self):
		Gtk.Window.__init__(self, title="XKCD Viewer")

		self.hb = Gtk.HeaderBar() 
		self.hb.set_show_close_button(True)
		self.hb.props.title = "XKCD"
		self.hb.set_property('spacing', 10)
		self.set_titlebar(self.hb) # titlebar set to headerbar

		# download button	
		self.downloadBtn = Gtk.Button()
		self.downloadBtn.connect('clicked', self.downloadBtn_activate) # signal handler for downloadBtn activate
		icon = Gio.ThemedIcon(name="go-down-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		self.downloadBtn.set_tooltip_text('Download current comic')
		self.downloadBtn.add(image)
		self.hb.pack_end(self.downloadBtn) # pack download button end of headerbar
		
		box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8) # box for left-right buttons
		
		# previous button 
		self.previousBtn = Gtk.Button()
		self.previousBtn.connect('clicked', self.previousBtn_activate) # signal handler for previousBtn activate
		icon = Gio.ThemedIcon(name="go-previous-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		self.previousBtn.set_tooltip_text('Previous comic')
		self.previousBtn.add(image)
		box.add(self.previousBtn) # pack previous button start of horizontal box - child of box
		
		# next button
		self.nextBtn = Gtk.Button()
		self.nextBtn.connect('clicked', self.nextBtn_activate) # signal handler for nextBtn activate
		icon  = Gio.ThemedIcon(name="go-next-symbolic")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		self.nextBtn.set_tooltip_text('Next comic')
		self.nextBtn.add(image)
		box.add(self.nextBtn) # pack next button after previous button - child of box
		
		self.hb.pack_start(box) # pack horizontal box start of headerbar
		
		# webview to load and display web data		
		self.webview = WebKit.WebView()	
		self.webview.set_full_content_zoom(True)
		scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
		scroll.set_size_request(700, 500)
		scroll.add(self.webview)
		self.add(scroll)
		
		self.url = "http://xkcd.com"
		
		
	def accel(self):
		accel = Gtk.AccelGroup()  # using Gtk as the accel group
		# shortcut for <ctrl>I 
		accel.connect(Gdk.keyval_from_name('I'), Gdk.ModifierType.CONTROL_MASK, 0, self.zoomIn)
		# shortcut for <ctrl>I 
		accel.connect(Gdk.keyval_from_name('O'), Gdk.ModifierType.CONTROL_MASK, 0, self.zoomOut)
		self.add_accel_group(accel)  # add Gtk accel group to accelerators
	
		
	def previousBtn_activate(self, previousBtn):
		self.CN = int(self.CN)
		self.CN = self.CN - 1  # current comic no. - 1
		self.CN  = str(self.CN)
		prevUrl = 'http://xkcd.com/'+ self.CN # previous url
		print(prevUrl)
		self.url = prevUrl
		
		self.accel()
		self.get_comic_url()
		self.load()
		
		
	def nextBtn_activate(self, nextBtn):
		self.CN = int(self.CN)
		self.CN = self.CN + 1  # current comic no. +1
		self.CN = str(self.CN)
		nextUrl = 'http://xkcd.com/' + self.CN # next url
		print(nextUrl)
		self.url = nextUrl
		
		self.accel()
		self.get_comic_url()
		self.load()


	def save_comic(self, dialog):
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			canSave = True
			# download image
			url = dialog.get_filename()
			os.chdir(url)
			print(self.url)
			
			os.system('wget ' + self.comicUrl)
			dialog.destroy()
			time.sleep(1.0)
			# notification 
			Notify.init('xkcd')
			saved = Notify.Notification.new("Default Title","Default Body")
			saved.update("'" + self.title + "' saved successfully")
			saved.show()
		else: 
			print('error')
			dialog.destroy()
				

	def downloadBtn_activate(self, downloadBtn):
		dialog = Gtk.FileChooserDialog('Save Comic to drive', self, 
				Gtk.FileChooserAction.SELECT_FOLDER,
				(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, 
				Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
		self.save_comic(dialog)

	
	def zoomIn(self, w, x, y, z):
		self.webview.zoom_in()
		
		
	def zoomOut(self, w, x , y, z):
		self.webview.zoom_out()
		
		
	def load(self):
		# load webview with url for comic image + set subtitle of titlebar to name of the comic
		home = os.path.expanduser('~')  # $HOME
		xkcdFolder = home + '/.xkcd'
		print(xkcdFolder)
		if not os.path.exists(xkcdFolder):   # if xkcdFolder isn't present
			os.chdir(os.path.expanduser('~'))
			os.makedirs('.xkcd')
			os.chdir('.xkcd')
		else:
			os.chdir(xkcdFolder)  # go into folder
		with open('comic.html', 'w') as f:
			# html markup to center  image
			f.write('<html>\n<center>\n<img src="' + self.comicUrl + '"/>\n</center>\n</html>')  
			
		self.webview.open(xkcdFolder + '/comic.html')
			
		res = requests.get(self.url)  # download current/next/prev comic
		soup = bs4.BeautifulSoup(res.text, 'lxml') # create bs4 object of res
		self.title = soup.select('#ctitle') # select <div id="ctitle'>
		self.title = self.title[0].getText() 
		print(self.title)
		self.hb.set_subtitle(self.title)  # set subtitle to title of current shown comic
		
		
	def get_comic_url(self):
		res = requests.get(self.url)
		try:
			res.raise_for_status()
		except Exception as e:
			print("failed")
		soup = bs4.BeautifulSoup(res.text, 'lxml')
		
		# get url for current xkcd.com comic
		comicElem = soup.select('#comic img') # url of comic located after <div id='comic'> and in img tag
		self.comicUrl = 'http:' + comicElem[0].get('src') # http: + url of comic locating in <img src="">
		print(self.comicUrl)	
		
		# get number of current comic
		self.CN = soup.select('a[rel="prev"]') # select <a> with rel="prev"
		self.CN = self.CN[0].get('href') # number for main page xkcd.com comic 
		self.CN = self.CN[1:-1] # trim '/value/' to 'value'
		self.CN = int(self.CN)  # convert str to int
		self.CN = self.CN + 1 # current comic
		print(self.CN)
		

def main():
	
	win = App()
	
	win.accel()
	win.get_comic_url()
	win.load()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	
	
	
main()
Gtk.main()		
