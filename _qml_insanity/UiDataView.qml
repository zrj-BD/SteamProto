import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    
    property var uiDataList: []
    
    function refresh() {
        let json = dataManager.getUiDataListJson()
        uiDataList = JSON.parse(json)
        tableModel.clear()
        for (let i = 0; i < uiDataList.length; i++) {
            tableModel.append(uiDataList[i])
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
                    editorWindow.editorType = "exe"
                    editorWindow.show()
                }
            }
            
            Button {
                text: "Refresh"
                Layout.preferredWidth: 100
                onClicked: root.refresh()
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
                    text: "Exe Source"
                    font.bold: true
                    Layout.preferredWidth: 300
                }
                Label {
                    text: "PNG"
                    font.bold: true
                    Layout.preferredWidth: 60
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
                            text: model.exesrc || ""
                            Layout.preferredWidth: 300
                            elide: Text.ElideMiddle
                        }
                        
                        Image {
                            Layout.preferredWidth: 40
                            Layout.preferredHeight: 40
                            source: model.has_image ? "file:///data/local/check_DATA.png" : "file:///data/local/x_DATA.png"
                        }
                    }
                }
            }
        }
    }
}
