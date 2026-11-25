import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    objectName: "apps"
    property string title: Translator.tr("nav.apps")

    Component.onCompleted: DeviceBridge.refreshApps()

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
                        Label {
                            text: modelData.package || modelData["package"] || ""
                            color: "#e2e8f0"
                            font.pixelSize: 13
                            elide: Text.ElideMiddle
                            Layout.fillWidth: true
                        }
                        Label {
                            visible: (modelData.system || modelData["system"]) === "true"
                            text: "system"
                            color: "#64748b"
                            font.pixelSize: 11
                        }
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
