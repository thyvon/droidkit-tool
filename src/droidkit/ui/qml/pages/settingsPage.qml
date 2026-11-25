import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: page
    objectName: "settings"
    property string title: Translator.tr("nav.settings")

    Component.onCompleted: UpdateApi.check()

    ColumnLayout {
        anchors.fill: parent
        spacing: 14
        width: Math.min(parent.width, 560)
        anchors.horizontalCenter: parent.horizontalCenter

        // Language
        Rectangle {
            Layout.fillWidth: true
            radius: 10
            color: "#111a2e"
            border.color: "#243049"
            implicitHeight: 90

            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                Label {
                    text: Translator.tr("label.language")
                    color: "#e2e8f0"
                    Layout.fillWidth: true
                }
                ComboBox {
                    model: Translator.supported
                    currentIndex: Translator.language === "km" ? 1 : 0
                    onActivated: Translator.setLanguage(currentText)
                }
            }
        }

        // Updates
        Rectangle {
            Layout.fillWidth: true
            radius: 10
            color: "#111a2e"
            border.color: "#243049"
            implicitHeight: upCol.implicitHeight + 32

            ColumnLayout {
                id: upCol
                anchors.fill: parent
                anchors.margins: 16
                spacing: 10

                RowLayout {
                    Layout.fillWidth: true
                    Label {
                        text: "Updates"
                        color: "#e2e8f0"
                        font.bold: true
                        Layout.fillWidth: true
                    }
                    Button {
                        text: Translator.tr("action.check_update")
                        enabled: !UpdateApi.checking
                        onClicked: UpdateApi.check()
                    }
                }

                Label {
                    text: UpdateApi.updateAvailable
                          ? Translator.tr("update.available") + " → " + UpdateApi.latestVersion
                          : (UpdateApi.errorMessage || Translator.tr("update.current"))
                    color: UpdateApi.updateAvailable ? "#38bdf8" : "#94a3b8"
                    font.pixelSize: 13
                    Layout.fillWidth: true
                }

                Button {
                    visible: UpdateApi.updateAvailable
                    text: "Open release page"
                    onClicked: UpdateApi.openReleasePage()
                }
            }
        }

        // Payments (offline KHQR demo)
        Rectangle {
            Layout.fillWidth: true
            radius: 10
            color: "#111a2e"
            border.color: "#243049"
            implicitHeight: payCol.implicitHeight + 32

            ColumnLayout {
                id: payCol
                anchors.fill: parent
                anchors.margins: 16
                spacing: 10

                Label {
                    text: Translator.tr("payment.scan_to_pay")
                    color: "#e2e8f0"
                    font.bold: true
                }

                RowLayout {
                    spacing: 8
                    TextField {
                        id: amountField
                        placeholderText: "Amount (KHR)"
                        text: "10000"
                        validator: DoubleValidator { bottom: 100; notation: DoubleValidator.StandardNotation }
                        Layout.preferredWidth: 140
                    }
                    TextField {
                        id: accountField
                        placeholderText: "merchant@bank"
                        Layout.fillWidth: true
                    }
                    Button {
                        text: "Create KHQR"
                        highlighted: true
                        onClicked: PaymentsApi.createOfflineQr(
                            Number(amountField.text),
                            accountField.text,
                            "DroidKit"
                        )
                    }
                }

                Label {
                    visible: PaymentsApi.errorMessage.length > 0
                    text: PaymentsApi.errorMessage
                    color: "#f87171"
                    font.pixelSize: 12
                }

                Image {
                    visible: PaymentsApi.qrBase64.length > 0
                    source: PaymentsApi.qrBase64.length > 0
                            ? "data:image/png;base64," + PaymentsApi.qrBase64
                            : ""
                    sourceSize.width: 180
                    sourceSize.height: 180
                    Layout.alignment: Qt.AlignHCenter
                }

                Label {
                    visible: PaymentsApi.qrBase64.length > 0
                    text: Translator.tr("payment." + PaymentsApi.status.toLowerCase())
                    color: PaymentsApi.status === "PAID" ? "#34d399" : "#94a3b8"
                    Layout.alignment: Qt.AlignHCenter
                }

                Button {
                    visible: PaymentsApi.qrBase64.length > 0
                    text: "Check payment"
                    onClicked: PaymentsApi.pollPayment()
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}
