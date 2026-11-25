import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: card
    property string label: ""
    property string value: "—"
    property string hint: ""
    property color accentColor: "#38bdf8"

    radius: 10
    color: "#111a2e"
    border.color: "#243049"
    implicitHeight: col.implicitHeight + 28
    Layout.fillWidth: true

    ColumnLayout {
        id: col
        anchors.fill: parent
        anchors.margins: 14
        spacing: 4

        Label {
            text: card.label
            color: "#94a3b8"
            font.pixelSize: 12
            font.weight: Font.Medium
        }
        Label {
            text: card.value
            color: "#e2e8f0"
            font.pixelSize: 22
            font.weight: Font.Bold
            elide: Text.ElideRight
            Layout.fillWidth: true
        }
        Label {
            visible: card.hint.length > 0
            text: card.hint
            color: card.accentColor
            font.pixelSize: 11
        }
    }
}
