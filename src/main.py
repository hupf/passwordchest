#
#  main.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
#  Copyright Mathis Hofer 2009. All rights reserved.
#

#import modules required by application
import objc
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
#import PasswordChestAppDelegate
import PCDocument

# pass control to AppKit
AppHelper.runEventLoop()
