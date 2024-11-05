from datetime import datetime
import os
import textwrap


class PrinterEmulator:
    """Эмулятор термопринтера для предварительного просмотра чека в текстовом виде"""

    def __init__(self, width=42):
        self.width = width  # Стандартная ширина для Font A
        self.buffer = []  # Буфер для хранения строк
        self.current_align = 'left'
        self.current_font = 'a'
        self.current_width = 1
        self.current_height = 1

        # Символы для визуального оформления
        self.decorators = {
            'header': '=',  # Для заголовков
            'separator': '-',  # Для разделителей
            'cut': '▼',  # Символ обрезки чека
            'double': '█'  # Для двойной высоты текста
        }

    def clear(self):
        """Очистка буфера печати"""
        self.buffer = []

    def text(self, text):
        """
        Добавление текста в буфер с учетом текущего форматирования
        """
        if not text:
            self.buffer.append('')
            return

        lines = text.rstrip('\n').split('\n')

        for line in lines:
            formatted_line = line

            # Применяем выравнивание
            if self.current_align == 'center':
                formatted_line = formatted_line.center(self.width)
            elif self.current_align == 'right':
                formatted_line = formatted_line.rjust(self.width)
            elif self.current_align == 'left':
                formatted_line = formatted_line.ljust(self.width)

            # Эмуляция двойной ширины/высоты
            if self.current_width == 2 or self.current_height == 2:
                self.buffer.append(self.decorators['double'] * self.width)
                self.buffer.append(formatted_line)
                self.buffer.append(self.decorators['double'] * self.width)
            else:
                self.buffer.append(formatted_line)

    def set(self, align='left', font='a', width=1, height=1):
        """Установка параметров форматирования"""
        self.current_align = align
        self.current_font = font
        self.current_width = width
        self.current_height = height
        # Изменяем ширину в зависимости от шрифта
        self.width = 56 if font == 'b' else 42

    def cut(self):
        """Эмуляция обрезки чека"""
        self.buffer.append(self.decorators['cut'] * self.width)

    def control(self, command):
        """Эмуляция управляющих команд"""
        if command == 'LF':
            self.buffer.append('')

    def hw(self, command):
        """Эмуляция аппаратных команд"""
        if command == 'init':
            self.clear()


class ThermalPrinterEmulator:
    """Эмулятор термопринтера с расширенными возможностями форматирования"""

    def __init__(self, paper_width=42):
        self.printer = PrinterEmulator(width=paper_width)
        self.chars_per_line = {
            'font_a': 42,  # Font A (12×24) - стандартный
            'font_b': 56  # Font B (9×17) - компактный
        }
        # Настройки колонок для таблицы товаров (для font_b)
        self.column_widths = {
            'name': 32,  # Наименование
            'qty': 5,  # Количество
            'price': 9,  # Цена
            'total': 10  # Сумма
        }
        self.current_font = 'font_a'

    def wrap_text(self, text, width=None):
        """Перенос текста с сохранением форматирования"""
        if width is None:
            width = self.chars_per_line[self.current_font]
        return textwrap.wrap(
            text,
            width=width,
            expand_tabs=False,
            replace_whitespace=False,
            drop_whitespace=False,
            break_long_words=True,
            break_on_hyphens=True
        )

    def format_product_line(self, name, qty, price, total):
        """Форматирование строки товара с учетом переноса"""
        name_width = self.column_widths['name']
        qty_str = f"{qty:>{self.column_widths['qty']}}"
        price_str = f"{price:>{self.column_widths['price']}.2f}"
        total_str = f"{total:>{self.column_widths['total']}.2f}"

        lines = []
        wrapped_name = self.wrap_text(name, width=name_width)

        for i, name_part in enumerate(wrapped_name):
            if i == 0:  # Первая строка с данными
                line = f"{name_part:<{name_width}}{qty_str}{price_str}{total_str}"
                lines.append(line)
            else:  # Последующие строки только с продолжением наименования
                padding = " " * (self.column_widths['qty'] +
                                 self.column_widths['price'] +
                                 self.column_widths['total'])
                line = f"{name_part:<{name_width}}{padding}"
                lines.append(line)

        # Добавляем разделитель после товара
        lines.append(self.printer.decorators['separator'] * self.chars_per_line[self.current_font])
        return lines

    def print_invoice(self, invoice_data):
        """Эмуляция печати накладной"""
        try:
            # Инициализация
            self.printer.hw('init')

            # Заголовок
            self.printer.set(align='center', font='a', width=2, height=2)
            self.current_font = 'font_a'
            self.printer.text('НАКЛАДНАЯ')
            self.printer.control('LF')

            # Основная информация
            self.printer.set(align='left', width=1, height=1)
            self.printer.text(f"Номер: {invoice_data.get('id', '')}")
            self.printer.text(f"Дата: {invoice_data.get('created_at', '').split('T')[0]}")

            # Контакт с переносом
            contact_text = f"Контакт: {invoice_data.get('contact', '')}"
            for line in self.wrap_text(contact_text):
                self.printer.text(line)

            self.printer.text(self.printer.decorators['separator'] * self.chars_per_line['font_a'])

            # Переключение на компактный шрифт для таблицы
            self.printer.set(font='b')
            self.current_font = 'font_b'

            # Шапка таблицы
            header = (
                f"{'Наименование':<{self.column_widths['name']}}"
                f"{'Кол.':<{self.column_widths['qty']}}"
                f"{'Цена':<{self.column_widths['price']}}"
                f"{'Сумма':<{self.column_widths['total']}}"
            )
            self.printer.text(header)
            self.printer.text(self.printer.decorators['separator'] * self.chars_per_line['font_b'])

            # Товары
            for item in invoice_data.get('items', []):
                name = item.get('name', '')
                qty = item.get('quantity', 0)
                price = float(item.get('price', 0))
                total = qty * price

                for line in self.format_product_line(name, qty, price, total):
                    self.printer.text(line)

            # Возврат к стандартному шрифту для итогов
            self.printer.set(font='a', align='right')
            self.current_font = 'font_a'

            # Итоги
            self.printer.text(f"Итого: {invoice_data.get('total', 0):.2f}")
            payment_status = "Оплачено" if invoice_data.get('is_paid', False) else "Не оплачено"
            self.printer.text(f"Статус оплаты: {payment_status}")

            # Дополнительная информация
            if additional_info := invoice_data.get('additional_info'):
                self.printer.set(align='left')
                self.printer.text(self.printer.decorators['separator'] * self.chars_per_line['font_a'])
                for line in self.wrap_text(additional_info):
                    self.printer.text(line)

            # Отступ и обрезка
            self.printer.text('\n\n')
            self.printer.cut()

            # Вывод предварительного просмотра
            self.print_preview()
            return True

        except Exception as e:
            print(f"Ошибка эмуляции печати: {str(e)}")
            return False

    def print_preview(self):
        """Вывод предварительного просмотра чека"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print('\n'.join(self.printer.buffer))


# Пример использования
if __name__ == '__main__':
    # Тестовые данные
    test_invoice = {
        'id': 'INV-2023-001',
        'created_at': '2023-11-05T12:00:00',
        'contact': 'ООО "Компания с очень длинным названием, которое не помещается в одну строку"',
        'items': [
            {
                'name': 'Многофункциональное устройство печати с возможностью двусторонней печати и автоподачей документов',
                'quantity': 2,
                'price': 100.50
            },
            {
                'name': 'Компьютерная мышь беспроводная эргономичная',
                'quantity': 1,
                'price': 50.75
            },
            {
                'name': 'Установка и настройка программного обеспечения на сервере предприятия',
                'quantity': 3,
                'price': 200.00
            }
        ],
        'total': 851.75,
        'is_paid': True,
        'additional_info': 'Дополнительная информация: товар получен в полном объеме, претензий по качеству нет. '
                           'Гарантийное обслуживание 12 месяцев. Товар сертифицирован.'
    }

    # Создание эмулятора и печать тестового чека
    emulator = ThermalPrinterEmulator()
    emulator.print_invoice(test_invoice)