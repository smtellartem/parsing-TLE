import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLineEdit,
                             QVBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QPointF, QRectF, QSize
from PyQt5.QtGui import (QPainter, QPen, QColor, QFont, QBrush,
                         QIcon, QPixmap, QFontMetrics)
from PyQt5.QtSvg import QSvgRenderer
from main import params

class InputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('TLE расчет')
        self.setGeometry(100, 100, 1920, 1280)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введите URL TLE данных...")
        self.url_input.setText("https://celestrak.org/NORAD/elements/gp.php?CATNR=61777")
        self.url_input.setStyleSheet("""
                QLineEdit {
                    background-color: #d3d3d3;  
                    color: black;               
                    border: 2px solid green;    
                    padding: 8px;               
                    border-radius: 5px;         
                }
            """)
        layout.addWidget(self.url_input)


        self.load_btn = QPushButton("Загрузить данные")
        self.load_btn.setStyleSheet("""
                QPushButton {
                    background-color: #800080;  
                    color: white;               
                    border-radius: 15px;        
                    padding: 10px 25px;         
                    font-weight: bold;          
                }
                QPushButton:hover {
                    background-color: #9932cc;
                }
                QPushButton:pressed {
                    background-color: #4b0082;  
                }
            """)
        self.load_btn.clicked.connect(self.process_tle_data)
        layout.addWidget(self.load_btn)

        self.setLayout(layout)

    def process_tle_data(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.critical(self, "Ошибка", "Введите URL адрес TLE данных")
            return
        try:

            self.orbital_window = EnhancedOrbitalDiagram(
                parent=self,
                **params
            )
            parent = self
            self.orbital_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обработки: {str(e)}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обработки: {str(e)}")

class EnhancedOrbitalDiagram(QWidget):
    def __init__(self, parent=None, **params):
        super().__init__()
        self.parent = parent
        self.params = {
            'наклонение': params.get('inclination', 0),
            'долгота восх. узла': params.get('raan', 0),
            'эксцентриситет': params.get('eccentricity', 0),
            'аргумент перигея': params.get('arg_perigee', 0),
            'средняя аномалия': params.get('mean_anomaly', 0),
            'среднее движение': params.get('mean_motion', 0),
            'истинная аномалия': params.get('true_anomaly', 0),
            'аргумент широты': params.get('argument_of_latitude', 0)
        }
        self.renderer = None
        self.rocket_rect = QRectF()
        self.initUI()

    def setup_connections(self):
        self.back_button.clicked.connect(self.return_to_main)

    def return_to_main(self):
        self.parent.show()
        self.close()


    def closeEvent(self, event):
        self.parent.show()
        event.accept()



    def initUI(self):
        self.setWindowTitle('TLE расчет')
        self.setGeometry(100, 100, 1400, 1000)
        self.setup_assets()
        self.create_widgets()
        self.setup_styles()
        self.setup_connections()

    def setup_assets(self):
        self.resource_paths = {
            'rocket': self.get_absolute_path('img/rocket_start.svg'),
            'icon': self.get_absolute_path('img/back.png')
        }
        if not os.path.exists(self.resource_paths['rocket']):
            raise FileNotFoundError("SVG ракеты не найден")
        self.renderer = QSvgRenderer(self.resource_paths['rocket'])
        if not self.renderer.isValid():
            raise ValueError("Неверный формат SVG файла")

    def create_widgets(self):
        self.back_button = QPushButton("   Назад", self)
        self.back_button.setObjectName("BackButton")
        self.load_button_icon()
        self.update_button_position()

    def load_button_icon(self):
        icon_path = self.resource_paths['icon']
        if os.path.exists(icon_path):
            self.back_button.setIcon(QIcon(QPixmap(icon_path)))
            self.back_button.setIconSize(QSize(32, 32))
        else:
            self.back_button.setIcon(self.style().standardIcon(QApplication.style().SP_DialogBackButton))

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: 'Arial';
            }
            QPushButton#BackButton {
                background-color: #2C3E50;
                border: 2px solid #34495E;
                color: white;
                padding: 12px 20px 12px 5px;
                border-radius: 8px;
                font: bold 19px;
                min-width: 160px;
                min-height: 45px;
                spacing: 12px;
            }
            QPushButton#BackButton:hover {
                background-color: #34495E;
            }
            QPushButton#BackButton:pressed {
                background-color: #233240;
            }
        """)

    def setup_connections(self):
        self.back_button.clicked.connect(self.close)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            self.draw_rocket(painter)
            self.update_button_position()
            self.draw_enhanced_orbital_params(painter)
            self.draw_orbit_point(painter)
            self.draw_argument_of_latitude(painter)
        except Exception as e:
            print(f"Ошибка отрисовки: {str(e)}")
        finally:
            painter.end()

    def draw_rocket(self, painter):
        if not self.renderer.isValid():
            return
        viewport = painter.viewport()
        rocket_width = viewport.width() * 0.3
        rocket_height = rocket_width * (self.renderer.viewBox().height() / self.renderer.viewBox().width())
        self.rocket_rect = QRectF(
            viewport.center().x() - rocket_width / 2,
            viewport.center().y() - rocket_height / 2,
            rocket_width,
            rocket_height
        )
        self.renderer.render(painter, self.rocket_rect)

    def draw_orbit_point(self, painter):
        if self.rocket_rect.isEmpty():
            return
        try:
            text = f"Точка орбиты: {self.params['истинная аномалия']}°"
            text_font = QFont("Arial", 16, QFont.Bold)
            painter.setFont(text_font)
            metrics = QFontMetrics(text_font)
            text_width = metrics.width(text) + 30
            text_height = metrics.height() + 20
            x = self.rocket_rect.center().x() - text_width / 2
            y = self.rocket_rect.top() - text_height - 20
            rect = QRectF(x, y, text_width, text_height)
            painter.setPen(QPen(QColor(255, 255, 0), 3))
            painter.setBrush(QColor(0, 128, 0))
            painter.drawRoundedRect(rect, 10.0, 10.0)
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(rect, Qt.AlignCenter, text)
        except Exception as e:
            print(f"Ошибка отрисовки точки орбиты: {str(e)}")

    def draw_enhanced_orbital_params(self, painter):
        if self.rocket_rect.isEmpty():
            return
        try:
            line_pen = QPen(QColor(70, 130, 180), 3, Qt.SolidLine, Qt.RoundCap)
            text_font = QFont("Arial", 12, QFont.Bold)
            text_bg = QBrush(QColor(240, 248, 255, 220))
            text_outline_pen = QPen(QColor(255, 255, 255), 2)
            text_main_pen = QPen(QColor(0, 0, 0), 1)
            painter.setFont(text_font)
            metrics = QFontMetrics(text_font)
            param_levels = [
                [('наклонение', False), ('аргумент перигея', True)],
                [('долгота восх. узла', False), ('эксцентриситет', True)],
                [('средняя аномалия', False), ('среднее движение', True)]
            ]
            for level, params in zip([0.25, 0.5, 0.75], param_levels):
                y_pos = self.rocket_rect.top() + level * self.rocket_rect.height()
                for param, is_left in params:
                    start_x = self.rocket_rect.left() if is_left else self.rocket_rect.right()
                    direction = -1 if is_left else 1
                    line_length = 180
                    line_end = start_x + direction * line_length
                    painter.setPen(line_pen)
                    painter.drawLine(QPointF(start_x, y_pos), QPointF(line_end, y_pos))
                    text = f"{param}: {self.params[param]}"
                    text_width = metrics.width(text) + 30
                    text_height = metrics.height() + 15
                    text_offset = 15 * direction
                    text_rect = QRectF(
                        line_end + (text_offset if not is_left else -text_width + text_offset),
                        y_pos - text_height / 2,
                        text_width,
                        text_height
                    )
                    painter.setBrush(text_bg)
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(text_rect, 8.0, 8.0)
                    painter.setPen(text_outline_pen)
                    painter.drawText(text_rect,
                                     Qt.AlignRight if is_left else Qt.AlignLeft | Qt.AlignVCenter,
                                     text)
                    painter.setPen(text_main_pen)
                    painter.drawText(text_rect,
                                     Qt.AlignRight if is_left else Qt.AlignLeft | Qt.AlignVCenter,
                                     text)
        except Exception as e:
            print(f"Ошибка отрисовки параметров: {str(e)}")

    def draw_argument_of_latitude(self, painter):
        try:
            # Текст для отображения
            text = f"Аргумент широты: {self.params['аргумент широты']}°"

            # Установка шрифта
            text_font = QFont("Arial", 14, QFont.Bold)
            painter.setFont(text_font)

            # Получение метрик шрифта
            font_metrics = painter.fontMetrics()
            text_width = font_metrics.horizontalAdvance(text)  # Ширина текста
            text_height = font_metrics.height()  # Высота текста

            # Добавление отступов вокруг текста
            padding_x = 20  # Отступ по горизонтали
            padding_y = 10  # Отступ по вертикали
            rect_width = text_width + padding_x
            rect_height = text_height + padding_y

            # Расчет позиции рамки (отсчитываем от нижнего левого угла)
            x = 50  # Отступ от левого края
            y = self.height() - rect_height - 50  # Отступ от нижнего края

            # Создание прямоугольника для рамки
            rect = QRectF(x, y, rect_width, rect_height)

            # Отрисовка рамки с закругленными углами
            painter.setPen(QColor(0, 0, 0))  # Цвет границы
            painter.setBrush(QColor(255, 255, 200))  # Цвет заливки
            painter.drawRoundedRect(rect, 8, 8)  # Закругленные углы

            # Отрисовка текста внутри рамки
            painter.drawText(rect, Qt.AlignCenter, text)

        except Exception as e:
            print(f"Ошибка отрисовки аргумента широты: {str(e)}")

    def update_button_position(self):
        if self.rocket_rect.isEmpty():
            return
        btn_size = self.back_button.sizeHint()
        x = self.rocket_rect.center().x() - btn_size.width() / 2
        y = self.rocket_rect.bottom() + 50
        self.back_button.move(int(x), int(y))

    def get_absolute_path(self, relative_path):
        base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    input_window = InputWindow()
    input_window.show()
    sys.exit(app.exec_())