import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

Item {
    id: page
    objectName: "license"
    property string title: Translator.tr("nav.license")

    Component.onCompleted: LicenseApi.refresh()

    ColumnLayout {
        anchors.fill: parent
        spacing: 14
        width: parent.width > 520 ? 520 : parent.width
        anchors.horizontalCenter: parent.horizontalCenter

        Rectangle {
            Layout.fillWidth: true
            radius: 12
            color: "#111a2e"
            border.color: LicenseApi.isActive ? "#34d399" : "#243049"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 12

                Label {
                    text: Translator.tr("nav.license")
                    color: "#e2e8f0"
                    font.pixelSize: 18
                    font.bold: true
                }

                RowLayout {
                    Layout.fillWidth: true
                    Label { text: Translator.tr("label.plan"); color: "#94a3b8"; Layout.preferredWidth: 120 }
                    Label { text: LicenseApi.plan; color: "#e2e8f0"; font.weight: Font.DemiBold }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Label { text: Translator.tr("label.expires"); color: "#94a3b8"; Layout.preferredWidth: 120 }
                    Label { text: LicenseApi.expiresLabel; color: "#e2e8f0" }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Label { text: Translator.tr("label.hwid"); color: "#94a3b8"; Layout.preferredWidth: 120 }
                    Label {
                        text: LicenseApi.hwid
                        color: "#38bdf8"
                        font.family: "Consolas, monospace"
                        font.pixelSize: 12
                        elide: Text.ElideMiddle
                        Layout.fillWidth: true
                    }
                }

                Label {
                    text: LicenseApi.statusMessage
                    color: LicenseApi.isActive ? "#34d399" : "#f87171"
                    font.pixelSize: 13
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                RowLayout {
                    spacing: 10
                    Button {
                        text: Translator.tr("action.activate")
                        highlighted: true
                        onClicked: licenseDialog.open()
                    }
                    Button {
                        text: Translator.tr("action.clear")
                        enabled: !LicenseApi.isActive
                        onClicked: LicenseApi.clear()
                    }
                }
            }
        }

        FileDialog {
            id: licenseDialog
            title: "Select license.bin"
            nameFilters: ["License files (*.bin)", "All files (*)"]
            onAccepted: {
                var url = selectedFile.toString()
                if (url.startsWith("file:///"))
                    LicenseApi.activateFromFile(decodeURIComponent(url.slice(8)))
                else
                    LicenseApi.activateFromFile(url)
            }
        }

        Item { Layout.fillHeight: true }
    }
}
