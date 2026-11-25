import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

ApplicationWindow {
    id: root
    width: 1180
    height: 760
    minimumWidth: 960
    minimumHeight: 640
    visible: true
    title: Translator.tr("app.title") + " " + AppVersion
    color: "#0b1220"

    // --- design tokens (single source of truth) ---
    readonly property color bg: "#0b1220"
    readonly property color panel: "#111a2e"
    readonly property color panelAlt: "#16203a"
    readonly property color border: "#243049"
    readonly property color accent: "#38bdf8"
    readonly property color accentDim: "#0ea5e9"
    readonly property color text: "#e2e8f0"
    readonly property color textDim: "#94a3b8"
    readonly property color danger: "#f87171"
    readonly property color ok: "#34d399"

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // Sidebar
        Rectangle {
            Layout.preferredWidth: 210
            Layout.fillHeight: true
            color: root.panel
            border.color: root.border
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 6

                Label {
                    text: "⬡  " + Translator.tr("app.title")
                    color: root.accent
                    font.pixelSize: 20
                    font.bold: true
                    Layout.bottomMargin: 16
                }

                Repeater {
                    model: ListModel {
                        ListElement { key: "dashboard"; labelKey: "nav.dashboard" }
                        ListElement { key: "apps"; labelKey: "nav.apps" }
                        ListElement { key: "shell"; labelKey: "nav.shell" }
                        ListElement { key: "files"; labelKey: "nav.files" }
                        ListElement { key: "fastboot"; labelKey: "nav.fastboot" }
                        ListElement { key: "license"; labelKey: "nav.license" }
                        ListElement { key: "settings"; labelKey: "nav.settings" }
                    }
                    delegate: SideNavItem {
                        Layout.fillWidth: true
                        labelText: Translator.tr(labelKey)
                        active: stack.currentItem && stack.currentItem.objectName === key
                        onClicked: stack.navigate(key)
                    }
                }

                Item { Layout.fillHeight: true }

                Label {
                    text: "v" + AppVersion
                    color: root.textDim
                    font.pixelSize: 11
                }
            }
        }

        // Main
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: root.bg

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 12

                // Top bar
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Label {
                        text: stack.currentItem ? (stack.currentItem.title || "") : ""
                        color: root.text
                        font.pixelSize: 22
                        font.bold: true
                        Layout.fillWidth: true
                    }

                    ComboBox {
                        id: langBox
                        model: Translator.supported
                        currentIndex: Translator.language === "km" ? 1 : 0
                        onActivated: Translator.setLanguage(currentText)
                        Layout.preferredWidth: 90
                    }

                    Button {
                        text: Translator.tr("action.refresh")
                        onClicked: DeviceBridge.refreshDevices()
                    }
                }

                // Status strip
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 34
                    radius: 6
                    color: root.panelAlt
                    border.color: root.border

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 10

                        Rectangle {
                            width: 8; height: 8; radius: 4
                            color: DeviceBridge.busy ? root.accent
                                 : (DeviceBridge.serial ? root.ok : root.textDim)
                        }
                        Label {
                            text: DeviceBridge.busy
                                  ? Translator.tr("status.scanning")
                                  : (DeviceBridge.serial
                                      ? Translator.tr("status.connected") + " · " + DeviceBridge.serial
                                      : Translator.tr("status.no_device"))
                            color: root.textDim
                            font.pixelSize: 12
                        }
                        Item { Layout.fillWidth: true }
                        Label {
                            visible: DeviceBridge.errorMessage.length > 0
                            text: DeviceBridge.errorMessage
                            color: root.danger
                            font.pixelSize: 12
                        }
                    }
                }

                StackView {
                    id: stack
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    initialItem: "pages/dashboardPage.qml"
                    clip: true

                    // Snappy built-in replace transitions (Qt 6 uses replaceEnter/Exit;
                    // do not also animate manually — that doubled the motion).
                    replaceEnter: Transition {
                        ParallelAnimation {
                            XAnimator {
                                from: 48
                                to: 0
                                duration: 170
                                easing.type: Easing.OutCubic
                            }
                            OpacityAnimator {
                                from: 0
                                to: 1
                                duration: 170
                                easing.type: Easing.OutCubic
                            }
                        }
                    }
                    replaceExit: Transition {
                        ParallelAnimation {
                            XAnimator {
                                from: 0
                                to: -32
                                duration: 130
                                easing.type: Easing.InCubic
                            }
                            OpacityAnimator {
                                from: 1
                                to: 0
                                duration: 130
                                easing.type: Easing.InCubic
                            }
                        }
                    }

                    // Cache page components so nav doesn't re-parse QML every click.
                    property var _cache: ({})

                    function pageComp(key) {
                        var c = _cache[key]
                        if (!c) {
                            c = Qt.createComponent("pages/" + key + "Page.qml")
                            if (c.status === Component.Error)
                                console.error("Failed to load page:", key, c.errorString())
                            _cache[key] = c
                        }
                        return c
                    }

                    function navigate(key) {
                        if (currentItem && currentItem.objectName === key)
                            return
                        replace(pageComp(key))
                    }
                }
            }
        }
    }

    // Initial device scan lives in dashboardPage.onCompleted (initial item);
    // do not also call refreshDevices here — it ran twice on startup.
}
