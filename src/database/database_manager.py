import sqlite3
from datetime import date

class DatabaseManager:
    def __init__(self, db_name: str = "baza_treningow.db"):
        """Inicjalizuje bazę i upewnia się, że struktura tabel istnieje."""
        self.db_name = db_name
        self._create_databases()

    def _create_databases(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Tabela główna: Treningi
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Treningi (
                    IDTreningu INTEGER PRIMARY KEY AUTOINCREMENT,
                    DataWykonania DATE,
                    CzasRozpoczecia TIME,
                    CzasZakonczenia TIME,
                    RodzajTreningu INTEGER 
                )
            ''')    # 1 wspierany #2 pojedynczego elementu
                
            # Tabela pomocnicza:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS StatystykiCwiczen (
                    IDTreningu INTEGER,
                    NazwaCwiczenia TEXT,
                    NazwaStanu TEXT,
                    SredniCzasTrwania REAL,
                    SredniaPoprawnosc REAL,
                    FOREIGN KEY(IDTreningu) REFERENCES Treningi(IDTreningu) ON DELETE CASCADE
                )
            ''')
            conn.commit()

    def save_training(self, trening_type: int, start_time: str, end_time: str, 
                     nazwa_cwiczenia: str, stats: dict):
        """
        Zapisuje główny trening i przypisuje uśrednione statystyki stanów ćwiczenia.
        """
        today_date = date.today().isoformat()

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Treningi (DataWykonania, CzasRozpoczecia, CzasZakonczenia, RodzajTreningu)
                VALUES (?, ?, ?, ?)
            ''', (today_date, start_time, end_time, trening_type))

            trening_id = cursor.lastrowid

            for nazwa_stanu, (durations, correctness) in stats.items():
                
                if len(durations) == 0 or len(correctness) == 0:
                    continue
                    
                # Liczenie średniej
                avg_duration = sum(durations) / len(durations)
                avg_correctness = sum(correctness) / len(correctness)

                cursor.execute('''
                    INSERT INTO StatystykiCwiczen 
                    (IDTreningu, NazwaCwiczenia, NazwaStanu, SredniCzasTrwania, SredniaPoprawnosc)
                    VALUES (?, ?, ?, ?, ?)
                ''', (trening_id, nazwa_cwiczenia, nazwa_stanu, avg_duration, avg_correctness))

            conn.commit()
            return trening_id