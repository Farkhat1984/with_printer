import textwrap
import serial
import serial.tools.list_ports
import qrcode
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ThermalPrinter:
    def __init__(self, port: Optional[str] = None, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.printer = None
        self.connected = False

        # Settings for 80mm printer
        self.chars_per_line = {
            'font_a': 42,  # Font A (12×24) - standard
            'font_b': 56  # Font B (9×17) - compact
        }
        self.current_font = 'font_a'

    @staticmethod
    def get_available_ports() -> List[Dict[str, str]]:
        """Get list of available ports"""
        return [
            {'port': port.device, 'description': port.description}
            for port in serial.tools.list_ports.comports()
        ]

    def connect(self) -> bool:
        """Establish connection with the printer"""
        try:
            if not self.port:
                available_ports = serial.tools.list_ports.comports()
                if not available_ports:
                    raise ConnectionError("No available serial ports found")
                self.port = available_ports[0].device

            self.printer = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=2
            )
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to printer: {str(e)}")
            self.connected = False
            return False

    def wrap_text(self, text: str, width: Optional[int] = None) -> str:
        """Wrap long text into multiple lines"""
        if width is None:
            width = self.chars_per_line[self.current_font]
        return textwrap.fill(text, width=width)

    def format_product_line(self, name: str, qty: str, price: str, total: str) -> List[str]:
        """Format product line with wrapping"""
        font_width = self.chars_per_line[self.current_font]
        name_width = font_width - 20  # Reserve space for quantity, price and total

        if len(name) > name_width:
            wrapped_name = textwrap.wrap(name, width=name_width)
            lines = []
            first_line = True
            for name_part in wrapped_name:
                if first_line:
                    lines.append(f"{name_part:<{name_width}} {qty:>3} {price:>8} {total:>8}")
                    first_line = False
                else:
                    lines.append(f"{name_part:<{font_width}}")
            return lines
        else:
            return [f"{name:<{name_width}} {qty:>3} {price:>8} {total:>8}"]

    def print_invoice(self, invoice_data: Dict[str, Any]) -> bool:
        """Print invoice on thermal printer"""
        if not self._validate_invoice_data(invoice_data):
            logger.error("Invalid invoice data")
            return False

        try:
            if not self.connected and not self.connect():
                return False

            # Initialize printer commands
            self._send_command(b'\x1B\x40')  # Initialize printer

            # Set alignment center and double size for header
            self._send_command(b'\x1B\x61\x01')  # Center alignment
            self._send_command(b'\x1D\x21\x11')  # Double width and height
            self._print_text('НАКЛАДНАЯ\n\n')

            # Reset text size and set left alignment
            self._send_command(b'\x1D\x21\x00')  # Normal size
            self._send_command(b'\x1B\x61\x00')  # Left alignment

            # Print invoice details
            self._print_text(f"Номер: {invoice_data.get('id', '')}\n")
            self._print_text(f"Дата: {invoice_data.get('created_at', '').split('T')[0]}\n")
            self._print_text(f"Контакт: {invoice_data.get('contact', '')}\n")
            self._print_text('-' * self.chars_per_line['font_a'] + '\n')

            # Print items
            self._print_items(invoice_data.get('items', []))

            # Print totals
            self._print_totals(invoice_data)

            # Print QR code if invoice ID exists
            if invoice_data.get('id'):
                self._print_qr_code(invoice_data['id'])

            # Cut paper
            self._send_command(b'\x1D\x56\x41')  # Full cut with feed
            return True

        except Exception as e:
            logger.error(f"Error printing invoice: {str(e)}")
            return False

    def _validate_invoice_data(self, invoice_data: Dict[str, Any]) -> bool:
        """Validate invoice data structure"""
        required_fields = ['id', 'created_at', 'items', 'total']
        return all(field in invoice_data for field in required_fields)

    def _send_command(self, command: bytes) -> None:
        """Send raw command to printer"""
        if self.printer and self.printer.is_open:
            self.printer.write(command)

    def _print_text(self, text: str) -> None:
        """Print text with proper encoding"""
        if self.printer and self.printer.is_open:
            self.printer.write(text.encode('cp866'))

    def _print_items(self, items: List[Dict[str, Any]]) -> None:
        """Print invoice items"""
        self._print_text("Наименование                      Кол.  Цена     Сумма\n")
        self._print_text('-' * self.chars_per_line['font_b'] + '\n')

        for item in items:
            name = item.get('name', '')
            qty = str(item.get('quantity', ''))
            price = f"{float(item.get('price', 0)):.2f}"
            total = f"{float(item.get('quantity', 0)) * float(item.get('price', 0)):.2f}"

            lines = self.format_product_line(name, qty, price, total)
            for line in lines:
                self._print_text(line + '\n')

    def _print_totals(self, invoice_data: Dict[str, Any]) -> None:
        """Print invoice totals"""
        self._print_text('-' * self.chars_per_line['font_b'] + '\n')
        self._send_command(b'\x1B\x61\x02')  # Right alignment
        self._print_text(f"Итого: {invoice_data.get('total', 0):.2f}\n")

        payment_status = "Оплачено" if invoice_data.get('is_paid', False) else "Не оплачено"
        self._print_text(f"Статус оплаты: {payment_status}\n\n")

    def _print_qr_code(self, invoice_id: str) -> None:
        """Print QR code for invoice"""
        qr = qrcode.QRCode(version=1, box_size=2)
        qr.add_data(f"invoice_id:{invoice_id}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Convert QR image to printer bitmap format
        # Implementation depends on your printer's specific requirements
        # This is a placeholder for the actual implementation
        pass

    def close(self) -> None:
        """Close printer connection"""
        if self.printer:
            try:
                self.printer.close()
            except Exception as e:
                logger.error(f"Error closing printer connection: {str(e)}")
            finally:
                self.printer = None
                self.connected = False