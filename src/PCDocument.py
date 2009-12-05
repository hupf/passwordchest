#
#  PCDocument.py
#  Password Chest
#
#  Created by Mathis Hofer on 09.10.09.
#  Copyright Mathis Hofer 2009. All rights reserved.
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from objc import IBAction, IBOutlet
from Foundation import *
from AppKit import *
from loxodo.vault import Vault
import time
import os

from PCSplitView import PCSplitView
from PCDataSource import PCDataSource, RecordNode, RecordGroupNode
from PasswordDialogController import PasswordDialogController
from EntryWindowController import EntryWindowController
from PreferencesWindowController import PreferencesWindowController
from util import urlize


class PCOutlineView(NSOutlineView):
    copyPasswordItemAction = None
    cutItemAction = None
    copyItemAction = None
    pasteItemAction = None
    expandAllItemAction = None
    collapseAllItemAction = None
    renameItemAction = None
    editItemAction = None
    deleteItemAction = None

    def setCopyPasswordItemAction_(self, action):
        self.copyPasswordItemAction = action
    
    def setCutItemAction_(self, action):
        self.cutItemAction = action
    
    def setCopyItemAction_(self, action):
        self.copyItemAction = action
    
    def setPasteItemAction_(self, action):
        self.pasteItemAction = action
    
    def setExpandAllItemAction_(self, action):
        self.expandAllItemAction = action
    
    def setCollapseAllItemAction_(self, action):
        self.collapseAllItemAction = action
    
    def setRenameItemAction_(self, action):
        self.renameItemAction = action
    
    def setEditItemAction_(self, action):
        self.editItemAction = action
    
    def setDeleteItemAction_(self, action):
        self.deleteItemAction = action
    
    def menuForEvent_(self, event):
        mousePoint = self.convertPoint_fromView_(event.locationInWindow(), None)
        row = self.rowAtPoint_(mousePoint)
        
        item = None
        if row != -1:
            item = self.itemAtRow_(row)
            self.selectRowIndexes_byExtendingSelection_(NSIndexSet.indexSetWithIndex_(row), False)
        else:
            self.deselectAll_(self)
        
        # prepare context menu
        contextMenu = NSMenu.alloc().initWithTitle_('Context menu')
        
        copyPasswordItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Copy Password", ""), self.copyPasswordItemAction, '')
        cutItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Cut", ""), self.cutItemAction, '')
        copyItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Copy", ""), self.copyItemAction, '')
        pasteItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Paste", ""), self.pasteItemAction, '')
        expandAllItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Expand All", ""), self.expandAllItemAction, '')
        collapseAllItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Collapse All", ""), self.collapseAllItemAction, '')
        renameItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Rename", ""), self.renameItemAction, '')
        editItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Edit", ""), self.editItemAction, '')
        deleteItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            NSLocalizedString("Delete", ""), self.deleteItemAction, '')
        
        if isinstance(item, RecordNode):
            contextMenu.addItem_(copyPasswordItem)
            contextMenu.addItem_(NSMenuItem.separatorItem())
        #if item:
        #    contextMenu.addItem_(cutItem)
        #    contextMenu.addItem_(copyItem)
        #contextMenu.addItem_(pasteItem)
        #contextMenu.addItem_(NSMenuItem.separatorItem())
        contextMenu.addItem_(expandAllItem)
        contextMenu.addItem_(collapseAllItem)
        if item:
            contextMenu.addItem_(NSMenuItem.separatorItem())
            contextMenu.addItem_(renameItem)
            if isinstance(item, RecordNode):
                contextMenu.addItem_(editItem)
            contextMenu.addItem_(deleteItem)
                    
        return contextMenu


class PCHyperlinkButtonCell(NSButtonCell):
    def init(self):
        self = super(PCHyperlinkButtonCell, self).init()
        
        self.useHandCursor = False
        self.setBordered_(False)
        self.setHighlightsBy_(NSNoCellMask)
        self.setAlignment_(NSLeftTextAlignment)
        
        # needed for mouseEntered/mouseExited
        self.setShowsBorderOnlyWhileMouseInside_(True)
        
        return self
    
    def enableHandCursor(self):
        self.useHandCursor = True
        
    def disableHandCursor(self):
        self.useHandCursor = False
    
    def mouseEntered_(self, event):
        if self.useHandCursor:
            NSCursor.pointingHandCursor().push()
        return super(PCHyperlinkButtonCell, self).mouseEntered_(event)

    def mouseExited_(self, event):
        if self.useHandCursor:
            NSCursor.pop()
        return super(PCHyperlinkButtonCell, self).mouseExited_(event)


class PCDocument(NSDocument):
    isNewFile = True
    vault = None
    password = None
    
    preferences = None
    dataSource = None
    entryWindowController = None
    
    outlineView = IBOutlet()
    infoView = IBOutlet()
    logoView = IBOutlet()
    titleLabel = IBOutlet()
    usernameLabel = IBOutlet()
    urlButton = IBOutlet()
    notesLabel = IBOutlet()
    lastModifiedLabel = IBOutlet()
    removeButton = IBOutlet()
    searchField = IBOutlet()

    def init(self):
        self = super(PCDocument, self).init()
        
        if self.isNewFile:
            self.vault = Vault('123456')
        
        defaultPreferencesFile = NSBundle.mainBundle().pathForResource_ofType_('Defaults', 'plist')
        defaultPreferences = NSDictionary.dictionaryWithContentsOfFile_(defaultPreferencesFile)
        self.preferences = NSUserDefaults.standardUserDefaults()
        self.preferences.registerDefaults_(defaultPreferences)
        
        return self
    
    def initWithContentsOfURL_ofType_error_(self, url, type, errorInfo):
        (self, errorInfo) = super(PCDocument, self).initWithContentsOfURL_ofType_error_(url, type, errorInfo)
        if self:
            self.isNewFile = False
        return (self, errorInfo)
        
    def windowNibName(self):
        return u'PCDocument'
    
    def windowControllerDidLoadNib_(self, aController):
        super(PCDocument, self).windowControllerDidLoadNib_(aController)
        
        # user interface preparation code
        self.entryWindowController = EntryWindowController.alloc().initWithDocument_(self)
        self.dataSource = PCDataSource.alloc().initWithPCDocument_(self)
        self.outlineView.setDataSource_(self.dataSource)
        self.outlineView.setDelegate_(self.dataSource)
        self.outlineView.setTarget_(self)
        self.outlineView.setDoubleAction_(self.listDoubleClicked_)
        self.outlineView.setCopyPasswordItemAction_(self.copyRecordPassword_)
        #self.outlineView.setCutItemAction_(action)
        #self.outlineView.setCopyItemAction_(action)
        #self.outlineView.setPasteItemAction_(action)
        self.outlineView.setExpandAllItemAction_(self.expandAll_)
        self.outlineView.setCollapseAllItemAction_(self.collapseAll_)
        self.outlineView.setRenameItemAction_(self.renameSelectedNode_)
        self.outlineView.setEditItemAction_(self.editSelectedRecord_)
        self.outlineView.setDeleteItemAction_(self.removeSelectedRecord_)
        
        hyperlinkCell = PCHyperlinkButtonCell.alloc().init()
        hyperlinkCell.setAction_(self.urlButton.cell().action())
        self.urlButton.setCell_(hyperlinkCell)
        
        self.updateInfo()
    
    def readFromURL_ofType_error_(self, url, type, errorInfo):
        if not url.isFileURL():
            return (False, errorInfo)
        
        passwordDialogController = PasswordDialogController.alloc().init()
        vault = None
        error = None
        while vault is None and error is None or error == Vault.BadPasswordError:
            vault = None
            error = None
            self.password = passwordDialogController.requestPassword(os.path.basename(url.path()))
            if self.password is None:
                # user pressed cancel
                break
            try:
                # try to open vault with given password
                vault = Vault(self.password, filename=url.path())
            except Vault.BadPasswordError:
                error = Vault.BadPasswordError
                
                alert = NSAlert.alloc().init()
                alert.setMessageText_(NSLocalizedString("Bad password", ""))
                alert.setInformativeText_(NSLocalizedString("Please try again.", ""))
                alert.setAlertStyle_(NSCriticalAlertStyle)
                alert.runModal()
            except Vault.VaultVersionError:
                error = Vault.VaultVersionError
                errorInfo = NSError.errorWithDomain_code_userInfo_('PCError', -1,
                    {NSLocalizedFailureReasonErrorKey: NSLocalizedString("File is not a PasswordSafe V3 file.", "")})
            except Vault.VaultFormatError:
                error = Vault.VaultFormatError
                errorInfo = NSError.errorWithDomain_code_userInfo_('PCError', -1,
                    {NSLocalizedFailureReasonErrorKey: NSLocalizedString("File integrity check failed.", "")})
        if vault and error is None:
            self.vault = vault
            return (True, errorInfo)
        else:
            self.vault = None
            self.password = None
            return (False, errorInfo)

    def writeToURL_ofType_error_(self, url, type, errorInfo):
        if not url.isFileURL():
            errorInfo = NSError.errorWithDomain_code_userInfo_('PCError', -1,
                {NSLocalizedFailureReasonErrorKey: NSLocalizedString("Invalid file URL.", "")})
            return (False, errorInfo)
        
        if self.isNewFile and self.password is None:
            passwordDialogController = PasswordDialogController.alloc().init()
            pw = ''
            while pw == '':
                pw = passwordDialogController.requestNewPassword(os.path.basename(url.path()))
            if pw is None:
                # user pressed cancel
                errorInfo = NSError.errorWithDomain_code_userInfo_('PCError', -1,
                    {NSLocalizedFailureReasonErrorKey: NSLocalizedString("Password entry aborted.", "")})
                return (False, errorInfo)
            self.password = pw
        self.isNewFile = False
        try:
            self.vault.write_to_file(url.path(), self.password)
            return (True, errorInfo)
        except Vault.VaultFormatError:
            errorInfo = NSError.errorWithDomain_code_userInfo_('PCError', -1,
                    {NSLocalizedFailureReasonErrorKey: NSLocalizedString("File integrity check failed.", "")})
            return (False, errorInfo)
        except:
            return (False, errorInfo)
    
    def addRecord_(self, sender):
        self.entryWindowController.showAddDialog()
    
    def editRecord_(self, record):
        self.entryWindowController.showEditDialog_(record)
    
    @objc.signature('v@:s')
    def editSelectedRecord_(self, sender):
        index = self.outlineView.selectedRow()
        if index != -1:
            item = self.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                self.editRecord_(item.record)
    
    @objc.signature('v@:s')
    def removeSelectedRecord_(self, sender):
        index = self.outlineView.selectedRow()
        if index != -1:
            item = self.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                self.dataSource.removeRecord_(item.record)
            elif isinstance(item, RecordGroupNode):
                self.dataSource.removeGroup_(item)
    
    def copyRecordPassword_(self, sender):
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
    
    def openRecordURL_(self, sender):
        record = None
        index = self.outlineView.selectedRow()
        if index != -1:
            item = self.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                record = item.record
        if record and record._get_url():
            NSWorkspace.sharedWorkspace().openURL_(NSURL.URLWithString_(urlize(record._get_url())))
    
    @objc.signature('v@:s')
    def renameSelectedNode_(self, sender):
        index = self.outlineView.selectedRow()
        if index != -1:
            self.outlineView.editColumn_row_withEvent_select_(0, index, None, True)
    
    def selectionChanged(self):
        self.updateInfo()
        self.removeButton.setEnabled_(self.outlineView.numberOfSelectedRows() != 0)
    
    def performFindPanelAction_(self, sender):
        self.searchField.selectText_(self)
    
    def search_(self, sender):
        if sender == self.searchField:
            searchString = sender.stringValue()
            if len(searchString):
                self.dataSource.updateFilter_(searchString)
                self.dataSource.expandAll()
            else:
                self.dataSource.resetFilter()
    
    def openPreferences_(self, sender):
        PreferencesWindowController.alloc().init()
    
    def changePassword_(self, sender):
        passwordDialogController = PasswordDialogController.alloc().init()
        pw = ''
        while pw == '':
            pw = passwordDialogController.requestNewPassword(
                self.fileURL() and os.path.basename(self.fileURL().path()) or NSLocalizedString("Untitled", ""))
        if pw is None:
            # user pressed cancel
            return
        
        self.password = pw
        self.updateChangeCount_(NSChangeDone)
    
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
                attrString = NSMutableAttributedString.alloc().initWithString_(record._get_url())
                range = NSMakeRange(0, attrString.length());
                attrString.beginEditing()
                attrString.addAttribute_value_range_(
                    NSForegroundColorAttributeName, NSColor.blueColor(), range)
                attrString.addAttribute_value_range_(
                    NSUnderlineStyleAttributeName, NSNumber.numberWithInt_(NSSingleUnderlineStyle), range)
                attrString.endEditing()
                
                self.urlButton.setAttributedTitle_(attrString)
                self.urlButton.cell().enableHandCursor()
            else:
                self.urlButton.setTitle_('--')
                self.urlButton.cell().disableHandCursor()
            
            self.notesLabel.setStringValue_(record._get_notes() or '--')
            self.lastModifiedLabel.setStringValue_(
                record._get_last_mod() and time.strftime('%c', time.gmtime(record._get_last_mod())) or '--')
            
            self.infoView.setHidden_(False)
            self.logoView.setHidden_(True)
        else:
            self.titleLabel.setStringValue_('--')
            self.usernameLabel.setStringValue_('--')
            self.urlButton.setStringValue_('--')
            self.notesLabel.setStringValue_('--')
            self.lastModifiedLabel.setStringValue_('--')
            
            self.infoView.setHidden_(True)
            self.logoView.setHidden_(False)

    @objc.signature('v@:s')
    def listDoubleClicked_(self, sender):
        index = self.outlineView.clickedRow()
        if index != -1:
            item = self.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                self.editRecord_(item.record)
    
    @objc.signature('v@:s')
    def expandAll_(self, sender):
        self.dataSource.expandAll()
    
    @objc.signature('v@:s')
    def collapseAll_(self, sender):
        self.dataSource.collapseAll()
    