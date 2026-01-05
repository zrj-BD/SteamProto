import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    id: settingsWindow
    width: 800
    height: 600
    title: appName + " Settings"
    modality: Qt.ApplicationModal
    
    property var settings: ({})
    
    function loadSettings() {
        let json = dataManager.getSettingsJson()
        settings = JSON.parse(json)
        automaticScansSwitch.checked = settings.automatic_scans || false
        designSwitch.checked = settings.design || false
    }
    
    function saveSettings() {
        settings.automatic_scans = automaticScansSwitch.checked
        settings.design = designSwitch.checked
        dataManager.saveSettings(JSON.stringify(settings))
    }
    
    Component.onCompleted: loadSettings()
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 0
        
        // Button bar
        RowLayout {
            Layout.fillWidth: true
            spacing: 0
            
            Button {
                text: "Exit"
                Layout.preferredWidth: 100
                onClicked: settingsWindow.close()
            }
            
            Button {
                text: "Save"
                Layout.preferredWidth: 100
                onClicked: {
                    saveSettings()
                    settingsWindow.close()
                }
            }
            
            Item {
                Layout.fillWidth: true
            }
        }
        
        // Settings content
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ColumnLayout {
                width: settingsWindow.width - 40
                spacing: 30
                
                // Automatic Scans setting
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 50
                    spacing: 50
                    
                    Label {
                        text: "Automatic Scans"
                        font.bold: true
                        Layout.preferredWidth: 200
                    }
                    
                    Item {
                        Layout.fillWidth: true
                    }
                    
                    Switch {
                        id: automaticScansSwitch
                        Layout.alignment: Qt.AlignRight
                    }
                }
                
                // Design setting
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 50
                    spacing: 50
                    
                    Label {
                        text: "Design"
                        font.bold: true
                        Layout.preferredWidth: 200
                    }
                    
                    Item {
                        Layout.fillWidth: true
                    }
                    
                    Switch {
                        id: designSwitch
                        Layout.alignment: Qt.AlignRight
                    }
                }
                
                Item {
                    Layout.fillHeight: true
                }
            }
        }
    }
}
