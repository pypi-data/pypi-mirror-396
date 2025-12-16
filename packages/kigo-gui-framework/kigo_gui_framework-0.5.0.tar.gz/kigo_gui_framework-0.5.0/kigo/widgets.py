from PyQt6.QtWidgets import (
    QLabel, QPushButton, QLineEdit, QComboBox, QWidget,
    QCheckBox, QProgressBar, QScrollBar, QSlider, 
    QVBoxLayout, QHBoxLayout # QHBoxLayout for the Row widget
)
from PyQt6.QtWebEngineWidgets import QWebEngineView 
from PyQt6.QtCore import QUrl, Qt 
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput 

# --- Existing Widgets ---

class Label:
    def __init__(self, text="Label", parent=None):
        self.qt_widget = QLabel(text, parent)
        self.qt_widget.setStyleSheet("font-size: 14pt; margin: 5px;")
    
    def set_text(self, text):
        self.qt_widget.setText(text)

class Button:
    def __init__(self, text="Button", on_click=None, parent=None):
        self.qt_widget = QPushButton(text, parent)
        self.qt_widget.setStyleSheet("padding: 8px 15px; background-color: #4CAF50; color: white; border-radius: 5px; border: none;")
        if on_click:
            self.qt_widget.clicked.connect(on_click)

class TextBox:
    def __init__(self, initial_text="", placeholder="Enter text...", parent=None):
        self.qt_widget = QLineEdit(initial_text, parent)
        self.qt_widget.setPlaceholderText(placeholder)
        self.qt_widget.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 3px;")
    
    def get_text(self):
        return self.qt_widget.text()

class Dropdown:
    def __init__(self, items=None, parent=None):
        self.qt_widget = QComboBox(parent)
        if items:
            self.qt_widget.addItems(items)
        self.qt_widget.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 3px;")
    
    def get_selected(self):
        return self.qt_widget.currentText()

class Browser:
    """A web browser widget using QWebEngineView."""
    def __init__(self, url="https://www.google.com", parent=None):
        self.qt_widget = QWebEngineView(parent)
        self.load_url(url)
        self.qt_widget.setMinimumHeight(400) 

    def load_url(self, url):
        """Loads a given URL in the browser view."""
        self.qt_widget.setUrl(QUrl(url))

    def reload(self):
        """Reloads the current page."""
        self.qt_widget.reload()

class Checkbox:
    """A simple check box for boolean input."""
    def __init__(self, text="Check me", checked=False, on_toggle=None, parent=None):
        self.qt_widget = QCheckBox(text, parent)
        self.qt_widget.setChecked(checked)
        self.qt_widget.setStyleSheet("margin: 5px;")
        if on_toggle:
            self.qt_widget.stateChanged.connect(on_toggle)

    def is_checked(self):
        return self.qt_widget.isChecked()

class ProgressBar:
    """A bar to display task progress."""
    def __init__(self, minimum=0, maximum=100, value=0, parent=None):
        self.qt_widget = QProgressBar(parent)
        self.qt_widget.setRange(minimum, maximum)
        self.qt_widget.setValue(value)
        self.qt_widget.setTextVisible(True)
        self.qt_widget.setStyleSheet("height: 20px; margin: 10px 0;")

    def set_value(self, value):
        self.qt_widget.setValue(value)

    def get_value(self):
        return self.qt_widget.value()

class Slider:
    """A horizontal slider for selecting a value in a range."""
    def __init__(self, minimum=0, maximum=100, value=50, on_value_change=None, parent=None):
        self.qt_widget = QSlider(Qt.Orientation.Horizontal, parent)
        self.qt_widget.setRange(minimum, maximum)
        self.qt_widget.setValue(value)
        self.qt_widget.setStyleSheet("margin: 10px 0;")
        
        if on_value_change:
            self.qt_widget.valueChanged.connect(on_value_change)

    def get_value(self):
        return self.qt_widget.value()

class Scrollbar:
    """A basic vertical scroll bar, useful for manual control or within custom widgets."""
    def __init__(self, minimum=0, maximum=100, value=0, on_value_change=None, parent=None):
        self.qt_widget = QScrollBar(Qt.Orientation.Vertical, parent)
        self.qt_widget.setRange(minimum, maximum)
        self.qt_widget.setValue(value)
        
        if on_value_change:
            self.qt_widget.valueChanged.connect(on_value_change)
            
    def get_value(self):
        return self.qt_widget.value()

class WavPlayer:
    """A widget for playing WAV or other audio files."""
    def __init__(self, filepath=None, parent=None):
        self.qt_widget = QWidget(parent)
        
        # Setup UI
        layout = QHBoxLayout(self.qt_widget)
        self.status_label = QLabel("Ready (No file loaded)")
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")

        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.status_label)
        
        # Setup Multimedia Backend
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        
        # Connect Controls
        self.play_button.clicked.connect(self.play)
        self.stop_button.clicked.connect(self.stop)
        self.media_player.playbackStateChanged.connect(self._update_status)

        # Load file if provided
        if filepath:
            self.load_file(filepath)

    def load_file(self, filepath):
        """Loads a local file path into the player."""
        if filepath:
            url = QUrl.fromLocalFile(filepath)
            self.media_player.setSource(url)
            self.status_label.setText(f"Loaded: {filepath.split('/')[-1]}")
            
    def play(self):
        """Starts or resumes playback."""
        if self.media_player.source():
            self.media_player.play()
        else:
            self.status_label.setText("Error: No audio file loaded.")

    def stop(self):
        """Stops playback."""
        self.media_player.stop()

    def _update_status(self, state):
        """Updates the status label based on the player state."""
        PlaybackState = QMediaPlayer.PlaybackState
        state_map = {
            PlaybackState.Stopped: "Stopped",
            PlaybackState.Playing: "Playing...",
            PlaybackState.Paused: "Paused"
        }
        status = state_map.get(state, "Ready/Error")
        self.status_label.setText(f"Status: {status}")


# --- New Structural Widget ---

class Row:
    """A container widget that lays out its children horizontally."""
    def __init__(self, parent=None):
        # The underlying Qt widget is a general QWidget
        self.qt_widget = QWidget(parent)
        # The internal layout is QHBoxLayout
        self.layout = QHBoxLayout(self.qt_widget)
        # Optional: Set margins/spacing for a clean appearance
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(10) 

    def add_widget(self, widget):
        """Adds a Kigo widget to the horizontal layout."""
        # Check if the object has the required .qt_widget attribute
        if hasattr(widget, 'qt_widget'):
            self.layout.addWidget(widget.qt_widget)
        else:
            print(f"Warning: Cannot add non-Kigo object {widget.__class__.__name__} to Row.")


__all__ = [
    'Label', 'Button', 'TextBox', 'Dropdown', 'Browser', 
    'Checkbox', 'ProgressBar', 'Slider', 'Scrollbar', 'WavPlayer', 'Row' 
]