from typing import Dict, Any, List
from utils.share_pdf import PDFManager
from utils.printer_manager import ThermalPrinter, logger  # Updated import to use our optimized class


class InvoiceActionsMixin:
    """Mixin for invoice-related actions"""

    def __init__(self):
        self.invoice_manager = PDFManager()
        self.printer = ThermalPrinter()  # Direct instantiation of ThermalPrinter

    def _collect_invoice_data(self) -> Dict[str, Any]:
        """Collect invoice data from the current context"""
        raise NotImplementedError("Subclasses must implement _collect_invoice_data()")

    def share_invoice(self) -> None:
        """Share invoice as PDF"""
        try:
            invoice_data = self._collect_invoice_data()
            self.invoice_manager.share_invoice(invoice_data)
        except Exception as e:
            logger.error(f"Error sharing invoice: {str(e)}")

    def print_invoice(self) -> None:
        """Print invoice on thermal printer"""
        try:
            invoice_data = self._collect_invoice_data()

            # Connect printer if not already connected
            if not self.printer.connected:
                if not self.printer.connect():
                    logger.error("Failed to connect to printer")
                    return

            if self.printer.print_invoice(invoice_data):
                logger.info("Invoice successfully sent to printer")
            else:
                logger.error("Error printing invoice")
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            self.printer.close()

    @staticmethod
    def get_available_printers() -> List[Dict[str, str]]:
        """Get list of available printers"""
        return ThermalPrinter.get_available_ports()