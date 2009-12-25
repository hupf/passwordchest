#
#  PCSplitView.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
#

from Foundation import *
from AppKit import *

INFO_WIDTH = 323


class PCSplitView(NSSplitView):
    def drawRect_(self, rect):
        NSColor.controlHighlightColor().set()
        NSRectFill(rect)
        
        return NSSplitView.drawRect_(self, rect)
    
    def adjustSubviews(self):
        leftFrameSize = self.subviews()[0].frame().size
        rightFrameSize = self.subviews()[1].frame().size
        
        # Right frame should not be smaller than info box
        rightFrameSize.width = max(rightFrameSize.width, INFO_WIDTH)
        
        self.subviews()[0].setFrameSize_(NSSize(
            self.frame().size.width - rightFrameSize.width,
            self.frame().size.height))
        
        self.subviews()[1].setFrameSize_(NSSize(
            rightFrameSize.width,
            self.frame().size.height))
        
        return NSSplitView.adjustSubviews(self)


class PCSplitViewDelegate(NSObject):
    def splitView_constrainMaxCoordinate_ofSubviewAt_(self, splitView, proposedMaximumPosition, dividerIndex):
        return min(proposedMaximumPosition, splitView.frame().size.width - INFO_WIDTH - 1)
