#
#  PreferencesWindowController.py
#  Password Chest
#
#  Created by Mathis Hofer on 07.11.09.
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

class PreferencesWindowController(NSWindowController):
    preferences = None
    
    defaultFileCheckboxMatrix = IBOutlet()
    defaultFileNoDefaultCheckbox = IBOutlet()
    defaultFileUseDefaultCheckbox = IBOutlet()
    defaultFileField = IBOutlet()
    defaultFileChooseButton = IBOutlet()
    
    def init(self):
        self = super(PreferencesWindowController, self).initWithWindowNibName_('PreferencesWindow')
        if self is None: return None

        self.setWindowFrameAutosaveName_('PreferencesWindow')
        self.showWindow_(self)
        self.retain()
        
        self.preferences = NSUserDefaults.standardUserDefaults()
        self._updateFields()
        
        return self
    
    def windowDidLoad(self):
        NSApp.activateIgnoringOtherApps_(True)
        self.window().makeKeyAndOrderFront_(None)
    
    def windowWillClose_(self, notification):
        self._save()
        self.autorelease()
    
    def chooseDefaultFile_(self, sender):
        chooseDialog = NSOpenPanel.openPanel()
        chooseDialog.setCanChooseDirectories_(False)
        chooseDialog.setCanChooseFiles_(True)
        chooseDialog.setAllowsMultipleSelection_(False)
        chooseDialog.setTitle_(NSLocalizedString("Choose default file", ""))
        
        result = chooseDialog.runModal()
        if result == NSOKButton:
            self.defaultFileField.setStringValue_(chooseDialog.URL().path())
    
    def defaultFileCheckboxChanged_(self, sender):
        self.defaultFileField.setEnabled_(self.defaultFileCheckboxMatrix.selectedCell() == self.defaultFileUseDefaultCheckbox)
        self.defaultFileChooseButton.setEnabled_(self.defaultFileCheckboxMatrix.selectedCell() == self.defaultFileUseDefaultCheckbox)
    
    def _updateFields(self):
        openDefaultFileOnStartup = self.preferences.boolForKey_('PCOpenDefaultFileOnStartup')
        if openDefaultFileOnStartup:
            self.defaultFileCheckboxMatrix.selectCellWithTag_(self.defaultFileUseDefaultCheckbox.tag())
        else:
            self.defaultFileCheckboxMatrix.selectCellWithTag_(self.defaultFileNoDefaultCheckbox.tag())
        self.defaultFileField.setEnabled_(openDefaultFileOnStartup)
        self.defaultFileChooseButton.setEnabled_(openDefaultFileOnStartup)
        
        self.defaultFileField.setStringValue_(self.preferences.stringForKey_('PCDefaultFile'))

    def _save(self):
        self.preferences.setBool_forKey_(
            self.defaultFileCheckboxMatrix.selectedCell() == self.defaultFileUseDefaultCheckbox,
            'PCOpenDefaultFileOnStartup')
        self.preferences.setObject_forKey_(
            self.defaultFileField.stringValue(),
            'PCDefaultFile')
        
        self.preferences.synchronize()
