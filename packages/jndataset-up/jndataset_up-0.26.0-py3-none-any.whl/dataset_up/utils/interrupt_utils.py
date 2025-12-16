import os
import signal
from dataset_up.utils.concurrent_utils import interrupt_event,can_quit_event
from dataset_up.log.logger import get_logger

logger = get_logger(__name__)
_signal_callback = None
def register_signal_handler(callback = None):
    global _signal_callback
    _signal_callback = callback
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
def signal_handler(sig, frame):
    print("\ninterrupt detected,force exit...\n")
    logger.critical("interrupt detected,force exit...")
    
    if _signal_callback:
        try:
            _signal_callback()
        except Exception as e:
            logger.error(f"interrupt signal callback error:{e}")
    interrupt_event.set()
    can_quit_event.wait(10)
    os._exit(0)
    
