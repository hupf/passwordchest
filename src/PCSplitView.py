#
#  PCSplitView.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
#

from Foundation import *
from AppKit import *

class PCSplitView(NSSplitView):
    def adjustSubviews(self):
        leftFrameSize = self.subviews()[0].frame().size
        rightFrameSize = self.subviews()[1].frame().size
        
        self.subviews()[0].setFrameSize_(NSSize(
            self.frame().size.width - rightFrameSize.width,
            self.frame().size.height))
        
        self.subviews()[1].setFrameSize_(NSSize(
            rightFrameSize.width,
            self.frame().size.height))
        
        NSSplitView.adjustSubviews(self)

    def drawRect_(self, rect):
        NSColor.controlHighlightColor().set()
        NSRectFill(rect)
        
        NSSplitView.drawRect_(self, rect)
