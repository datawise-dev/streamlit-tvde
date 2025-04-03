# utils/notifications.py
import streamlit as st
import time
from typing import Optional, Callable

def show_notification(
    message: str,
    type: str = "info",
    duration: Optional[float] = None,
    callback: Optional[Callable] = None
):
    """
    Show a notification message with optional auto-dismiss and callback.
    
    Args:
        message: Message to display
        type: Type of notification (info, success, warning, error)
        duration: Seconds to display the message (None for persistent)
        callback: Function to call after the message is displayed
    """
    # Display the message based on type
    if type == "success":
        notification = st.success(message)
    elif type == "warning":
        notification = st.warning(message)
    elif type == "error":
        notification = st.error(message)
    else:  # info is default
        notification = st.info(message)
    
    # Auto-dismiss after specified duration
    if duration is not None:
        time.sleep(duration)
        notification.empty()
    
    # Execute callback if provided
    if callback:
        callback()
