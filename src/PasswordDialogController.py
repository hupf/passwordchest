#
#  PasswordDialog.py
#  Password Chest
#
#  Created by Mathis Hofer on 27.09.09.
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

from util import calculate_password_strength

class PasswordDialogController(NSObject):
    passwordDialog = IBOutlet()
    titleLabel = IBOutlet()
    descriptionLabel = IBOutlet()
    passwordFormBox = IBOutlet()
    passwordCheckForm = IBOutlet()
    passwordDefineForm = IBOutlet()
    
    password = None
    passwordForm = None

    def init(self):
        self = super(PasswordDialogController, self).init()
        if self is None: return None
        
        NSBundle.loadNibNamed_owner_('PasswordDialog', self)
                
        return self
    
    def _showDialog(self):
        self.password = None
        self.passwordForm.reset()
        self.passwordDialog.center()
        NSApp.runModalForWindow_(self.passwordDialog) # blocking
        self.passwordDialog.orderOut_(self)
        return self.password
    
    def _setForm(self, form):
        self.passwordForm = form
        
        frame = self.passwordDialog.frame()
        newHeight = frame.size.height - self.passwordFormBox.contentView().frame().size.height + form.frame().size.height
        frame.origin.y = frame.origin.y - (newHeight - frame.size.height);
        frame.size.height = newHeight
        
        self.passwordFormBox.setContentView_(form)
        self.passwordDialog.setFrame_display_animate_(frame, True, False)
    
    def requestPassword(self, filename):
        self._setForm(self.passwordCheckForm)
        self.titleLabel.setStringValue_('Password Chest wants to open the "%s" password safe.' % filename)
        self.descriptionLabel.setStringValue_('Please enter the password.')
        return self._showDialog()
    
    def requestNewPassword(self, filename):
        self._setForm(self.passwordDefineForm)
        self.titleLabel.setStringValue_('Enter a new password for the password safe "%s".' % filename)
        self.descriptionLabel.setStringValue_('')
        return self._showDialog()
    
    def ok_(self, sender):
        valid, error = self.passwordForm.isValid()
        if valid:
            self.password = self.passwordForm.getPassword()
            NSApp.stopModal()
        else:
            NSAlert.alertWithError_(error).runModal()
            self.passwordForm.reset()
    
    def cancel_(self, sender):
        NSApp.stopModal()


class PasswordForm(NSView):
    def isValid(self):
        raise NotImplementedError

    def getPassword(self):
        raise NotImplementedError
    
    def reset(self):
        raise NotImplementedError


class PasswordCheckForm(PasswordForm):
    passwordField = IBOutlet()
    
    def isValid(self):
        return (True, None)
    
    def getPassword(self):
        return self.passwordField.stringValue() 
    
    def reset(self):
        self.passwordField.setStringValue_('')
        
        self.passwordField.selectText_(self)


class PasswordDefineForm(PasswordForm):
    passwordField = IBOutlet()
    passwordVerifyField = IBOutlet()
    passwordStrengthIndicator = IBOutlet()
    
    def isValid(self):
        if self.passwordField.stringValue() != self.passwordVerifyField.stringValue():
            errorInfo = NSError.errorWithDomain_code_userInfo_('PCError', -1,
                {NSLocalizedDescriptionKey: 'Your password is not the same as the verify password.',
                 NSLocalizedRecoverySuggestionErrorKey: 'Try entering your information again.'})
            return (False, errorInfo)
        return (True, None)
    
    def getPassword(self):
        return self.passwordField.stringValue() 
    
    def reset(self):
        self.passwordField.setStringValue_('')
        self.passwordVerifyField.setStringValue_('')
        
        self.passwordField.selectText_(self)
    
    def controlTextDidChange_(self, notification):
        if notification.object() == self.passwordField:
            self._updatePasswordStrengthLevel()
    
    def _updatePasswordStrengthLevel(self):
        password = self.passwordField.stringValue()
        score = calculate_password_strength(password)
        self.passwordStrengthIndicator.setIntValue_(score)
