import sys
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QTextEdit, QLineEdit, 
                               QComboBox, QPushButton, QProgressBar, QSpinBox, 
                               QGroupBox, QTextBrowser, QMessageBox, QCheckBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from .config import Config
from .veo_client import VeoClient

# Configure Logging to emit signal to GUI
class SignallingLogHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)

class GenerationWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, prompt, aspect_ratio, person_generation, negative_prompt, seed):
        super().__init__()
        self.prompt = prompt
        self.aspect_ratio = aspect_ratio
        self.person_generation = person_generation
        self.negative_prompt = negative_prompt
        self.seed = seed

    def run(self):
        # Redirect logger to this thread's signal
        handler = SignallingLogHandler(self.log_signal)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Get root logger or specific logger
        logger = logging.getLogger("VeoClient")
        logger.addHandler(handler)
        
        try:
            client = VeoClient()
            result_path = client.generate_video(
                prompt=self.prompt,
                aspect_ratio=self.aspect_ratio,
                person_generation=self.person_generation,
                negative_prompt=self.negative_prompt,
                seed=self.seed
            )
            
            if result_path:
                self.finished_signal.emit(result_path)
            else:
                self.error_signal.emit("Generation completed but no file returned.")
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            logger.removeHandler(handler)

class VeoStudioWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Veo Studio")
        self.resize(1000, 800)
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left Panel - Inputs
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, 1)
        
        # Right Panel - Logs & Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel, 1)
        
        # --- Left Panel Content ---
        
        # Prompt Group
        prompt_group = QGroupBox("Prompt")
        prompt_layout = QVBoxLayout()
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your video description here...")
        prompt_layout.addWidget(self.prompt_edit)
        prompt_group.setLayout(prompt_layout)
        left_layout.addWidget(prompt_group, 2)
        
        # Model Selection Group
        model_group = QGroupBox("Model Selection")
        model_layout = QVBoxLayout()
        self.model_combo = QComboBox()
        self.load_models()
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        model_layout.addWidget(self.model_combo)
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)
        
        # Negative Prompt Group
        neg_prompt_group = QGroupBox("Negative Prompt")
        neg_prompt_layout = QVBoxLayout()
        self.neg_prompt_edit = QLineEdit()
        self.neg_prompt_edit.setPlaceholderText("Content to avoid...")
        neg_prompt_layout.addWidget(self.neg_prompt_edit)
        neg_prompt_group.setLayout(neg_prompt_layout)
        left_layout.addWidget(neg_prompt_group)
        
        # Configuration Group
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        
        # Aspect Ratio
        ar_layout = QHBoxLayout()
        ar_layout.addWidget(QLabel("Aspect Ratio:"))
        self.ar_combo = QComboBox()
        self.ar_combo.addItems(["16:9", "9:16"])
        ar_layout.addWidget(self.ar_combo)
        config_layout.addLayout(ar_layout)
        
        # Person Generation
        pg_layout = QHBoxLayout()
        pg_layout.addWidget(QLabel("Person Generation:"))
        self.pg_combo = QComboBox()
        self.pg_combo.addItems(["allow_adult", "dont_allow"])
        pg_layout.addWidget(self.pg_combo)
        config_layout.addLayout(pg_layout)
        
        # Seed
        seed_layout = QHBoxLayout()
        self.use_seed_cb = QCheckBox("Use Seed")
        seed_layout.addWidget(self.use_seed_cb)
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 2147483647)
        self.seed_spin.setEnabled(False)
        seed_layout.addWidget(self.seed_spin)
        config_layout.addLayout(seed_layout)
        
        self.use_seed_cb.stateChanged.connect(lambda state: self.seed_spin.setEnabled(state == Qt.CheckState.Checked.value))
        
        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)
        
        # Generate Button
        self.generate_btn = QPushButton("Generate Video")
        self.generate_btn.setMinimumHeight(50)
        self.generate_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; font-size: 16px;")
        self.generate_btn.clicked.connect(self.start_generation)
        left_layout.addWidget(self.generate_btn)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # --- Right Panel Content ---
        
        # Log Output
        log_group = QGroupBox("Console Output")
        log_layout = QVBoxLayout()
        self.log_browser = QTextBrowser()
        self.log_browser.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: monospace;")
        log_layout.addWidget(self.log_browser)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)

        # Check API Key on startup
        self.check_config()

    def check_config(self):
        try:
            Config.validate()
        except ValueError as e:
            self.log_message(f"CONFIGURATION ERROR: {e}")
            QMessageBox.critical(self, "Configuration Error", str(e))
            self.generate_btn.setEnabled(False)

    def log_message(self, message):
        self.log_browser.append(message)
        # Auto scroll to bottom
        scrollbar = self.log_browser.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def load_models(self):
        """Load models from config into the combobox."""
        models = Config.get_models()
        current_model_id = Config.get_current_model()
        
        self.model_combo.clear()
        for i, model in enumerate(models):
            # Display Name (ID)
            display_text = f"{model['name']} ({model['id']})"
            self.model_combo.addItem(display_text, model['id'])
            
            # Set tooltip for description
            self.model_combo.setItemData(i, model['description'], Qt.ItemDataRole.ToolTipRole)
            
            # Select if it's the current model
            if model['id'] == current_model_id:
                self.model_combo.setCurrentIndex(i)

    def on_model_changed(self, index):
        """Update config when model selection changes."""
        if index >= 0:
            model_id = self.model_combo.itemData(index) # itemData(index, Qt.UserRole) by default gets the second arg of addItem
            # PySide6 addItem(text, userData) stores userData in UserRole
            Config.set_current_model(model_id)
            self.log_message(f"Selected Model: {model_id}")

    def start_generation(self):
        prompt = self.prompt_edit.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Input Error", "Please enter a prompt.")
            return

        # Disable UI
        self.generate_btn.setEnabled(False)
        self.progress_bar.setRange(0, 0) # Indeterminate mode
        
        # Get Params
        aspect_ratio = self.ar_combo.currentText()
        person_generation = self.pg_combo.currentText()
        negative_prompt = self.neg_prompt_edit.text().strip() or None
        seed = self.seed_spin.value() if self.use_seed_cb.isChecked() else None
        
        # Start Worker
        self.worker = GenerationWorker(prompt, aspect_ratio, person_generation, negative_prompt, seed)
        self.worker.log_signal.connect(self.log_message)
        self.worker.finished_signal.connect(self.on_generation_finished)
        self.worker.error_signal.connect(self.on_generation_error)
        self.worker.start()

    def on_generation_finished(self, result_path):
        self.generate_btn.setEnabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.log_message(f"SUCCESS: Video generated at {result_path}")
        QMessageBox.information(self, "Success", f"Video generated successfully!\nSaved to: {result_path}")

    def on_generation_error(self, error_msg):
        self.generate_btn.setEnabled(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.log_message(f"ERROR: {error_msg}")
        QMessageBox.critical(self, "Generation Failed", f"An error occurred:\n{error_msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VeoStudioWindow()
    window.show()
    sys.exit(app.exec())
