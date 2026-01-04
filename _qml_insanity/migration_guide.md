# PyQt Widgets to QML Migration Guide

## Overview

I've converted your Steam Proto application from PyQt6 Widgets to PyQt6 QML. Here's what changed and how to use the new structure.

## Architecture Changes

### Before (Widgets)
- **UI in Python**: All UI elements created in Python code
- **Mixed concerns**: UI and logic tightly coupled
- **Imperative**: Manually manage widget creation, layout, updates

### After (QML)
- **UI in QML**: Declarative UI in separate .qml files
- **Separated concerns**: Clean separation between backend (Python) and frontend (QML)
- **Declarative**: QML automatically handles rendering and updates

## File Structure

```
project/
├── main_qml.py              # Python backend (replaces your old main file)
├── main.qml                 # Main window structure
├── LibraryView.qml          # Library tab
├── DataView.qml             # Data tab  
├── UiDataView.qml           # Data 2 tab
├── SettingsWindow.qml       # Settings window
├── EditorWindow.qml         # Editor window
├── ImageBrowserWindow.qml   # Image browser
├── web.py                   # Your existing module
├── remover.py               # Your existing module
├── main.py                  # Your existing module
└── data/                    # Your data directory
```

## Key Changes

### 1. Backend Architecture

**Old approach**: Everything in one file with QWidget classes

**New approach**: Clean backend classes that expose data to QML:

- **DataManager**: Handles all JSON file operations
- **GameLauncher**: Launches game executables
- **ScanManager**: Handles scanning operations
- **ImageDownloader**: Downloads game images

### 2. Data Flow

**Python → QML**:
```python
# Python exposes data
@pyqtSlot(result=str)
def getAllGamesJson(self) -> str:
    return json.dumps(list(self._ui_data.keys()))
```

```qml
// QML accesses data
let gamesJson = dataManager.getAllGamesJson()
let games = JSON.parse(gamesJson)
```

**QML → Python**:
```qml
// QML calls Python method
Button {
    onClicked: scanManager.performScan()
}
```

```python
# Python method executes
@pyqtSlot()
def performScan(self):
    main.main()
    self.scanFinished.emit()
```

### 3. Signals and Slots

**Signals in Python**:
```python
class DataManager(QObject):
    dataChanged = pyqtSignal()
    
    def load_all_data(self):
        # ... load data ...
        self.dataChanged.emit()  # Notify QML
```

**Connections in QML**:
```qml
Connections {
    target: dataManager
    function onDataChanged() {
        refresh()  // Update UI
    }
}
```

### 4. UI Components

**Old (Widgets)**:
```python
button = QPushButton("Click me")
button.setFixedWidth(100)
button.clicked.connect(self.handler)
layout.addWidget(button)
```

**New (QML)**:
```qml
Button {
    text: "Click me"
    Layout.preferredWidth: 100
    onClicked: handler()
}
```

## Running the Application

### Prerequisites
```bash
pip install PyQt6 PyQt6-WebEngine
```

### Launch
```bash
python main_qml.py
```

### With Arguments (same as before)
```bash
python main_qml.py --metadata path/to/metadata.json --uidata path/to/ui.json
```

## Benefits of QML

### 1. **Better Performance**
- Hardware-accelerated rendering
- Efficient scene graph
- Better for animations and visual effects

### 2. **Cleaner Code**
- Separation of concerns
- More maintainable
- Easier to modify UI without touching logic

### 3. **Modern UI**
- Better styling capabilities
- Smoother animations
- Responsive layouts

### 4. **Hot Reload** (optional)
- Can reload QML without restarting Python
- Faster iteration during development

## Migrating Additional Features

### Custom Widgets

**Old (PyQt6_SwitchControl)**:
You used a custom switch control widget. In QML, use the built-in `Switch` component:

```qml
Switch {
    checked: settings.automatic_scans
    onToggled: settings.automatic_scans = checked
}
```

### Styling

**Old (setStyleSheet)**:
```python
button.setStyleSheet("""
    QPushButton { background-color: rgba(0, 0, 0, 100) }
    QPushButton:hover { background-color: rgba(0, 0, 0, 150) }
""")
```

**New (QML properties)**:
```qml
Button {
    background: Rectangle {
        color: parent.pressed ? "#C8000000" 
             : (parent.hovered ? "#96000000" : "#64000000")
        radius: 4
    }
}
```

### Web Views

**Old**:
```python
self.viewer = QWebEngineView(self)
self.page = QWebEnginePage(profile, self.viewer)
self.viewer.setPage(self.page)
self.viewer.load(QUrl(url))
```

**New**:
```qml
WebEngineView {
    url: "https://example.com"
    profile: WebEngineProfile {
        httpUserAgent: "..."
        httpCacheType: WebEngineProfile.MemoryHttpCache
    }
}
```

## Common Patterns

### 1. Refreshing Data
```qml
function refresh() {
    let json = dataManager.getDataJson()
    items = JSON.parse(json)
    // Update model
}
```

### 2. Modal Dialogs
```qml
Dialog {
    id: confirmDialog
    modal: true
    title: "Confirm"
    standardButtons: Dialog.Yes | Dialog.No
    onAccepted: performAction()
}
```

### 3. Lists and Tables
```qml
ListView {
    model: ListModel { id: tableModel }
    delegate: Rectangle {
        // Row layout
        Label { text: model.game }
        Label { text: model.appid }
    }
}
```

### 4. File Dialogs
```qml
FileDialog {
    id: fileDialog
    nameFilters: ["Executable Files (*.exe)"]
    onAccepted: handleFile(selectedFile)
}
```

## Troubleshooting

### Images Not Showing
- QML requires `file:///` prefix for local files
- Use absolute paths: `"file:///" + absolutePath`

### Data Not Updating
- Ensure signals are emitted: `self.dataChanged.emit()`
- Check Connections in QML
- Verify JSON parsing

### WebEngine Not Working
- Import: `from PyQt6.QtWebEngineQuick import QtWebEngineQuick`
- Initialize: `QtWebEngineQuick.initialize()` before creating app

### Layout Issues
- Use `Layout.preferredWidth` not `width` in layouts
- Use `Layout.fillWidth: true` for expanding items

## Next Steps

### 1. Add Custom Styling
Create a `Style.qml` singleton for consistent theming:
```qml
pragma Singleton
import QtQuick

QtObject {
    readonly property color primary: "#34b233"
    readonly property color background: "#f0f0f0"
    readonly property int buttonWidth: 100
}
```

### 2. Add Animations
```qml
Button {
    Behavior on opacity {
        NumberAnimation { duration: 200 }
    }
}
```

### 3. Optimize Performance
- Use `Loader` for complex components
- Implement lazy loading for large lists
- Cache expensive operations

### 4. Add State Management
```qml
Item {
    states: [
        State { name: "loading"; PropertyChanges { target: spinner; visible: true } },
        State { name: "ready"; PropertyChanges { target: content; visible: true } }
    ]
}
```

## Additional Resources

- [Qt QML Documentation](https://doc.qt.io/qt-6/qmlapplications.html)
- [Qt Quick Controls](https://doc.qt.io/qt-6/qtquickcontrols-index.html)
- [QML Best Practices](https://doc.qt.io/qt-6/qtquick-bestpractices.html)

## Need Help?

The conversion maintains all your original functionality while providing a modern, maintainable architecture. Each component is now clearly separated and easier to modify independently.
