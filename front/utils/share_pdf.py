import os
from utils.pdf_generator import InMemoryPDFGenerator
from kivy.utils import platform
from views.popup_view import MessagePopup


class PDFManager:
    def __init__(self):
        self.pdf_generator = InMemoryPDFGenerator()
        self.platform = platform

    def share_invoice(self, invoice_data):
        try:
            if not invoice_data["items"]:
                MessagePopup.show_message("Ошибка: накладная пуста")
                return

            # Генерируем PDF в памяти
            pdf_buffer = self.pdf_generator.generate_pdf_in_memory(invoice_data)
            pdf_buffer.seek(0)

            # Создаем временный файл
            temp_dir = os.path.join(os.path.expanduser('~'), '.temp_invoices')
            os.makedirs(temp_dir, exist_ok=True)
            temp_file = os.path.join(temp_dir, f'invoice_{os.getpid()}.pdf')

            with open(temp_file, 'wb') as f:
                f.write(pdf_buffer.getvalue())

            if platform == 'android':
                self._share_file_android(temp_file)

            # Удаляем временный файл
            def cleanup_temp_file():
                try:
                    os.remove(temp_file)
                except:
                    pass

            from threading import Timer
            Timer(60, cleanup_temp_file).start()

        except Exception as e:
            MessagePopup.show_message(f"Ошибка при отправке накладной: {str(e)}")

    def _share_file_android(self, file_path):
        try:
            from jnius import autoclass, cast

            File = autoclass('java.io.File')
            Uri = autoclass('android.net.Uri')
            Intent = autoclass('android.content.Intent')
            FileProvider = autoclass('androidx.core.content.FileProvider')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            activity = PythonActivity.mActivity

            file = File(file_path)
            file_uri = FileProvider.getUriForFile(
                activity,
                str(activity.getApplicationContext().getPackageName()) + ".fileprovider",
                file
            )

            intent = Intent()
            intent.setAction(Intent.ACTION_SEND)
            intent.setType("application/pdf")
            intent.putExtra(Intent.EXTRA_STREAM, file_uri)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)

            chooser = Intent.createChooser(intent, "Отправить накладную через...")
            activity.startActivity(chooser)

        except Exception as e:
            MessagePopup.show_message(f"Ошибка при отправке файла: {str(e)}")