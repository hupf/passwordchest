#
#  PasswordGenerator.py
#  Password Chest
#
#  Created by Mathis Hofer on 29.11.09.
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

from util import generate_random_password


NUM_SUGGESTED_PASSWORDS = 20

class PasswordGeneratorController(NSWindowController):
    uppercaseCheckbox = IBOutlet()
    digitsCheckbox = IBOutlet()
    punctuationCheckbox = IBOutlet()
    lengthSlider = IBOutlet()
    lengthValue = IBOutlet()
    suggestionsCombo = IBOutlet()
    
    callback = None
    entryWindow = None

    def initWithCallback_andEntryWindow_(self, callback, entryWindow):
        self = super(PasswordGeneratorController, self).initWithWindowNibName_('PasswordGenerator')
        if self is None: return None

        self.callback = callback
        self.entryWindow = entryWindow
        self.preferences = NSUserDefaults.standardUserDefaults()
        self._positionWindow()
        self.showWindow_(self)
        
        # Load defaults from settings
        self.uppercaseCheckbox.setState_(self.preferences.boolForKey_('PCPasswordGeneratorUppercase'))
        self.digitsCheckbox.setState_(self.preferences.boolForKey_('PCPasswordGeneratorDigits'))
        self.punctuationCheckbox.setState_(self.preferences.boolForKey_('PCPasswordGeneratorPunctuation'))
        self.lengthSlider.setIntValue_(self.preferences.integerForKey_('PCPasswordGeneratorLength'))
        self.lengthValue.setIntValue_(self.preferences.integerForKey_('PCPasswordGeneratorLength'))
        
        self.generatePasswords_(self)
        
        return self
    
    def windowDidLoad(self):
        NSApp.activateIgnoringOtherApps_(True)
        self.window().makeKeyAndOrderFront_(None)
    
    def windowWillClose_(self, notification):
        self.preferences.synchronize()
    
    def suggestionSelected_(self, sender):
        if self.callback:
            self.callback(self.suggestionsCombo.stringValue())
    
    def generatePasswords_(self, sender):
        length = self.lengthSlider.intValue()
        use_uppercase = self.uppercaseCheckbox.state()
        use_digits = self.digitsCheckbox.state()
        use_punctuation = self.punctuationCheckbox.state()
        
        self.lengthValue.setIntValue_(length)
        self.suggestionsCombo.removeAllItems()
        for i in range(0, NUM_SUGGESTED_PASSWORDS):
            password = generate_random_password(length, use_uppercase, use_digits, use_punctuation)
            self.suggestionsCombo.addItemWithObjectValue_(password)
        self.suggestionsCombo.setStringValue_(self.suggestionsCombo.objectValues()[0])
        
        # Update settings
        self.preferences.setBool_forKey_(self.uppercaseCheckbox.state(), 'PCPasswordGeneratorUppercase')
        self.preferences.setBool_forKey_(self.digitsCheckbox.state(), 'PCPasswordGeneratorDigits')
        self.preferences.setBool_forKey_(self.punctuationCheckbox.state(), 'PCPasswordGeneratorPunctuation')
        self.preferences.setInteger_forKey_(self.lengthSlider.intValue(), 'PCPasswordGeneratorLength')
    
    def _positionWindow(self):
        referenceWindowOrigin = self.entryWindow.frame().origin
        referenceWindowSize = self.entryWindow.frame().size
        panelSize = self.window().frame().size
        margin = 10
        
        if referenceWindowOrigin.y - margin - panelSize.height > 0:
            # Place panel below window
            x = referenceWindowOrigin.x
            y = referenceWindowOrigin.y - margin
        elif referenceWindowOrigin.x - panelSize.width - margin > 0:
            # Place panel left from window
            x = referenceWindowOrigin.x - panelSize.width - margin
            y = referenceWindowOrigin.y + referenceWindowSize.height
        else:
            # Place panel right from window
            x = referenceWindowOrigin.x + referenceWindowSize.width + margin
            y = referenceWindowOrigin.y + referenceWindowSize.height
        self.window().setFrameTopLeftPoint_((x, y))
