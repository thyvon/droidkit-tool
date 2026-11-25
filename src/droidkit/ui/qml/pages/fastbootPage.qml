import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    objectName: "fastboot"
    property string title: Translator.tr("nav.fastboot")

    Component.onCompleted: DeviceBridge.refreshFastboot()

    ColumnLayout {
        anchors.fill: parent
        spacing: 14

        Rectangle {
            Layout.fillWidth: true
            radius: 10
            color: "#111a2e"
            border.color: "#243049"
            implicitHeight: col.implicitHeight + 28

            ColumnLayout {
                id: col
                anchors.fill: parent
                anchors.margins: 14
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: "Fastboot devices"
                        color: "#e2e8f0"
                        font.bold: true
                        Layout.fillWidth: true
                    }
                    Button {
                        text: Translator.tr("action.refresh")
                        onClicked: DeviceBridge.refreshFastboot()
                    }
                }

                Label {
                    text: DeviceBridge.fastbootDevices.length > 0
                          ? DeviceBridge.fastbootDevices.join(", ")
                          : Translator.tr("status.no_device")
                    color: "#94a3b8"
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            radius: 10
            color: "#111a2e"
            border.color: "#243049"
            implicitHeight: 140

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 10

                Label {
                    text: "Reboot"
                    color: "#e2e8f0"
                    font.bold: true
                }

                RowLayout {
                    spacing: 10
                    Button {
                        text: "→ System"
                        enabled: DeviceBridge.fastbootDevices.length > 0
                        onClicked: DeviceBridge.fbRebootSystem()
                    }
                    Button {
                        text: "→ Bootloader"
                        enabled: DeviceBridge.fastbootDevices.length > 0
                        onClicked: DeviceBridge.fbRebootBootloader()
                    }
                }

                Label {
                    text: "Flash helpers ship in later milestones — keep fastboot ops explicit and logged."
                    color: "#64748b"
                    font.pixelSize: 12
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
