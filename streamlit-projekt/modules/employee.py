import datetime as dt
from typing import List
import copy

from modules import person
from modules import dbms


class mitarbeiter(person.person):

    id = 0
    table_name = "MITARBEITER"
    table_row_names = [
        ["EMPL_ID", "integer PRIMARY KEY", "Mitarbeiter-ID"],
        ["PERS_ID", "integer", "Personen-ID"],
        ["EMPL_ENTRYDATE", "text NOT NULL", "Eintrittsdatum"],
        ["EMPL_BRUTTOGEHALT", "integer NOT NULL", "Bruttogehalt"],
        ["FOREIGN KEY (PERS_ID)", "REFERENCES PERSON(PERS_ID)", "Verknüpfung zur Person"]
    ]

    @classmethod
    def initialize_db_table(cls, dbms_obj: dbms.dbms):
        """
        Erstellt die Datenbanktabelle anhand der statischen Attribute
        Args:
            dbms (dbms.dbms): Die verbundene Datenbanken
        """
        dbms_obj.create_table(table_name=cls.table_name, table_row_name=cls.table_row_names)

    @classmethod
    def select_all(cls, dbms_obj: dbms.dbms) -> List["mitarbeiter"]:
        """
        Lädt alle
        Args:
            dbms (dbms.dbms): Die verbundene Datenbanken

        Returns:
            _type_: _description_
        """
        obj_list = []
        list_from_db, description = dbms_obj.select_all(table_name=cls.table_name, join_table_name=person.person.table_name, table_row_FK=cls.table_row_names[1][0], join_table_PK=person.person.table_row_names[0][0])
        if list_from_db is None:
            return obj_list
        for (id, persid, eintrittsdatum, gehalt, persid1, surname, firstname, birthdate, street, housenr, floor, zip, place) in list_from_db:
            try:
                obj_list.append(mitarbeiter(vorname=firstname, nachname=surname, geburtsdatum=birthdate, eintrittsdatum=eintrittsdatum, gehalt=gehalt, persid=persid, ma_id=id, straße=street, hausnr=housenr, stiege_top_etc=floor, plz=zip, ort=place))
            except:
                ...
        return obj_list

    @classmethod
    def select_specific(cls, dbms_obj: dbms.dbms, id: int) -> List["mitarbeiter"]:
        """
        Lädt alle
        Args:
            dbms (dbms.dbms): Die verbundene Datenbanken

        Returns:
            _type_: _description_
        """
        obj_list = []
        list_from_db, description = dbms_obj.select_specific(table_name=cls.table_name, join_table_name=person.person.table_name, table_row_FK=cls.table_row_names[1][0], join_table_PK=person.person.table_row_names[0][0], limitations=f"{cls.table_row_names[0][0]} = {id}")
        if list_from_db is None:
            return obj_list
        for (id, persid, eintrittsdatum, gehalt, persid1, surname, firstname, birthdate, street, housenr, floor, zip, place) in list_from_db:
            try:
                obj_list.append(mitarbeiter(vorname=firstname, nachname=surname, geburtsdatum=birthdate, eintrittsdatum=eintrittsdatum, gehalt=gehalt, persid=persid, ma_id=id, straße=street, hausnr=housenr, stiege_top_etc=floor, plz=zip, ort=place))
            except:
                print(obj_list)

        return obj_list

    def __init__(self, vorname: str, nachname: str, geburtsdatum: str, eintrittsdatum=dt.datetime.now().strftime("%d.%m.%Y"), gehalt: float = 0., persid: int = None, ma_id: int = None, straße: str = None, hausnr: int = None, stiege_top_etc: str = None, plz: int = None, ort: str = None):
        """
        Erstellt den Mitarbeiter anhand der bekannten Parameter
        Args:
            vorname (str): Vorname des Mitarbeiters
            nachname (str): Nachname des Mitarbeiters
            geburtsdatum (str): Geburtsdatum des Mitarbeiters
            eintrittsdatum (_type_, optional): Eintrittsdatum in die Firma. Defaults to dt.datetime.now().strftime("%d.%m.%Y").
            gehalt (float, optional): Gehalt des Mitarbeiters lt Dienstvertrag. Defaults to 0..
            persid (int, optional): ID lt. Personen-Tabelle der DB. Defaults to None.
            ma_id (int, optional): ID der Mitarbeiter-Tabelle der DB. Defaults to None.
            straße (str, optional): Straße der Adresse des Mitarbeiters
            hausnr (int, optional): Hausnummer des Mitarbeiters. Defaults to None.
            stiege_top_etc (str, optional): Adresszusatz des Mitarbeiters. Defaults to None.
            plz (int, optional): Postleitzahl der Adresse des Mitarbeiters. Defaults to None.
            ort (str, optional): Ort der Adresse des Mitarbeiters. Defaults to None.
        """
        self.pers_id = super().__init__(vorname=vorname, nachname=nachname, geburtsdatum=geburtsdatum, straße=straße, hausnr=hausnr, stiege_top_etc=stiege_top_etc, plz=plz, ort=ort, id=persid)
        if ma_id is None:
            mitarbeiter.id = mitarbeiter.id + 1
        else:
            mitarbeiter.id = copy.deepcopy(ma_id)
        self.empolyee_ID = copy.deepcopy(mitarbeiter.id)
        self.entrydate = eintrittsdatum
        if type(gehalt) == str:
            if ";" in gehalt:
                gehalt = gehalt.replace(".", "").replace(",", ".")
            else:
                gehalt = gehalt.replace(",", ".")
            gehalt = float(gehalt)
        self.__salary = gehalt

    @property
    def salary(self) -> float:
        return self.__salary

    @salary.setter
    def salary(self, val: float):
        if val < 0:
            print("Das geht ned, du kannst nicht negativ bezahlt werden!")
        else:
            self.__salary = val

    def value(self) -> tuple:
        """
        Gibt die Werte der Attribute als Tuple zurück
        Returns:
            tuple: Anordnung der Attributswerte
        """
        return (self.empolyee_ID, self.obj_id, self.entrydate, self.salary)

    def insert(self, db_ms: dbms.dbms):
        """
        Fügt den Mitarbeiter in die Datenbank ein
        Args:
            db_ms (dbms): Die verbundene Datenbanken
        """
        db_ms.insert(table_name=self.table_name, table_row_name=self.table_row_names[:-1], values=self.value())

    def update(self, dbms_obj: dbms.dbms, values: tuple):
        """
        Updated die Daten des Mitarbeiters in der Datenbank
        Args:
            dbms (dbms.dbms): Die verbundene Datenbanken
        """
        dbms_obj.update(table_name=self.table_name, table_row_name=self.table_row_names[:-1], values=values, primary_key=self.table_row_names[0][0], primary_key_value=self.empolyee_ID)

    def delete(self, dbms_obj: dbms.dbms):
        """
        Löscht den Mitarbeiter aus der Datenbank
        Args:
            dbms (dbms.dbms): Die verbundene Datenbanken
        """
        dbms_obj.delete(table_name=self.table_name, table_idrow_name=self.table_row_names[0][0], id=self.empolyee_ID)
