import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine

ApplicationWindow {
    id: root
    visible: true
    width: 1500
    height: 900
    title: appName
    
    // Tab bar at the top
    header: TabBar {
        id: tabBar
        width: parent.width
        
        TabButton {
            text: "Library"
        }
        TabButton {
            text: "Data"
        }
        TabButton {
            text: "Data 2"
        }
    }
    
    // Stack layout for tab content
    StackLayout {
        anchors.fill: parent
        currentIndex: tabBar.currentIndex
        
        // Library Tab
        LibraryView {
            id: libraryView
        }
        
        // Data Tab
        DataView {
            id: dataView
        }
        
        // Data 2 Tab (UI Data)
        UiDataView {
            id: uiDataView
        }
    }
    
    // Settings window (initially hidden)
    SettingsWindow {
        id: settingsWindow
    }
    
    // Editor window (initially hidden)
    EditorWindow {
        id: editorWindow
    }
    
    // Image browser window
    ImageBrowserWindow {
        id: imageBrowserWindow
    }
    
    // Connections to refresh data
    Connections {
        target: dataManager
        function onDataChanged() {
            libraryView.refresh()
            dataView.refresh()
            uiDataView.refresh()
        }
    }
    
    Connections {
        target: gameLauncher
        function onGameLaunched() {
            root.close()
        }
    }
}
