"""
@file database.py
@brief Singleton-Connector für Zugriff auf TinyDB-Datenbank im JSON-Format

Dieses Modul kapselt den Zugriff auf eine zentrale TinyDB-Datenbank, die als JSON-Datei 
("database.json") gespeichert ist. Es stellt sicher, dass nur eine Instanz der Datenbank 
gleichzeitig aktiv ist, um inkonsistente Schreibzugriffe zu vermeiden.

Die Datenbank wird für alle gespeicherten MQTT-Daten verwendet und kann zentral über 
"get_table()" auf spezifische Topics zugreifen.
"""

import os
from tinydb import TinyDB
from tinydb.table import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware

serializer = SerializationMiddleware(JSONStorage)

class DatabaseConnector:
    """
    @class DatabaseConnector
    @brief Singleton-Klasse zur Verwaltung der TinyDB-Instanz

    Verhindert mehrfaches Öffnen derselben Datei durch geteilte Instanz. Bietet Methoden
    zur Tabellenabfrage sowie zum Schließen der Datenbank.
    """

    __instance = None # Singleton-Instanz

    def __new__(cls):
        """
        @brief Erstellt eine neue Instanz der Klasse (falls nicht vorhanden)
        @return Instanz von DatabaseConnector
        """
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
            cls.__instance._db = None
        return cls.__instance
    
    def get_db(self) -> TinyDB:
        """
        @brief Gibt die zentrale TinyDB-Datenbankinstanz zurück
        Initialisiert bei Bedarf die Datenbank mit Serialisierungssupport (z.B. für Listen, Dictionaries).
        @return Referenz auf geöffnete TinyDB-Datenbank
        """
        if self._db is None:
            self._db = TinyDB(self.path, storage=serializer)
        return self._db

    def get_table(self, table_name: str) -> Table:
        """
        @brief Gibt eine Referenz auf eine bestimmte Tabelle (nach Topic) zurück
        Falls die Tabelle nicht existiert, wird sie angelegt.
        @param table_name Name der gewünschten Tabelle (z.B. "temperature", "final_weight", ...)
        @return TinyDB Table-Objekt
        """
        db = self.get_db()
        return db.table(table_name)
    
    def close(self):
        """
        @brief Schließt die aktuelle TinyDB-Verbindung und setzt die Instanz auf None
        Sollte vor dem Kopieren/Löschen von "database.json" aufgerufen werden.
        """
        if self._db is not None:
            self._db.close()
            self._db = None