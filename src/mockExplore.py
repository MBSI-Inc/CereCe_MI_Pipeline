import csv
import time
import threading
import numpy as np

# A mock packet class that resembles explorepy.packet.EEG


class MockPacket:
    """Simulate the packet object returned by ExplorePy with .get_data() method."""

    def __init__(self, timestamps, data):
        """
        Args:
            timestamps: numpy array of shape (n_samples,)
            data: numpy array of shape (n_samples, n_channels)
        """
        self._timestamps = timestamps
        self._data = data

    def get_data(self):
        """
        Returns:
            A tuple (timestamps, eeg_data).
            'timestamps' is shape (n_samples,)
            'eeg_data' is shape (n_samples, n_channels).
        """
        return (self._timestamps, self._data)


class MockStreamProcessor:
    """Mimics the stream_processor in ExplorePy with a subscribe method."""

    def __init__(self):
        self.subscribers = []  # list of (callback, topic)

    def subscribe(self, callback, topic=None):
        """
        Store callbacks so they can be called when new data arrives.
        In real ExplorePy, you often see usage like:
            explore.stream_processor.subscribe(callback=..., topic=TOPICS.raw_ExG)
        """
        self.subscribers.append((callback, topic))

    def _emit_packet(self, packet):
        """Call all subscribed callbacks with the packet."""
        for callback, topic in self.subscribers:
            # If you want to filter by topic, you can check `topic` here.
            callback(packet)


class MockExplore:
    """
    Mocks the behavior of explorepy.Explore but reads from a CSV file
    instead of a real EEG device. The CSV should have:
        TimeStamp,ch1,ch2,ch3,ch4
    as columns.
    """

    def __init__(self, csv_path, chunk_size=16, sampling_rate=250.0):
        """
        Args:
            csv_path (str): Path to your CSV file with columns
                            TimeStamp, ch1, ch2, ch3, ch4.
            chunk_size (int): How many samples are sent in each 'packet'.
            sampling_rate (float): Rate at which data was originally sampled
                                   (used to simulate real-time streaming).
        """
        self.csv_path = csv_path
        self.chunk_size = chunk_size
        self.sampling_rate = sampling_rate

        # This is what your AsyncMICore code calls: explore.stream_processor.subscribe(...)
        # so we mimic that with a MockStreamProcessor instance:
        self.stream_processor = MockStreamProcessor()

        self._stop_thread = False
        self._thread = None

    def connect(self, device_name=None):
        """
        Mocks the 'connect' method. Here, we load the CSV data
        and start streaming in a background thread.
        """
        # Load the entire CSV into memory so we can iterate through it.
        self.all_timestamps, self.all_data = self._read_csv()

        # Start streaming in a separate thread.
        self._stop_thread = False
        self._thread = threading.Thread(target=self._start_streaming, daemon=True)
        self._thread.start()

    def stop(self):
        """Call this to stop streaming and join the thread."""
        self._stop_thread = True
        if self._thread:
            self._thread.join()

    def _read_csv(self):
        """
        Read CSV, returning (timestamps, data).
        `timestamps` -> shape (N,)
        `data` -> shape (N, 4) for 4 channels
        """
        timestamps = []
        data = []
        with open(self.csv_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # adjust names if your CSV has exact headers "TimeStamp", "ch1", "ch2", ...
                ts = float(row["TimeStamp"])
                ch1 = float(row["ch1"])
                ch2 = float(row["ch2"])
                ch3 = float(row["ch3"])
                ch4 = float(row["ch4"])
                timestamps.append(ts)
                data.append([ch1, ch2, ch3, ch4])

        timestamps = np.array(timestamps)
        data = np.array(data)
        return timestamps, data

    def _start_streaming(self):
        """
        Continuously feed data to the subscribers in chunks
        at a rate that approximates real-time streaming.
        """
        num_samples = len(self.all_timestamps)
        idx = 0
        # We'll read chunk_size samples at a time, then sleep
        # chunk_size / sampling_rate seconds to mimic real-time.
        dt = self.chunk_size / self.sampling_rate

        while not self._stop_thread and idx < num_samples:
            end_idx = min(idx + self.chunk_size, num_samples)

            # Slice out a chunk
            chunk_timestamps = self.all_timestamps[idx:end_idx]
            chunk_data = self.all_data[idx:end_idx, :].T

            # Build a packet and emit it
            packet = MockPacket(chunk_timestamps, chunk_data)
            self.stream_processor._emit_packet(packet)

            # Advance the index
            idx = end_idx

            # Simulate the real device time spacing
            time.sleep(dt)

        # Done streaming
        print("MockExplore: Streaming finished or stopped.")

    def disconnect(self):
        pass
