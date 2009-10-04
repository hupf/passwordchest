#
#  PasswordChestAppDelegate.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
#  Copyright Mathis Hofer 2009. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from AppKit import *
from loxodo.vault import Vault

from PasswordDialogController import PasswordDialogController
from MainWindowController import MainWindowController
from CustomSplitView import CustomSplitView

class PasswordChestAppDelegate(NSObject):
    passwordDialog = None

    def applicationDidFinishLaunching_(self, sender):
        NSLog("Application did finish launching.")

    def newDocument_(self, sender):
        mainWindowController = MainWindowController.alloc().init()

    def openDocument_(self, sender):
        dialog = NSOpenPanel.openPanel()
        dialog.setCanChooseFiles_(YES)
        dialog.setCanChooseDirectories_(NO)
        dialog.setAllowsMultipleSelection_(NO)
        
        if dialog.runModalForDirectory_file_(None, None) == NSOKButton:
            filename = dialog.filenames().objectAtIndex_(0)
            
            passwordDialogController = PasswordDialogController.alloc().init()
            vault = None
            error = None
            while vault is None or vault and error == Vault.BadPasswordError:
                password = passwordDialogController.askForPassword()
                vault = None
                error = None
                if password is not None:
                    try:
                        vault = Vault(password, filename=filename)
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
                mainWindowController = MainWindowController.alloc().initWithFilename_andVault_(filename, vault)
