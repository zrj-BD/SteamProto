import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine

Window {
    id: imageBrowserWindow
    width: 1500
    height: 900
    title: "Copy Image Address"
    modality: Qt.ApplicationModal
    
    property string currentGame: ""
    
    onVisibleChanged: {
        if (visible && currentGame) {
            let url = imageDownloader.getSearchUrl(currentGame)
            webView.url = url
        }
    }
    
    ColumnLayout {
        anchors.fill: parent
        spacing: 0
        
        // Top bar with instructions
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 50
            color: "#f0f0f0"
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 5
                
                Label {
                    text: "Right-click on an image and copy its address, then paste it below"
                    font.bold: true
                }
            }
        }
        
        // Web view
        WebEngineView {
            id: webView
            Layout.fillWidth: true
            Layout.fillHeight: true
            
            profile: WebEngineProfile {
                httpUserAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                httpCacheType: WebEngineProfile.MemoryHttpCache
                persistentCookiesPolicy: WebEngineProfile.NoPersistentCookies
            }
        }
        
        // Bottom bar with URL input
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 60
            color: "#f0f0f0"
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 10
                
                TextField {
                    id: urlField
                    Layout.fillWidth: true
                    placeholderText: "Paste image URL here..."
                }
                
                Button {
                    text: "Download"
                    Layout.preferredWidth: 100
                    onClicked: {
                        let url = urlField.text.trim()
                        if (url) {
                            imageDownloader.downloadImage(url, currentGame)
                        }
                    }
                }
                
                Button {
                    text: "Cancel"
                    Layout.preferredWidth: 100
                    onClicked: imageBrowserWindow.close()
                }
            }
        }
    }
    
    Connections {
        target: imageDownloader
        
        function onDownloadFinished() {
            urlField.text = ""
            imageBrowserWindow.close()
        }
        
        function onDownloadError(message) {
            errorDialog.text = message
            errorDialog.open()
        }
    }
    
    Dialog {
        id: errorDialog
        title: "Error"
        modal: true
        anchors.centerIn: parent
        standardButtons: Dialog.Ok
        
        property alias text: errorLabel.text
        
        Label {
            id: errorLabel
        }
    }
}
