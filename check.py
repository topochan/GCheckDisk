#!/usr/bin/env python
import gobject
import gtk
import pygtk
import sys
import os
import gtk
from listdisks import listdisks
import subprocess

'''Constant for easy modifications, next version I use dictionaries'''
COL_PATH = 0
COL_PIXBUF = 2
VOLUME_STORE=0
VOLUME_VOLUM=1
VOLUME_FS=4
VOLUME_MOUNT=3
DISK_STORE=0
DISK_PRODUCT=1

class CheckDisk:
	
	
	def about_check(self,widget):
		about=self.builder.get_object('aboutWin')
		about.set_logo(self.diskIcon)		
		about.run()
		about.hide()
		
	
	def error_message(self, message):
		print message
		# create an error message dialog and display modally to the user
		dialog = gtk.MessageDialog(None,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
		dialog.run()
		dialog.destroy()
	
	'''
	Event form combobox, get the partitions and disks from self(init method)
	and iterate to find the partitions from disk selected at iconview and fill
	data at form.
	
	'''
	def on_cb_change(self,combo):
		
		selected=combo.get_active_text()
		for volume in self.volums:
			if selected ==volume[VOLUME_VOLUM]:
				self.lbVolume.set_text(volume[VOLUME_VOLUM])
				self.lbFS.set_text(volume[VOLUME_FS])
				if volume[VOLUME_MOUNT]!='':
					self.lbMount.set_text(volume[VOLUME_MOUNT])
					self.hboxWarning.show()
					self.btCheck.set_sensitive(False)
					
					
				else:
					self.hboxWarning.hide()
					self.lbMount.set_text("None")
					self.btCheck.set_sensitive(True)					
	
	'''
	Help method for get icon from actual theme, we pass size and name icon
	'''
	def get_icon(self, name, size):
		theme = gtk.icon_theme_get_default()
		return theme.load_icon(name, size, 0)
		
	'''
	Fill comobox model declarated at builder file(glade)
	'''
	def fill_comboBox(self,volums,disk):
		self.comboModel.clear()

		for volum in volums:
			if volum[VOLUME_STORE]==self.disks[disk][DISK_STORE]:
				self.comboModel.append([str(volum[VOLUME_VOLUM]),volum[VOLUME_FS],self.volumIcon])
	
	'''
	Fill iconView with disk stores
	'''
	def fill_iconView(self,disks):
		self.iconModel.clear()
		
		for disk in disks:			
			self.iconModel.append([disk[DISK_STORE]+"\n"+disk[DISK_PRODUCT],disk[DISK_PRODUCT],self.diskIcon])
			
	
	'''
	When iconView double click activate this callback
	'''
	def on_listaDiscos_selection_changed(self,widget):
		self.clear_data()
		self.fill_comboBox(self.volums,widget.get_text_column())
	
	'''
	Easy method to quit app
	'''
	def quit_app(self,widget):
		gtk.main_quit()
	'''
	Refres list of Disks and fill into IconView
	'''
	def refresh_disks(self,widget):
		self.disks, self.volums = listdisks.discover()
		self.fill_iconView(self.disks)
		self.clear_data()
		
	'''Reset the state of form to initial'''		
	def clear_data(self):
		
		self.comboModel.clear()
		self.lbVolume.set_text("None")
		self.lbFS.set_text("None")
		self.lbMount.set_text("None")
		self.btCheck.set_sensitive(False)
		self.hboxWarning.hide()
		
	'''Launch check to actual selected partition, lauch gobject io_add_watch to fill buffer text'''		
	def launch_check(self,widget):
		self.wCheck.show()
		self.textBufferVT.set_text("")
		
		if self.sourceId!=None:
			gobject.source_remove(self.sourceId)

		cmd="fsck -y " + self.lbVolume.get_text()		
		command = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE) 
		self.sourceId=gobject.io_add_watch(command.stdout, gobject.IO_IN | gobject.IO_HUP,
			self.read_output)
		self.lbStatus.set_text("Checking partition " + self.lbVolume.get_text())
		self.wCheck.show()
		
	'''Callback for io_add_watch to fill textBuffer'''
	def read_output(self,source, condition):
		if condition == gobject.IO_IN:
			line = source.readline()
			self.progress.pulse()
			self.textBufferVT.insert_at_cursor(line)
		if condition == gobject.IO_HUP:
			self.progress.set_fraction(1)
			self.textBufferVT.insert_at_cursor("Command finished.\n")
			return False
		return True
	
	'''
	
	Callback to hide check window
	
	'''
	def on_btCerrar_clicked(self, widget):
		self.wCheck.hide()
				
		
	def __init__(self):
		
		'''Init variables and data from aplication'''
		self.sourceId=None
		self.disks, self.volums = listdisks.discover()
		self.shareDir ='share'
		self.update = True
		self.xmlFile = 'check.glade'
		self.pathGlade= os.path.join(sys.path[0],self.shareDir,self.xmlFile)		
		self.iconImage='icon.png'
		self.iconPath = os.path.join(sys.path[0],self.shareDir,self.iconImage)
		self.diskIcon=self.get_icon(gtk.STOCK_HARDDISK,48)
		self.volumIcon= self.get_icon(gtk.STOCK_HARDDISK,22)

		self.builder = gtk.Builder()
		self.builder.add_from_file(self.pathGlade) 

		self.builder.connect_signals(self)
		'''Init widgets that we use in app'''
		self.iconModel=self.builder.get_object('iconModel')
		self.comboModel=self.builder.get_object('comboModel')
		self.iconView = self.builder.get_object('listaDiscos')
		self.window= self.builder.get_object('mainWindow')
		self.combo = self.builder.get_object('cbPartitions')
		self.lbVolume = self.builder.get_object('lbVolume')
		self.lbFS = self.builder.get_object('lbFsType')
		self.lbMount = self.builder.get_object('lbMount')
		self.lbStatus = self.builder.get_object('lbStatus')
		self.hboxWarning=self.builder.get_object('hboxWarning')
		self.btCheck=self.builder.get_object('btCheck')
		self.textBufferVT=self.builder.get_object('textBufferVT')
		self.wCheck= self.builder.get_object('wCheck')
		self.progress= self.builder.get_object('pbCheck')
		

		
		'''Set icon from app'''
		self.window.set_icon_from_file(self.iconPath)
		
		'''Fill for fist time iconView'''		
		self.fill_iconView(self.disks)
		self.iconView.set_text_column(COL_PATH)
		self.iconView.set_pixbuf_column(COL_PIXBUF)
		
		'''Init combobox render'''
		self.cellImage = gtk.CellRendererPixbuf()
		self.cellVolum = gtk.CellRendererText()
		self.cellFS = gtk.CellRendererText()
		self.combo.pack_start(self.cellVolum, True)
		self.combo.pack_start(self.cellFS, True)
		self.combo.pack_start(self.cellImage,True)
		self.combo.add_attribute(self.cellVolum, 'text', 0)
		self.combo.add_attribute(self.cellFS, 'text', 1)
		self.combo.add_attribute(self.cellImage,'pixbuf',2)


	def main(self):
		self.window.show()
		gtk.main()
if __name__ == "__main__":
	check = CheckDisk()
	check.main()


