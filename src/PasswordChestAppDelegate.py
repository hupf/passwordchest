#
#  PasswordChestAppDelegate.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
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
import os


class PasswordChestAppDelegate(NSObject):
    def applicationDidFinishLaunching_(self, sender):
        defaultPreferencesFile = NSBundle.mainBundle().pathForResource_ofType_('Defaults', 'plist')
        defaultPreferences = NSDictionary.dictionaryWithContentsOfFile_(defaultPreferencesFile)
        self.preferences = NSUserDefaults.standardUserDefaults()
        self.preferences.registerDefaults_(defaultPreferences)
        
        if self.preferences.boolForKey_('PCOpenDefaultFileOnStartup'):
            defaultFile = self.preferences.stringForKey_('PCDefaultFile')
            if not os.path.exists(defaultFile):
                alert = NSAlert.alloc().init()
                alert.setMessageText_(NSLocalizedString("Unable to open default file", ""))
                alert.setInformativeText_(NSLocalizedString("File does not exist.", ""))
                alert.setAlertStyle_(NSCriticalAlertStyle)
                alert.runModal()
                return
            
            documentController = NSDocumentController.sharedDocumentController()
            documentController.closeAllDocumentsWithDelegate_didCloseAllSelector_contextInfo_(None, None, None)
            documentController.openDocumentWithContentsOfURL_display_error_(NSURL.fileURLWithPath_(defaultFile), True, None)
