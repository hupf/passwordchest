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
    isNewFile = True
    vault = None
    password = None
    
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
        if self.isNewFile:
            self.vault = Vault('123456')
        return self
    
    def initWithContentsOfURL_ofType_error_(self, url, type, errorInfo):
        (self, errorInfo) = super(PCDocument, self).initWithContentsOfURL_ofType_error_(url, type, errorInfo)
        if self:
            self.isNewFile = False
        return (self, errorInfo)
        
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
    
    def readFromURL_ofType_error_(self, url, type, errorInfo):
        if not url.isFileURL():
            return (False, errorInfo)
        
        passwordDialogController = PasswordDialogController.alloc().init()
        vault = None
        error = None
        while vault is None and error is None or error == Vault.BadPasswordError:
            vault = None
            error = None
            self.password = passwordDialogController.askForPassword()
            if self.password is None:
                # user pressed cancel
                break
            try:
                # try to open vault with given password
                vault = Vault(self.password, filename=url.path())
            except Vault.BadPasswordError:
                error = Vault.BadPasswordError
                
                alert = NSAlert.alloc().init()
                alert.setMessageText_("Bad password")
                alert.setInformativeText_("Please try again.")
                alert.setAlertStyle_(NSCriticalAlertStyle)
                alert.runModal()
            except Vault.VaultVersionError:
                error = Vault.VaultVersionError
                errorInfo = NSError.errorWithDomain_code_userInfo_("PCError", -1,
                    NSDictionary.dictionaryWithObject_forKey_("File is not a PasswordSafe V3 file.", NSLocalizedFailureReasonErrorKey))
            except Vault.VaultFormatError:
                error = Vault.VaultFormatError
                errorInfo = NSError.errorWithDomain_code_userInfo_("PCError", -1,
                    NSDictionary.dictionaryWithObject_forKey_("File integrity check failed.", NSLocalizedFailureReasonErrorKey))
        if vault and error is None:
            self.vault = vault
            return (True, errorInfo)
        else:
            self.vault = None
            self.password = None
            return (False, errorInfo)

    def writeToURL_ofType_error_(self, url, type, errorInfo):
        if not url.isFileURL():
            return (False, errorInfo)
        
        if self.isNewFile:
            while self.password is None:
                passwordDialogController = PasswordDialogController.alloc().init()
                self.password = passwordDialogController.askForPassword()
            self.isNewFile = False
        self.vault.write_to_file(url.path(), self.password)
        try:
            self.vault.write_to_file(url.path(), self.password)
            return (True, errorInfo)
        except Vault.VaultFormatError:
            errorInfo = NSError.errorWithDomain_code_userInfo_("PCError", -1,
                    NSDictionary.dictionaryWithObject_forKey_("File integrity check failed.", NSLocalizedFailureReasonErrorKey))
            return (False, errorInfo)
        except:
            return (False, errorInfo)
    
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
        record = None
        index = self.outlineView.selectedRow()
        if index != -1:
            item = self.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                record = item.record
        if record:
            pasteboard = NSPasteboard.generalPasteboard()
            pasteboard.clearContents()
            copiedObjects = NSArray.arrayWithObject_(record._get_passwd())
            pasteboard.writeObjects_(copiedObjects)
    
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
            
            if record._get_url():
                self.urlLabel.setAllowsEditingTextAttributes_(True)
                self.urlLabel.setSelectable_(True)

                attrString = NSAttributedString.alloc().initWithString_attributes_(record._get_url(), {NSLinkAttributeName:record._get_url()})
                self.urlLabel.setAttributedStringValue_(attrString)
            else:
                self.urlLabel.setStringValue_('--')
            
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
