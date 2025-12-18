import os.path

import h5py
import silx.gui.hdf5
from silx.gui import qt
from silx.gui.hdf5._utils import H5Node


class Hdf5TreeView(silx.gui.hdf5.Hdf5TreeView):

    h5NodeActivated = qt.Signal(H5Node)
    """Signal emitted when a H5Node is activated for viewing"""

    def __init__(self, parent: qt.QWidget | None = None):
        super().__init__(parent)
        self.setSelectionMode(qt.QAbstractItemView.SelectionMode.MultiSelection)
        self.setDragDropMode(qt.QAbstractItemView.DragDropMode.NoDragDrop)
        self.addContextMenuCallback(self.__customContextMenu)
        self.activated.connect(self.__activated)

    def selectionCommand(
        self, index: qt.QModelIndex, event: qt.QEvent | None
    ) -> qt.QItemSelectionModel.SelectionFlag:
        """Enable item selection only with left mouse button"""
        if (
            event is not None
            and event.type() == qt.QEvent.Type.MouseButtonPress
            and event.button() != qt.Qt.LeftButton
        ):
            return qt.QItemSelectionModel.SelectionFlag.NoUpdate
        return super().selectionCommand(index, event)

    def __activated(self, index: qt.QModelIndex):
        if not index.isValid():
            return
        firstIndex = index.siblingAtColumn(0)
        if not firstIndex.isValid():
            return
        item = self.model().data(firstIndex, silx.gui.hdf5.Hdf5TreeModel.H5PY_ITEM_ROLE)
        if item is None:
            return
        self.h5NodeActivated.emit(H5Node(item))

    def __customContextMenu(self, event: silx.gui.hdf5.Hdf5ContextMenuEvent):
        """
        Populate the custom context menu for the HDF5 tree viewer.

        Adds additional options to remove or reload HDF5 files in the tree view when the
        context menu is triggered.
        """
        menu = event.menu()

        if not menu.isEmpty():
            menu.addSeparator()

        h5node = event.hoveredObject()
        action = qt.QAction("View", event.source())
        action.triggered.connect(lambda: self.h5NodeActivated.emit(h5node))
        menu.addAction(action)

        if h5node.ntype is h5py.File:
            filename = os.path.basename(h5node.local_filename)
            action = qt.QAction(f"Remove {filename}", event.source())
            action.triggered.connect(
                lambda: self.findHdf5TreeModel().removeH5pyObject(h5node.h5py_object)
            )
            menu.addAction(action)
            action = qt.QAction(f"Reload {filename}", event.source())
            action.triggered.connect(
                lambda: self.findHdf5TreeModel().synchronizeH5pyObject(
                    h5node.h5py_object
                )
            )
            menu.addAction(action)
