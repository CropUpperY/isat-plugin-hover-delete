# -*- coding: utf-8 -*-
"""Hover-to-delete support for ISAT-SAM."""

from PyQt5 import QtCore, QtGui, QtWidgets

from ISAT.widgets.plugin_base import PluginBase

from . import __author__, __description__, __version__


class _DeleteKeyEventFilter(QtCore.QObject):
    """Forward unmodified Delete key events to the plugin."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def eventFilter(self, watched, event):
        if not self.plugin.enabled:
            return False

        event_type = event.type()
        if event_type not in (QtCore.QEvent.ShortcutOverride, QtCore.QEvent.KeyPress):
            return False
        if event.key() != QtCore.Qt.Key_Delete:
            return False
        if event.modifiers() != QtCore.Qt.NoModifier:
            return False

        vertex = self.plugin.vertex_under_cursor()
        if vertex is None:
            return False

        # Accept ShortcutOverride so ISAT's QAction shortcut does not delete a
        # separately selected annotation before the KeyPress reaches us.
        if event_type == QtCore.QEvent.ShortcutOverride:
            event.accept()
            return True

        if event.isAutoRepeat():
            event.accept()
            return True

        if self.plugin.delete_vertex(vertex):
            event.accept()
            return True
        return False


class HoverDeletePlugin(PluginBase):
    """Delete the hovered polygon vertex without selecting it first."""

    def __init__(self):
        super().__init__()
        self.mainwindow = None
        self._event_filter = None
        self._application = None
        self._last_scene_pos = None

    def init_plugin(self, mainwindow):
        self.mainwindow = mainwindow
        self._event_filter = _DeleteKeyEventFilter(self)

    def enable_plugin(self):
        if self.enabled:
            return
        self._application = QtWidgets.QApplication.instance()
        if self._application is None:
            return
        self._application.installEventFilter(self._event_filter)
        self.enabled = True

    def disable_plugin(self):
        if self._application is not None and self._event_filter is not None:
            self._application.removeEventFilter(self._event_filter)
        self._application = None
        self._last_scene_pos = None
        self.enabled = False

    def get_plugin_author(self):
        return __author__

    def get_plugin_version(self):
        return __version__

    def get_plugin_description(self):
        return __description__

    def on_mouse_move_event(self, scene_pos):
        self._last_scene_pos = QtCore.QPointF(scene_pos)

    def after_image_open_event(self):
        self._last_scene_pos = None

    def application_shutdown_event(self):
        self.disable_plugin()

    def _is_safe_canvas_state(self):
        if self.mainwindow is None:
            return False

        scene = getattr(self.mainwindow, "scene", None)
        view = getattr(self.mainwindow, "view", None)
        if scene is None or view is None:
            return False
        if not getattr(self.mainwindow, "can_be_annotated", True):
            return False

        mode_name = getattr(getattr(scene, "mode", None), "name", "")
        if mode_name not in ("VIEW", "EDIT"):
            return False

        app = QtWidgets.QApplication.instance()
        if app is not None and app.activeModalWidget() is not None:
            return False
        return True

    @staticmethod
    def _polygon_for_vertex(vertex):
        """Support both PyPI ISAT 1.5.2 and the newer GitHub vertex API."""
        polygon = getattr(vertex, "parent_shape", None)
        if polygon is None:
            polygon = getattr(vertex, "polygon", None)
        return polygon

    def vertex_at(self, scene_pos):
        """Return the topmost annotation vertex at a scene position."""
        if not self._is_safe_canvas_state():
            return None

        scene = self.mainwindow.scene
        polygons = self.mainwindow.polygons
        if not polygons:
            return None

        # QGraphicsScene.items() is ordered from the highest visible item to
        # the lowest. Polygon fills/edges and non-annotation helpers are skipped.
        for item in scene.items(scene_pos):
            parent_shape = self._polygon_for_vertex(item)
            if (
                parent_shape in polygons
                and item in getattr(parent_shape, "vertices", [])
            ):
                return item
        return None

    def vertex_under_cursor(self):
        """Resolve the hovered vertex from the cursor's current screen position."""
        if not self._is_safe_canvas_state():
            return None

        # ISAT-SAM explicitly maintains this value from PolygonVertex's
        # hoverEnterEvent/hoverLeaveEvent. It is more reliable than generic
        # point hit-testing for the very small vertex QPainterPath.
        scene = self.mainwindow.scene
        hovered_vertex = getattr(scene, "hovered_vertex", None)
        parent_shape = self._polygon_for_vertex(hovered_vertex)
        if (
            parent_shape in self.mainwindow.polygons
            and hovered_vertex in getattr(parent_shape, "vertices", [])
        ):
            return hovered_vertex

        # Fallback for ISAT-SAM versions that do not expose hovered_vertex.
        view = self.mainwindow.view
        viewport = view.viewport()
        viewport_pos = viewport.mapFromGlobal(QtGui.QCursor.pos())
        if not viewport.rect().contains(viewport_pos):
            return None

        scene_pos = view.mapToScene(viewport_pos)
        return self.vertex_at(scene_pos)

    def delete_vertex(self, vertex):
        """Delete one vertex and keep the annotation valid and synchronized."""
        if not self._is_safe_canvas_state():
            return False

        mainwindow = self.mainwindow
        scene = mainwindow.scene
        polygon = self._polygon_for_vertex(vertex)
        if polygon not in mainwindow.polygons or vertex not in polygon.vertices:
            return False

        if getattr(scene, "hovered_vertex", None) is vertex:
            scene.hovered_vertex = None

        vertex_index = polygon.vertices.index(vertex)
        polygon.removePoint(vertex_index)

        # Match ISAT-SAM's vertex-deletion behaviour: deleting a vertex from a
        # four-point polygon removes the entire annotation instead of leaving
        # a three-point polygon.
        if len(polygon.vertices) <= 3:
            self._delete_invalid_polygon(polygon)
        else:
            calculate_area = getattr(polygon, "calculate_area", None)
            if callable(calculate_area):
                polygon.area = calculate_area()
            mainwindow.set_saved_state(False)

        scene.update()
        return True

    def _delete_invalid_polygon(self, polygon):
        """Remove a polygon that can no longer contain three vertices."""
        mainwindow = self.mainwindow
        scene = mainwindow.scene
        deleted_layer = polygon.zValue()

        selected_polygons = getattr(scene, "selected_polygons_list", None)
        if selected_polygons is not None and polygon in selected_polygons:
            selected_polygons.remove(polygon)

        mainwindow.polygons.remove(polygon)
        mainwindow.annos_dock_widget.listwidget_remove_polygon(polygon)
        polygon.delete()
        if polygon.scene() is scene:
            scene.removeItem(polygon)

        for remaining_polygon in mainwindow.polygons:
            if remaining_polygon.zValue() > deleted_layer:
                remaining_polygon.setZValue(remaining_polygon.zValue() - 1)
                for vertex in getattr(remaining_polygon, "vertices", []):
                    vertex.setZValue(remaining_polygon.zValue())

        action_delete = getattr(mainwindow, "actionDelete", None)
        if action_delete is not None:
            action_delete.setEnabled(bool(scene.selectedItems()))

