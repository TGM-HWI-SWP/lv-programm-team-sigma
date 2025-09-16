import sqlite3
from typing import List, Tuple
from sqlite3 import Error
import traceback


class dbms:
    """A dbms class, that provides connection and executes commands
    """
    def __init__(self, db_name : str):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_name)
        except Error as e:
            print(e)
        # self.create_table()

    def execute_command(self, execute_sql : str , params = None, fetch = False):
        """ execute a command from the execute_sql statement
        :param conn: Connection object
        :param execute_sql: a executable SQL statement
        :return:
        """
        try:
            c = self.conn.cursor()
            if params:
                c.execute(execute_sql, params)
            else:
                c.execute(execute_sql)
            self.conn.commit()

            if fetch and c.description:
                return c.fetchall(), c.description[0]
            else:
                return c.fetchall(), None
        except sqlite3.Error as e:  # Spezifisch für SQLite-Fehler
            self.conn.rollback()
            print("🚨 SQL Error während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {execute_sql}")
            print(f"🔹 Parameter: {params}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")  # Gibt den vollständigen Fehler-Traceback aus
        except Exception as e:  # Falls ein anderer Fehler auftritt
            self.conn.rollback()
            print("🚨 Allgemeiner Fehler während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {execute_sql}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")
            
            
    def create_table(self, table_name : str, table_row_name : List):
        """
        Erstellt die Tabellen in der DB anhand der gegebenen Namen und Parameter
        Args:
            table_name (str): Name der Tabelle in der DB
            table_row_name (List): Namen der Spalten der jeweiligen Tabelle samt Datentypen in einer Liste
        """
        
        sql_create_table = f" CREATE TABLE IF NOT EXISTS {table_name} ("
        
        for item in table_row_name:
            sql_create_table += f"{item[0]} {item[1]}, "
        sql_create_table = sql_create_table.rstrip(', ')
        sql_create_table += ");"
        print("sql_string created")
        try:
            self.execute_command(sql_create_table)
            print(f"{table_name} table created!")
        except sqlite3.Error as e:  # Spezifisch für SQLite-Fehler
            print("🚨 SQL Error während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {sql_create_table}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")  # Gibt den vollständigen Fehler-Traceback aus
        except Exception as e:  # Falls ein anderer Fehler auftritt
            print("🚨 Allgemeiner Fehler während 'sql command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {sql_create_table}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")
            
    def empty_return_check(self, return_list : List):
        
        try:
            if return_list == None:
                raise sqlite3.Warning("Datenbankabfrage ergab keine Treffer!")
            elif len(return_list) < 1:
                raise sqlite3.Warning("Datenbankabfrage ergab keine Treffer!")
        except sqlite3.Warning as e:
            print("🚨 SQL Warning während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")

    def select_all(self, table_name : str, join_table_name : str = None, table_row_FK : str = None,
                   table_row_FK_value : int = None, join_table_PK : str = None, join_table_PK_value : int = None) -> Tuple[List,List]:
        """
        Lädt alle Einträge aus der jeweilgen DB-Tabelle
        Args:
            table_name (str): Name der jeweiligen DB-Tabelle

        Returns:
            List: Eine Liste der Einträge in der DB
        """
        if join_table_name and table_row_FK_value:
            print("joint clause with condition")
            sql_select_table = f"SELECT * FROM {table_name} JOIN {join_table_name} ON {table_name}.{table_row_FK} = {join_table_name}.{join_table_PK} WHERE {table_name}.{table_row_FK} = {table_row_FK_value} AND {join_table_name}.{join_table_PK} = {join_table_PK_value};"
        elif join_table_name and not table_row_FK_value:
            print("joint clause withOUT condition")
            sql_select_table = f"SELECT * FROM {table_name} JOIN {join_table_name} ON {table_name}.{table_row_FK} = {join_table_name}.{join_table_PK};"
        else:
            sql_select_table = f"SELECT * FROM {table_name};"
        try:
            return_list, description = self.execute_command(sql_select_table, None, True)
            #print(return_list)
            self.empty_return_check(return_list=return_list)
            #print(return_list)
            return return_list, description
        except sqlite3.Error as e:  # Spezifisch für SQLite-Fehler
            print("🚨 SQL Error während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {sql_select_table}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")  # Gibt den vollständigen Fehler-Traceback aus
        except Exception as e:  # Falls ein anderer Fehler auftritt
            print("🚨 Allgemeiner Fehler während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {sql_select_table}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")
            
    def insert(self, table_name : str, table_row_name : str, values : List):
        # Extrahiere nur die Spaltennamen (erste Einträge aus der Tabelle)
        column_names = ", ".join([row[0] for row in table_row_name])

        # Erstelle Platzhalter für die Werte
        placeholders = ", ".join(["?" for _ in values])

        # Baue das SQL-Statement richtig auf
        sql_insert = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        try:
            self.execute_command(sql_insert, values, False)
            print(f"{table_name} row inserted!")
        except sqlite3.Error as e:  # Spezifisch für SQLite-Fehler
            print("🚨 SQL Error während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {sql_insert}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")  # Gibt den vollständigen Fehler-Traceback aus
        except Exception as e:  # Falls ein anderer Fehler auftritt
            print("🚨 Allgemeiner Fehler während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {sql_insert}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")

    def select_specific(self, table_name : str, limitations : str, join_table_name : str = None, table_row_FK : str = None,
                   table_row_FK_value : int = None, join_table_PK : str = None, join_table_PK_value : int = None) -> List:
        """
        Lädt alle Einträge aus der jeweilgen DB-Tabelle
        Args:
            table_name (str): Name der jeweiligen DB-Tabelle
            limitations (str): Einschränkungen für die Datenbankabfrage

        Returns:
            List: Eine Liste der Einträge in der DB unter Voraussetzung der Limitations
        """
        
        sql_select_table = f"SELECT * FROM {table_name}"
        
        if join_table_name and table_row_FK_value:
            print("joint clause with condition")
            sql_select_table = f"SELECT * FROM {table_name} JOIN {join_table_name} ON {table_name}.{table_row_FK} = {join_table_name}.{join_table_PK} WHERE {table_name}.{table_row_FK} = {table_row_FK_value} AND {join_table_name}.{join_table_PK} = {join_table_PK_value} WHERE {limitations};"
        elif join_table_name and not table_row_FK_value:
            print("joint clause withOUT condition")
            sql_select_table = f"SELECT * FROM {table_name} JOIN {join_table_name} ON {table_name}.{table_row_FK} = {join_table_name}.{join_table_PK} WHERE {limitations};"
        else:
            sql_select_table = f"SELECT * FROM {table_name} WHERE {limitations};"

        try:
            return_list, description = self.execute_command(sql_select_table, None, True)
            self.empty_return_check(return_list=return_list)
            return return_list, description

        
        except sqlite3.Error as e:  # Spezifisch für SQLite-Fehler
            print("🚨 SQL Error während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {sql_select_table}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")  # Gibt den vollständigen Fehler-Traceback aus
        except Exception as e:  # Falls ein anderer Fehler auftritt
            print("🚨 Allgemeiner Fehler während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {sql_select_table}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")

    def update(self, table_name : str, table_row_name : str, primary_key : str, primary_key_value : int,   values : List):
        set_clause = ", ".join(f"{col[0]} = ?" for col in table_row_name)
        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = {primary_key_value}"
        try:
            # print(update_sql)
            rows, description = self.execute_command(execute_sql=update_sql, params=values, fetch=True)

            if rows.__len__ == 0:
                # INSERT ausführen, falls kein Eintrag existiert
                column_str = ", ".join([primary_key] + values)
                placeholders = ", ".join(["?"] * (len(values) + 1))
                insert_sql = f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
                self.conn.cursor.execute(insert_sql, (values))

        except sqlite3.Error as e:  # Spezifisch für SQLite-Fehler
            print("🚨 SQL Error während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {update_sql}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")  # Gibt den vollständigen Fehler-Traceback aus
        except Exception as e:  # Falls ein anderer Fehler auftritt
            print("🚨 Allgemeiner Fehler während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {update_sql}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")

    def delete(self, table_name : str, table_idrow_name : str, id : int):
        delete_sql = f"DELETE FROM {table_name} WHERE {table_idrow_name} = {id}"
        try:
            self.execute_command(delete_sql)
            print(f"{table_name} Entry with {table_idrow_name} = {id} deleted!")
        except sqlite3.Error as e:  # Spezifisch für SQLite-Fehler
            print("🚨 SQL Error während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {delete_sql}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")  # Gibt den vollständigen Fehler-Traceback aus
        except Exception as e:  # Falls ein anderer Fehler auftritt
            print("🚨 Allgemeiner Fehler während 'execute command':")
            print(f"🔹 Fehlernachricht: {e}")
            print(f"🔹 SQL-Statement: {delete_sql}")
            print(f"🔹 Traceback:\n{traceback.format_exc()}")
            