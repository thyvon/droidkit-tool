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
                enabled: !DeviceBridge.busy
                onClicked: runCmd()
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
            border.color: "#243049"

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
        }
    }

    function runCmd() {
        var c = cmd.text.trim()
        if (!c) return
        var res = DeviceBridge.shellSync(c)
        output.text = "$ " + c + "\n" + res + "\n\n" + output.text
    }
}
