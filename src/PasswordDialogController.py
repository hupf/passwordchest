#
#  PasswordDialog.py
#  Password Chest
#
#  Created by Mathis Hofer on 27.09.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from CoreData import *
from AppKit import *


class PasswordDialogController(NSObject):
    passwordDialog = IBOutlet()
    label = IBOutlet()
    passwordField = IBOutlet()
    password = None

    def init(self):
        self = super(PasswordDialogController, self).init()
        if self is None: return None
        
        NSBundle.loadNibNamed_owner_("PasswordDialog", self)
                
        return self
    
    def askForPassword(self):
        self.password = None
        self.passwordField.setStringValue_("")
        self.passwordDialog.center()
        NSApp.runModalForWindow_(self.passwordDialog) # blocking
        self.passwordDialog.orderOut_(self)
        return self.password

    def ok_(self, sender):
        self.password = self.passwordField.stringValue()
        NSApp.stopModal()
    
    def cancel_(self, sender):
        NSApp.stopModal()
