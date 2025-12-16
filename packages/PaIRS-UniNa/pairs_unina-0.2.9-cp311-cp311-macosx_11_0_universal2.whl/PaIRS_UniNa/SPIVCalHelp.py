from PySide6 import QtWidgets, QtGui, QtCore
import sys
from .PaIRS_pypacks import icons_path, fontPixelSize

def showSPIVCalHelp(parent=None,disable_callback=None):
    """
    Shows an informational dialog explaining the correct calibration setup
    for stereoscopic PIV in PaIRS, ensuring compatibility with disparity
    correction and full stereoscopic reconstruction.
    """
    dlg = QtWidgets.QDialog(parent)
    dlg.setWindowTitle("Guidelines for stereoscopic PIV calibration")
    #dlg.resize(900, 750)
    dlg.setMinimumWidth(900)
    dlg.setMinimumHeight(750)

    main_layout = QtWidgets.QVBoxLayout(dlg)

    # --- Explanatory text (English, corrected axes) ---
    text = (
        "For stereoscopic PIV, PaIRS assumes that:<br><br>"

        "&nbsp;&nbsp;• the <b>calibration plate defines "
        "the x–y plane</b> of the calibration coordinate system;<br>"
        
        "&nbsp;&nbsp;• the <b>x-axis</b> is <b>aligned with the stereoscopic baseline</b>, i.e. "
        "the direction along which the projections of the two camera viewing rays diverge "
        "on the calibration plate (the dominant disparity direction);<br>"

        "&nbsp;&nbsp;• the <b>y-axis</b> is then defined as the axis <b>perpendicular to the plane containing "
        "the two cameras</b> (i.e. perpendicular to the triangulation plane formed by the two "
        "optical axes);<br>"

        "&nbsp;&nbsp;• the <b>z-axis is normal to the plate</b> (typically pointing towards the cameras).<br><br>"

        "To ensure full compatibility with the operations performed in the disparity correction step and the stereoscopic reconstruction,"
        " the calibration procedure must always adhere to the above coordinate convention.<br>"
        " The example below shows a <b>correct</b> configuration (left) and an <b>incorrect</b> one (right).<br>"
    )

    text_label = QtWidgets.QLabel()
    text_label.setWordWrap(True)
    text_label.setTextFormat(QtCore.Qt.RichText)
    text_label.setText(f"<div>{text}</div>")
    main_layout.addWidget(text_label)
    font=dlg.font()
    font.setPixelSize(fontPixelSize+4)
    text_label.setFont(font)

    # --- Side-by-side images ---
    img_layout = QtWidgets.QHBoxLayout()
    img_layout.setSpacing(10)
    main_layout.addLayout(img_layout)

    # Paths to images (adjust to match PaIRS resources folder)
    img_ok_path = icons_path+"spiv_setup_ok.png"
    img_no_path = icons_path+"spiv_setup_no.png"

    # --- Correct configuration image ---
    ok_widget = QtWidgets.QVBoxLayout()
    ok_caption = QtWidgets.QLabel()
    caption_text = "<b>Correct configuration (x–z stereo plane)</b>"
    ok_caption.setText(f"<div>{caption_text}</div>")
    ok_caption.setFont(font)
    ok_caption.setTextFormat(QtCore.Qt.RichText)
    ok_caption.setAlignment(QtCore.Qt.AlignCenter)

    ok_label_img = QtWidgets.QLabel()
    ok_label_img.setAlignment(QtCore.Qt.AlignCenter)
    ok_label_img.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    ok_label_img.setScaledContents(True)
    
    ok_pix = QtGui.QPixmap(img_ok_path)
    if not ok_pix.isNull():
        ok_pix = ok_pix.scaledToWidth(400, QtCore.Qt.SmoothTransformation)
        ok_label_img.setPixmap(ok_pix)
    ok_label_img.setFixedSize(ok_pix.width(),ok_pix.height())

    ok_widget.addWidget(ok_caption)
    ok_widget.addWidget(ok_label_img)
    img_layout.addLayout(ok_widget)

    # --- Incorrect configuration image ---
    no_widget = QtWidgets.QVBoxLayout()
    no_caption = QtWidgets.QLabel()
    caption_text = "<b>Incorrect configuration</b>"
    no_caption.setText(f"<div'>{caption_text}</div>")
    no_caption.setFont(font)
    no_caption.setTextFormat(QtCore.Qt.RichText)
    no_caption.setAlignment(QtCore.Qt.AlignCenter)

    no_label_img = QtWidgets.QLabel()
    no_label_img.setAlignment(QtCore.Qt.AlignCenter)
    no_label_img.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    no_label_img.setScaledContents(True)
    
    no_pix = QtGui.QPixmap(img_no_path)
    if not no_pix.isNull():
        no_pix = no_pix.scaledToWidth(400, QtCore.Qt.SmoothTransformation)
        no_label_img.setPixmap(no_pix)
    no_label_img.setFixedSize(no_pix.width(),no_pix.height())

    no_widget.addWidget(no_caption)
    no_widget.addWidget(no_label_img)
    img_layout.addLayout(no_widget)

    # Prevent bottom clipping: allow images row to shrink/expand as needed
    main_layout.setStretch(0, 1)
    main_layout.setStretch(1, 0)

    # Create a horizontal layout for buttons
    button_layout = QtWidgets.QHBoxLayout()

    # Spacer pushes OK to the right
    button_layout.addStretch(1)

    # Left button
    if disable_callback is not None:
        button_disable = QtWidgets.QPushButton("Don't show this message again")
        def on_disable():
            disable_callback()
            dlg.accept()
        button_disable.clicked.connect(on_disable)
        button_layout.addWidget(button_disable)

    # Right button (OK)
    button_ok = QtWidgets.QPushButton("OK")
    def on_ok():
        dlg.accept()
    button_ok.clicked.connect(on_ok)
    button_layout.addWidget(button_ok)

    # Add the layout to the dialog
    main_layout.addSpacing(12)
    main_layout.addLayout(button_layout)

    button_ok.setDefault(True)
    button_ok.setFocus()

    main_layout.setContentsMargins(20, 25, 20, 25)  # slightly larger bottom margin to avoid macOS clipping

    dlg.exec()

if __name__ == "__main__":
    # QApplication MUST be created before any QWidget
    app = QtWidgets.QApplication(sys.argv)

    # Parent window (optional)
    main_window = QtWidgets.QMainWindow()
    main_window.show()

    # Show the SPIV calibration dialog
    showSPIVCalHelp(parent=main_window)

    sys.exit(app.exec())