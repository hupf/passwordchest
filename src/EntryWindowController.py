#
#  EntryWindowController.py
#  Password Chest
#
#  Created by Mathis Hofer on 26.09.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from CoreData import *
from AppKit import *
from loxodo.vault import Vault


class EntryWindowController(NSObject):
    document = None
    dataSource = None
    vault = None
    record = None
    
    entryWindow = IBOutlet()

    groupCombo = IBOutlet()
    titleField = IBOutlet()
    userField = IBOutlet()
    passwordStrengthIndicator = IBOutlet()
    passwordField = IBOutlet()
    showPasswordButton = IBOutlet()
    urlField = IBOutlet()
    notesField = IBOutlet()
    
    okButton = IBOutlet()

    def initWithDocument_(self, document):
        self = super(EntryWindowController, self).init()
        if self is None: return None
        
        self.document = document
        self.dataSource = document.dataSource
        self.vault = document.vault
        NSBundle.loadNibNamed_owner_("EntryWindow", self)
        
        return self
    
    def showAddDialog(self):
        self.record = None
        self._updateGroupCombo()
        self._resetFields()
        self.okButton.setTitle_('Add')
        
        self._showDialog()
    
    def showEditDialog_(self, record):
        self.record = record
        self._updateGroupCombo()
        self._fillFieldsFromRecord()
        self.okButton.setTitle_('Save')
        
        self._showDialog()
    
    def sheetDidEnd_returnCode_contextInfo_(self, sheet, returnCode, contextInfo):
        self.entryWindow.orderOut_(self)
    
    def _updateGroupCombo(self):
        groups = []
        map(lambda r: groups.append(r._get_group()), self.vault.records)
        groups = dict.fromkeys(groups).keys()
        
        self.groupCombo.removeAllItems()
        for group in groups:
            self.groupCombo.addItemWithObjectValue_(group)
    
    def _resetFields(self):
        self.groupCombo.setStringValue_("")
        self.titleField.setStringValue_("")
        self.userField.setStringValue_("")
        self.passwordStrengthIndicator.setIntValue_(0)
        self.passwordField.setStringValue_("")
        self.showPasswordButton.setState_(NSOffState)
        self.urlField.setStringValue_("")
        self.notesField.setString_("")
        
    def _fillFieldsFromRecord(self):
        self._resetFields()
        
        if self.record:
            self.groupCombo.setStringValue_(self.record._get_group())
            self.titleField.setStringValue_(self.record._get_title())
            self.userField.setStringValue_(self.record._get_user())
            self.passwordField.setStringValue_(self.record._get_passwd())
            self.urlField.setStringValue_(self.record._get_url())
            self.notesField.setString_(self.record._get_notes())
    
    def _fillRecordFromFields(self):
        if self.record:
            self.record._set_group(self.groupCombo.stringValue())
            self.record._set_title(self.titleField.stringValue())
            self.record._set_user(self.userField.stringValue())
            self.record._set_passwd(self.passwordField.stringValue())
            self.record._set_url(self.urlField.stringValue())
            self.record._set_notes(self.notesField.string())
            self.record.mark_modified()
    
    def _showDialog(self):
        NSApp.beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
            self.entryWindow, self.document.outlineView.window(),
            self, None, None)
    
    def _closeDialog(self):
        NSApp.endSheet_(self.entryWindow)
        self.entryWindow.orderOut_(self)
    
    def ok_(self, sender):
        if self.record:
            oldRecord = self.record
        else:
            self.record = Vault.Record.create()
        self._fillRecordFromFields()
        
        #if oldRecord:
        #    dataSource.updateRecord_withOldRecord_(self.record, oldRecord)
        #else:
        #    dataSource.addRecord_(self.record)
        
        self.record = None
        self._closeDialog()
    
    def cancel_(self, sender):
        self.record = None
        self._closeDialog()
