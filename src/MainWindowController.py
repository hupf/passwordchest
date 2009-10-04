#
#  MainWindowController.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from AppKit import *
from loxodo.vault import Vault
import time

from datasource import ListDataSource, RecordNode
from EntryWindowController import EntryWindowController

class MainWindowController(NSWindowController):
    filename = None
    vault = None
    
    removeButton = IBOutlet()
    
    titleLabel = IBOutlet()
    usernameLabel = IBOutlet()
    urlLabel = IBOutlet()
    notesLabel = IBOutlet()
    lastModifiedLabel = IBOutlet()
    infoView = IBOutlet()
    outlineView = IBOutlet()
    
    dataSource = None

    def init(self):
        self = super(MainWindowController, self).init()
        if self is None: return None
        
        self.vault = Vault('123456')
        self.vault.modified = False
        self.entryWindowController = EntryWindowController.alloc().initWithMainWindowController_(self)
        
        self = self.initWithWindowNibName_("MainWindow")
        self.setWindowFrameAutosaveName_("MainWindow")
        self.showWindow_(self)
        self.retain()
        
        return self
    
    def initWithFilename_andVault_(self, filename, vault):
        self = super(MainWindowController, self).init()
        if self is None: return None
        
        self.filename = filename
        self.vault = vault
        self.vault.modified = False
        self.entryWindowController = EntryWindowController.alloc().initWithMainWindowController_(self)
        
        self = self.initWithWindowNibName_("MainWindow")
        self.setWindowFrameAutosaveName_("MainWindow")
        self.showWindow_(self)
        self.retain()
        
        return self

    def windowDidLoad(self):
        self.dataSource = ListDataSource.alloc().initWithMainWindowController_(self)
        self.outlineView.setDataSource_(self.dataSource)
        self.outlineView.setDelegate_(self.dataSource)
        self.outlineView.setTarget_(self)
        self.outlineView.setDoubleAction_(self.listDoubleClicked_)

    def windowWillClose_(self, notification):
        self.autorelease()

    def addEntry_(self, sender):
        self.entryWindowController.showAddDialog()
    
    def editEntry_(self, record):
        self.entryWindowController.showEditDialog_(record)
    
    def editSelectedEntry_(self, sender):
        pass
    
    def removeEntry_(self, sender):
        pass
    
    def copyPassword_(self, sender):
        pass
    
    def updateList(self):
        self.dataSource.updateRecords()
        self.outlineView.reloadData()
    
    def updateInfo(self):
        record = None
        index = self.outlineView.selectedRow()
        if index != -1:
            item = self.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                record = item.record
        if record:
            self.titleLabel.setStringValue_(record._get_title())
            self.usernameLabel.setStringValue_(record._get_user() or '--')
            self.urlLabel.setStringValue_(record._get_url() or '--')
            self.notesLabel.setStringValue_(record._get_notes() or '--')
            self.lastModifiedLabel.setStringValue_(record._get_last_mod() and time.strftime('%c', time.gmtime(record._get_last_mod())) or '--')
            for component in self.infoView.subviews():
                if isinstance(component, NSControl):
                    component.setEnabled_(YES)
        else:
            self.titleLabel.setStringValue_('--')
            self.usernameLabel.setStringValue_('--')
            self.urlLabel.setStringValue_('--')
            self.notesLabel.setStringValue_('--')
            self.lastModifiedLabel.setStringValue_('--')
            for component in self.infoView.subviews():
                if isinstance(component, NSControl):
                    component.setEnabled_(NO)

    @objc.signature('v@:s')
    def listDoubleClicked_(self, sender):
        index = self.outlineView.clickedRow()
        if index != -1:
            item = self.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                self.editEntry_(item.record)
