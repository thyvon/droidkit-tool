import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform as Platform

Item {
    id: page
    objectName: "apps"
    property string title: Translator.tr("nav.apps")

    Component.onCompleted: DeviceBridge.refreshApps()

    FileDialog {
        id: apkDialog
        title: Translator.tr("action.install")
        nameFilters: ["APK files (*.apk)", "All files (*)"]
        fileMode: Platform.FileDialog.OpenFile
        onAccepted: DeviceBridge.installApk(selectedFile.toString())
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            TextField {
                id: filter
                Layout.fillWidth: true
                placeholderText: "Filter packages…"
                onTextChanged: appList.model = filtered()
            }
            Button {
                text: Translator.tr("action.install")
                enabled: DeviceBridge.serial.length > 0 && !DeviceBridge.busy
                onClicked: apkDialog.open()
            }
            Button {
                text: Translator.tr("action.refresh")
                onClicked: DeviceBridge.refreshApps()
            }
        }

        ListView {
            id: appList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: filtered()

            function filtered() {
                var q = filter.text.toLowerCase()
                var out = []
                var src = DeviceBridge.apps
                for (var i = 0; i < src.length; i++) {
                    var p = src[i].package || ""
                    if (q.length === 0 || p.toLowerCase().indexOf(q) >= 0)
                        out.push(src[i])
                }
                return out
            }

            Connections {
                target: DeviceBridge
                function onAppsChanged() { appList.model = appList.filtered() }
            }

            delegate: Rectangle {
                width: appList.width
                height: 48
                color: index % 2 === 0 ? "#111a2e" : "#0f172a"
                radius: 6

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 12
                    anchors.rightMargin: 8
                    spacing: 10

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        RowLayout {
                            spacing: 6
                            Label {
                                text: modelData.package || modelData["package"] || ""
                                color: "#e2e8f0"
                                font.pixelSize: 13
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }
                            Label {
                                visible: (modelData.disabled || modelData["disabled"]) === "true"
                                text: "disabled"
                                color: "#fbbf24"
                                font.pixelSize: 10
                            }
                        }
                        Label {
                            visible: (modelData.system || modelData["system"]) === "true"
                            text: "system"
                            color: "#64748b"
                            font.pixelSize: 11
                        }
                    }

                    Button {
                        text: Translator.tr("action.backup")
                        flat: true
                        enabled: !DeviceBridge.busy
                        onClicked: DeviceBridge.backupApp(modelData.package || modelData["package"])
                    }
                    Button {
                        visible: (modelData.system || modelData["system"]) === "true"
                                && (modelData.disabled || modelData["disabled"]) !== "true"
                        text: Translator.tr("action.disable")
                        flat: true
                        enabled: !DeviceBridge.busy
                        onClicked: DeviceBridge.disableApp(modelData.package || modelData["package"])
                    }
                    Button {
                        visible: (modelData.disabled || modelData["disabled"]) === "true"
                        text: Translator.tr("action.enable")
                        flat: true
                        enabled: !DeviceBridge.busy
                        onClicked: DeviceBridge.enableApp(modelData.package || modelData["package"])
                    }
                    Button {
                        text: Translator.tr("action.uninstall")
                        flat: true
                        enabled: !DeviceBridge.busy
                        onClicked: DeviceBridge.uninstallApp(modelData.package || modelData["package"])
                    }
                }
            }

            ScrollBar.vertical: ScrollBar {}
        }
    }
}
