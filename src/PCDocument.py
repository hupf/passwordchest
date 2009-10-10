#
#  PCDocument.py
#  Password Chest
#
#  Created by Mathis Hofer on 09.10.09.
#  Copyright Mathis Hofer 2009. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from CoreData import *
from AppKit import *
from loxodo.vault import Vault
import time

from VaultDataSource import VaultDataSource, RecordNode, RecordGroupNode
from PasswordDialogController import PasswordDialogController
from EntryWindowController import EntryWindowController


class PCDocument(NSDocument):
    vault = None
    dataSource = None
    entryWindowController = None
    
    outlineView = IBOutlet()
    infoView = IBOutlet()
    titleLabel = IBOutlet()
    usernameLabel = IBOutlet()
    urlLabel = IBOutlet()
    notesLabel = IBOutlet()
    lastModifiedLabel = IBOutlet()
    removeButton = IBOutlet()

    def init(self):
        self = super(PCDocument, self).init()
        return self
        
    def windowNibName(self):
        return u"PCDocument"
    
    def windowControllerDidLoadNib_(self, aController):
        super(PCDocument, self).windowControllerDidLoadNib_(aController)
        
        # user interface preparation code
        self.entryWindowController = EntryWindowController.alloc().initWithDocument_(self)
        self.dataSource = VaultDataSource.alloc().initWithPCDocument_(self)
        self.outlineView.setDataSource_(self.dataSource)
        self.outlineView.setDelegate_(self.dataSource)
        self.outlineView.setTarget_(self)
        self.outlineView.setDoubleAction_(self.listDoubleClicked_)

    def readFromFile_ofType_(self, path, type):
        passwordDialogController = PasswordDialogController.alloc().init()
        vault = None
        error = None
        while vault is None and error is None or error == Vault.BadPasswordError:
            vault = None
            error = None
            password = passwordDialogController.askForPassword()
            if password is None:
                # user pressed cancel
                break
            try:
                # try to open vault with given password
                vault = Vault(password, filename=path)
            except Vault.BadPasswordError:
                error = Vault.BadPasswordError
                
                alert = NSAlert.alloc().init()
                alert.setMessageText_("Bad password")
                alert.setInformativeText_("Please try again.")
                alert.setAlertStyle_(NSCriticalAlertStyle)
                alert.runModal()
            except Vault.VaultVersionError:
                error = Vault.VaultVersionError
                
                alert = NSAlert.alloc().init()
                alert.setMessageText_("Bad file version")
                alert.setInformativeText_("This is not a PasswordSafe V3 file.")
                alert.setAlertStyle_(NSCriticalAlertStyle)
                alert.runModal()
            except Vault.VaultFormatError:
                error = Vault.VaultFormatError
                
                alert = NSAlert.alloc().init()
                alert.setMessageText_("Bad file format")
                alert.setInformativeText_("File integrity check failed.")
                alert.setAlertStyle_(NSCriticalAlertStyle)
                alert.runModal()
        if vault and error is None:
            self.vault = vault
            return True
        else:
            self.vault = None
            return False

    def writeToFile_ofType_(self, path, tp):
        return False
    
    def addRecord_(self, sender):
        self.entryWindowController.showAddDialog()
    
    def editRecord_(self, record):
        self.entryWindowController.showEditDialog_(record)
    
    def removeRecord_(self, sender):
        index = self.outlineView.selectedRow()
        if index != -1:
            item = self.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                self.dataSource.removeRecord_(item.record)
            elif isinstance(item, RecordGroupNode):
                self.dataSource.removeGroup_(item)
    
    def copyPassword_(self, sender):
        pass
    
    def selectionChanged(self):
        self.updateInfo()
        self.removeButton.setEnabled_(self.outlineView.numberOfSelectedRows() != 0)
    
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
                self.editRecord_(item.record)
