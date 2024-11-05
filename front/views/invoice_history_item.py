# views/invoice_history_item.py
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.app import App
from views.popup_view import MessagePopup


class InvoiceItemWidget(BoxLayout):
    number = StringProperty('')
    date = StringProperty('')
    contact = StringProperty('')
    total = NumericProperty(0.0)
    is_paid = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def edit_invoice(self, instance) -> None:
        try:
            app = App.get_running_app()
            screen_manager = app.root
            history_view = screen_manager.get_screen('history')

            if history_view:
                print(f"Editing invoice {self.number}")  # Отладка
                history_view.edit_invoice(int(self.number))
            else:
                raise ValueError("History view not found")
        except Exception as e:
            print(f"Error in edit_invoice: {e}")  # Отладка
            MessagePopup.show_message(f"Ошибка при редактировании: {str(e)}")

    def delete_invoice(self, instance) -> None:
        try:
            # В popup_view.py нужно добавить метод для диалога подтверждения
            MessagePopup.show_confirm_dialog(
                message=f'Вы уверены, что хотите удалить накладную {self.number}?',
                confirm_callback=self.confirm_delete,
                cancel_callback=self.cancel_delete
            )
        except Exception as e:
            print(f"Error in delete_invoice: {e}")  # Отладка
            MessagePopup.show_message(f"Ошибка при удалении: {str(e)}")

    def confirm_delete(self) -> None:
        try:
            app = App.get_running_app()
            screen_manager = app.root
            history_view = screen_manager.get_screen('history')

            if history_view:
                print(f"Deleting invoice {self.number}")  # Отладка
                history_view.delete_invoice(int(self.number))
            else:
                raise ValueError("History view not found")
        except Exception as e:
            print(f"Error in confirm_delete: {e}")  # Отладка
            MessagePopup.show_message(f"Ошибка при удалении: {str(e)}")

    def cancel_delete(self) -> None:
        try:
            print("Delete cancelled")  # Отладка
        except Exception as e:
            print(f"Error in cancel_delete: {e}")  # Отладка
            MessagePopup.show_message(f"Ошибка при отмене удаления: {str(e)}")