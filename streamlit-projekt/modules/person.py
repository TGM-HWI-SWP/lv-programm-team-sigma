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
        ["PERS_ID", "integer NOT NULL", "ID"],
        ["PERS_SURNAME", "text NOT NULL", "Nachname"],
        ["PERS_FIRSTNAME", "text NOT NULL", "Vorname"],
        ["PERS_BIRTHDATE", "text NOT NULL", "Geburtsdatum"],
        ["PERS_STREET", "text", "Straße"],
        ["PERS_HOUSENR", "integer", "Hausnummer"],
        ["PERS_FLOOR", "text", "Tür/Stockwerk"],
        ["PERS_ZIP", "integer", "PLZ"],
        ["PERS_PLACE", "text", "Ort"],
        ["PERS_REC_ID", "integer NOT NULL PRIMARY KEY", "Record ID"],
        ["PERS_SEX", "text", "Geschlecht"],
        ["PERS_CHILDREN", "integer", "Anzahl Kinder"]
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
        for row in list_from_db:
            try:
                # Handle different column counts gracefully
                if len(row) >= 9:
                    persid, nachname, vorname, geburtsdatum, straße, hausnr, stiege, plz, ort = row[:9]
                    # Extract additional fields if available
                    rec_id = row[9] if len(row) > 9 else None
                    sex = row[10] if len(row) > 10 else None
                    children = row[11] if len(row) > 11 else None
                    
                    obj_list.append(person(
                        id=int(persid), 
                        nachname=nachname, 
                        vorname=vorname, 
                        geburtsdatum=geburtsdatum, 
                        straße=straße, 
                        hausnr=hausnr, 
                        stiege_top_etc=stiege, 
                        plz=plz, 
                        ort=ort,
                        rec_id=rec_id,
                        sex=sex,
                        children=children
                    ))
            except Exception as e:
                print("Problem during select all in person with id: ", row[0] if row else "unknown", e, traceback.print_exc())
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
        for row in list_from_db:
            try:
                # Handle different column counts gracefully
                if len(row) >= 9:
                    persid, nachname, vorname, geburtsdatum, straße, hausnr, stiege, plz, ort = row[:9]
                    # Extract additional fields if available
                    rec_id = row[9] if len(row) > 9 else None
                    sex = row[10] if len(row) > 10 else None
                    children = row[11] if len(row) > 11 else None
                    
                    obj_list.append(person(
                        id=int(persid), 
                        nachname=nachname, 
                        vorname=vorname, 
                        geburtsdatum=geburtsdatum, 
                        straße=straße, 
                        hausnr=hausnr, 
                        stiege_top_etc=stiege, 
                        plz=plz, 
                        ort=ort,
                        rec_id=rec_id,
                        sex=sex,
                        children=children
                    ))
            except:
                print("Problem during specific selection in person")

        return obj_list

    def __init__(self, vorname: str, nachname: str, geburtsdatum: str, id: int = None, straße: str = None, hausnr: int = None, stiege_top_etc: str = None, plz: int = None, ort: str = None, rec_id: int = None, sex: str = None, children: int = None) -> int:
        """Erstellt ein Personenobjekt anhand der gegebenen Parameter

        Args:
            vorname (str): Vorname der Person
            nachname (str): Nachname der Person
            geburtsdatum (str): Geburtsdatum der Person
            id (int, optional): ID der Person
            straße (str, optional): Straße
            hausnr (int, optional): Hausnummer
            stiege_top_etc (str, optional): Stiege/Top/etc
            plz (int, optional): PLZ
            ort (str, optional): Ort
            rec_id (int, optional): Record ID (Primary Key)
            sex (str, optional): Geschlecht
            children (int, optional): Anzahl Kinder
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
        self.rec_id = rec_id
        self.sex = sex
        self.children = children

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
        return (self.obj_id, self.surname, self.name, self.__birthdate, self.street, self.housenr, self.floor, self.zip, self.place, self.rec_id, self.sex, self.children)

    def eval_age(self) -> int:
        """
        Berechnet das Alter der Person anhand des Geburtsdatums
        Returns:
            int: Alter der Person, oder -1 wenn Datum ungültig
        """
        try:
            geburtsdatum = dt.datetime.strptime(self.birthdate, "%d.%m.%Y")
            heute = dt.datetime.today()
            alter = heute.year - geburtsdatum.year - ((heute.month, heute.day) < (geburtsdatum.month, geburtsdatum.day))
            return alter
        except (ValueError, AttributeError):
            return -1

    def insert(self, db_ms: dbms.dbms):
        """
        Fügt ein neues Objekt in die Datenbank ein

        Args:
            dbms (dbms.dbms): Aktives DBMS
        """
        db_ms.insert(table_name=self.table_name, table_row_name=self.table_row_names, values=(self.obj_id, self.surname, self.name, self.birthdate, self.street, self.housenr, self.floor, self.zip, self.place, self.rec_id, self.sex, self.children))

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
