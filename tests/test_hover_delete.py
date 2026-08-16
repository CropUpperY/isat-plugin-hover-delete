import importlib
import sys
import types
import unittest


class _QObject:
    def __init__(self):
        pass


class _QPointF:
    def __init__(self, value=None):
        self.value = value


class _QEvent:
    ShortcutOverride = 1
    KeyPress = 2


class _Qt:
    Key_Delete = 100
    NoModifier = 0


class _Application:
    current = None

    @classmethod
    def instance(cls):
        return cls.current

    def __init__(self):
        self.filters = []
        self.modal = None

    def installEventFilter(self, event_filter):
        self.filters.append(event_filter)

    def removeEventFilter(self, event_filter):
        if event_filter in self.filters:
            self.filters.remove(event_filter)

    def activeModalWidget(self):
        return self.modal


class _PluginBase:
    def __init__(self):
        self.enabled = False


def _load_plugin_module():
    pyqt5 = types.ModuleType("PyQt5")
    pyqt5.QtCore = types.SimpleNamespace(QObject=_QObject, QPointF=_QPointF, QEvent=_QEvent, Qt=_Qt)
    pyqt5.QtGui = types.SimpleNamespace(QCursor=types.SimpleNamespace(pos=lambda: None))
    pyqt5.QtWidgets = types.SimpleNamespace(QApplication=_Application)

    isat = types.ModuleType("ISAT")
    widgets = types.ModuleType("ISAT.widgets")
    plugin_base = types.ModuleType("ISAT.widgets.plugin_base")
    plugin_base.PluginBase = _PluginBase

    sys.modules.update(
        {
            "PyQt5": pyqt5,
            "ISAT": isat,
            "ISAT.widgets": widgets,
            "ISAT.widgets.plugin_base": plugin_base,
        }
    )
    sys.modules.pop("isat_plugin_hover_delete.main", None)
    return importlib.import_module("isat_plugin_hover_delete.main")


class _Mode:
    name = "VIEW"


class _Vertex:
    def __init__(self, parent_shape):
        self.parent_shape = parent_shape
        self.layer = None

    def setZValue(self, layer):
        self.layer = layer


class _PyPIStyleVertex:
    """ISAT-SAM 1.5.2 from PyPI names the owner attribute `polygon`."""

    def __init__(self, polygon):
        self.polygon = polygon
        self.layer = None

    def setZValue(self, layer):
        self.layer = layer


class _Polygon:
    def __init__(self, layer, scene, vertex_count=5):
        self.layer = layer
        self._scene = scene
        self.vertices = [_Vertex(self) for _ in range(vertex_count)]
        self.points = list(range(vertex_count))
        self.deleted = False
        self.area = 0

    def zValue(self):
        return self.layer

    def setZValue(self, layer):
        self.layer = layer

    def delete(self):
        self.deleted = True
        self.vertices.clear()
        self.points.clear()

    def removePoint(self, index):
        self.points.pop(index)
        return self.vertices.pop(index)

    def calculate_area(self):
        return len(self.vertices) * 10

    def scene(self):
        return self._scene


class _Scene:
    def __init__(self):
        self.mode = _Mode()
        self.hit_items = []
        self.selected_polygons_list = []
        self.hovered_vertex = None
        self.removed = []
        self.updated = False

    def items(self, position):
        return self.hit_items

    def removeItem(self, item):
        self.removed.append(item)
        item._scene = None

    def selectedItems(self):
        return []

    def update(self):
        self.updated = True


class _Dock:
    def __init__(self):
        self.removed = []

    def listwidget_remove_polygon(self, polygon):
        self.removed.append(polygon)


class _Action:
    def __init__(self):
        self.enabled = None

    def setEnabled(self, enabled):
        self.enabled = enabled


class _MainWindow:
    def __init__(self, scene, polygons):
        self.scene = scene
        self.polygons = polygons
        self.view = object()
        self.can_be_annotated = True
        self.annos_dock_widget = _Dock()
        self.actionDelete = _Action()
        self.saved_states = []

    def set_saved_state(self, state):
        self.saved_states.append(state)


class _Event:
    def __init__(self, event_type, auto_repeat=False):
        self._event_type = event_type
        self._auto_repeat = auto_repeat
        self.accepted = False

    def type(self):
        return self._event_type

    def key(self):
        return _Qt.Key_Delete

    def modifiers(self):
        return _Qt.NoModifier

    def isAutoRepeat(self):
        return self._auto_repeat

    def accept(self):
        self.accepted = True


class HoverDeletePluginTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_plugin_module()

    def setUp(self):
        _Application.current = _Application()
        self.scene = _Scene()
        self.bottom = _Polygon(1, self.scene)
        self.top = _Polygon(2, self.scene)
        self.mainwindow = _MainWindow(self.scene, [self.bottom, self.top])
        self.plugin = self.module.HoverDeletePlugin()
        self.plugin.init_plugin(self.mainwindow)
        self.plugin.enable_plugin()

    def test_resolves_only_an_actual_vertex(self):
        helper = types.SimpleNamespace(parent_shape=self.top)
        target = self.top.vertices[1]
        self.scene.hit_items = [object(), helper, target, self.bottom]
        self.assertIs(self.plugin.vertex_at(object()), target)

    def test_polygon_fill_or_edge_is_not_a_delete_target(self):
        self.scene.hit_items = [self.top, self.bottom]
        self.assertIsNone(self.plugin.vertex_at(object()))

    def test_uses_isat_native_hovered_vertex_state(self):
        target = self.top.vertices[3]
        self.scene.hovered_vertex = target
        self.assertIs(self.plugin.vertex_under_cursor(), target)

    def test_supports_pypi_1_5_2_vertex_polygon_attribute(self):
        target = _PyPIStyleVertex(self.top)
        self.top.vertices[2] = target
        self.scene.hovered_vertex = target
        self.assertIs(self.plugin.vertex_under_cursor(), target)
        self.assertTrue(self.plugin.delete_vertex(target))
        self.assertEqual(len(self.top.vertices), 4)

    def test_delete_removes_only_hovered_vertex(self):
        target = self.top.vertices[2]
        self.scene.hovered_vertex = target
        self.assertTrue(self.plugin.delete_vertex(target))
        self.assertEqual(self.mainwindow.polygons, [self.bottom, self.top])
        self.assertEqual(len(self.top.vertices), 4)
        self.assertNotIn(target, self.top.vertices)
        self.assertFalse(self.top.deleted)
        self.assertEqual(self.top.area, 40)
        self.assertEqual(self.mainwindow.saved_states, [False])
        self.assertIsNone(self.scene.hovered_vertex)
        self.assertEqual(self.mainwindow.annos_dock_widget.removed, [])
        self.assertTrue(self.scene.updated)

    def test_four_point_polygon_is_removed_when_one_vertex_is_deleted(self):
        quadrilateral = _Polygon(1, self.scene, vertex_count=4)
        self.mainwindow.polygons = [quadrilateral, self.top]
        target = quadrilateral.vertices[0]
        self.assertTrue(self.plugin.delete_vertex(target))
        self.assertEqual(self.mainwindow.polygons, [self.top])
        self.assertEqual(self.mainwindow.annos_dock_widget.removed, [quadrilateral])
        self.assertEqual(self.scene.removed, [quadrilateral])
        self.assertTrue(quadrilateral.deleted)
        self.assertEqual(self.top.layer, 1)
        self.assertEqual(self.top.vertices[0].layer, 1)
        self.assertTrue(self.scene.updated)

    def test_shortcut_override_prevents_selected_delete_race(self):
        self.plugin.vertex_under_cursor = lambda: self.top.vertices[0]
        event = _Event(_QEvent.ShortcutOverride)
        self.assertTrue(self.plugin._event_filter.eventFilter(None, event))
        self.assertTrue(event.accepted)
        self.assertEqual(len(self.mainwindow.polygons), 2)

    def test_delete_key_deletes_hovered_vertex_once(self):
        target = self.top.vertices[0]
        self.plugin.vertex_under_cursor = lambda: target
        event = _Event(_QEvent.KeyPress)
        self.assertTrue(self.plugin._event_filter.eventFilter(None, event))
        self.assertTrue(event.accepted)
        self.assertEqual(len(self.top.vertices), 4)
        self.assertEqual(self.mainwindow.polygons, [self.bottom, self.top])

        repeated = _Event(_QEvent.KeyPress, auto_repeat=True)
        self.plugin.vertex_under_cursor = lambda: self.top.vertices[0]
        self.assertTrue(self.plugin._event_filter.eventFilter(None, repeated))
        self.assertEqual(len(self.top.vertices), 4)


if __name__ == "__main__":
    unittest.main()

