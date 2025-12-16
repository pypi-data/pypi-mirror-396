import platform
import random
import threading
from collections import deque
from concurrent.futures import Future
from dataclasses import dataclass
from time import sleep, time
import queue
from typing import Any, Callable, Dict, List, Optional

from serial import Serial, SerialException
from serial.tools import list_ports


@dataclass
class StimulusEpoch:
    label: str
    onset_sample: int
    offset_sample: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    data: Optional[List[List[float]]] = None

    def to_dict(self) -> Dict[str, Any]:
        length = None
        if self.offset_sample is not None:
            length = max(0, self.offset_sample - self.onset_sample)
        return {
            "label": self.label,
            "onset_sample": self.onset_sample,
            "offset_sample": self.offset_sample,
            "length_samples": length,
            "metadata": self.metadata or {},
            "data": self.data,
        }


class Device:
    __DEBUG_MODE = False
    __PREV_END = '\n'
    __VERSION = '1.2.0'

    def __init__(self, debug_mode=False, data_ready_callback=None, settings_written_callback=None, data_chunk=0,
                 faker=False, faker_data=None, connection_state_callback=None, connection_check_interval=1.0,
                 epoch_buffer_size=20000):
        self.__DEBUG_MODE = debug_mode

        self.signalGenerator = faker
        self._faker_last_emit = None
        self._faker_sample_residual = 0.0

        if faker_data is None:
            self.faker_data = []
        else:
            self.faker_data = faker_data

        # Device Info
        self.deviceName = "No Device Found"
        self.sampleCount = 0
        self.firmwareVersion = "0.0.0"
        self.unicID = "No Data"
        self.flashData = "No Data"
        self.chCount = 8
        self.exCount = 0

        # Flags
        self.signalGeneratingFlag = False
        self.dataGatheringFlag = False
        self.answerToInitFlag = False
        self.settingModeFlag = False
        self.newDataCount = 0
        self.chunk = data_chunk

        # Settings
        self.linkedEar = False
        self.testSignal = False
        self.leadoffMode = False
        self._samplingRate = 2000
        self._gain = 24
        self._exgain = 24
        self.channelsOn = [True] * 21
        self.exchannelsOn = [False] * 3
        self.interaction = ['0'] * 4

        # Threads
        self.data_received_thread = None
        self.data_ready_callback = data_ready_callback
        self.stop_event = threading.Event()
        self.settings_written_callback = settings_written_callback

        # Ports & Buffers
        self.data = []
        self.receiveBuffer = []
        self.sendBuffer = bytearray(32)
        self.tempBuffer = bytearray()
        self.ports = self.find_port(["USB Serial Device", 'STM32 Virtual ComPort'])

        self._serial = None
        self._io_queue = queue.Queue()
        self._io_thread = threading.Thread(target=self._io_worker, name="NeuroPortIO", daemon=True)
        self._io_thread.start()
        self._io_shutdown = False
        self._io_lock = threading.Lock()
        self._connect_future = None
        self._is_connected = False
        self._connect_error = None
        self._current_port = None
        self._connection_state_callback = connection_state_callback
        try:
            interval = float(connection_check_interval)
        except (TypeError, ValueError):
            interval = 1.0
        self._connection_check_interval = max(0.25, interval)
        self._connection_watchdog_enabled = True
        self._connection_monitor_stop = threading.Event()
        self._connection_monitor_thread = threading.Thread(
            target=self._connection_monitor_loop,
            name="NeuroPortConnectionMonitor",
            daemon=True
        )
        self._connection_monitor_thread.start()

        # Stimulus/epoch tracking
        self._stim_lock = threading.Lock()
        self._stim_epochs: List[StimulusEpoch] = []
        self._active_stimulus: Optional[StimulusEpoch] = None
        self._stimulus_event_callback: Optional[
            Callable[[str, StimulusEpoch, int], None]
        ] = None

        # Rolling sample buffer for epoch extraction
        try:
            buf_size = int(epoch_buffer_size or 0)
        except (TypeError, ValueError):
            buf_size = 0
        self._epoch_buffer_size = max(0, buf_size)
        self._epoch_buffer = deque(maxlen=self._epoch_buffer_size) if self._epoch_buffer_size else None
        self._epoch_lock = threading.Lock()

        self.set_buffer()
        self.connect_async()

    def __del__(self):
        try:
            self.shutdown()
        except Exception:
            pass

    @staticmethod
    def _completed_future(result: Any = None) -> Future:
        future = Future()
        future.set_result(result)
        return future

    def _io_worker(self):
        while True:
            task, future, _name = self._io_queue.get()
            if task is None:
                if future and not future.done():
                    future.set_result(True)
                break
            try:
                result = task()
            except Exception as exc:
                if future and not future.done():
                    future.set_exception(exc)
            else:
                if future and not future.done():
                    future.set_result(result)

    def _submit_task(self, task: Callable[[], Any], name: str = "") -> Future:
        if self._io_shutdown:
            raise RuntimeError("Device I/O loop already shut down")
        future = Future()
        self._io_queue.put((task, future, name))
        return future

    def shutdown(self):
        if getattr(self, "_io_shutdown", False):
            return

        # Attempt to close the serial port within the worker thread.
        try:
            self._submit_task(lambda: self._close_serial_impl(destroy=True), name="shutdown-close").result(timeout=2)
        except Exception:
            pass

        sentinel = Future()
        self._io_queue.put((None, sentinel, "shutdown"))
        try:
            sentinel.result(timeout=2)
        except Exception:
            pass

        if self._io_thread and self._io_thread.is_alive():
            self._io_thread.join(timeout=2)

        self._io_shutdown = True
        self._set_connection_state(False)

        monitor_stop = getattr(self, "_connection_monitor_stop", None)
        if monitor_stop:
            monitor_stop.set()
        monitor_thread = getattr(self, "_connection_monitor_thread", None)
        if monitor_thread and monitor_thread.is_alive():
            monitor_thread.join(timeout=2)

    def set_connection_state_callback(
            self,
            callback: Optional[Callable[[bool, Optional[str], Optional[BaseException]], None]]
    ):
        """Register a callback that receives (connected, port, reason)."""
        self._connection_state_callback = callback

    def unset_connection_state_callback(self):
        self._connection_state_callback = None

    def _set_connection_state(self, connected: bool, *, port: Optional[str] = None,
                              reason: Optional[BaseException] = None) -> bool:
        """Update cached connection state and notify listeners on changes."""
        previous = bool(self._is_connected)
        last_port = self._current_port

        if connected:
            self._is_connected = True
            if port:
                self._current_port = port
            event_port = self._current_port
            self._connect_error = None
        else:
            self._is_connected = False
            event_port = port if port is not None else last_port
            self._current_port = None
            if reason is not None:
                self._connect_error = reason

        changed = previous != self._is_connected
        if changed:
            callback = self._connection_state_callback
            if callback:
                try:
                    callback(self._is_connected, event_port, reason)
                except Exception as exc:
                    self.print(f"Connection state callback raised: {exc}")
        return changed

    def _connection_monitor_loop(self):
        """Continuously verify that the connected device is still enumerated by the OS."""
        wait = self._connection_monitor_stop.wait
        while not wait(self._connection_check_interval):
            if self.signalGenerator:
                continue

            if not getattr(self, "_connection_watchdog_enabled", True):
                continue

            if self._is_connected and self._current_port:
                try:
                    available_ports = self.find_port(["USB Serial Device", 'STM32 Virtual ComPort'])
                except Exception as exc:
                    self.print(f"Connection monitor error: {exc}")
                    continue

                if self._current_port not in available_ports:
                    self._handle_connection_lost(RuntimeError("Device disconnected from system."))

    def set_connection_watchdog_enabled(self, enabled: bool):
        self._connection_watchdog_enabled = bool(enabled)

    def connection_watchdog_enabled(self) -> bool:
        return bool(self._connection_watchdog_enabled)

    @property
    def is_connected(self) -> bool:
        return bool(self._is_connected)

    # --- Stimulus/epoch API ---
    def set_stimulus_event_callback(
            self,
            callback: Optional[Callable[[str, StimulusEpoch, int], None]]
    ):
        """Register a callback receiving (event_type, epoch, sample_index)."""
        self._stimulus_event_callback = callback

    def unset_stimulus_event_callback(self):
        self._stimulus_event_callback = None

    def mark_stimulus_on(self, label: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Mark the start of a stimulus; returns the sample index at onset."""
        if not label:
            raise ValueError("Stimulus label is required.")
        with self._stim_lock:
            if self._active_stimulus is not None:
                raise RuntimeError("A stimulus is already active; call mark_stimulus_off() first.")
            start_sample = self.sampleCount
            epoch = StimulusEpoch(label=label, onset_sample=start_sample, metadata=metadata or {})
            self._active_stimulus = epoch
            self._stim_epochs.append(epoch)
        self._emit_stimulus_event("on", epoch, start_sample)
        return start_sample

    def mark_stimulus_off(self, label: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Mark the end of the current stimulus; returns the sample index at offset."""
        with self._stim_lock:
            epoch = self._active_stimulus
            if epoch is None:
                raise RuntimeError("No active stimulus to mark off.")
            if label:
                epoch.label = label
            epoch.offset_sample = self.sampleCount
            if metadata:
                if epoch.metadata:
                    epoch.metadata.update(metadata)
                else:
                    epoch.metadata = metadata
            self._active_stimulus = None
            self._capture_epoch_data(epoch)
            end_sample = epoch.offset_sample
        self._emit_stimulus_event("off", epoch, end_sample)
        return end_sample

    def mark_stimulus_event(self, label: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Record an instantaneous event (onset=offset)."""
        idx = self.mark_stimulus_on(label, metadata)
        self.mark_stimulus_off()
        return idx

    def get_stimulus_epochs(self, reset: bool = False, include_open: bool = False) -> List[Dict[str, Any]]:
        """Return list of epochs as dicts; optionally clear closed epochs."""
        with self._stim_lock:
            epochs = []
            for epoch in self._stim_epochs:
                if epoch.offset_sample is None and not include_open:
                    continue
                epochs.append(epoch.to_dict())
            if reset:
                self._stim_epochs = [e for e in self._stim_epochs if e.offset_sample is None]
        return epochs

    def clear_stimulus_epochs(self):
        """Drop all recorded epochs."""
        with self._stim_lock:
            self._stim_epochs.clear()
            self._active_stimulus = None

    def _emit_stimulus_event(self, event_type: str, epoch: StimulusEpoch, sample_index: int):
        callback = self._stimulus_event_callback
        if callback:
            try:
                callback(event_type, epoch, sample_index)
            except Exception as exc:
                self.print(f"Stimulus callback raised: {exc}")

    def _capture_epoch_data(self, epoch: StimulusEpoch):
        """Attach sample data for the epoch from the rolling buffer."""
        if self._epoch_buffer is None or epoch.offset_sample is None:
            return
        with self._epoch_lock:
            epoch.data = [
                list(sample)
                for sample_idx, sample in self._epoch_buffer
                if epoch.onset_sample <= sample_idx < epoch.offset_sample
            ]

    def _append_epoch_sample(self, sample: List[float]):
        if self._epoch_buffer is None:
            return
        try:
            sample_index = int(sample[0]) if sample else self.sampleCount
        except Exception:
            sample_index = self.sampleCount
        with self._epoch_lock:
            self._epoch_buffer.append((sample_index, list(sample)))

    def connect_async(self, force: bool = False) -> Future:
        with self._io_lock:
            existing = self._connect_future
            if not force and existing and not existing.cancelled():
                if not existing.done():
                    return existing
                if existing.done() and self._is_connected:
                    return self._completed_future(True)
            self.answerToInitFlag = False
            self._connect_error = None
            self._connect_future = self._submit_task(self._connect_impl, name="connect")
            return self._connect_future

    def connect(self, wait: bool = True, force: bool = False):
        future = self.connect_async(force=force)
        if wait:
            return future.result()
        return future

    def reset_device_async(self) -> Future:
        return self.connect_async(force=True)

    def reset_device(self, wait: bool = True):
        future = self.reset_device_async()
        if wait:
            return future.result()
        return future

    def configure_settings_async(self) -> Future:
        # Ensure a connection attempt is queued before applying settings.
        self.connect_async()
        return self._submit_task(self._configure_settings_impl, name="configure_settings")

    def configure_settings(self, wait: bool = True):
        future = self.configure_settings_async()
        if wait:
            return future.result()
        return future

    def start_async(self) -> Future:
        self.connect_async()
        return self._submit_task(self._start_impl, name="start")

    def start(self, wait: bool = True):
        future = self.start_async()
        if wait:
            return future.result()
        return future

    def stop_async(self) -> Future:
        return self._submit_task(self._stop_impl, name="stop")

    def stop(self, wait: bool = True):
        future = self.stop_async()
        if wait:
            return future.result()
        return future

    @property
    def sampling_rate(self):
        return self._samplingRate

    @sampling_rate.setter
    def sampling_rate(self, value):
        if value <= 250:
            self._samplingRate = 250
        elif 250 < value <= 500:
            self._samplingRate = 500
        elif 500 < value <= 1000:
            self._samplingRate = 1000
        else:
            self._samplingRate = 2000

    @property
    def gain(self):
        return self._gain

    @gain.setter
    def gain(self, value):
        if value <= 1:
            self._gain = 1
        elif 1 < value <= 2:
            self._gain = 2
        elif 2 < value <= 4:
            self._gain = 4
        elif 4 < value <= 6:
            self._gain = 6
        elif 6 < value <= 8:
            self._gain = 8
        elif 8 < value <= 12:
            self._gain = 12
        else:
            self._gain = 24

    @property
    def firmware_version(self):
        return 'FirmwareV' + self.firmwareVersion.replace("", ".")[1:-1]

    @property
    def exgain(self):
        return self._exgain

    @exgain.setter
    def exgain(self, value):
        if value <= 1:
            self._exgain = 1
        elif 1 < value <= 2:
            self._exgain = 2
        elif 2 < value <= 4:
            self._exgain = 4
        elif 4 < value <= 6:
            self._exgain = 6
        elif 6 < value <= 8:
            self._exgain = 8
        elif 8 < value <= 12:
            self._exgain = 12
        else:
            self._exgain = 24

    def set_data_ready_callback(self, callback):
        self.data_ready_callback = callback

    def unset_data_ready_callback(self):
        self.data_ready_callback = None

    def set_settings_written_callback(self, callback):
        self.settings_written_callback = callback

    def unset_settings_written_callback(self):
        self.settings_written_callback = None

    def set_signal_generator_mode(self, enabled: bool, faker_data=None):
        """
        Enable/disable the internal signal generator without recreating the Device instance.
        :param enabled: True to enable fake data emission, False to use the hardware.
        :param faker_data: Optional list of samples when a prerecorded IEC file should be replayed.
        """
        enabled = bool(enabled)
        dataset = faker_data if faker_data is not None else []
        previous_state = bool(self.signalGenerator)

        def _safe_stop():
            try:
                self.stop(wait=True)
            except Exception:
                pass

        def _safe_close_serial():
            try:
                future = self._submit_task(lambda: self._close_serial_impl(destroy=True), name="faker-close")
                future.result(timeout=2)
            except Exception:
                pass

        _safe_stop()
        _safe_close_serial()

        if enabled:
            self.signalGenerator = True
            self.faker_data = dataset
            self.signalGeneratingFlag = False
            self.dataGatheringFlag = False
            self.receiveBuffer.clear()
            self.tempBuffer = bytearray()
            self.newDataCount = 0
            self.sampleCount = 0
            self._faker_last_emit = None
            self._faker_sample_residual = 0.0
            self.deviceName = "Fascin8"
            self.firmwareVersion = "1.0.0"
            self.unicID = 1
            self.flashData = 1
            self.chCount = 21
            self.exCount = 3
            self._set_connection_state(False)
            if not previous_state:
                self.print("Signal generator mode enabled.")
            return

        self.signalGenerator = False
        self.faker_data = []
        self.signalGeneratingFlag = False
        self.dataGatheringFlag = False
        self.receiveBuffer.clear()
        self.tempBuffer = bytearray()
        self.newDataCount = 0
        self.sampleCount = 0
        self._faker_last_emit = None
        self._faker_sample_residual = 0.0
        if previous_state:
            self.deviceName = "No Device Found"
            self.firmwareVersion = "0.0.0"
            self.unicID = "No Data"
            self.flashData = "No Data"
            self.chCount = 8
            self.exCount = 0
        self._set_connection_state(False)
        if previous_state:
            self.print("Signal generator mode disabled.")

    def print(self, *args, sep=' ', end='\n', file=None):
        if self.__DEBUG_MODE:
            if args:
                if self.__PREV_END == '\n':
                    print("NeuroPort:", end='')

                print(*args, sep=sep, end=end, file=file)
            else:
                print(end=end, file=file)

            self.__PREV_END = end

    def find_port(self, desc):
        suspect_coms = []

        if self.signalGenerator:
            return ["faker"]

        for port in list_ports.comports():
            try:
                for d in desc:
                    if d.lower() in port.description.lower():

                        if platform.system() == 'Darwin' and not port.name.startswith('/dev/tty.'):
                            dummyport = port.name.split(".")[1]
                            port1 = '/dev/tty.' + dummyport
                        else:
                            port1 = port.name

                        suspect_coms.append(port1)
                        break
            except Exception as e:
                self.print(e)

        return suspect_coms

    def set_buffer(self):
        self.sendBuffer[0] = ord('U')
        self.sendBuffer[1] = ord('8')
        self.sendBuffer[2] = ord('_')
        self.sendBuffer[3] = ord('s')
        self.sendBuffer[4] = ord('T')
        self.sendBuffer[5] = ord('8')
        self.sendBuffer[6] = ord(' ')
        self.sendBuffer[7] = ord('C')  # SRB1 connected  to all Nchs
        self.sendBuffer[8] = 0x01  # Bias Derivation to 3-0 Pchs 0xD Register ADS
        self.sendBuffer[9] = 0x03  # Bias Derivation to 7-4 Pchs 0xE Register ADS
        self.sendBuffer[10] = 0x0E  # Bias Derivation to 3-0 Nchs 0xD Register ADS
        self.sendBuffer[11] = 0x0D  # Bias Derivation to 7-4 Nchs 0xE Register ADS
        self.sendBuffer[12] = 0x60  # Channel 1 Setting
        self.sendBuffer[13] = 0x60  # Channel 2 Setting
        self.sendBuffer[14] = 0x60  # Channel 3 Setting
        self.sendBuffer[15] = 0x60  # Channel 4 Setting
        self.sendBuffer[16] = 0x60  # Channel 5 Setting
        self.sendBuffer[17] = 0x60  # Channel 6 Setting
        self.sendBuffer[18] = 0x60  # Channel 7 Setting
        self.sendBuffer[19] = 0x60  # Channel 8 Setting
        self.sendBuffer[20] = ord(' ')
        self.sendBuffer[21] = ord(' ')
        self.sendBuffer[22] = ord(' ')
        self.sendBuffer[23] = ord(' ')
        self.sendBuffer[24] = ord(' ')
        self.sendBuffer[25] = ord(' ')
        self.sendBuffer[26] = ord(' ')
        self.sendBuffer[27] = ord(' ')
        self.sendBuffer[28] = ord(' ')
        self.sendBuffer[29] = ord(' ')
        self.sendBuffer[30] = ord(' ')
        self.sendBuffer[31] = ord('V')

    def _connect_impl(self):
        if self._is_connected:
            self._set_connection_state(False)
        self._connect_error = None
        self._current_port = None
        self.answerToInitFlag = False
        self.settingModeFlag = False

        if self.dataGatheringFlag:
            return False

        # Refresh the list of available ports on each connection attempt.
        self.ports = self.find_port(["USB Serial Device", 'STM32 Virtual ComPort'])

        if self.signalGenerator:
            self.deviceName = "Fascin8"
            self.firmwareVersion = "1.0.0"
            self.unicID = 1
            self.flashData = 1
            self.chCount = 21
            self.exCount = 3

            self.print("Signal generator activated ...")
            self._set_connection_state(True, port="faker")
            return True

        if self.ports:
            self.print("Checking all COM ports ...")

            for port in self.ports:
                self.print("Try to connect to port {}".format(port))

                max_attempts = 5
                serial_created = False
                for attempt in range(1, max_attempts + 1):
                    try:
                        self._serial = Serial(port, timeout=2)
                        serial_created = True
                        break
                    except SerialException as e:
                        self.print("Can't connect to port {} on attempt {}/{}: {}".format(port, attempt, max_attempts, e))
                        self._close_serial_impl(destroy=True)
                        if attempt < max_attempts:
                            sleep(1.0)
                if not serial_created:
                    continue

                self.print("Port {} accepted, Try to Handshake".format(port))

                try:
                    self.print("Send a reset command to the device")
                    self.sendBuffer[3] = ord('R')
                    self.print('sendBuffer:', self.sendBuffer)
                    self._serial.write(self.sendBuffer)
                    self._close_serial_impl()
                except SerialException as e:
                    self.print("Can't connect to this COM port: {}".format(e))
                    self._close_serial_impl(destroy=True)
                    continue

                self.print("Wating for device to reinitializing...")
                failed_flag = False
                max_retries = 10
                retry_count = 0

                while True:
                    try:
                        if not self._serial.is_open:
                            self._serial.open()
                        sleep(1)
                        break
                    except SerialException:
                        retry_count += 1
                        if retry_count > max_retries:
                            failed_flag = True
                            break
                        else:
                            sleep(1)
                            self.print("Waiting for device connected to " + port + " to restart...")

                if failed_flag:
                    self.print("Timeout exceeded while waiting for device to restart")
                    self._close_serial_impl(destroy=True)
                    continue

                self.start_data_received_thread()

                try:
                    self.print("Sending handshake setting to device")
                    self.sendBuffer[3] = ord('s')  # setting mode
                    self.print('sendBuffer:', self.sendBuffer)

                    if not self._serial.is_open:
                        self._serial.open()
                        sleep(.2)
                    self._serial.write(self.sendBuffer)
                except SerialException as e:
                    self.print("Error sending handshake setting: {}".format(e))
                    self._close_serial_impl(destroy=True)
                    continue

                self.print("Waiting for device to respond...")

                failed_flag = False
                max_retries = 10
                retry_count = 0
                while not self.answerToInitFlag:
                    if retry_count < max_retries:
                        retry_count += 1
                        sleep(1)
                    else:
                        failed_flag = True
                        break

                if failed_flag:
                    self.print("Exceeded maximum number of retries. Aborting...")
                    self._close_serial_impl(destroy=True)
                    continue

                self.print("Device is Connected on", port)
                self._set_connection_state(True, port=port)
                self._close_serial_impl()
                return True

            message = "No I8Devices found"
            self.print(message)
            self._connect_error = RuntimeError(message)
            raise self._connect_error
        else:
            message = "No serial ports available"
            self.print(message)
            self._connect_error = RuntimeError(message)
            raise self._connect_error

    def _close_serial_impl(self, destroy=False):
        try:
            self.stop_data_received_thread()

            if self.signalGenerator:
                return

            if self._serial and self._serial.is_open:
                self._serial.close()
                sleep(1)
        except SerialException as e:
            self.print("An error occurred on closing port: {}".format(e))

        if destroy:
            self._serial = None

    def _handle_connection_lost(self, exc=None):
        if exc:
            self.print(f"Serial connection lost: {exc}")
        else:
            self.print("Serial connection lost.")
        reason = exc or RuntimeError("Serial connection lost.")
        last_port = self._current_port
        self._set_connection_state(False, port=last_port, reason=reason)
        self.dataGatheringFlag = False
        self.signalGeneratingFlag = False
        self.answerToInitFlag = False
        self.settingModeFlag = False
        self.stop_event.set()

    def start_data_received_thread(self):
        if self.data_received_thread is None:
            self.stop_event.clear()
            self.data_received_thread = threading.Thread(target=self.data_received_listener)
            self.data_received_thread.daemon = True
            self.data_received_thread.start()
            return True
        return False

    def stop_data_received_thread(self):
        if self.data_received_thread is not None:
            self.stop_event.set()
            self.data_received_thread.join()
            self.data_received_thread = None
            print("Data received thread stopped.")

    def data_received_listener(self):
        while not self.stop_event.is_set():
            try:
                if self.signalGenerator:
                    if self.signalGeneratingFlag:
                        self.signal_generator_received()
                elif self._serial and self._serial.is_open:
                    try:
                        waiting = self._serial.in_waiting
                    except SerialException as exc:
                        raise exc
                    if waiting > 0:
                        if not self.answerToInitFlag:
                            rec_data = bytearray(self._serial.read(32))
                            self.init_mode_received(rec_data)
                        elif self.settingModeFlag:
                            rec_data = bytearray(self._serial.read(32))
                            self.setting_mode_received(rec_data)
                        elif self.dataGatheringFlag:
                            self.tempBuffer.extend(self._serial.read(waiting))
                            self.data_mode_received()
                sleep(1 / 200)
            except (SerialException, OSError) as exc:
                self._handle_connection_lost(exc)
                break
            except Exception as exc:
                self.print(str(exc))
                break

    def init_mode_received(self, rec_data):
        if rec_data[31] == 144:  # Indicate I8Device ID
            sleep(0.5)
            if rec_data[27] == 48:  # Indicate Fascin8 device
                self.deviceName = "Fascin8"
                self.firmwareVersion = str(rec_data[24])
                self.unicID = str((256 * rec_data[25]) + rec_data[26])
                self.flashData = str(rec_data[28]) + str(rec_data[29]) + str(rec_data[30])
                self.chCount = 21
                self.exCount = 3
            elif rec_data[27] == 47:  # Indicate Ultim8 device
                self.deviceName = "Ultim8"
                self.firmwareVersion = str(rec_data[24])
                self.unicID = str((256 * rec_data[25]) + rec_data[26])
                self.flashData = self.convert_bytes(rec_data[28], rec_data[29], rec_data[30])
                self.chCount = 8
                self.exCount = 0
            self.answerToInitFlag = True

    def setting_mode_received(self, rec_data):
        if rec_data[31] == 144:  # Indicate I8Device ID
            sleep(0.5)
            if rec_data[27] == 48:  # Indicate Fascin8 device
                self.print("Fascin8 writing setting done successfully.")

                c = 0
                self.print("Chip Registers (see datasheet):")
                for b in rec_data:
                    self.print(f"     {c:02X}- {b:02X}")
                    c += 1
                    if c > 23:
                        break

            elif rec_data[27] == 47:  # Indicate Ultim8 device
                self.print("Ultim8 writing setting done successfully.")

                c = 0
                self.print("Chip Settings:")
                for b in rec_data:
                    self.print(f"{c:02X}- {b:02X}")
                    c += 1
                    if c > 23:
                        break

            self.settingModeFlag = False

    def data_mode_received(self):
        try:
            if self.deviceName == "Fascin8":
                while len(self.tempBuffer) >= 80:
                    received = self.tempBuffer[:80]
                    self.tempBuffer = self.tempBuffer[80:]

                    converted = [0] * 26
                    converted[0] = self.sampleCount  # firmware sample count
                    # converted[0] = self.convert_bytes(received[0], received[1], received[2])  # firmware sample count

                    i, p = 1, 8  # i = converted position, p = input data position
                    for k in range(i + 3, i + 24):  # Data channels
                        n = 3 * (k - i) + p
                        # create data from byte and then convert to uV
                        converted[k - 3] = self.convert_bytes(received[n], received[n + 1], received[n + 2]) * 0.536

                    for k in range(i, i + 3):  # Extra channels
                        n = 3 * (k - i) + p
                        # create data from byte and then convert to uV
                        converted[k + 21] = self.convert_bytes(received[n], received[n + 1], received[n + 2]) * 0.536

                    converted[25] = received[4]  # user input keys

                    self.receiveBuffer.append(converted)
                    self._append_epoch_sample(converted)
                    self.sampleCount += 1
                    self.newDataCount += 1

                    if self.data_ready_callback:
                        self.data_ready_callback(self.get_data())
            elif self.deviceName == "Ultim8":
                while len(self.tempBuffer) >= 26:
                    received = self.tempBuffer[:26]
                    self.tempBuffer = self.tempBuffer[26:]

                    if received[25] == 47:
                        converted = [0] * 9
                        converted[0] = self.sampleCount  # firmware sample count

                        i = 1
                        for k in range(i, 8 + i):
                            n = 3 * (k - i)
                            converted[k] = self.convert_bytes(received[n], received[n + 1], received[n + 2])
                            converted[k] *= 0.536

                        self.receiveBuffer.append(converted)
                        self._append_epoch_sample(converted)
                        self.sampleCount += 1
                        self.newDataCount += 1

                        if self.data_ready_callback:
                            self.data_ready_callback(self.get_data())
                    else:
                        self.print("Something is wrong!")
        except Exception as e:
            self.print(e)
            self.print("Port is not open?")

    def signal_generator_received(self):
        if not self.signalGeneratingFlag or not self.dataGatheringFlag:
            sleep(0.01)
            return

        sr = max(self.sampling_rate, 1)
        now = time()
        if self._faker_last_emit is None:
            self._faker_last_emit = now
            return

        elapsed = max(0.0, now - self._faker_last_emit)
        total_samples = self._faker_sample_residual + (elapsed * sr)
        sample_count = int(total_samples)
        self._faker_sample_residual = total_samples - sample_count
        self._faker_last_emit = now

        if sample_count <= 0:
            return

        try:
            samples = self._next_fake_samples(sample_count)
            if not samples:
                return

            seq_start = self.sampleCount
            for offset, sample in enumerate(samples):
                sample.insert(0, seq_start + offset)

            self.receiveBuffer.extend(samples)
            for sample in samples:
                self._append_epoch_sample(sample)
            emitted = len(samples)
            self.sampleCount += emitted
            self.newDataCount += emitted

            if self.data_ready_callback:
                self.data_ready_callback(self.get_data())

            self.print(f"Sending simulated samples. {emitted}")
        except Exception as e:
            self.print('Error in signal generator,', str(e))
            sleep(0.05)

    def _next_fake_samples(self, count):
        if count <= 0:
            return []

        if self.faker_data:
            total = len(self.faker_data)
            if total == 0:
                return []

            start_index = self.sampleCount % total
            block = []
            for i in range(count):
                block.append(list(self.faker_data[(start_index + i) % total]))
            return block

        return [[random.randint(0, 18000) for _ in range(25)] for _ in range(count)]

    def convert_bytes(self, byte1, byte2, byte3):
        value = (byte1 << 16) | (byte2 << 8) | byte3
        return self.twos_complement(value, 24)

    @staticmethod
    def twos_complement(value, bits):
        if (value & (1 << (bits - 1))) != 0:
            value = value - (1 << bits)
        return value

    def _configure_settings_impl(self):
        self.settingModeFlag = True

        self.print("Sampling rate=", self.sampling_rate)
        self.print("Test Mode=", self.testSignal)
        self.print("linked_ear Mode=", self.linkedEar)
        self.print("Lead off=", self.leadoffMode)
        self.print("Gain=", self.gain)
        self.print("Extera Gain=", self.exgain)
        self.print("Channels on/off (1 to 24):", end=' ')
        for channel in self.channelsOn:
            self.print(" ", int(channel), end=' ')
        self.print()
        self.print("Extra Channels on/off (1 to 3):", end=' ')
        for channel in self.exchannelsOn:
            self.print(" ", int(channel), end=' ')
        self.print()

        if self.signalGenerator:
            if self.settings_written_callback:
                self.settings_written_callback(True, 'Signal Generator')

            return True

        self.sendBuffer[3] = ord('s')  # Enter setting mode
        self.sendBuffer[4] = ord('T') if self.testSignal else ord('n')  # Test signal enable/disable
        self.sendBuffer[5] = ord('0') + (self.sampling_rate // 250)  # Sampling rate (1=250, 2=500, 4=1000, 8=2000)
        self.sendBuffer[6] = ord('L') if self.leadoffMode else ord(' ')  # Lead-off enable/disable
        self.sendBuffer[7] = ord('C')  # SRB1 connected to all Nchs

        self.sendBuffer[8] = self.gain  # Regular channel gain
        self.sendBuffer[9] = self.exgain  # Extra channel gain

        self.sendBuffer[10] = ord('I') if self.linkedEar else ord('n')  # Linked ear mode
        self.sendBuffer[11] = 0x00  # Reserved
        self.sendBuffer[12] = 0x00  # Reserved
        self.sendBuffer[13] = 0x00  # Reserved
        self.sendBuffer[14] = 0x00  # Reserved

        # Convert channels_on and exchannels_on to bytes
        # ch_data = bytearray(0)
        # for ch in self.channelsOn:
        #     ch_data.append(int(ch))
        self.sendBuffer[15] = 0xFF  # Channels 1 to 8 on/off status
        self.sendBuffer[16] = 0xFF  # Channels 9 to 16 on/off status
        self.sendBuffer[17] = 0xFF  # Channels 17 to 24 on/off status

        # exch_data = bytearray(0)
        # for ch in self.exchannelsOn:
        #     exch_data.append(int(ch))
        self.sendBuffer[18] = 0x00  # Extra channels 1 to 8 on/off status

        self.sendBuffer[19] = 0x00  # Reserved

        self.sendBuffer[20] = int(self.interaction[0])  # User interaction module settings
        self.sendBuffer[21] = int(self.interaction[1])  # User interaction module settings
        self.sendBuffer[22] = int(self.interaction[2])  # User interaction module settings
        self.sendBuffer[23] = int(self.interaction[3])  # User interaction module settings

        try:
            self._serial.open()
            self.start_data_received_thread()
            self.print('sendBuffer:', self.sendBuffer)
            self._serial.write(self.sendBuffer)
        except Exception as e:
            self.print(e)

            if self.settings_written_callback:
                self.settings_written_callback(False, str(e))

            return False

        try:
            self.print("Waiting for device to send back acknowledge about write setting ...")

            while self.settingModeFlag:
                pass

            self._close_serial_impl()

            if self.settings_written_callback:
                self.settings_written_callback(True, '')

            return True
        except Exception as e:
            self.print(e)

            if self.settings_written_callback:
                self.settings_written_callback(False, str(e))

            return False

    def get_status(self, val="all"):
        self.print("Gathering Mode(mode):", self.dataGatheringFlag)
        self.print("sample_count(cnt):", self.sampleCount)
        self.print("Buffer Length(buff_len):", self.newDataCount)

        if val == "mode":
            return self.dataGatheringFlag
        elif val == "cnt":
            return self.sampleCount
        elif val == "buff_len":
            return self.newDataCount
        elif val == "all":
            status = {
                "mode": self.dataGatheringFlag,
                "cnt": self.sampleCount,
                "buff_len": self.newDataCount
            }
            return status

        self.print("Not a valid input for getStatus")
        return "nothing to respond"

    def _start_impl(self):
        if self.signalGenerator:
            self.print("Starting signal generating ...")
            self.receiveBuffer.clear()
            self.tempBuffer = bytearray()
            self.newDataCount = 0
            self.data = [[] for _ in range(self.chCount + self.exCount + 2)]
            self.dataGatheringFlag = True
            self.sampleCount = 0
            self._faker_last_emit = time()
            self._faker_sample_residual = 0.0
            self.signalGeneratingFlag = True
            self.start_data_received_thread()
            return True

        if self.deviceName != "No Device Found":
            if not self.dataGatheringFlag:
                self.receiveBuffer.clear()
                self.tempBuffer = bytearray()
                self.newDataCount = 0
                self.data = [[] for _ in range(self.chCount + self.exCount + 2)]
                self.dataGatheringFlag = True
                self.print("Starting data gathering ...")
                self.sampleCount = 0

                try:
                    if not self._serial:
                        raise SerialException("Serial port is not available.")
                    if not self._serial.is_open:
                        self._serial.open()
                    self.start_data_received_thread()

                    self.sendBuffer[3] = ord('B')  # start mode
                    self.print('sendBuffer:', self.sendBuffer)
                    self._serial.write(self.sendBuffer)
                except SerialException as exc:
                    self.print(f"Failed to start data gathering: {exc}")
                    self._handle_connection_lost(exc)
                    self._close_serial_impl(destroy=True)
                    self.dataGatheringFlag = False
                    return False
                return True

            self.print("The device is already in data gathering mode!")
            return False

        self.print("No device connected to start data gathering!")
        return False

    def _stop_impl(self):
        if self.signalGenerator:
            self.print("Signal generating stoped ...")
            self.signalGeneratingFlag = False
            self.dataGatheringFlag = False
            self.newDataCount = 0
            self.receiveBuffer.clear()
            self._faker_last_emit = None
            self._faker_sample_residual = 0.0
            self._close_serial_impl()
            return 0

        if self.deviceName != "No Device Found":
            if self.dataGatheringFlag:
                wait_until = time() + 1.0
                while self.sampleCount < 10 and time() < wait_until and not self.stop_event.is_set():
                    sleep(0.01)
                self.dataGatheringFlag = False

                serial_available = self._serial and getattr(self._serial, "is_open", False)
                if serial_available:
                    try:
                        self.sendBuffer[3] = ord('E')  # stop mode
                        self.print('sendBuffer:', self.sendBuffer)
                        self._serial.write(self.sendBuffer)

                        try:
                            pending = self._serial.in_waiting
                        except SerialException:
                            pending = 0
                        if pending:
                            self.tempBuffer.extend(self._serial.read(pending))
                            self.data_mode_received()
                    except SerialException as exc:
                        self.print("Error while stopping data gathering: {}".format(exc))
                        self._handle_connection_lost(exc)

                self._close_serial_impl(destroy=not serial_available)

                self.print("Data gathering has been finished.")
                return self.sampleCount

            self.print("The device was not in data gathering mode to stop it, please call 'start' method first.")
            return -1

        self.print("No device connected! Data gathering will remain unfinished :(")
        return -2

    def get_data(self):
        if self.dataGatheringFlag:
            if self.chunk == 0:
                while self.newDataCount == 0:
                    pass

                self.newDataCount = 0
                result = self.receiveBuffer.copy()
                self.receiveBuffer.clear()
                self.print(f"Sending all buffered samples. {len(result)}")
            elif self.newDataCount < self.chunk:
                while self.newDataCount < self.chunk:
                    pass

                self.newDataCount = 0
                result = self.receiveBuffer.copy()
                self.receiveBuffer.clear()
                self.print(f"Sending all buffered samples with size of '{self.chunk}' that you asked for.")
            else:
                result = self.receiveBuffer[-self.chunk:]
                self.receiveBuffer.clear()
                self.newDataCount = 0
                self.print(f"Sending last {self.chunk} sample(s).")
        elif self.newDataCount > 0:
            if self.chunk == 0:
                result = self.receiveBuffer.copy()
                self.receiveBuffer.clear()
                self.newDataCount = 0
                self.print("Sending all buffered samples.")
            elif self.newDataCount >= self.chunk:
                result = self.receiveBuffer[-self.chunk:]
                self.receiveBuffer.clear()
                self.newDataCount = 0
                self.print(f"Sending last {self.chunk} sample(s).")
            else:
                self.print("Device is not in gathering mode "
                           "and the receive buffer contains fewer samples than you requested.")
                result = []
        else:
            self.print("Device is not in gathering mode and the receive buffer is empty too.")
            result = []

        return result
