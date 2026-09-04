from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Qt, Signal
from PySide6.QtGui import QCloseEvent, QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .device import device_summary
from .parsing import ParagraphItem, parse_document, read_text_file
from .service import GenerationService
from .styles import APP_STYLESHEET


class MainWindow(QMainWindow):
    generate_requested = Signal(dict)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Higgs Voice Studio")
        self.resize(1320, 840)
        self.setMinimumSize(1080, 700)
        self.setStyleSheet(APP_STYLESHEET)
        self.items: list[ParagraphItem] = []
        self.text_path = ""
        self.reference_path = ""
        self.output_dir = str(Path.home() / "HiggsVoiceStudio_Output")
        self._build_ui()
        self._setup_service()
        self._refresh_hardware()

    def _card(self, title: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("Card")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        label = QLabel(title)
        label.setObjectName("SectionTitle")
        layout.addWidget(label)
        return frame, layout

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QHBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        root_layout.addWidget(splitter)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setMinimumWidth(360)
        sidebar.setMaximumWidth(430)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(22, 22, 22, 22)
        side.setSpacing(14)

        title = QLabel("HIGGS VOICE STUDIO")
        title.setObjectName("Title")
        sub = QLabel("Desktop voice cloning • CPU / NVIDIA GPU • Batch paragraphs")
        sub.setObjectName("Subtitle")
        sub.setWordWrap(True)
        side.addWidget(title)
        side.addWidget(sub)

        hardware_card, hw = self._card("1. Thiết bị")
        self.device_combo = QComboBox()
        self.device_combo.addItems(["Auto", "NVIDIA CUDA", "CPU"])
        self.hardware_label = QLabel("Đang kiểm tra phần cứng…")
        self.hardware_label.setObjectName("Subtitle")
        self.hardware_label.setWordWrap(True)
        self.cpu_threads = QSpinBox()
        self.cpu_threads.setRange(1, 256)
        self.cpu_threads.setValue(max(1, 4))
        self.cpu_threads.setPrefix("CPU threads: ")
        hw.addWidget(self.device_combo)
        hw.addWidget(self.hardware_label)
        hw.addWidget(self.cpu_threads)
        side.addWidget(hardware_card)

        ref_card, ref = self._card("2. Giọng mẫu")
        ref_row = QHBoxLayout()
        self.reference_edit = QLineEdit()
        self.reference_edit.setPlaceholderText("voice.wav hoặc voice.mp3")
        ref_btn = QPushButton("Chọn file")
        ref_btn.clicked.connect(self.pick_reference)
        ref_row.addWidget(self.reference_edit, 1)
        ref_row.addWidget(ref_btn)
        ref.addLayout(ref_row)
        self.reference_text = QPlainTextEdit()
        self.reference_text.setMaximumHeight(84)
        self.reference_text.setPlaceholderText("Transcript của voice mẫu (không bắt buộc, nhưng tăng độ giống giọng)")
        ref.addWidget(self.reference_text)
        self.consent = QCheckBox("Tôi xác nhận có quyền/được phép sử dụng giọng mẫu này")
        self.consent.setChecked(False)
        ref.addWidget(self.consent)
        side.addWidget(ref_card)

        output_card, out = self._card("3. Thư mục xuất")
        out_row = QHBoxLayout()
        self.output_edit = QLineEdit(self.output_dir)
        out_btn = QPushButton("Chọn")
        out_btn.clicked.connect(self.pick_output)
        out_row.addWidget(self.output_edit, 1)
        out_row.addWidget(out_btn)
        out.addLayout(out_row)
        side.addWidget(output_card)

        settings_card, settings = self._card("4. Generation")
        grid = QGridLayout()
        self.temperature = QDoubleSpinBox()
        self.temperature.setRange(0.05, 1.5)
        self.temperature.setSingleStep(0.05)
        self.temperature.setValue(0.70)
        self.top_p = QDoubleSpinBox()
        self.top_p.setRange(0.1, 1.0)
        self.top_p.setSingleStep(0.01)
        self.top_p.setValue(0.95)
        self.top_k = QSpinBox()
        self.top_k.setRange(0, 1026)
        self.top_k.setValue(50)
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(128, 8192)
        self.max_tokens.setSingleStep(128)
        self.max_tokens.setValue(2048)
        self.seed = QSpinBox()
        self.seed.setRange(-1, 2_147_483_647)
        self.seed.setValue(-1)
        grid.addWidget(QLabel("Temperature"), 0, 0)
        grid.addWidget(self.temperature, 0, 1)
        grid.addWidget(QLabel("Top-p"), 1, 0)
        grid.addWidget(self.top_p, 1, 1)
        grid.addWidget(QLabel("Top-k"), 2, 0)
        grid.addWidget(self.top_k, 2, 1)
        grid.addWidget(QLabel("Max tokens"), 3, 0)
        grid.addWidget(self.max_tokens, 3, 1)
        grid.addWidget(QLabel("Seed (-1=random)"), 4, 0)
        grid.addWidget(self.seed, 4, 1)
        settings.addLayout(grid)
        side.addWidget(settings_card)
        side.addStretch(1)

        self.generate_btn = QPushButton("TẠO TOÀN BỘ AUDIO")
        self.generate_btn.setObjectName("Primary")
        self.generate_btn.setMinimumHeight(48)
        self.generate_btn.clicked.connect(self.start_generation)
        self.cancel_btn = QPushButton("Dừng sau đoạn hiện tại")
        self.cancel_btn.setObjectName("Danger")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_generation)
        side.addWidget(self.generate_btn)
        side.addWidget(self.cancel_btn)

        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(22, 22, 22, 22)
        main_layout.setSpacing(14)

        top = QHBoxLayout()
        heading_box = QVBoxLayout()
        heading = QLabel("Batch từ file văn bản")
        heading.setStyleSheet("font-size:22px;font-weight:800;")
        hint = QLabel("Mỗi đoạn cách nhau bằng một dòng trống → một file WAV. Số thứ tự đầu đoạn sẽ không được đọc.")
        hint.setObjectName("Subtitle")
        heading_box.addWidget(heading)
        heading_box.addWidget(hint)
        top.addLayout(heading_box, 1)
        self.badge = QLabel("0 đoạn")
        self.badge.setObjectName("Badge")
        top.addWidget(self.badge, alignment=Qt.AlignTop)
        main_layout.addLayout(top)

        file_row = QHBoxLayout()
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Chọn file .txt…")
        choose_text = QPushButton("Chọn TXT")
        choose_text.clicked.connect(self.pick_text)
        reload_text = QPushButton("Nạp lại")
        reload_text.clicked.connect(self.reload_text)
        file_row.addWidget(self.text_edit, 1)
        file_row.addWidget(choose_text)
        file_row.addWidget(reload_text)
        main_layout.addLayout(file_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["#", "Tên file xuất", "Nội dung sẽ đọc", "Trạng thái"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, self.table.horizontalHeader().ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, self.table.horizontalHeader().Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, self.table.horizontalHeader().ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        main_layout.addWidget(self.table, 1)

        status_card, status = self._card("Tiến trình")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setObjectName("Subtitle")
        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(120)
        status.addWidget(self.progress)
        status.addWidget(self.status_label)
        status.addWidget(self.log_box)
        main_layout.addWidget(status_card)

        splitter.addWidget(sidebar)
        splitter.addWidget(main)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def _setup_service(self) -> None:
        self.service_thread = QThread(self)
        self.service = GenerationService()
        self.service.moveToThread(self.service_thread)
        self.generate_requested.connect(self.service.generate_batch)
        self.service.log.connect(self.append_log)
        self.service.progress.connect(self.on_progress)
        self.service.item_done.connect(self.on_item_done)
        self.service.failed.connect(self.on_failed)
        self.service.finished.connect(self.on_finished)
        self.service_thread.start()

    def _refresh_hardware(self) -> None:
        info = device_summary()
        self.cpu_threads.setMaximum(max(1, int(info["cpu_threads"])))
        self.cpu_threads.setValue(max(1, min(int(info["cpu_threads"]), max(1, int(info["cpu_threads"]) - 1))))
        if info["cuda_available"]:
            self.hardware_label.setText(
                f"GPU: {info['cuda_name']} • {info['cuda_vram_gb']} GB VRAM\nCPU threads: {info['cpu_threads']}"
            )
        else:
            self.hardware_label.setText(f"Không thấy CUDA GPU • CPU threads: {info['cpu_threads']}")

    def pick_reference(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Chọn voice mẫu", "", "Audio (*.wav *.mp3 *.flac *.m4a);;All files (*.*)")
        if path:
            self.reference_path = path
            self.reference_edit.setText(path)

    def pick_output(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Chọn thư mục xuất", self.output_edit.text() or str(Path.home()))
        if path:
            self.output_dir = path
            self.output_edit.setText(path)

    def pick_text(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Chọn file văn bản", "", "Text (*.txt);;All files (*.*)")
        if path:
            self.text_path = path
            self.text_edit.setText(path)
            self.reload_text()

    def reload_text(self) -> None:
        path = self.text_edit.text().strip()
        if not path:
            return
        try:
            text = read_text_file(path)
            self.items = parse_document(text)
            self._populate_table()
            self.badge.setText(f"{len(self.items)} đoạn")
            self.append_log(f"Đã nạp {len(self.items)} đoạn từ {Path(path).name}")
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi đọc file", str(exc))

    def _populate_table(self) -> None:
        self.table.setRowCount(len(self.items))
        for row, item in enumerate(self.items):
            display_no = item.source_number if item.source_number is not None else item.sequence
            preview = " ".join(item.spoken_text.split())
            if len(preview) > 220:
                preview = preview[:217] + "…"
            self.table.setItem(row, 0, QTableWidgetItem(str(display_no)))
            self.table.setItem(row, 1, QTableWidgetItem(item.filename))
            self.table.setItem(row, 2, QTableWidgetItem(preview))
            self.table.setItem(row, 3, QTableWidgetItem("Chờ"))

    def _device_value(self) -> str:
        text = self.device_combo.currentText()
        if text == "NVIDIA CUDA":
            return "cuda"
        if text == "CPU":
            return "cpu"
        return "auto"

    def start_generation(self) -> None:
        self.reference_path = self.reference_edit.text().strip()
        self.output_dir = self.output_edit.text().strip()
        if not self.items:
            QMessageBox.warning(self, "Thiếu nội dung", "Hãy chọn file TXT có ít nhất một đoạn văn.")
            return
        if not self.reference_path or not Path(self.reference_path).is_file():
            QMessageBox.warning(self, "Thiếu voice mẫu", "Hãy chọn file MP3/WAV dùng để clone giọng.")
            return
        if not self.output_dir:
            QMessageBox.warning(self, "Thiếu thư mục", "Hãy chọn thư mục xuất audio.")
            return
        if not self.consent.isChecked():
            QMessageBox.warning(self, "Xác nhận quyền sử dụng", "Bạn cần xác nhận có quyền/được phép sử dụng giọng mẫu.")
            return

        for row in range(self.table.rowCount()):
            self.table.item(row, 3).setText("Chờ")
        self.generate_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setValue(0)
        self.status_label.setText("Đang khởi động…")

        job = {
            "items": self.items,
            "reference_path": self.reference_path,
            "reference_text": self.reference_text.toPlainText().strip(),
            "output_dir": self.output_dir,
            "device": self._device_value(),
            "cpu_threads": self.cpu_threads.value(),
            "settings": {
                "temperature": self.temperature.value(),
                "top_p": self.top_p.value(),
                "top_k": self.top_k.value(),
                "max_new_tokens": self.max_tokens.value(),
                "seed": self.seed.value(),
            },
        }
        self.generate_requested.emit(job)

    def cancel_generation(self) -> None:
        self.service.request_cancel()
        self.status_label.setText("Đã yêu cầu dừng; app sẽ dừng sau đoạn đang tạo.")
        self.cancel_btn.setEnabled(False)

    def append_log(self, text: str) -> None:
        self.log_box.appendPlainText(text)

    def on_progress(self, done: int, total: int, message: str) -> None:
        pct = int(done * 100 / total) if total else 0
        self.progress.setValue(pct)
        self.status_label.setText(message)
        if done < total and done < self.table.rowCount():
            self.table.item(done, 3).setText("Đang tạo…")
            self.table.scrollToItem(self.table.item(done, 0))

    def on_item_done(self, row: int, path: str) -> None:
        if 0 <= row < self.table.rowCount():
            self.table.item(row, 3).setText("✓ Xong")
        self.append_log(f"✓ {path}")

    def on_failed(self, message: str) -> None:
        self.append_log("LỖI: " + message)
        QMessageBox.critical(self, "Generation error", message)

    def on_finished(self, success: bool, message: str) -> None:
        self.generate_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText(message)
        if success:
            self.progress.setValue(100)
            self.append_log(message)
            box = QMessageBox(self)
            box.setWindowTitle("Hoàn tất")
            box.setText(message)
            open_btn = box.addButton("Mở thư mục", QMessageBox.AcceptRole)
            box.addButton("Đóng", QMessageBox.RejectRole)
            box.exec()
            if box.clickedButton() is open_btn:
                QDesktopServices.openUrl(Path(self.output_dir).resolve().as_uri())

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.service.busy:
            answer = QMessageBox.question(
                self,
                "Đang tạo audio",
                "Tác vụ vẫn đang chạy. Đóng app có thể làm mất đoạn hiện tại. Vẫn đóng?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                event.ignore()
                return
            self.service.request_cancel()
        self.service_thread.quit()
        self.service_thread.wait(1500)
        event.accept()
