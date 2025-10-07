import datetime as dt
from typing import List
import traceback
import copy

from modules import dbms


class person:

    # Vor dem Konstruktor dürfen nur statische Attribute und Methoden stehen.
    id = 0
    table_name = "PERSON"
    table_row_names = [
        ["PERS_ID", "integer PRIMARY KEY", "ID"],
        ["PERS_SURNAME", "text NOT NULL", "Nachname"],
        ["PERS_FIRSTNAME", "text NOT NULL", "Vorname"],
        ["PERS_BIRTHDATE", "text NOT NULL", "Geburtsdatum"],
        ["PERS_STREET", "text", "Straße"],
        ["PERS_HOUSENR", "integer", "Hausnummer"],
        ["PERS_FLOOR", "text", "Tür/Stockwerk"],
        ["PERS_ZIP", "integer", "PLZ"],
        ["PERS_PLACE", "text", "Ort"]
    ]

    @classmethod
    def initialize_db_table(cls, db_ms: dbms.dbms):
        """
        Erstellt die Datenbanktabelle anhand der statischen Attribute
        Args:
            dbms (dbms.dbms): Die verbundene Datenbanken
        """
        db_ms.create_table(table_name=cls.table_name, table_row_name=cls.table_row_names)

    @classmethod
    def select_all(cls, db_ms: dbms.dbms) -> List["person"]:
        """
        Lädt alle
        Args:
            dbms (dbms.dbms): Die verbundene Datenbanken

        Returns:
            List["person"]: Gibt eine Liste aller Personen zurück
        """
        obj_list = []
        list_from_db, description = db_ms.select_all(table_name=cls.table_name)
        if list_from_db is None:
            return obj_list
        for (persid, nachname, vorname, geburtsdatum, straße, hausnr, stiege, plz, ort) in list_from_db:
            try:
                obj_list.append(person(id=int(persid), nachname=nachname, vorname=vorname, geburtsdatum=geburtsdatum, straße=straße, hausnr=hausnr, stiege_top_etc=stiege, plz=plz, ort=ort))
            except Exception as e:
                print("Problem during select all in person with id: ", persid, e, traceback.print_exc())
        return obj_list

    @classmethod
    def select_specific(cls, db_ms: dbms.dbms, id: int) -> List["person"]:
        """
        Lädt alle
        Args:
            dbms (dbms.dbms): Die verbundene Datenbanken

        Returns:
            List["person"]: Gibt eine Liste aller Personen zurück
        """
        obj_list = []
        list_from_db, description = db_ms.select_specific(table_name=cls.table_name, limitations=f"{cls.table_row_names[0][0]} = {id}")

        if list_from_db is None:
            return obj_list
        for (persid, nachname, vorname, geburtsdatum, straße, hausnr, stiege, plz, ort) in list_from_db:
            try:
                obj_list.append(person(id=int(persid), nachname=nachname, vorname=vorname, geburtsdatum=geburtsdatum, straße=straße, hausnr=hausnr, stiege_top_etc=stiege, plz=plz, ort=ort))
            except:
                print("Problem during sepecific selection in person")

        return obj_list

    def __init__(self, vorname: str, nachname: str, geburtsdatum: str, id: int = None, straße: str = None, hausnr: int = None, stiege_top_etc: str = None, plz: int = None, ort: str = None) -> int:
        """Erstellt ein Personenobjekt anhand der gegebenen Parameter

        Args:
            vorname (str): Vorname der Person
            nachname (str): Nachname der Person
            alter (int): Alter der Person
        """

        if id is None:
            person.id = person.id + 1
        else:
            person.id = copy.deepcopy(id)
        self.obj_id = copy.deepcopy(person.id)
        self.name = vorname
        self.surname = nachname
        self.__birthdate = geburtsdatum
        self.street = straße
        self.housenr = hausnr
        self.floor = stiege_top_etc
        self.zip = plz
        self.place = ort

    @property
    def birthdate(self):
        return self.__birthdate

    @birthdate.setter
    def birthdate(self, val: str):
        if dt.datetime.strptime(val, "%d.%m.%Y") < dt.datetime.strptime("01.01.1950", "%d.%m.%Y"):
            print("Die Sau ist zu alt, so geht das ned!\nDer ghört in Pension!")
        else:
            self.__birthdate = val

    def __repr__(self) -> str:
        """
        Representer für Abfragen
        Returns:
            str: Beschreibung des Objekts
        """
        return f"Hallo ich bin {self.surname} {self.name}, habe am {self.__birthdate} Geburtstag und ich bin {self.eval_age()} Jahre alt."

    def value(self) -> tuple:
        """
        Gibt die Werte der Attribute als Tuple zurück
        Returns:
            tuple: Anordnung der Attributswerte
        """
        return (self.obj_id, self.surname, self.name, self.__birthdate, self.street, self.housenr, self.floor, self.zip, self.place)

    def eval_age(self) -> int:
        """
        Berechnet das Alter der Person anhand des Geburtsdatums
        Returns:
            int: Alter der Person
        """
        geburtsdatum = dt.datetime.strptime(self.birthdate, "%d.%m.%Y")
        heute = dt.datetime.today()
        alter = heute.year - geburtsdatum.year - ((heute.month, heute.day) < (geburtsdatum.month, geburtsdatum.day))
        return alter

    def insert(self, db_ms: dbms.dbms):
        """
        Fügt ein neues Objekt in die Datenbank ein

        Args:
            dbms (dbms.dbms): Aktives DBMS
            gui (gui.MyGUI): Aktive GUI zum Auslesen der eingegebenen Daten
        """
        db_ms.insert(table_name=self.table_name, table_row_name=self.table_row_names, values=(self.obj_id, self.surname, self.name, self.birthdate, self.street, self.housenr, self.floor, self.zip, self.place))

    def update(self, db_ms: dbms.dbms, values: tuple):
        """
        Aktualisiert ein Objekt in der Datenbank
        Args:
            dbms (dbms.dbms): DB-Verbindung
        """

        db_ms.update(table_name=self.table_name, table_row_name=self.table_row_names, primary_key=self.table_row_names[0][0], primary_key_value=self.obj_id, values=values)

    def delete(self, db_ms: dbms.dbms):
        """
        Entfernt das Objekt aus der DB
        Args:
            dbms (dbms.dbms): DB-Verbindung
        """

        db_ms.delete(table_name=self.table_name, table_idrow_name=self.table_row_names[0][0], id=self.obj_id)
