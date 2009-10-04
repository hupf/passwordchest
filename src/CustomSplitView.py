#
#  CustomSplitView.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
#

from Foundation import *
from AppKit import *

class CustomSplitView(NSSplitView):
    def adjustSubviews(self):
        leftFrame = self.subviews()[0].frame()
        rightFrame = self.subviews()[1].frame()
        
        self.subviews()[0].setFrameSize_(NSSize(
            self.frame().size.width - rightFrame.size.width,
            self.frame().size.height))
        
        self.subviews()[1].setFrameSize_(NSSize(
            rightFrame.size.width,
            self.frame().size.height))
