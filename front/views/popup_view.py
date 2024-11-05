# views/popup_view.py
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

# Определяем цвета как в вашем .kv файле
PRIMARY_COLOR = (0.2, 0.6, 1, 1)
SECONDARY_COLOR = (0.3, 0.3, 0.3, 1)
BACKGROUND_COLOR = (0.96, 0.96, 0.98, 1)
TEXT_COLOR = (1, 1, 1, 1)
BORDER_RADIUS = [10, ]


class MessagePopup(Popup):
    def __init__(self, **kwargs):
        # Устанавливаем стандартные значения стиля
        kwargs['background'] = ''
        kwargs['background_color'] = PRIMARY_COLOR
        kwargs['title_color'] = TEXT_COLOR
        kwargs['separator_height'] = 0
        kwargs['border'] = (0, 0, 0, 0)
        super().__init__(**kwargs)

    @staticmethod
    def show_message(message):
        content = Label(
            text=message,
            text_size=(380, None),
            size_hint_y=None,
            halign='left',
            valign='middle',
            font_size='14sp',
            color=TEXT_COLOR,
            padding=(10, 10)
        )

        content.bind(texture_size=content.setter('size'))

        popup = MessagePopup(
            title='Сообщение',
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            auto_dismiss=True
        )
        popup.open()

    @staticmethod
    def show_confirm_dialog(message, confirm_callback, cancel_callback):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        message_label = Label(
            text=message,
            text_size=(380, None),
            size_hint_y=None,
            halign='left',
            valign='middle',
            font_size='14sp',
            color=TEXT_COLOR
        )
        content.add_widget(message_label)

        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)

        confirm_btn = Button(
            text='Удалить',
            size_hint_y=None,
            height=dp(30),
            background_color=(1, 0.3, 0.3, 1),
            color=TEXT_COLOR,
            font_size='14sp',
            bold=True
        )

        cancel_btn = Button(
            text='Отмена',
            size_hint_y=None,
            height=dp(30),
            background_color=SECONDARY_COLOR,
            color=TEXT_COLOR,
            font_size='14sp',
            bold=True
        )

        popup = MessagePopup(
            title='',
            content=content,
            size_hint=(None, None),
            size=(400, 250),
            auto_dismiss=False
        )

        def on_confirm(instance):
            popup.dismiss()
            confirm_callback()

        def on_cancel(instance):
            popup.dismiss()
            cancel_callback()

        confirm_btn.bind(on_press=on_confirm)
        cancel_btn.bind(on_press=on_cancel)

        buttons.add_widget(confirm_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)

        popup.open()