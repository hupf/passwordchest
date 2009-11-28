#
#  PCDataSource.py
#  Password Chest
#
#  Created by Mathis Hofer on 25.09.09.
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
class PCDataSource(NSObject, NSOutlineViewDataSource):
    document = None
    vault = None
    nodes = {}
    filterString = ''
    filteredNodes = {}

    def initWithPCDocument_(self, document):
        self = super(PCDataSource, self).init()
        if self is None: return None

        self.document = document
        self.vault = document.vault
        self._updateRecordsFromVault()
        
        return self
    
    def outlineView_numberOfChildrenOfItem_(self, outlineView, item):
        nodes = None
        if len(self.filterString):
            nodes = self.filteredNodes
        else:
            nodes = self.nodes
        
        return item is None and len(nodes) \
            or isinstance(item, RecordGroupNode) and len(nodes[item]) \
            or 0

    def outlineView_isItemExpandable_(self, outlineView, item):
        return not isinstance(item, RecordNode)
    
    def outlineView_child_ofItem_(self, outlineView, index, item):
        nodes = None
        if len(self.filterString):
            nodes = self.filteredNodes
        else:
            nodes = self.nodes
        
        if item is None:
            sorted_keys = nodes.keys()
            sorted_keys.sort(lambda n1, n2: cmp(n1._get_title(), n2._get_title()))
        return item is None and sorted_keys[index] \
            or isinstance(item, RecordGroupNode) and nodes[item][index] \
            or None

    def outlineView_objectValueForTableColumn_byItem_(self, outlineView, tableColumn, item):
        return item is not None and item._get_title() or '<root>'
    
    def outlineView_setObjectValue_forTableColumn_byItem_(self, outlineView, object, tableColumn, item):
        if isinstance(item, RecordNode):
            self.renameRecord_toName_(item, object)
        if isinstance(item, RecordGroupNode):
            self.renameGroup_toName_(item, object)
    
    def outlineViewSelectionDidChange_(self, notification):
        self.document.selectionChanged()
    
    def addRecord_(self, record):
        # update vault
        self.vault.records.append(record)
        
        # update outline view
        groupNode = self._getGroupNodeWithTitle_(record._get_group())
        if not groupNode:
            # create new group
            groupNode = RecordGroupNode.alloc().initWithTitle_(record._get_group())
            self.nodes[groupNode] = []
        newNode = RecordNode.alloc().initWithRecord_(record)
        self.nodes[groupNode].append(newNode)
        self._sortNodes()
        self._refreshOutlineViewAndFocusRecordNode_(newNode)
        
        self.document.updateChangeCount_(NSChangeDone)
        
    def removeRecord_(self, record):
        # update vault
        self.vault.records.remove(record)
        
        # update outline view
        groupNode = None
        for g in self.nodes.keys():
            if record._get_group() == g._get_title():
                groupNode = g
                break
        if len(self.nodes[groupNode]) == 1:
            # the only element in this group -> remove group completely
            self.nodes.pop(groupNode)
        else:
            for r in self.nodes[groupNode]:
                if r.record._get_uuid() == record._get_uuid():
                    self.nodes[groupNode].remove(r)
                    break
        self._refreshOutlineView()
        
        self.document.updateChangeCount_(NSChangeDone)
    
    def recordUpdated_(self, record):
        # update outline view
        recordNode, groupNode = self._getRecordAndGroupNodeForUUID_(record._get_uuid())
        if record._get_group() != groupNode._get_title():
            # group changed
            if len(self.nodes[groupNode]) == 1:
                # the only element in this group -> remove group completely
                self.nodes.pop(groupNode)
            else:
                self.nodes[groupNode].remove(recordNode)
            # check if new group exists
            groupNode = self._getGroupNodeWithTitle_(record._get_group())
            if not groupNode:
                # create new group
                groupNode = RecordGroupNode.alloc().initWithTitle_(record._get_group())
                self.nodes[groupNode] = []
            recordNode = RecordNode.alloc().initWithRecord_(record)
            self.nodes[groupNode].append(recordNode)
        self._sortNodes()
        self._refreshOutlineViewAndFocusRecordNode_(recordNode)
        self.document.updateInfo()
        
        self.document.updateChangeCount_(NSChangeDone)
    
    def renameRecord_toName_(self, recordNode, newName):
        recordNode.record._set_title(newName)
        recordNode.record.mark_modified()
        
        self._sortNodes()
        self._refreshOutlineView()
        self.document.updateInfo()
        
        self.document.updateChangeCount_(NSChangeDone)
    
    def removeGroup_(self, groupNode):
        for r in self.nodes[groupNode]:
            self.vault.records.remove(r.record)
        self.nodes.pop(groupNode)
        
        self._refreshOutlineView()
        
        self.document.updateChangeCount_(NSChangeDone)
    
    def renameGroup_toName_(self, groupNode, newName):
        for r in self.nodes[groupNode]:
            r.record._set_group(newName)
            r.record.mark_modified()
        
        groupNode.title = newName
        for g in self.nodes.keys():
            if g != groupNode and g._get_title() == newName:
                # a group with newName exists already
                self.nodes[g].extend(self.nodes[groupNode])
                self.nodes.pop(groupNode)
                self._sortNodes()
                break
        self.document.outlineView.reloadData()
        
        self.document.updateChangeCount_(NSChangeDone)
    
    def updateFilter_(self, filterString):
        self.filterString = filterString
        self.filteredNodes = {}
        for g in self.nodes.keys():
            groupNodes = []
            for r in self.nodes[g]:
                if filterString in r.record._get_group() or \
                    filterString in r.record._get_title() or \
                    filterString in r.record._get_user() or \
                    filterString in r.record._get_url() or \
                    filterString in r.record._get_notes():
                    groupNodes.append(r)
            if len(groupNodes):
                self.filteredNodes[g] = groupNodes
        
        node = None
        index = self.document.outlineView.selectedRow()
        if index != -1:
            node = self.document.outlineView.itemAtRow_(index)
        self.document.outlineView.reloadData()
        if node:
            index = self.document.outlineView.rowForItem_(node)
            if index != -1:
                self.document.outlineView.scrollRowToVisible_(index)
                self.document.outlineView.selectRowIndexes_byExtendingSelection_(NSIndexSet.indexSetWithIndex_(index), False)
    
    def resetFilter(self):
        self.filterString = ''
        self.filteredNodes = {}
        self.document.outlineView.reloadData()
    
    def expandAll(self):
        nodes = None
        if len(self.filterString):
            nodes = self.filteredNodes
        else:
            nodes = self.nodes
        
        for g in nodes.keys():
            self.document.outlineView.expandItem_(g)
    
    def collapseAll(self):
        nodes = None
        if len(self.filterString):
            nodes = self.filteredNodes
        else:
            nodes = self.nodes
        
        for g in nodes.keys():
            self.document.outlineView.collapseItem_(g)
    
    def _updateRecordsFromVault(self):
        self._sortVaultRecords()
        self.nodes = {}
        last_group = None
        group = []
        for record in self.vault.records:
            if record._get_group() != last_group:
                if last_group:
                    self.nodes[RecordGroupNode.alloc().initWithTitle_(last_group)] = group
                last_group = record._get_group()
                group = []
            group.append(RecordNode.alloc().initWithRecord_(record))
        if group:
            self.nodes[RecordGroupNode.alloc().initWithTitle_(last_group)] = group
    
    def _sortNodes(self):
        for group in self.nodes.keys():
            self.nodes[group].sort(lambda n1, n2: cmp(n1._get_title(), n2._get_title()))
        pass
    
    def _sortVaultRecords(self):
        # sort vault records by group then by title
        def comp(r1, r2):
            if r1._get_group() == r2._get_group():
                return cmp(r1._get_title(), r2._get_title())
            return cmp(r1._get_group(), r2._get_group())
        
        self.vault.records.sort(comp)
    
    def _getGroupNodeWithTitle_(self, title):
        for g in self.nodes.keys():
            if g._get_title() == title:
                return g
        return None
    
    def _getRecordAndGroupNodeForUUID_(self, uuid):
        for g in self.nodes.keys():
            for r in self.nodes[g]:
                if r.record._get_uuid() == uuid:
                    return (r, g)
        return None
    
    def _refreshOutlineView(self):
        self._refreshOutlineViewAndFocusRecordNode_(None)
    
    def _refreshOutlineViewAndFocusRecordNode_(self, recordNode):
        groupNode = None
        if recordNode:
            groupNode = self._getGroupNodeWithTitle_(recordNode.record._get_group())
            
        if len(self.filterString):
            self.updateFilter_(self.filterString)
            if recordNode and groupNode in self.filteredNodes.keys():
                self.document.outlineView.expandItem_(groupNode)
        else:
            self.document.outlineView.reloadData()
            if recordNode:
                self.document.outlineView.expandItem_(groupNode)
        if recordNode:
            index = self.document.outlineView.rowForItem_(recordNode)
            if index != -1:
                self.document.outlineView.scrollRowToVisible_(index)
                self.document.outlineView.selectRowIndexes_byExtendingSelection_(NSIndexSet.indexSetWithIndex_(index), False)

