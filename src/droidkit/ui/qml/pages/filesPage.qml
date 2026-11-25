import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform as Platform

Item {
    id: page
    objectName: "files"
    property string title: Translator.tr("nav.files")

    Component.onCompleted: DeviceBridge.refreshFiles("/sdcard")

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            Button {
                text: "⬆"
                enabled: DeviceBridge.cwd !== "/" && DeviceBridge.cwd !== "/sdcard"
                onClicked: DeviceBridge.goUp()
            }
            Label {
                text: DeviceBridge.cwd
                color: "#38bdf8"
                font.family: "Consolas, monospace"
                elide: Text.ElideMiddle
                Layout.fillWidth: true
            }
            Button {
                text: Translator.tr("action.refresh")
                onClicked: DeviceBridge.refreshFiles(DeviceBridge.cwd)
            }
        }

        ListView {
            id: fileList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: DeviceBridge.files

            delegate: Rectangle {
                width: fileList.width
                height: 42
                color: hover.hovered ? "#1e293b" : (index % 2 === 0 ? "#111a2e" : "#0f172a")
                radius: 6
                HoverHandler { id: hover }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 8
                    spacing: 10

                    Label {
                        text: modelData.isDir ? "📁" : "📄"
                        font.pixelSize: 14
                    }
                    Label {
                        text: modelData.name
                        color: "#e2e8f0"
                        elide: Text.ElideMiddle
                        Layout.fillWidth: true
                    }
                    Label {
                        text: modelData.size || ""
                        color: "#64748b"
                        font.pixelSize: 11
                    }
                    Button {
                        visible: !modelData.isDir
                        text: Translator.tr("action.pull")
                        flat: true
                        onClicked: DeviceBridge.pullFile(
                            modelData.path,
                            Platform.StandardPaths.writableLocation(Platform.StandardPaths.DownloadLocation)
                        )
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    enabled: modelData.isDir
                    cursorShape: modelData.isDir ? Qt.PointingHandCursor : Qt.ArrowCursor
                    onClicked: if (modelData.isDir) DeviceBridge.refreshFiles(modelData.path)
                }
            }

            ScrollBar.vertical: ScrollBar {}
        }
    }
}
