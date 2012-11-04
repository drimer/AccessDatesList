from setuptools import setup
from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem
from PyQt4.QtCore import QStringList, QString
from PyQt4.QtGui import QColor
from datetime import datetime
import os



class Item(QTreeWidgetItem):
    ACCESS_DENIED = 1
    ACCESS_ALLOWED = 2
    
    
    def __init__(self, fullPath, displayName = None, parent = None):
        assert isinstance(fullPath, str)

        if displayName is None:
            displayName = fullPath
        self.__fullPath = fullPath
        self.__displayName = displayName

        stringList = QStringList()
        stringList.append(QString(displayName))

        st = os.stat(fullPath)
        self.__lastAccessDate = datetime.fromtimestamp(st.st_atime)

        dateStr = self.getStrDate()
        stringList.append(QString(dateStr))
        super(Item, self).__init__(parent, stringList)


    def getStrDate(self):
        return self.__lastAccessDate.strftime("%H:%M:%S %d/%m/%Y")
    
    
    def __str__(self):
        return self.__fullPath
    
    def getFullPath(self):
        return self.__fullPath
    
    
    def getDisplayName(self):
        return self.__displayName
    
    
    def getLastAccessDate(self):
        return self.__lastAccessDate


    def setAccess(self, access):
        self.__access = access
        numCols = self.columnCount()
        for count in range(numCols):
            if access == Item.ACCESS_ALLOWED:
                self.setTextColor(count, QColor(0, 0, 0))
            elif access == Item.ACCESS_DENIED:
                self.setTextColor(count, QColor(255, 0, 0))


class ItemFactory(object):
    @staticmethod
    def createItem(path, displayName = None):
        assert isinstance(path, str)
        try:
            if os.path.isdir(path):
                newItem = DirectoryTreeItem(path, displayName = displayName)
            else:
                newItem = FileTreeItem(path, displayName = displayName)
            return newItem
        except Exception, ex:
            print '>> createItem: ', ex
            return None


    @staticmethod
    def createSubItems(treeItem):
        assert isinstance(treeItem, Item)
        subDirs = os.listdir(treeItem.getFullPath())
        subDirsFullPath = map(lambda d: treeItem.getFullPath() + '/' + d,
                              subDirs)
        
        children = []
        for count, path in enumerate(subDirsFullPath):
            newItem = None
            try:
                if os.path.isdir(subDirsFullPath[count]):
                    newItem = DirectoryTreeItem(path, subDirs[count])
                else:
                    newItem = FileTreeItem(path, subDirs[count])
                children.append(newItem)
            except Exception, ex:
                print '>> createSubItems:', ex
        
        sortedChildren = ItemFactory.sortItems(children,
                                               ItemFactory.compMostRecent)
        for item in sortedChildren:
            treeItem.addChild(item)
        
    
    @staticmethod
    def compMostRecent(item1, item2):
        date1 = item1.getLastAccessDate()
        date2 = item2.getLastAccessDate()
        if date1 < date2:
            return 1
        elif date1 == date2:
            return 0
        else:
            return -1
    
    @staticmethod
    def sortItems(items, funcComp):
        sortedItems = [item for item in items]
        sortedItems.sort(cmp = funcComp)
        return sortedItems


class FileTreeItem(Item):
    def __init__(self, fullPath, displayName = None, parent = None):
        super(FileTreeItem, self).__init__(fullPath,
                                           displayName = displayName,
                                           parent = parent)

        if not os.access(fullPath, os.R_OK):
            self.setAccess(Item.ACCESS_DENIED)
        else:
            self.setAccess(Item.ACCESS_ALLOWED)


class DirectoryTreeItem(Item):
    def __init__(self, fullPath, displayName = None, parent = None):
        if displayName != None and displayName[-1] != '/':
            displayName = displayName + '/'
        super(DirectoryTreeItem, self).__init__(fullPath,
                                                displayName = displayName,
                                                parent = parent)
        
        if not os.access(fullPath, os.X_OK):
            self.setAccess(Item.ACCESS_DENIED)
        else:
            self.setAccess(Item.ACCESS_ALLOWED)
    

class AccessDatesList(QTreeWidget):
    def __init__(self, parent = None, topLevelItems = None,
                    rootDir = '/', title = ''):
        super(AccessDatesList, self).__init__(parent)

        assert isinstance(rootDir, str)
        assert isinstance(title, str)

        if title == '':
            title = rootDir

        self.setColumnCount(2)
        headersList = QStringList()
        headersList.append(QString('Path'))
        headersList.append(QString('Last Access Date'))
        self.setHeaderLabels(headersList)

        self.setWindowTitle('Last Access Dates')
        self.setColumnWidth(0, 250)
        self.setColumnWidth(1, 200)

        if rootDir[-1:] != '/':
            rootDir = rootDir + '/'

        self.__tree = []
        if topLevelItems:
            assert isinstance(topLevelItems, list)
            self.addTopLevelItems(topLevelItems)
        else:
            baseDirs = os.listdir(rootDir)
            for dir in baseDirs:
                newItem = ItemFactory.createItem(rootDir + dir,
                                                 displayName = dir)
                if newItem is not None:
                    self.__tree.append(newItem)

        self.__tree = ItemFactory.sortItems(self.__tree,
                                            ItemFactory.compMostRecent)
        self.addTopLevelItems(self.__tree)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)


    def onItemDoubleClicked(self, item):
        if isinstance(item, DirectoryTreeItem):
            ItemFactory.createSubItems(item)
