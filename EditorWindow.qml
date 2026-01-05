import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Window {
    id: editorWindow
    width: 1500
    height: 900
    title: appName + " Editor"
    modality: Qt.ApplicationModal
    
    property string editorType: "data" // "data" or "exe"
    property var itemsList: []
    
    function loadData() {
        if (editorType === "data") {
            let json = dataManager.getMetadataListJson()
            itemsList = JSON.parse(json)
        } else {
            let json = dataManager.getUiDataListJson()
            itemsList = JSON.parse(json)
        }
        tableModel.clear()
        for (let i = 0; i < itemsList.length; i++) {
            tableModel.append(itemsList[i])
        }
    }
    
    function saveData() {
        for (let i = 0; i < tableModel.count; i++) {
            let item = tableModel.get(i)
            let game = item.game
            let data = {}
            
            if (editorType === "data") {
                data.appid = item.appid
                data.emulator = item.emulator
                data.build = item.build
                dataManager.updateMetadata(game, JSON.stringify(data))
            } else {
                data.exesrc = item.exesrc
                dataManager.updateUiData(game, JSON.stringify(data))
            }
        }
    }
    
    Component.onCompleted: loadData()
    onVisibleChanged: {
        if (visible) loadData()
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Button bar
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            spacing: 0
            
            Button {
                text: "Exit"
                Layout.preferredWidth: 100
                onClicked: editorWindow.close()
            }
            
            Button {
                text: "Save"
                Layout.preferredWidth: 100
                onClicked: {
                    confirmDialog.message = "Save changes?"
                    confirmDialog.acceptAction = function() {
                        saveData()
                        editorWindow.close()
                    }
                    confirmDialog.open()
                }
            }
            
            Item {
                Layout.fillWidth: true
            }
        }
        
        // Header
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 30
            color: "#f0f0f0"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 5
                spacing: 50
                
                Label {
                    text: "Game"
                    font.bold: true
                    Layout.preferredWidth: 150
                }
                
                Label {
                    text: editorType === "data" ? "AppID" : "Exe Source"
                    font.bold: true
                    Layout.preferredWidth: 200
                }
                
                Label {
                    text: editorType === "data" ? "Emulator" : "PNG"
                    font.bold: true
                    Layout.preferredWidth: 100
                }
                
                Label {
                    text: editorType === "data" ? "Build" : ""
                    font.bold: true
                    Layout.preferredWidth: 100
                    visible: editorType === "data"
                }
            }
        }
        
        // Scrollable table
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            ListView {
                id: listView
                model: ListModel {
                    id: tableModel
                }
                spacing: 10
                
                delegate: Rectangle {
                    width: listView.width
                    height: editorType === "exe" ? 80 : 40
                    color: index % 2 === 0 ? "white" : "#f9f9f9"
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        spacing: 50
                        
                        Label {
                            text: model.game || ""
                            Layout.preferredWidth: 150
                        }
                        
                        // Different fields based on editor type
                        Loader {
                            Layout.fillWidth: true
                            sourceComponent: editorType === "data" ? dataFieldsComponent : exeFieldsComponent
                            
                            property int itemIndex: index
                        }
                    }
                }
            }
        }
    }
    
    // Data fields component
    Component {
        id: dataFieldsComponent
        
        RowLayout {
            spacing: 50
            
            TextField {
                text: model.appid || ""
                Layout.preferredWidth: 200
                Layout.preferredHeight: 40
                onTextChanged: model.appid = text
            }
            
            TextField {
                text: model.emulator || ""
                Layout.preferredWidth: 100
                Layout.preferredHeight: 40
                onTextChanged: model.emulator = text
            }
            
            TextField {
                text: model.build || ""
                Layout.preferredWidth: 100
                Layout.preferredHeight: 40
                onTextChanged: model.build = text
            }
        }
    }
    
    // Exe fields component
    Component {
        id: exeFieldsComponent
        
        RowLayout {
            spacing: 50
            
            Button {
                text: model.exesrc || "Select EXE"
                Layout.preferredWidth: 300
                Layout.preferredHeight: 40
                
                onClicked: {
                    fileDialog.currentGame = model.game
                    fileDialog.currentIndex = itemIndex
                    fileDialog.open()
                }
            }
            
            ColumnLayout {
                Layout.preferredHeight: 70
                
                Image {
                    Layout.preferredWidth: 40
                    Layout.preferredHeight: 40
                    source: model.has_image ? "file:///data/local/check_DATA.png" : "file:///data/local/x_DATA.png"
                }
                
                Button {
                    text: "Change/Add"
                    Layout.preferredWidth: 100
                    onClicked: {
                        imageBrowserWindow.currentGame = model.game
                        imageBrowserWindow.show()
                    }
                }
            }
        }
    }
    
    // File dialog for selecting exe
    FileDialog {
        id: fileDialog
        title: "Select EXE"
        nameFilters: ["Executable Files (*.exe)", "All Files (*)"]
        
        property string currentGame: ""
        property int currentIndex: -1
        
        onAccepted: {
            if (currentIndex >= 0) {
                let path = selectedFile.toString().replace("file:///", "")
                tableModel.setProperty(currentIndex, "exesrc", path)
            }
        }
    }
    
    // Confirmation dialog
    Dialog {
        id: confirmDialog
        title: "Confirm Action"
        modal: true
        anchors.centerIn: parent
        
        property string message: ""
        property var acceptAction: null
        
        standardButtons: Dialog.Yes | Dialog.No
        
        Label {
            text: confirmDialog.message
        }
        
        onAccepted: {
            if (acceptAction) {
                acceptAction()
            }
        }
    }
}
