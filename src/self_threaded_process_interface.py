from abc import ABC, abstractmethod
from typing import Any


class AbstractSelfThreadedProcess(ABC):
    """
    Interface for a class that can run itself in its own thread.
    This thread should update some data inside itself.
    This data can be extracted by an exterior thread.

    Asides from the interface, it should implement a means of controlling a thread with emphasis on how to stop it.
    https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/

    Example:

    class MySelfThreadedProcess(SelfThreadedProcessInterface):
        def __init__(self):
            ''' store a data, a self contained thread, and a bool for if that thread is running '''
            self.data = 0
            self.thread = None
            self.running = False

        def __runInThread(self):
            ''' This function is run inside the thread and should update self.data'''
            while True:
                self.data += 1
                if not self.running:
                    break
            sleep(1)

        def start(self):
            ''' Starts the thread '''
            self.running = True

            # Setting thread as daemon ensure this is killed even if stop is not called.
            # EG this class is disposed but stop is not called.
            # Setting may not be necessary, but probably a good precaution.
            self.thread = Thread(target=self.__run, daemon=True)
            self.thread.start()

        def stop(self):
            ''' Stops the thread '''
            self.running = False # tells thread to end
            self.thread.join() # wait for thread to exit before continuing
    """

    @abstractmethod
    def __init__(self):
        """Constructor to initialize itself"""
        pass

    @abstractmethod
    def start(self):
        """Start the thread. Init any thread control variables/processes needed."""
        pass

    @abstractmethod
    def stop(self):
        """Use thread control method to end the thread"""
        pass

    @abstractmethod
    def getData(self) -> Any:
        """Fetches the latest stored data as updated by the thread"""
        pass

    def __enter__(self):
        """Context manager entry - starts the thread"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stops the thread"""
        self.stop()
        return False  # Don't suppress exceptions
