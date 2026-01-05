import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    
    property var games: []
    
    function refresh() {
        let gamesJson = dataManager.getAllGamesJson()
        games = JSON.parse(gamesJson)
        gridRepeater.model = games
    }
    
    Component.onCompleted: refresh()
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Top button bar
        RowLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: 40
            spacing: 0
            
            Button {
                text: "Refresh"
                Layout.preferredWidth: 100
                onClicked: root.refresh()
            }
            
            Item {
                Layout.fillWidth: true
            }
            
            Button {
                text: "Settings"
                Layout.preferredWidth: 100
                onClicked: settingsWindow.show()
            }
        }
        
        // Scrollable grid of games
        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            GridLayout {
                id: grid
                columns: 5
                rowSpacing: 40
                columnSpacing: 40
                anchors.margins: 10
                
                Repeater {
                    id: gridRepeater
                    model: []
                    
                    Item {
                        Layout.preferredWidth: 250
                        Layout.preferredHeight: 375
                        
                        Rectangle {
                            anchors.fill: parent
                            color: "transparent"
                            
                            Image {
                                id: gameImage
                                anchors.fill: parent
                                source: dataManager.getGameImage(modelData)
                                fillMode: Image.PreserveAspectCrop
                                
                                Rectangle {
                                    color: "transparent"
                                    anchors.fill: parent
                                    
                                    ColumnLayout {
                                        anchors.fill: parent
                                        spacing: 0
                                        
                                        // Game title at top
                                        Rectangle {
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 60
                                            color: "#64000000"
                                            
                                            Label {
                                                anchors.fill: parent
                                                anchors.margins: 5
                                                text: modelData
                                                font.bold: true
                                                font.pixelSize: 20
                                                color: "white"
                                                wrapMode: Text.WordWrap
                                                horizontalAlignment: Text.AlignHCenter
                                                verticalAlignment: Text.AlignVCenter
                                            }
                                        }
                                        
                                        Item {
                                            Layout.fillWidth: true
                                            Layout.fillHeight: true
                                        }
                                        
                                        // Play button at bottom
                                        Button {
                                            Layout.preferredWidth: 100
                                            Layout.preferredHeight: 50
                                            Layout.alignment: Qt.AlignHCenter | Qt.AlignBottom
                                            Layout.bottomMargin: 10
                                            text: "Play"
                                            
                                            background: Rectangle {
                                                color: parent.pressed ? "#C8000000" : (parent.hovered ? "#96000000" : "#64000000")
                                                radius: 4
                                            }
                                            
                                            contentItem: Text {
                                                text: parent.text
                                                font: parent.font
                                                color: "white"
                                                horizontalAlignment: Text.AlignHCenter
                                                verticalAlignment: Text.AlignVCenter
                                            }
                                            
                                            onClicked: {
                                                let exePath = dataManager.getGameExePath(modelData)
                                                if (exePath) {
                                                    gameLauncher.launchGame(exePath)
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
