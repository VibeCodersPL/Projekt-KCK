import os
import sqlite3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.properties import partial

from ui.components.rounded_button import RoundedButton


class StatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        title_label = Label(
            text='Twoje Statystyki',
            font_size='32sp',
            size_hint_y=0.1,
            bold=True
        )
        self.layout.add_widget(title_label)

        self.summary_label = Label(
            text='Ładowanie statystyk...',
            font_size='20sp',
            size_hint_y=0.15,
            halign='center',
            valign='middle'
        )
        self.summary_label.bind(size=self.summary_label.setter('text_size'))
        self.layout.add_widget(self.summary_label)

        self.chart_image = Image(size_hint_y=0.6)
        self.layout.add_widget(self.chart_image)

        btn_layout = BoxLayout(size_hint_y=0.15, padding=[0, 10, 0, 10])
        btn = RoundedButton(
            text="Powrót do menu",
            font_size='18sp',
            bg_color=(0.15, 0.45, 0.85, 1),
            radius=30,
            size_hint=(0.4, 1),
            pos_hint={'center_x': 0.5}
        )
        btn.bind(on_press=partial(self.change_screen, 'menu'))

        btn_layout.add_widget(Label(size_hint_x=0.3))
        btn_layout.add_widget(btn)
        btn_layout.add_widget(Label(size_hint_x=0.3))
        self.layout.add_widget(btn_layout)

        self.add_widget(self.layout)

    def on_enter(self, *args):
        self.load_statistics()

    def load_statistics(self):
        db_path = "baza_treningow.db"
        if not os.path.exists(db_path):
            self.summary_label.text = "Nie znaleziono bazy danych. Wykonaj pierwszy trening!"
            return

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(DISTINCT IDTreningu) FROM StatystykiCwiczen")
                total_trainings = cursor.fetchone()[0]

                if not total_trainings or total_trainings == 0:
                    self.summary_label.text = "Nie masz jeszcze żadnych zapisanych wyników.\nPrzejdź do treningu!"
                    self.chart_image.source = ""
                    return

                cursor.execute("SELECT AVG(SredniCzasTrwania), AVG(SredniaPoprawnosc) FROM StatystykiCwiczen")
                avg_time, avg_correct = cursor.fetchone()

                cursor.execute(
                    "SELECT NazwaStanu, AVG(SredniCzasTrwania), AVG(SredniaPoprawnosc) FROM StatystykiCwiczen GROUP BY NazwaStanu")
                state_data = cursor.fetchall()
        except Exception as e:
            self.summary_label.text = f"Wystąpił błąd odczytu danych: {e}"
            return

        time_str = f"{avg_time:.2f} s" if avg_time else "0.0 s"
        correct_val = (avg_correct * 100) if (avg_correct and avg_correct <= 1.0) else (avg_correct or 0)
        correct_str = f"{correct_val:.1f} %"

        self.summary_label.text = (
            f"Liczba ukończonych ćwiczeń/treningów: [b]{total_trainings}[/b]\n"
            f"Ogólny średni czas wykonania elementu: [b]{time_str}[/b]\n"
            f"Ogólna średnia poprawność: [b]{correct_str}[/b]"
        )
        self.summary_label.markup = True

        self.generate_charts(state_data)

    def generate_charts(self, data):
        if not data:
            return

        states = [row[0] if row[0] else "Nieznany" for row in data]
        times = np.array([row[1] if row[1] else 0 for row in data])

        correctness = np.array([(row[2] * 100 if row[2] <= 1.0 else row[2]) if row[2] else 0 for row in data])

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        fig.patch.set_alpha(0.0)

        color_time = '#2673D9'
        color_correct = '#2E994C'
        text_color = 'white'

        def style_axis(ax, title):
            ax.set_title(title, color=text_color, pad=15, fontsize=12, fontweight='bold')
            ax.tick_params(axis='x', colors=text_color, rotation=20)
            ax.tick_params(axis='y', colors=text_color)
            ax.set_facecolor((1, 1, 1, 0.05))
            for spine in ax.spines.values():
                spine.set_edgecolor('gray')

        ax1.bar(states, times, color=color_time, edgecolor=text_color, linewidth=1.5, alpha=0.8)
        style_axis(ax1, 'Średni czas (sekundy) per Stan')

        ax2.bar(states, correctness, color=color_correct, edgecolor=text_color, linewidth=1.5, alpha=0.8)
        style_axis(ax2, 'Poprawność (%) per Stan')
        ax2.set_ylim(0, 105)

        plt.tight_layout()

        chart_path = 'src/dev/stats_chart.png' #plik do ktorego bedzie zapisywany wykres i ktory otworzy kivy
        plt.savefig(chart_path, dpi=100, facecolor=fig.get_facecolor(), transparent=True)
        plt.close(fig)

        self.chart_image.source = chart_path
        self.chart_image.reload()

    def change_screen(self, target_screen, instance):
        self.manager.current = target_screen