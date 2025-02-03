from PIL import ImageGrab
import time
from db import Session, ScreenShot
from ocr import OCR
from datetime import datetime

class ScreenshotManager:
    def __init__(self, ocr_model):
        self.session = Session()
        self.ocr_model = ocr_model
        self._subscribers = []  # List to hold callback functions

    def subscribe(self, callback):
        """Add a subscriber to be notified of new screenshots."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback):
        """Remove a subscriber."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _notify_subscribers(self):
        """Notify all subscribers of changes."""
        for callback in self._subscribers:
            callback()

    def capture_screenshot(self, bbox):
        """Capture and save a screenshot of the specified area."""
        screenshot = ImageGrab.grab(bbox=bbox)
        filename = f"screenshot_{int(time.time())}.png"
        screenshot.save(filename)
        
        text = self.ocr_model.extract_text(filename)
        
        new_ss = ScreenShot(
            stored_at=filename,
            text=text,
            created_at=datetime.now()
        )
        self.session.add(new_ss)
        self.session.commit()
        
        # Notify subscribers of the new screenshot
        self._notify_subscribers()
        
        return filename

    def get_screenshots(self, page, per_page):
        """Get a paginated list of screenshots."""
        offset_val = page * per_page
        return (self.session.query(ScreenShot)
               .order_by(ScreenShot.id.desc())  # Show newest first
               .limit(per_page)
               .offset(offset_val)
               .all())

    def get_total_screenshots(self):
        """Get total number of screenshots."""
        return self.session.query(ScreenShot).count()