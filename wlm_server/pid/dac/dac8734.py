"""Module for DAC8734 controlled via an ArtyS7 FPGA."""

import serial
from qcodes_driver.AD9912.ArtyS7 import ArtyS7

from .base import BaseDAC

class DAC8734(BaseDAC):
    """DAC8734 controlled via an ArtyS7 FPGA.
    
    Constants:
        NUM_CHANNELS: Number of channels on the DAC8734.
        VREF: Reference voltage for voltage-to-code conversion in V.
        MIN_V: Minimum allowed output voltage in V.
        MAX_V: Maximum allowed output voltage in V.
    """

    NUM_CHANNELS = 8
    VREF = 2.5
    MIN_V, MAX_V = 0, 2.5

    def __init__(self, port: str):
        """Extended."""
        super().__init__(port)
        self._fpga: ArtyS7 | None = None

    def open(self):
        """Overridden."""
        if self._is_open:
            print(f'DAC8734 on {self._port} is already open')
            return
        try:
            self._fpga = ArtyS7(self._port)
        except serial.SerialException as e:
            print(f'Failed to open DAC8734: {e}')
        else:
            self._is_open = True

    def close(self):
        """Overridden."""
        if not self._is_open:
            print(f'DAC8734 on {self._port} is not open')
            return
        self._fpga.close()
        self._fpga = None
        self._is_open = False

    def set_voltage(self, channel: int, voltage: float):
        """Overridden."""
        if not 0 <= channel < self.NUM_CHANNELS:
            print(f'Invalid channel: {channel}')
            return
        if voltage < self.MIN_V or voltage > self.MAX_V:
            print(f'Voltage out of range: {voltage}')
            return
        code = self._volts_to_code(voltage)
        dac_number = channel // 4
        dac_channel = channel % 4
        self._fpga.send_mod_BTF_int_list([
            1 << dac_number,
            0x04 + dac_channel,
            code // 256,
            code % 256,
        ])
        self._fpga.send_command('WRITE REG')
        self._fpga.send_command('LDAC')

    def _volts_to_code(self, voltage: float) -> int:
        """Converts voltage to DAC code.
        
        Args:
            voltage: Target voltage in V.
        
        Returns:
            DAC code (0-65535).
        """
        raw = int((65536 / (4 * self.VREF)) * voltage)
        return min(max(raw, 0), 65535)
