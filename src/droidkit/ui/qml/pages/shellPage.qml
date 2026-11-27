import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    objectName: "shell"
    property string title: Translator.tr("nav.shell")

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        RowLayout {
            Layout.fillWidth: true
            TextField {
                id: cmd
                Layout.fillWidth: true
                placeholderText: "getprop ro.build.version.release"
                onAccepted: runCmd()
            }
            Button {
                text: "Run"
                enabled: !DeviceBridge.busy && DeviceBridge.serial.length > 0
                onClicked: runCmd()
            }
            Button {
                text: DeviceBridge.logcatRunning
                      ? Translator.tr("action.logcat_stop")
                      : Translator.tr("action.logcat_start")
                highlighted: DeviceBridge.logcatRunning
                enabled: DeviceBridge.serial.length > 0
                onClicked: DeviceBridge.logcatRunning
                            ? DeviceBridge.stopLogcat()
                            : DeviceBridge.startLogcat()
            }
            Button {
                text: Translator.tr("action.clear")
                onClicked: { output.text = ""; cmd.text = "" }
            }
            Button {
                text: Translator.tr("action.screenshot")
                enabled: DeviceBridge.serial.length > 0
                onClicked: DeviceBridge.screenshot()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 8
            color: "#0a0f1a"
            border.color: DeviceBridge.logcatRunning ? "#38bdf8" : "#243049"

            Flickable {
                id: flick
                anchors.fill: parent
                anchors.margins: 8
                contentHeight: output.implicitHeight
                clip: true

                TextEdit {
                    id: output
                    width: flick.width
                    readOnly: true
                    text: ""
                    color: "#a5f3fc"
                    font.family: "Consolas, monospace"
                    font.pixelSize: 12
                    wrapMode: TextEdit.Wrap
                    selectByMouse: true
                }

                ScrollBar.vertical: ScrollBar {}
            }

            // Auto-scroll while logcat streams
            Connections {
                target: DeviceBridge
                function onLogLine(line) {
                    appendLine(line)
                }
            }
        }
    }

    function appendLine(line) {
        // Keep the buffer bounded — a busy logcat fills memory fast.
        var maxLines = 5000
        output.text += line + "\n"
        var lines = output.text.split("\n")
        if (lines.length > maxLines) {
            output.text = lines.slice(lines.length - maxLines).join("\n")
        }
        flick.contentY = Math.max(0, flick.contentHeight - flick.height)
    }

    function runCmd() {
        var c = cmd.text.trim()
        if (!c) return
        var res = DeviceBridge.shellSync(c)
        appendLine("$ " + c)
        if (res) appendLine(res)
    }
}
