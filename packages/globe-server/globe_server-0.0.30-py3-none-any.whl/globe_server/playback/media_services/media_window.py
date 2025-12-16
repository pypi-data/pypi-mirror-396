"""
PyQt-based Media Window Manager.

This module provides a single Qt window with stacked layout containing:
- QWebEngineView for earth-viz visualization
- QWidget for VLC video playback

The window can switch between the two views programmatically.
"""

import logging
import threading
import platform
from typing import Optional
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, pyqtSignal, QObject, QThread, QTimer

logger = logging.getLogger(__name__)


class MediaWindowSignals(QObject):
    """Signals for cross-thread communication with Qt window."""
    show_vlc_signal = pyqtSignal()
    show_earth_viz_signal = pyqtSignal()
    show_window_signal = pyqtSignal()
    hide_window_signal = pyqtSignal()
    close_signal = pyqtSignal()


class MediaWindow(QMainWindow):
    """Qt window with stacked layout for VLC and earth-viz."""
    
    def __init__(self, earth_viz_url: str = "http://localhost:8000/earth-viz-app/"):
        super().__init__()
        
        # Set up window
        self.setWindowTitle("Globe Media Player")
        # Window will be shown fullscreen via _show_window()
        
        # Create stacked widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create earth-viz web view (don't load URL yet)
        self.earth_viz_view = QWebEngineView()
        self.earth_viz_url = earth_viz_url
        self._earth_viz_loaded = False
        
        # Set up load handlers for debugging
        self.earth_viz_view.loadStarted.connect(self._on_load_started)
        self.earth_viz_view.loadFinished.connect(self._on_load_finished)
        self.earth_viz_view.loadProgress.connect(self._on_load_progress)
        
        # Set a simple background while loading
        self.earth_viz_view.setStyleSheet("background-color: #1a1a1a;")
        
        self.stack.addWidget(self.earth_viz_view)  # Index 0
        
        # Create VLC video widget (real widget for VLC embedding)
        self.vlc_widget = QWidget()
        self.vlc_widget.setStyleSheet("background-color: black;")
        vlc_layout = QVBoxLayout()
        vlc_layout.setContentsMargins(0, 0, 0, 0)
        self.vlc_widget.setLayout(vlc_layout)
        self.stack.addWidget(self.vlc_widget)  # Index 1
        
        # Start with VLC (black screen) visible - earth-viz will load on first switch
        self.stack.setCurrentIndex(1)
        
        # Store widget ID immediately (must be done in Qt thread)
        self.vlc_widget_id = int(self.vlc_widget.winId())
        logger.info(f"VLC widget ID captured: {self.vlc_widget_id}")
        
        # Set up signals for cross-thread control
        self.signals = MediaWindowSignals()
        self.signals.show_vlc_signal.connect(self._switch_to_vlc)
        self.signals.show_earth_viz_signal.connect(self._switch_to_earth_viz)
        self.signals.show_window_signal.connect(self._show_window)
        self.signals.hide_window_signal.connect(self._hide_window)
        self.signals.close_signal.connect(self.close)
        
        logger.info("Media window created with VLC and earth-viz views")
    
    def _on_load_started(self):
        """Called when earth-viz starts loading."""
        logger.info("Earth-viz page load started")
    
    def _on_load_progress(self, progress: int):
        """Called during earth-viz loading."""
        if progress % 25 == 0:  # Log every 25%
            logger.info(f"Earth-viz loading: {progress}%")
    
    def _on_load_finished(self, success: bool):
        """Called when earth-viz finishes loading."""
        if success:
            logger.info("Earth-viz page loaded successfully")
        else:
            logger.error("Earth-viz page failed to load - check if server is running")
    
    def _switch_to_vlc(self):
        """Switch to VLC view (called from Qt thread)."""
        self.stack.setCurrentIndex(1)
        logger.info("Switched to VLC view")
    
    def _switch_to_earth_viz(self):
        """Switch to earth-viz view (called from Qt thread)."""
        # Switch to earth-viz view first
        self.stack.setCurrentIndex(0)
        logger.info("Switched to earth-viz view")
        
        # Load URL on first switch (asynchronous)
        if not self._earth_viz_loaded:
            logger.info(f"Initiating load of earth-viz URL: {self.earth_viz_url}")
            self.earth_viz_view.setUrl(QUrl(self.earth_viz_url))
            self._earth_viz_loaded = True
    
    def _show_window(self):
        """Show window and bring to front (called from Qt thread)."""
        self.showFullScreen()
        self.activateWindow()
        self.raise_()
        logger.info("Media window shown (fullscreen)")
    
    def _hide_window(self):
        """Hide/minimize window (called from Qt thread)."""
        self.showMinimized()
        logger.info("Media window minimized")
    
    def get_vlc_widget_id(self):
        """Get the window ID for VLC embedding (cached, safe to call from any thread)."""
        return self.vlc_widget_id


class QtRunner(QObject):
    """Helper class to run Qt window creation in the Qt thread."""
    window_ready = pyqtSignal(object, int)  # Emits (window, vlc_widget_id) when ready
    
    def __init__(self, earth_viz_url: str):
        super().__init__()
        self.earth_viz_url = earth_viz_url
        self.window = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_window(self):
        """Create the media window (must be called in Qt thread)."""
        try:
            self.logger.info("Creating media window in Qt thread")
            self.window = MediaWindow(self.earth_viz_url)
            self.window.showFullScreen()  # Show fullscreen immediately
            # Emit both window and widget ID (both captured in Qt thread)
            widget_id = self.window.get_vlc_widget_id()
            self.window_ready.emit(self.window, widget_id)
            self.logger.info(f"Media window created and shown fullscreen (widget ID: {widget_id})")
        except Exception as e:
            self.logger.error(f"Error creating window: {e}", exc_info=True)
            self.window_ready.emit(None, 0)


class MediaWindowManager:
    """Manages the Qt application and media window in a separate thread."""
    
    def __init__(self):
        self.app: Optional[QApplication] = None
        self.window: Optional[MediaWindow] = None
        self.thread: Optional[threading.Thread] = None
        self.qt_thread: Optional[QThread] = None
        self.qt_runner: Optional[QtRunner] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._started = False
        self._window_ready = threading.Event()
        self.vlc_widget_id = None
    
    def start(self, earth_viz_url: str = "http://localhost:8000/earth-viz-app/") -> bool:
        """Start the Qt application and window in a background thread."""
        if self._started:
            self.logger.warning("Media window already started")
            return True
        
        try:
            def run_qt_app():
                """Run Qt application in thread."""
                try:
                    # Create QApplication in this thread
                    self.app = QApplication.instance()
                    if self.app is None:
                        self.app = QApplication([])
                    
                    # Create Qt runner to handle window creation
                    self.qt_runner = QtRunner(earth_viz_url)
                    self.qt_runner.window_ready.connect(self._on_window_ready)
                    
                    # Use QTimer to create window after event loop starts
                    QTimer.singleShot(100, self.qt_runner.create_window)
                    
                    self.logger.info("Starting Qt event loop for media window")
                    self.app.exec_()
                    
                except Exception as e:
                    self.logger.error(f"Error in Qt thread: {e}")
                    self._window_ready.set()
            
            # Start Qt in background thread
            self.thread = threading.Thread(target=run_qt_app, daemon=True)
            self.thread.start()
            
            # Wait for window to be ready
            self.logger.info("Waiting for media window to be ready...")
            if not self._window_ready.wait(timeout=5.0):
                self.logger.error("Timeout waiting for media window")
                return False
            
            if self.window is None:
                self.logger.error("Media window creation failed")
                return False
            
            self._started = True
            self.logger.info("Media window started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start media window: {e}")
            return False
    
    def _on_window_ready(self, window, widget_id):
        """Called when window is ready (from Qt thread)."""
        self.window = window
        self.vlc_widget_id = widget_id
        self._window_ready.set()
    
    def is_running(self) -> bool:
        """Check if the media window is running."""
        return self._started and self.window is not None
    
    def switch_to_vlc(self) -> bool:
        """Switch to VLC view."""
        try:
            if self.window:
                self.window.signals.show_vlc_signal.emit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to switch to VLC: {e}")
            return False
    
    def switch_to_earth_viz(self) -> bool:
        """Switch to earth-viz view."""
        try:
            if self.window:
                self.window.signals.show_earth_viz_signal.emit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to switch to earth-viz: {e}")
            return False
    
    def show_window(self) -> bool:
        """Show the media window (bring to front)."""
        try:
            if self.window:
                self.window.signals.show_window_signal.emit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to show window: {e}")
            return False
    
    def hide_window(self) -> bool:
        """Hide/minimize the media window."""
        try:
            if self.window:
                self.window.signals.hide_window_signal.emit()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to hide window: {e}")
            return False
    
    def get_vlc_widget_id(self) -> Optional[int]:
        """Get the window ID for VLC embedding."""
        try:
            if self.window:
                return self.window.get_vlc_widget_id()
            return None
        except Exception as e:
            self.logger.error(f"Failed to get VLC widget ID: {e}")
            return None
    
    def get_earth_viz_view(self) -> Optional[QWebEngineView]:
        """Get the earth-viz web view widget."""
        if self.window:
            return self.window.earth_viz_view
        return None
    
    def cleanup(self) -> None:
        """Clean up Qt resources."""
        try:
            if self.window:
                self.window.signals.close_signal.emit()
            
            # Quit Qt application if it exists
            if self.app:
                self.app.quit()
            
            self._started = False
            self.logger.info("Media window cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up media window: {e}")
