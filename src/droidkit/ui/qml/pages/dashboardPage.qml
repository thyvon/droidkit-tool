import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"

Item {
    id: page
    objectName: "dashboard"
    property string title: Translator.tr("nav.dashboard")

    Component.onCompleted: {
        DeviceBridge.refreshDevices()
        DeviceBridge.refreshInfo()
    }

    GridLayout {
        anchors.fill: parent
        columns: 3
        columnSpacing: 12
        rowSpacing: 12

        InfoCard {
            label: Translator.tr("label.model")
            value: DeviceBridge.info.model || "—"
            hint: DeviceBridge.info.brand || ""
        }
        InfoCard {
            label: Translator.tr("label.android")
            value: DeviceBridge.info.android_version || "—"
            hint: DeviceBridge.info.abi ? "SDK " + DeviceBridge.info.sdk + " · " + DeviceBridge.info.abi : ""
        }
        InfoCard {
            label: Translator.tr("label.battery")
            value: DeviceBridge.info.battery_level ? DeviceBridge.info.battery_level + "%" : "—"
            hint: [DeviceBridge.info.battery_status,
                   DeviceBridge.info.battery_health,
                   DeviceBridge.info.battery_temp].filter(function (s) { return s }).join(" · ")
        }
        InfoCard {
            label: Translator.tr("label.storage")
            value: DeviceBridge.info.free_storage || "—"
            hint: DeviceBridge.info.total_storage ? "free / total" : ""
        }
        InfoCard {
            label: Translator.tr("label.screen")
            value: DeviceBridge.info.screen || "—"
        }
        InfoCard {
            label: Translator.tr("label.serial")
            value: DeviceBridge.info.serial || "—"
            hint: DeviceBridge.info.device || ""
        }

        // Device list + actions
        Rectangle {
            Layout.columnSpan: 3
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 10
            color: "#111a2e"
            border.color: "#243049"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 14
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: "Devices"
                        color: "#e2e8f0"
                        font.pixelSize: 15
                        font.bold: true
                        Layout.fillWidth: true
                    }
                    Button {
                        text: Translator.tr("action.screenshot")
                        enabled: DeviceBridge.serial.length > 0 && !DeviceBridge.busy
                        onClicked: DeviceBridge.screenshot()
                    }
                }

                // Reboot modes — the bread-and-butter of a repair bench
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8
                    visible: DeviceBridge.serial.length > 0
                    Label {
                        text: Translator.tr("action.reboot") + ":"
                        color: "#94a3b8"
                        font.pixelSize: 12
                    }
                    Button {
                        text: Translator.tr("action.reboot_system")
                        enabled: !DeviceBridge.busy
                        onClicked: DeviceBridge.reboot("")
                    }
                    Button {
                        text: Translator.tr("action.reboot_bootloader")
                        enabled: !DeviceBridge.busy
                        onClicked: DeviceBridge.reboot("bootloader")
                    }
                    Button {
                        text: Translator.tr("action.reboot_recovery")
                        enabled: !DeviceBridge.busy
                        onClicked: DeviceBridge.reboot("recovery")
                    }
                    Button {
                        text: Translator.tr("action.reboot_sideload")
                        enabled: !DeviceBridge.busy
                        onClicked: DeviceBridge.reboot("sideload")
                    }
                }

                ListView {
                    id: devList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: DeviceBridge.devices

                    delegate: Rectangle {
                        required property var modelData
                        required property int index
                        width: devList.width
                        height: 44
                        radius: 6
                        color: modelData.serial === DeviceBridge.serial
                               ? "#1d4ed8"
                               : (hover.hovered ? "#1e293b" : "#0f172a")
                        HoverHandler { id: hover }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 12
                            anchors.rightMargin: 12
                            Label {
                                text: modelData.serial
                                color: "#e2e8f0"
                                font.family: "Consolas, monospace"
                                Layout.fillWidth: true
                            }
                            Label {
                                text: modelData.state || ""
                                color: modelData.state === "device" ? "#34d399" : "#fbbf24"
                                font.pixelSize: 12
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            enabled: modelData.state === "device"
                            onClicked: DeviceBridge.selectDevice(modelData.serial)
                        }
                    }

                    Label {
                        anchors.centerIn: parent
                        visible: devList.count === 0
                        text: Translator.tr("status.no_device")
                        color: "#64748b"
                    }
                }

                Label {
                    text: Translator.tr("label.serial") + ": " + (DeviceBridge.serial || "—")
                    color: "#94a3b8"
                    font.pixelSize: 12
                }
            }
        }
    }
}
