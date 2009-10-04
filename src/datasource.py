#
#  datasource.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
#  Copyright (c) 2009 Mathis Hofer. All rights reserved.
#

from objc import YES, NO, IBAction, IBOutlet
from Foundation import *
from AppKit import *
from loxodo.vault import Vault


class RecordNode(NSObject):
    def initWithRecord_(self, record):
        self = super(RecordNode, self).init()
        if self is None: return None

        self.record = record
        
        return self
    
    def _get_title(self):
        return self.record._get_title()


class RecordGroupNode(NSObject):
    def initWithTitle_(self, title):
        self = super(RecordGroupNode, self).init()
        if self is None: return None

        self.title = title
        
        return self
    
    def _get_title(self):
        return self.title


NSOutlineViewDataSource = objc.protocolNamed('NSOutlineViewDataSource')
class ListDataSource(NSObject, NSOutlineViewDataSource):
    mainWindowController = None
    vault = None
    records = {}

    def initWithMainWindowController_(self, mainWindowController):
        self = super(ListDataSource, self).init()
        if self is None: return None

        self.mainWindowController = mainWindowController
        self.vault = mainWindowController.vault
        self.updateRecords()
        
        return self
    
    def outlineView_numberOfChildrenOfItem_(self, outlineView, item):
        return item is None and len(self.records) \
            or isinstance(item, RecordGroupNode) and len(self.records[item]) \
            or 0

    def outlineView_isItemExpandable_(self, outlineView, item):
        return not isinstance(item, RecordNode)
    
    def outlineView_child_ofItem_(self, outlineView, index, item):
        return item is None and self.records.keys()[index] \
            or isinstance(item, RecordGroupNode) and self.records[item][index] \
            or None

    def outlineView_objectValueForTableColumn_byItem_(self, outlineView, tableColumn, item):
        return item is not None and item._get_title() or '<root>'
    
    def outlineView_setObjectValue_forTableColumn_byItem_(self, outlineView, object, tableColumn, item):
        #item.rename(object)
        #self.mainWindowController.updateEntryInfo(item.entry)
        pass
    
    #def outlineView_shouldEditTableColumn_item_(self, outlineView, tableColumn, item):
    #    if isinstance(item, RecordNode):
    #        self.mainWindowController.editEntry(item.record)
    
    def outlineViewSelectionDidChange_(self, notification):
        self.mainWindowController.updateInfo()
    
    def updateRecords(self):
        # sort vault records by group then by title
        def comp(r1, r2):
            if r1._get_group() == r2._get_group():
                return cmp(r1._get_title(), r2._get_title())
            return cmp(r1._get_group(), r2._get_group())
        self.vault.records.sort(comp)
        
        # update records dict
        self.records = {}
        last_group = None
        group = []
        for record in self.vault.records:
            if record._get_group() != last_group:
                if last_group:
                    self.records[RecordGroupNode.alloc().initWithTitle_(last_group)] = group
                last_group = record._get_group()
                group = []
            group.append(RecordNode.alloc().initWithRecord_(record))
        if group:
            self.records[RecordGroupNode.alloc().initWithTitle_(last_group)] = group
