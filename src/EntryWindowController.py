#
#  EntryWindowController.py
#  Password Chest
#
#  Created by Mathis Hofer on 26.09.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
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

from PCDataSource import RecordNode, RecordGroupNode
from util import calculate_password_strength


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
    clearPasswordField = IBOutlet()
    bulletPasswordField = IBOutlet()
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
        NSBundle.loadNibNamed_owner_('EntryWindow', self)
        
        return self
    
    def showAddDialog(self):
        self.record = None
        self._updateGroupCombo()
        self._resetFields()
        self.okButton.setTitle_('Add')
        
        index = self.document.outlineView.selectedRow()
        if index != -1:
            item = self.document.outlineView.itemAtRow_(index)
            if isinstance(item, RecordNode):
                self.groupCombo.setStringValue_(item.record._get_group())
            elif isinstance(item, RecordGroupNode):
                self.groupCombo.setStringValue_(item._get_title())
        
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
        self.groupCombo.setStringValue_('')
        self.titleField.setStringValue_('')
        self.userField.setStringValue_('')
        self.passwordStrengthIndicator.setIntValue_(0)
        self.clearPasswordField.setStringValue_('')
        self.bulletPasswordField.setStringValue_('')
        self.clearPasswordField.setHidden_(True)
        self.bulletPasswordField.setHidden_(False)
        self.passwordStrengthIndicator.setIntValue_(0)
        self.showPasswordButton.setState_(NSOffState)
        self.urlField.setStringValue_('')
        self.notesField.setString_('')
        
        # focus title field
        self.titleField.selectText_(self)
        
    def _fillFieldsFromRecord(self):
        self._resetFields()
        
        if self.record:
            self.groupCombo.setStringValue_(self.record._get_group())
            self.titleField.setStringValue_(self.record._get_title())
            self.userField.setStringValue_(self.record._get_user())
            self.clearPasswordField.setStringValue_(self.record._get_passwd())
            self.bulletPasswordField.setStringValue_(self.record._get_passwd())
            self._updatePasswordStrengthLevel()
            self.urlField.setStringValue_(self.record._get_url())
            self.notesField.setString_(self.record._get_notes())
    
    def _fillRecordFromFields(self):
        if self.record:
            self.record._set_group(self.groupCombo.stringValue())
            self.record._set_title(self.titleField.stringValue())
            self.record._set_user(self.userField.stringValue())
            if self.showPasswordButton.state() == NSOnState:
                self.record._set_passwd(self.clearPasswordField.stringValue())
            else:
                self.record._set_passwd(self.bulletPasswordField.stringValue())
            self.record._set_url(self.urlField.stringValue())
            self.record._set_notes(self.notesField.string())
            self.record.mark_modified()
    
    def _showDialog(self):
        NSApp.beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
            self.entryWindow, self.document.windowForSheet(),
            self, None, None)
    
    def _closeDialog(self):
        NSApp.endSheet_(self.entryWindow)
        self.entryWindow.orderOut_(self)
    
    def _updatePasswordStrengthLevel(self):
        password = None
        if self.showPasswordButton.state() == NSOnState:
            password = self.clearPasswordField.stringValue()
        else:
            password = self.bulletPasswordField.stringValue()
        username = self.userField.stringValue() != '' and self.userField.stringValue() or None
        score = calculate_password_strength(password, username)
        self.passwordStrengthIndicator.setIntValue_(score)
    
    def togglePasswordVisibility_(self, sender):
        if self.showPasswordButton.state() == NSOnState:
            self.clearPasswordField.setStringValue_(self.bulletPasswordField.stringValue())
            self.clearPasswordField.setHidden_(False)
            self.bulletPasswordField.setHidden_(True)
        else:
            self.bulletPasswordField.setStringValue_(self.clearPasswordField.stringValue())
            self.clearPasswordField.setHidden_(True)
            self.bulletPasswordField.setHidden_(False)
    
    def controlTextDidChange_(self, notification):
        if notification.object() == self.clearPasswordField or notification.object() == self.bulletPasswordField:
            self._updatePasswordStrengthLevel()
    
    def ok_(self, sender):
        if self.groupCombo.stringValue() == '':
            alert = NSAlert.alloc().init()
            alert.setMessageText_('Group name may not be empty')
            alert.setAlertStyle_(NSCriticalAlertStyle)
            alert.runModal()
            return
        if self.titleField.stringValue() == '':
            alert = NSAlert.alloc().init()
            alert.setMessageText_('Title may not be empty')
            alert.setAlertStyle_(NSCriticalAlertStyle)
            alert.runModal()
            return
        
        edit = True
        if not self.record:
            edit = False
            self.record = Vault.Record.create()
        self._fillRecordFromFields()
        
        if edit:
            self.document.dataSource.recordUpdated_(self.record)
        else:
            self.document.dataSource.addRecord_(self.record)
        
        self.record = None
        self._closeDialog()
    
    def cancel_(self, sender):
        self.record = None
        self._closeDialog()
