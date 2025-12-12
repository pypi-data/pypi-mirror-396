"""
Cross-platform desktop notification system.
Supports Windows, macOS, and Linux with fallback options.
"""
import platform
import subprocess
import sys
from typing import Optional
from pathlib import Path


class Notifier:
    def __init__(self):
        self.system = platform.system()
        self._setup_notifyer()

    def _setup_notifyer(self):
        if self.system == "Windows":
            self.notifyer = self._notify_windows
        elif self.system == "Darwin":
            self.notifyer = self._notify_macos
        elif self.system == "Linux":
            self.notifyer = self._notify_linux
        else:
            self.notifyer = self._fallback_notifyer

    def notify(
        self, message: str, title: str = "Email Notification", urgency: str = "normal"
    ):
        """
        Send a desktop notification.

        Args:
            message: The notification message body
            title: The notification title (default: "Email Notification")
            urgency: Urgency level - "low", "normal", or "critical" (Linux only)
        """
        try:
            self.notifyer(message, title, urgency)
        except Exception as e:
            print(f"Notification error: {e}")
            self.notifyer = self._notify_fallback
            self.notifyer(message, title, urgency)

    def _notify_windows(self,  message: str, title: str, urgency: str):
        """

        Send notification on Windows using PowerShell.
        """

        try:
            from plyer import notification

            notification.notify(
                title=title,
                message=message,
                app_name="Inbox Zero",
                timeout=5
            )
        except ImportError:
            # Fallback to PowerShell toast notification
            ps_script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $toastXml = [xml] $template.GetXml()
            $toastXml.GetElementsByTagName("text")[0].AppendChild($toastXml.CreateTextNode("{title}")) > $null
            $toastXml.GetElementsByTagName("text")[1].AppendChild($toastXml.CreateTextNode("{message}")) > $null
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($toastXml.OuterXml)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Inbox Zero").Show($toast)
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                timeout=3
            )
    def _notify_macos(self, message: str, title: str, urgency: str):
        """
        Send notification on macOS using osascript
        """

        try: 
            import pync
            pync.notify(message, title=title, app_name="Inbox Zero")
        except ImportError:
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], capture_output=True, timeout=3)

    def _notify_linux(self, message: str, title: str, urgency: str):
        """
        Send notification on Linux using notify-send
        """
        try:
            import notify2
            notify2.init("Inbox Zero")
            n = notify2.Notification(title, message)
            n.set_urgency(self._get_urgency_level(urgency))
            n.show()
        except ImportError:
            urgency_flag = self._get_urgency_level(urgency)
            subprocess.run(
                ["notify-send", "-u", urgency_flag, title, message],
                capture_output=True,
                timeout=3,
            )

    def _get_urgency_level(self, urgency: str) -> str:
        """Convert urgency string to appropriate format."""
        urgency_map = {"low": "low", "normal": "normal", "critical": "critical"}
        return urgency_map.get(urgency.lower(), "normal")

    def _notify_fallback(self, message: str, title: str, urgency: str):
        """Fallback notification method - print to console."""
        print(f"\n{'='*50}")
        print(f"🔔 {title}")
        print(f"{'-'*50}")
        print(f"{message}")
        print(f"{'='*50}\n")

    # Global notifier instance for easy import


_notifier_instance = None


def get_notifier() -> Notifier:
    """Get or create the global notifier instance."""
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = Notifier()
    return _notifier_instance

def notify(message: str, title: str = "Email Notification", urgency: str = "normal"):
    """
    Convenience function to send a notification.

    Usage:
        from notifier import notify
        notify("You have 3 new emails!", title="Inbox Zero", urgency="normal")

    Args:
        message: The notification message
        title: The notification title
        urgency: "low", "normal", or "critical"
    """

    get_notifier().notify(message, title, urgency)

# Example usage and testing
if __name__ == "__main__":
    # Test notifications
    print("Testing desktop notifications...")

    notifier = Notifier()
    print(f"Detected OS: {notifier.system}")

    # Test basic notification
    notifier.notify("This is a test notification!", title="Test Alert")

    # Test with different urgency levels
    import time

    time.sleep(2)
    notifier.notify("Low priority message", title="Low Priority", urgency="low")

    time.sleep(2)
    notifier.notify("Critical alert!", title="Critical Alert", urgency="critical")

    print("Notification tests completed!")
