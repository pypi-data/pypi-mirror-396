import sys
import time
from datetime import datetime as dt

# Third-party dependencies
# PyQt6
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton,
    QLineEdit, QMessageBox,
    QHBoxLayout, QSpinBox, QFileDialog, QFormLayout, QScrollArea,QComboBox, QDoubleSpinBox, QTabWidget, QGridLayout, QFrame,QTextEdit
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal
)
from PyQt6.QtGui import (
    QIcon, QPixmap, QImage, QCursor, QColor
)
from pathlib import Path

# Image processing
from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt

from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from diffusers import StableDiffusionPipeline

import torch

import os
from huggingface_hub import HfApi

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEngineScript, QWebEnginePage
from PyQt6.QtCore import QUrl

token = "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"

def is_diffusers_folder(path):
    return os.path.isfile(os.path.join(path, "model_index.json"))

def is_ckpt_file(path):
    return path.endswith(".ckpt") or path.endswith(".safetensors")


# ------------------------------------------------------------
# Core Logic
# ------------------------------------------------------------
def find_icon(icon_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    for path in [
        os.path.join(script_dir, icon_name),
        os.path.join(script_dir, "menu", icon_name),
        os.path.abspath(os.path.join(script_dir, os.pardir, icon_name))
    ]:
        if os.path.exists(path):
            return path
    return None

# Other
QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

# ------------------- THREAD FOR IMAGE GENERATION (OVERHAUL) -------------------
class ImageGenerator(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    eta_signal = pyqtSignal(float)

    def __init__(self, pipe, prompt, steps, guidance, width, height, device_type="cpu", seed=42):
        super().__init__()
        self.pipe = pipe
        self.prompt = prompt
        self.steps = steps
        self.guidance = guidance
        self.width = width
        self.height = height
        self.device_type = device_type
        self.seed = seed
        self.stop_flag = False
        self.start_time = None

    @staticmethod
    def _make_multiple_of_8(x):
        return max(8, int(x) // 8 * 8)

    def run(self):
        try:
            self.start_time = time.time()

            # Ensure width/height are valid for many SD VAEs/UNets
            width = self._make_multiple_of_8(self.width)
            height = self._make_multiple_of_8(self.height)

            # build a reasonable negative prompt
            negative_prompt = (
                "low quality, blurry, low-res, pixelated, grain, noise, jpeg artifacts, oversharpened, overprocessed, "
                "bad anatomy, deformed, bad hands, extra fingers, mutated, malformed, missing limbs, bad proportions, "
                "cartoon, anime, sketch, cgi, 3d render, toy, illustration, drawing, cropped, out of frame, "
                "bad perspective, bad composition, background clutter, overexposed, underexposed, harsh lighting, "
                "unnatural colors, oversaturated, undersaturated, washed out, text, logo, watermark, signature, frame"
            )

            # Create torch generator for correct device
            device = "cuda" if (self.device_type == "cuda" and torch.cuda.is_available()) else "cpu"
            gen = torch.Generator(device=device).manual_seed(self.seed)

            # Callback used by diffusers: called every callback_steps
            def callback(step, timestep, latents):
                if self.stop_flag:
                    # Raise custom exception to be handled below
                    raise KeyboardInterrupt("Generation aborted by user")

                completed = step + 1
                total = max(1, self.steps)
                progress_percent = int(completed / total * 100)
                elapsed = time.time() - self.start_time
                avg_step = elapsed / completed if completed > 0 else 0.0
                eta = max((total - completed) * avg_step, 0.0)
                self.progress.emit(progress_percent)
                self.eta_signal.emit(eta)

            # Use autocast on CUDA for mixed precision if model supports it
            use_autocast = (device == "cuda")

            # Run the pipeline call inside correct autocast / inference mode
            with torch.inference_mode():
                if use_autocast:
                    # fp16 on cuda
                    with torch.autocast(device_type="cuda"):
                        result = self.pipe(
                            prompt=self.prompt,
                            negative_prompt=negative_prompt,
                            height=height,
                            width=width,
                            num_inference_steps=self.steps,
                            guidance_scale=self.guidance,
                            generator=gen,
                            callback=callback,
                            callback_steps=1,
                            output_type="pil"
                        )
                else:
                    # CPU / fp32
                    result = self.pipe(
                        prompt=self.prompt,
                        negative_prompt=negative_prompt,
                        height=height,
                        width=width,
                        num_inference_steps=self.steps,
                        guidance_scale=self.guidance,
                        generator=gen,
                        callback=callback,
                        callback_steps=1,
                        output_type="pil"
                    )

            # diffusers returns a StableDiffusionPipelineOutput with .images
            image = result.images[0]

            # gentle sharpening/unsharp mask (better control)
            try:
                image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
            except Exception:
                # fallback
                image = image.filter(ImageFilter.SHARPEN)

            # final emit
            self.finished.emit(image)

        except KeyboardInterrupt as k:
            # user stopped generation
            self.error.emit("⛔ Generation stopped by user.")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            # send a concise error message but include traceback in status_label if you want
            self.error.emit(f"Error during generation: {str(e)}\n{tb}")

class ImageDisplayWidget(QWidget):
    def __init__(self, image):
        super().__init__()
        self.setWindowTitle("Generated Image")
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setWindowIcon(QIcon(find_icon('background/NectarX.png') or 'background/NectarX.png'))
        self.resize(400, 400)  # scalable instead of fixed
        self.image = image

        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout()
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.update_image(image)

    def update_image(self, image: Image.Image):
        """Convert PIL image to QPixmap safely."""
        # Ensure image is in RGBA format
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        # Convert PIL image → bytes → QImage → QPixmap
        data = image.tobytes("raw", "RGBA")
        qimage = QImage(
            data,
            image.width,
            image.height,
            QImage.Format.Format_RGBA8888
        )
        pixmap = QPixmap.fromImage(qimage)

        # Scale pixmap to fit window but keep aspect ratio
        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled)

class HomePage(QWidget):
    """Modern animated homepage with feature cards"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QWidget {
                background-color: #141414;
                color: #ffffff;
            }
            QLabel#titleLabel {
                font-size: 28px;
                font-weight: bold;
                color: #ffffff;
                border-radius: 12px;
            }
            QLabel#subtitleLabel {
                font-size: 13px;
                color: #c9c9c9;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(25)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(main_layout)

        # --- Header ---
        header = QWidget()
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        title = QLabel("Welcome to NectarGraphix")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        subtitle = QLabel("Local Image Generation • Productivity Tools • Intelligent Automation")
        subtitle.setObjectName("subtitleLabel")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        main_layout.addWidget(header)

        # --- Feature Cards ---
        grid = QGridLayout()
        grid.setSpacing(20)

        features = [
            ("⚡ Local Model Runner", "Load and run AI models instantly."),
            ("📁 Assets Manager", "Manage your AI assets and files."),
            ("🔊 Fast Studio", "Speech synthesis, waveforms & processing."),
            ("🧠 Local Studio", "Generate images on your hardware."),
            ("🌐 Browser Tools", "Web generation & enhancement utilities."),
            ("🛡 Online Studio", "Generate images in cloud."),
        ]

        for i, (title, desc) in enumerate(features):
            card = self.create_card(title, desc)
            grid.addWidget(card, i // 2, i % 2)

        main_layout.addLayout(grid)

    # -------------------------------------------------
    # CARD CREATOR
    # -------------------------------------------------
    def create_card(self, title_text, desc_text):
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: #1f1f1f;
                border: 1px solid #2a2a2a;
                border-radius: 14px;
            }
            QWidget:hover {
                background-color: #282828;
                border: 1px solid #3f3f3f;
            }
        """)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; font-weight: 600; color: #ffffff;")

        # Description
        desc = QLabel(desc_text)
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 12px; color: #b9b9b9;")

        card_layout.addWidget(title)
        card_layout.addWidget(desc)
        card.setLayout(card_layout)

        # Allow clicking
        card.mousePressEvent = lambda event: self.card_clicked(title_text)

        return card

    # -------------------------------------------------
    # CLICK HANDLER
    # -------------------------------------------------
    def card_clicked(self, name):
        print(f"[HOMEPAGE] Card clicked → {name}")
        # You can switch pages here, e.g.:
        # self.parent().navigate_to("models")

# ------------------- MAIN APP -------------------
class Studio(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NectarGraphix")
        self.setWindowIcon(QIcon(find_icon('background/easel.png') or 'background/NectarX.png'))
        self.setGeometry(100, 100, 600, 350)
        self.Studio()

    def Studio(self):    

        layout = QVBoxLayout()

        # --- Model selection ---
        model_layout = QHBoxLayout()
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "Select Model...",
            "stable-diffusion-v1-5",
            "dreamlike-photoreal-2.0"
        ])

        # Styling for dark modern theme
        self.model_combo.setStyleSheet("""
            QComboBox {
                background-color: #000000;
                color: white;
                padding: 8px 12px;
                border: 2px solid None;
                border-radius: 8px;
                font-size: 14px;
                min-width: 180px;
            }
            QComboBox:hover {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid None;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #555;
                border-radius: 0px 8px 8px 0px;
                background-color: #000000;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #000000;
                color: white;
                selection-background-color: #4CAF50;
                selection-color: black;
                border-radius: 8px;
                padding: 5px;
                outline: 0;
            }
        """)

        self.model_path_input = QLineEdit()
        self.model_path_input.setPlaceholderText("Or browse custom model path...")
        self.model_path_input.setReadOnly(True)
        self.model_path_input.setStyleSheet("background-color: #000000; color: #ffffff")
        self.model_path_input.setFixedHeight(38)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setFixedHeight(38)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #3E8E41;
            }
        """)

        self.device_combo = QComboBox()
        self.device_combo.addItems(["CPU", "GPU"])

        # Styling for dark modern theme
        self.device_combo.setStyleSheet("""
            QComboBox {
                background-color: #000000;
                color: white;
                padding: 8px 12px;
                border: 2px solid None;
                border-radius: 8px;
                font-size: 14px;
                min-width: 100px;
            }
            QComboBox:hover {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid None;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid #555;
                border-radius: 0px 8px 8px 0px;
                background-color: #000000;
            }
            QComboBox::down-arrow {
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #000000;
                color: white;
                selection-background-color: #4CAF50;
                selection-color: black;
                border-radius: 8px;
                padding: 5px;
                outline: 0;
            }
        """)

        self.load_model_button = QPushButton("Load Model")
        self.load_model_button.setFixedHeight(38)
        self.load_model_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #3E8E41;
            }
        """)
        model_layout.addWidget(self.model_combo)
        model_layout.addWidget(self.model_path_input)
        model_layout.addWidget(self.browse_button)
        device_label = QLabel("Device:")
        device_label.setStyleSheet("""
            QLabel {
                background-color: #ffffff;      /* Dark background */
                color: #000000;               /* White text */
                font-size: 14px;              /* Medium font size */
                padding: 4px 0;               /* Small vertical padding */
            }
        """)
        device_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Add to layout
        model_layout.addWidget(device_label)
        model_layout.addWidget(self.device_combo)
        model_layout.addWidget(self.load_model_button)
        layout.addLayout(model_layout)

        # --- Settings ---
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignCenter)
        form_layout.setHorizontalSpacing(15)
        form_layout.setVerticalSpacing(10)

        # Steps SpinBox
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(5, 100)
        self.steps_spin.setValue(30)
        self.steps_spin.setStyleSheet("""
            QLabel {
                    Background-color: #ffffff;
                    color: #000000;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 2px 0;
                }
            QSpinBox {
                background-color: #000000;
                color: white;
                border: 2px solid None;
                border-radius: 8px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QSpinBox:focus {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid None;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                background-color: #ffffff;
                border-left: 1px solid #555;
                border-top-right-radius: 6px;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                background-color: #ffffff;
                border-left: 1px solid #555;
                border-bottom-right-radius: 6px;
            }
            QSpinBox::up-button:hover,
            QSpinBox::down-button:hover {
                background-color: #1e1e1e;        /* Green hover effect */
            }
            QSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
                width: 10px;
                height: 10px;
            }
            
        """)

        # Guidance DoubleSpinBox
        self.guidance_spin = QDoubleSpinBox()
        self.guidance_spin.setRange(1.0, 20.0)
        self.guidance_spin.setSingleStep(0.5)
        self.guidance_spin.setValue(8.5)
        self.guidance_spin.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #000000;        /* Dark background */
                color: #ffffff;                   /* White text */
                border: 2px solid None;           /* Subtle border */
                border-radius: 8px;               /* Rounded corners */
                padding: 5px 10px;                /* Inner padding */
                font-size: 14px;                  /* Readable text */
                min-width: 100px;
            }
            QDoubleSpinBox:hover {
                background-color: #ffffff;        /* Dark background */
                color: #000000; 
                border: 2px solid None;        /* Green hover accent */
            }
            QDoubleSpinBox:focus {
                border: 2px solid None;        /* Focus highlight */
            }
            QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 18px;
                background-color: #ffffff;
                border-left: 1px solid #555;
                border-top-right-radius: 6px;
            }
            QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 18px;
                background-color: #ffffff;
                border-left: 1px solid #555;
                border-bottom-right-radius: 6px;
            }
            QDoubleSpinBox::up-button:hover,
            QDoubleSpinBox::down-button:hover {
                background-color: #1e1e1e;        /* Green hover effect */
            }
            QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
                width: 10px;
                height: 10px;
            }
        """)

        # Width SpinBox
        self.width_spin = QSpinBox()
        self.width_spin.setRange(128, 2048)
        self.width_spin.setValue(360)
        self.width_spin.setStyleSheet(self.steps_spin.styleSheet())

        # Height SpinBox
        self.height_spin = QSpinBox()
        self.height_spin.setRange(128, 2048)
        self.height_spin.setValue(360)
        self.height_spin.setStyleSheet(self.steps_spin.styleSheet())

        # Labels styling
        for label_text in ["Steps:", "Guidance:", "Width:", "Height:"]:
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    Background-color: #ffffff;
                    color: #ffffff;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 2px 0;
                }
            """)

        # Add rows to form layout
        form_layout.addRow(QLabel("Steps:"), self.steps_spin)
        form_layout.addRow(QLabel("Guidance:"), self.guidance_spin)
        form_layout.addRow(QLabel("Width:"), self.width_spin)
        form_layout.addRow(QLabel("Height:"), self.height_spin)

        layout.addLayout(form_layout)

        # --- Prompt input ---
        prompt_layout = QHBoxLayout()
        self.prompt_input = QLineEdit()
        self.prompt_input.setFixedHeight(38)
        self.prompt_input.setPlaceholderText("Describe your image...")
        self.prompt_input.setStyleSheet("""
            QLineEdit {
                background-color: #000000;
                color: white;
                padding: 10px;
                border: 2px solid None;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                background-color: #1e1e1e;
                color: white;
                border: 2px solid None;
            }
        """)
        self.generate_button = QPushButton("Generate Image")
        self.generate_button.setFixedHeight(38)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #3E8E41;
            }
        """)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedHeight(38)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #3E8E41;
            }
        """)
        self.save_button = QPushButton("Save Image")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton:pressed {
                background-color: #3E8E41;
            }
        """)
        self.cancel_button.setEnabled(False)
        self.save_button.setEnabled(False)
        prompt_layout.addWidget(self.prompt_input)
        prompt_layout.addWidget(self.generate_button)
        prompt_layout.addWidget(self.cancel_button)
        prompt_layout.addWidget(self.save_button)
        layout.addLayout(prompt_layout)

        # --- Status and progress ---
        self.status_label = QLabel("   Model not loaded.")
        self.status_label.setFixedHeight(30)
        self.status_label.setStyleSheet("background-color: #ffffff; color: #000000;")
        layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                text-align: center;
                color: #444444;
                font-weight: bold;
            }

            QProgressBar::chunk {
                background-color: #ffffff;
                border-radius: 4px;
            }
            """)
        layout.addWidget(self.progress_bar)
        self.eta_label = QLabel("ETA: --")
        self.eta_label.setFixedHeight(30)
        self.eta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.eta_label.setStyleSheet("background-color: #ffffff; color: #000000;")
        layout.addWidget(self.eta_label)

        # --- Image display ---
        self.scroll_area = QScrollArea()
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

        # --- Connections ---
        self.browse_button.clicked.connect(self.browse_model)
        self.load_model_button.clicked.connect(self.load_model)
        self.generate_button.clicked.connect(self.generate_image)
        self.cancel_button.clicked.connect(self.cancel_generation)
        self.save_button.clicked.connect(self.save_image)
        self.model_combo.currentIndexChanged.connect(self.model_selection_changed)

    # ------------------- FUNCTIONS -------------------
    def model_selection_changed(self):
        selected = self.model_combo.currentText()
        if selected != "Select Model...":
            self.model_path_input.setText(selected)

    def browse_model(self):
        path = QFileDialog.getExistingDirectory(self, "Select Model Directory")
        if path:
            self.model_path_input.setText(path)

    def load_model(self):
        path = self.model_path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "Error", "Please select a model path or HuggingFace model ID.")
            return

        device_choice = self.device_combo.currentText().lower()
        use_cuda = device_choice == "gpu" and torch.cuda.is_available()
        device_type = "cuda" if use_cuda else "cpu"
        torch_dtype = torch.float16 if use_cuda else torch.float32

        self.status_label.setText(f"Loading model on {device_type.upper()}...")
        QApplication.processEvents()

        try:
            # If path is a directory, search for model_index.json recursively
            if os.path.isdir(path):
                found = None
                for root, dirs, files in os.walk(path):
                    if "model_index.json" in files:
                        found = root
                        break
                if found:
                    self.pipe = StableDiffusionPipeline.from_pretrained(
                        found,
                        torch_dtype=torch_dtype,
                        safety_checker=None,
                        use_safetensors=True
                    )
                else:
                    raise Exception("No model_index.json found in this folder or its subfolders")

            # If path looks like a HuggingFace model ID
            else:
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    path,
                    torch_dtype=torch_dtype,
                    safety_checker=None,
                    use_safetensors=True,
                    cache_dir=os.path.join(os.getcwd(), "models")
                )

            # Scheduler & device
            try:
                self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(self.pipe.scheduler.config)
            except Exception:
                pass

            self.pipe = self.pipe.to(device_type)

            # Enable optimizations
            try:
                self.pipe.enable_attention_slicing()
                self.pipe.enable_vae_slicing()
                self.pipe.enable_vae_tiling()
                self.pipe.enable_xformers_memory_efficient_attention()
            except Exception:
                pass

            self.status_label.setText(f"Model loaded successfully on {device_type.upper()}.")
        except Exception as e:
            QMessageBox.critical(self, "Error loading model", str(e))
            self.status_label.setText("Failed to load model.")
            self.pipe = None

    def generate_image(self):
        if not self.pipe:
            QMessageBox.warning(self, "Error", "Model is not loaded.")
            return
        prompt = self.prompt_input.text().strip()
        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a prompt.")
            return

        self.status_label.setText("   Generating image...")
        self.progress_bar.setValue(0)
        self.eta_label.setText("ETA: calculating...")
        self.generate_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.save_button.setEnabled(False)

        steps = self.steps_spin.value()
        guidance = self.guidance_spin.value()
        width = self.width_spin.value()
        height = self.height_spin.value()

        self.thread = ImageGenerator(self.pipe, prompt, steps, guidance, width, height)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.display_image)
        self.thread.error.connect(self.show_error)
        self.thread.eta_signal.connect(self.update_eta)
        self.thread.start()

    def cancel_generation(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop_flag = True
            self.cancel_button.setEnabled(False)
            self.status_label.setText("Stopping generation...")

    def display_image(self, image: Image.Image):
        self.current_image = image  # store full-res image
        # Open the dedicated image display widget
        self.image_display_widget = ImageDisplayWidget(image)
        self.image_display_widget.show()

        # Update status and progress bar
        self.status_label.setText("Image generated successfully!")
        self.progress_bar.setValue(100)
        self.eta_label.setText("ETA: done")
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.save_button.setEnabled(True)

        # Automatically save the image
        self.save_image(auto=True)

    def save_image(self, auto=False):
        if self.current_image:
            if auto:
                filename = dt.now().strftime("outputs/image_%Y%m%d_%H%M%S.png")
            else:
                filename, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png)")
                if not filename:
                    return
            self.current_image.save(filename)
            if not auto:
                QMessageBox.information(self, "Saved", f"Image saved to {filename}")

    def update_eta(self, eta):
        self.eta_label.setText(f"ETA: {eta:.1f}s")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)
        self.status_label.setText("Error generating image.")
        self.progress_bar.setValue(0)
        self.eta_label.setText("ETA: --")
        self.generate_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.save_button.setEnabled(False)

class ColabViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Google Colab Viewer")
        self.resize(1200, 800)

        layout = QVBoxLayout(self)

        self.web = QWebEngineView()
        layout.addWidget(self.web)

        self.configure_webengine()

        # Load your Colab link
        url = "https://colab.research.google.com/drive/1daR-OW1sBxJyLK2pUr46tSf7WWtC7CXI#scrollTo=OX_P872cQ9b8"
        self.web.setUrl(QUrl(url))

    def configure_webengine(self):
        settings = self.web.settings()

        # IMPORTANT: Enable all JS & Web features Google Colab needs
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        # Allow popup windows (Colab uses them)
        page = self.web.page()
        page.profile().setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.AllowPersistentCookies
        )
        page.profile().setHttpCacheType(QWebEngineProfile.HttpCacheType.DiskHttpCache)

        page.setFeaturePermission(
            QUrl("https://colab.research.google.com"),
            QWebEnginePage.Feature.Notifications,
            QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
        )

# ---------------- Model Download Thread ----------------
class ModelDownloaderThread(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, model_id, local_path, download_type="diffusers", token=None):
        super().__init__()
        self.model_id = model_id
        self.local_path = Path(local_path)
        self.download_type = download_type
        self.token = token  # <- Store token

    def run(self):
        try:
            self.progress.emit(5, "Initializing download...")

            from huggingface_hub import snapshot_download, hf_hub_download

            # ↓ Pass token here
            if self.download_type == "diffusers":
                snapshot_download(
                    repo_id=self.model_id,
                    local_dir=self.local_path,
                    local_dir_use_symlinks=False,
                    resume_download=True,
                    token=self.token
                )
            else:
                hf_hub_download(
                    repo_id=self.model_id,
                    filename=(
                        "model.safetensors"
                        if "safetensors" in self.model_id.lower()
                        else "model.ckpt"
                    ),
                    local_dir=self.local_path,
                    local_dir_use_symlinks=False,
                    resume_download=True,
                    token=self.token
                )

            self.progress.emit(95, "Verifying files...")
            self.finished.emit(str(self.local_path))

        except Exception as e:
            self.error.emit(str(e))

# ---------------- Model Card Widget ----------------
class ModelCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, model_id, description=""):
        super().__init__()
        self.model_id = model_id
        self.setFixedHeight(120)
        self.setFixedWidth(366)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 8px;
            }
            QFrame:hover {
                background-color: #3c3c3c;
            }
            QLabel {
                color: #cbd2f7;
            }
            QLabel#title {
                font-weight: 600;
                font-size: 14px;
            }
            QLabel#desc {
                color: #a0a8c0;
                font-size: 12px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(2)

        self.title_label = QLabel(model_id)
        self.title_label.setObjectName("title")
        layout.addWidget(self.title_label)

        self.desc_label = QLabel(description)
        self.desc_label.setObjectName("desc")
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)

    def mousePressEvent(self, event):
        self.clicked.emit(self.model_id)

# ---------------- Main UI ----------------
class NectarModelDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nectar Model Downloader")
        self.downloader_thread = None
        self.api = HfApi()
        self.init_ui()
        self.fetch_model_feed()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        split_layout = QHBoxLayout()
        split_layout.setSpacing(25)

        # ---------------- Left: Model Feed ----------------
        self.model_scroll = QScrollArea()
        self.model_scroll.setWidgetResizable(True)
        self.model_scroll.setFixedWidth(400)
        scroll_content = QWidget()
        self.model_layout = QVBoxLayout(scroll_content)
        self.model_layout.setSpacing(10)
        scroll_content.setLayout(self.model_layout)
        self.model_scroll.setWidget(scroll_content)
        split_layout.addWidget(self.model_scroll)

        # ---------------- Right: Controls ----------------
        right_panel = QVBoxLayout()
        right_panel.setSpacing(20)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Enter model ID")
        self.model_input.setFixedHeight(30)
        right_panel.addWidget(self.model_input)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Diffusers (Recommended)", "Checkpoint (.safetensors)"])
        right_panel.addWidget(self.type_combo)

        icon_path_refresh = find_icon("background/explore.png")

        path_layout = QHBoxLayout()
        self.download_path = QLineEdit(os.path.expanduser("~NectarModels"))
        self.download_path.setFixedHeight(30)
        browse_btn = QPushButton()
        browse_btn.setIcon(QIcon(icon_path_refresh))
        browse_btn.setFixedSize(30, 30)
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.download_path)
        path_layout.addWidget(browse_btn)
        right_panel.addLayout(path_layout)

        threads_layout = QHBoxLayout()
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(1, 8)
        self.workers_spin.setValue(3)
        threads_layout.addWidget(QLabel("Threads:"))
        threads_layout.addWidget(self.workers_spin)
        threads_layout.addStretch()
        right_panel.addLayout(threads_layout)

        self.download_btn = QPushButton("⬇️ Download Model")
        self.download_btn.setFixedHeight(45)
        self.download_btn.clicked.connect(self.start_download)
        right_panel.addWidget(self.download_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_panel.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(200)
        right_panel.addWidget(self.log_text)

        split_layout.addLayout(right_panel)
        main_layout.addLayout(split_layout)

        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#1e1e1e"))
        self.setPalette(palette)

    # ---------------- Hugging Face Feed ----------------
    def fetch_model_feed(self):
        self.log("🌐 Fetching models from Hugging Face Hub...")
        try:
            models = self.api.list_models(
                filter="stable-diffusion",
                sort="downloads",
                limit=20
            )

            for m in models:
                desc = f"{m.downloads:,} downloads"
                card = ModelCard(m.modelId, desc)
                card.clicked.connect(self.on_model_selected)
                self.model_layout.addWidget(card)

            self.model_layout.addStretch()
            self.log("✅ Model feed loaded!")

        except Exception as e:
            self.log(f"❌ Failed to fetch model feed: {e}")


    # ---------------- Handlers ----------------
    def on_model_selected(self, model_id):
        self.model_input.setText(model_id)

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if path:
            self.download_path.setText(path)

    def log(self, message):
        from datetime import datetime
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{ts}] {message}")

    def start_download(self):
        model_id = self.model_input.text().strip()
        if not model_id:
            self.log("❌ Enter a model ID")
            return
        path = self.download_path.text().strip()
        os.makedirs(path, exist_ok=True)
        final_path = os.path.join(path, model_id.split("/")[-1])
        self.progress_bar.setVisible(True)
        self.download_btn.setEnabled(False)

        self.downloader_thread = ModelDownloaderThread(
            model_id, 
            final_path,
            "diffusers" if self.type_combo.currentText() == "Diffusers (Recommended)" else "checkpoint",
            token=token
        )
        self.downloader_thread.progress.connect(self.update_progress)
        self.downloader_thread.finished.connect(self.on_finished)
        self.downloader_thread.error.connect(self.on_error)
        self.downloader_thread.start()

    def update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.log(text)

    def on_finished(self, path):
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        self.log(f"✅ Download finished: {path}")

    def on_error(self, error):
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        self.log(f"❌ Error: {error}")

# ------------------- MAIN APP -------------------
class StableDiffusionApp(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NectarGraphix")
        self.setWindowFlags(Qt.WindowType.Dialog)
        self.setWindowIcon(QIcon(find_icon('background/easel.png') or 'background/NectarX.png'))
        self.setGeometry(100, 100, 600, 350)

        self.pipe = None
        self.thread = None
        self.current_image = None  # store full-resolution image

        self.init_ui()
        os.makedirs("outputs", exist_ok=True)  # folder to save images

    def init_ui(self):
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab {
                background: #000000;
                color: #ffffff;
                padding: 12px 20px;
                border-radius: 8px;
                margin-right: 10px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #000000;
            }
            QTabBar::tab:last {
                margin-right: 0;
            }
        """)

        self.Home_tab = HomePage()
        self.Local_Studio_tab = Studio()
        self.Online_Studio_tab = ColabViewer()
        self.Model_tab = NectarModelDownloader()

        self.tab_widget.addTab(self.Home_tab, "Home")
        self.tab_widget.addTab(self.Local_Studio_tab, "Local Studio")
        self.tab_widget.addTab(self.Online_Studio_tab, "Online Studio")
        self.tab_widget.addTab(self.Model_tab, "Model")

        # container layout to center tab_widget
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(self.tab_widget)
        container_layout.addStretch()

        self.layout = QVBoxLayout()
        self.layout.addLayout(container_layout)
        self.setLayout(self.layout)

def main():
    app = QApplication(sys.argv)
    window = StableDiffusionApp()
    window.show()
    sys.exit(app.exec())

# Allow direct execution: python main.py
if __name__ == "__main__":
    main()