import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    property string labelText: ""
    property bool active: false
    signal clicked

    height: 40
    radius: 8
    color: active ? "#1d4ed8" : (hover.hovered ? "#1e293b" : "transparent")
    border.color: active ? "#3b82f6" : "transparent"

    HoverHandler { id: hover }

    Behavior on color { ColorAnimation { duration: 120 } }

    // Subtle press feedback
    scale: pressed.pressed ? 0.97 : 1.0
    Behavior on scale { NumberAnimation { duration: 80; easing.type: Easing.OutCubic } }
    TapHandler { id: pressed }

    Label {
        anchors.centerIn: parent
        text: root.labelText
        color: root.active ? "#ffffff" : "#94a3b8"
        font.pixelSize: 14
        font.weight: root.active ? Font.DemiBold : Font.Normal
    }

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }
}
