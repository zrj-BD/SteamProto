import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    
    property var metadataList: []
    
    function refresh() {
        let json = dataManager.getMetadataListJson()
        metadataList = JSON.parse(json)
        tableModel.clear()
        for (let i = 0; i < metadataList.length; i++) {
            tableModel.append(metadataList[i])
        }
    }
    
    Component.onCompleted: refresh()
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Button bar
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            spacing: 0
            
            Button {
                text: "Edit"
                Layout.preferredWidth: 100
                onClicked: {
                    editorWindow.editorType = "data"
                    editorWindow.show()
                }
            }
            
            Button {
                text: "Refresh"
                Layout.preferredWidth: 100
                onClicked: root.refresh()
            }
            
            Button {
                text: "Update"
                Layout.preferredWidth: 100
                onClicked: {
                    scanManager.performUpdate()
                }
            }
            
            Button {
                text: "Scan"
                Layout.preferredWidth: 100
                onClicked: {
                    scanManager.performScan()
                }
            }
            
            Button {
                text: "Rescan"
                Layout.preferredWidth: 100
                onClicked: {
                    confirmDialog.message = "This will reset also the fixed_metadata. Only do this if there had been an error previously. Continue?"
                    confirmDialog.acceptAction = function() {
                        scanManager.performRescan()
                    }
                    confirmDialog.open()
                }
            }
            
            Item {
                Layout.fillWidth: true
            }
        }
        
        // Table header
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
                    text: "AppID"
                    font.bold: true
                    Layout.preferredWidth: 80
                }
                Label {
                    text: "Emulator"
                    font.bold: true
                    Layout.preferredWidth: 100
                }
                Label {
                    text: "Last Build"
                    font.bold: true
                    Layout.preferredWidth: 100
                }
                Label {
                    text: "Last Date"
                    font.bold: true
                    Layout.preferredWidth: 180
                }
                Label {
                    text: "Newest Build"
                    font.bold: true
                    Layout.preferredWidth: 100
                }
                Label {
                    text: "Newest Date"
                    font.bold: true
                    Layout.preferredWidth: 180
                }
            }
        }
        
        // Scrollable table content
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
                    height: 40
                    color: index % 2 === 0 ? "white" : "#f9f9f9"
                    
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 5
                        spacing: 50
                        
                        Label {
                            text: model.game || ""
                            Layout.preferredWidth: 150
                            elide: Text.ElideRight
                        }
                        Label {
                            text: model.appid || ""
                            Layout.preferredWidth: 80
                        }
                        Label {
                            text: model.emulator || ""
                            Layout.preferredWidth: 100
                        }
                        Label {
                            text: model.build || ""
                            Layout.preferredWidth: 100
                        }
                        Label {
                            text: model.date ? new Date(model.date * 1000).toLocaleString() : ""
                            Layout.preferredWidth: 180
                        }
                        Label {
                            text: model.recent_build || ""
                            Layout.preferredWidth: 100
                        }
                        Label {
                            text: model.recent_date ? new Date(model.recent_date * 1000).toLocaleString() : ""
                            Layout.preferredWidth: 180
                        }
                        
                        // Status indicator
                        Rectangle {
                            Layout.preferredWidth: 40
                            Layout.preferredHeight: 40
                            color: "transparent"
                            
                            Image {
                                anchors.centerIn: parent
                                width: 40
                                height: 40
                                source: (model.build && model.recent_build && model.build === model.recent_build) 
                                    ? "file:///data/local/check_DATA.png" 
                                    : "file:///data/local/x_DATA.png"
                            }
                        }
                    }
                }
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
    
    Connections {
        target: scanManager
        function onScanFinished() {
            root.refresh()
        }
    }
}
