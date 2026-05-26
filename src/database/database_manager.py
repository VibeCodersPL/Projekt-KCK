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
            ''') #w RodzajTreningu: jeżeli 1 -> trening wpierany; 2 -> trening jednego elementu
        

            # Tabela pomocnicza: TreningWspierany (Rodzaj = 1)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS TreningWspierany (
                    IDTreningu INTEGER,
                    NrCwiczenia INTEGER,
                    StanCwiczenia INTEGER,
                    FOREIGN KEY(IDTreningu) REFERENCES Treningi(IDTreningu)
                )
            ''')

            # Tabela pomocnicza: TreningJednegoElementu (Rodzaj = 2)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS TreningJednegoElementu (
                    IDTreningu INTEGER,
                    NrCwiczenia INTEGER,
                    StanCwiczenia INTEGER,
                    FOREIGN KEY(IDTreningu) REFERENCES Treningi(IDTreningu)
                )
            ''')
            conn.commit()

    def save_trening(self, trening_type: int, start_time: str, end_time: str,
                     reps: list):
        """
        Zapisuje główny trening i automatycznie przypisuje do niego wszystkie ćwiczenia.

        Args:
            trening_type (int): 1 (Wspierany) lub 2 (Jednego elementu)
            start_time (str): np. "15:30:00"
            end_time (str): np. "15:45:00"
            reps (list): Lista krotek np. [(1, 1), (2, 0), (3, 1)]
                                format: (NrCwiczenia, StanCwiczenia)
        """
        today_date = date.today().isoformat()

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO Treningi (DataWykonania, CzasRozpoczecia, CzasZakonczenia, RodzajTreningu)
                VALUES (?, ?, ?, ?)
            ''', (today_date, start_time, end_time, trening_type))

            trening_id = cursor.lastrowid

            if trening_type == 1:
                target_table = "TreningWspierany"
            elif trening_type == 2:
                target_table = "TreningJednegoElementu"
            else:
                raise ValueError(f"Nieznany rodzaj treningu: {trening_type}")

            for excercise, excercise_state in reps:
                cursor.execute(f'''
                    INSERT INTO {target_table} (IDTreningu, NrCwiczenia, StanCwiczenia)
                    VALUES (?, ?, ?)
                ''', (trening_id, excercise, excercise_state))

            conn.commit()