import customtkinter as ctk
from tkinter import ttk
from typing import List
import traceback
import ctypes
import copy
import datetime as dt

try:
    import person
    import dbms
    import employee
    import Abrechnung
except ImportError:
    from . import person
    from . import dbms
    from . import employee
    from . import Abrechnung

class MyGUI(ctk.CTk):
    def __init__(self, db_ms : dbms.dbms):
        super().__init__()

        self.title("Das beste Personalverrechnungstool überhaupt")
        self.geometry("1200x640")  # GUI breite erhöhen
        self.db_ms = db_ms

        # Hauptcontainer mit zwei Spalten (Tabelle & Eingabe)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.main_frame.grid_columnconfigure(0, weight=5)  # Tabelle (größer am Anfang)
        self.main_frame.grid_columnconfigure(1, weight=0)  # Eingabe-Feld (ausgeblendet)

        # Frame für Tabelle (links)
        self.table_frame = ctk.CTkFrame(self.main_frame)
        self.table_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)

        # Frame für Eingabe (rechts) → standardmäßig ausgeblendet
        self.entry_frame = ctk.CTkFrame(self.main_frame)
        self.entry_frame.grid(row=0, column=1, sticky="nse", padx=20, pady=10)
        self.entry_frame.grid_remove()  # Anfangs versteckt

        # Create a tab view
        self.tab_view = ctk.CTkTabview(self.table_frame)
        self.tab_view.pack(expand=True, fill="both")

        # Eingabefeld-Speicherung
        self.entry_fields = {}

        self.last_tab = self.tab_view.get()
        self.check_tab_change()

        # Tabs erstellen
        self.create_tabs()

    def create_tabs(self):
        """Erstellt die Tabs mit Tabellen und CRUD-Buttons"""
        self.tabs = {
            "Personalstammblatt": [row[2] for row in person.person.table_row_names],
            "Mitarbeiterdaten": [row[2] for row in employee.mitarbeiter.table_row_names[:-1]]
            ,"Lohnverrechnung": [row[2] for row in employee.mitarbeiter.table_row_names[:-1]]
        }

        tabs_and_tables = {"Personalstammblatt": person.person.table_name,
                           "Mitarbeiterdaten": employee.mitarbeiter.table_name,
                           "Lohnverrechnung": "ABRECHNUNG"}
        
        self.pers_obj = person.person.select_all(db_ms=self.db_ms)
        self.ma_obj = employee.mitarbeiter.select_all(dbms=self.db_ms)
        
        self.table_container = {}
        self.tree = {}
        for tab_name, columns in self.tabs.items():
            tab = self.tab_view.add(tab_name)

            
            # Frame für die Tabelle mit Scrollbar
            self.table_container = {}

            if tab_name == "Personalstammblatt" or tab_name == "Mitarbeiterdaten":
                self.table_container[tab_name] = ctk.CTkFrame(tab)
                self.table_container[tab_name].pack(expand=True, fill="both", padx=10, pady=10)

                # Scrollbars hinzufügen
                tree_scroll_y = ctk.CTkScrollbar(self.table_container[tab_name], orientation="vertical")
                tree_scroll_y.pack(side="right", fill="y")

                tree_scroll_x = ctk.CTkScrollbar(self.table_container[tab_name], orientation="horizontal")
                tree_scroll_x.pack(side="bottom", fill="x")

                # Treeview (Tabelle) mit Scrollbars
                self.tree[copy.deepcopy(tab_name)] = ttk.Treeview(self.table_container[tab_name], columns=columns, show="headings", yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
                self.tree[tab_name].pack(expand=True, fill="both")

                # Scrollbars mit Tabelle verbinden
                tree_scroll_y.configure(command=self.tree[tab_name].yview)
                tree_scroll_x.configure(command=self.tree[tab_name].xview)

                # Initialize a list to hold maximum lengths for each column
                max_lengths = [0] * len(columns)

                # Set column headings and initial width
                for i, col in enumerate(columns):
                    self.tree[tab_name].heading(col, text=col)
                    self.tree[tab_name].column(col, width=0)  # Set initial width to 0
                
                dpi_scaling = self.get_dpi_scaling()
                style = ttk.Style()
                style.configure("Treeview", rowheight=int(25 * dpi_scaling))  # Setze die Zeilenhöhe dynamisch
                
                # Load data and determine maximum lengths
                item_list = self.pers_obj if tab_name == "Personalstammblatt" else self.ma_obj
                
                for row in item_list:
                    values = row.value()
                    self.tree[tab_name].insert("", "end", values=values)

                    # Update maximum lengths
                    for i, value in enumerate(values):
                        max_lengths[i] = max(max_lengths[i], len(str(value)), 8) 

                # Set column widths based on maximum lengths
                for i, col in enumerate(columns):
                    self.tree[tab_name].column(col, width=int(max_lengths[i] *10 * dpi_scaling))  # Adjust multiplier for padding

                # Buttons für CRUD-Operationen in Stammdaten und Mitarbeiterdaten
                button_frame = ctk.CTkFrame(tab)
                button_frame.pack(fill="x", pady=5)

                create_btn = ctk.CTkButton(button_frame, text="Erstellen", command=lambda: self.show_entry_fields(self.tabs, mode="create", tab_name=self.tab_view.get()))
                create_btn.pack(side="left", padx=5)

                update_btn = ctk.CTkButton(button_frame, text="Aktualisieren", command=lambda: self.show_entry_fields(self.tabs, mode="update", tab_name=self.tab_view.get()))
                update_btn.pack(side="left", padx=5)

                delete_btn = ctk.CTkButton(button_frame, text="Löschen", command=lambda: self.delete_entry(tab_name=self.tab_view.get()))
                delete_btn.pack(side="left", padx=5)

            elif tab_name == "Lohnverrechnung":
                # Neuer Container für LV-Tab mit 2 Spalten (links: Tabelle, rechts: Info)
                lv_main_container = ctk.CTkFrame(tab)
                lv_main_container.pack(fill="both", expand=True, padx=10, pady=10)
                lv_main_container.grid_columnconfigure((0, 1), weight=1)
                lv_main_container.grid_rowconfigure(0, weight=1)

                # Linker Bereich – Tabelle
                self.table_container[tab_name] = ctk.CTkFrame(lv_main_container)
                self.table_container[tab_name].grid(row=0, column=0, sticky="nsew", padx=(0, 10))

                tree_scroll_y = ctk.CTkScrollbar(self.table_container[tab_name], orientation="vertical")
                tree_scroll_y.pack(side="right", fill="y")

                tree_scroll_x = ctk.CTkScrollbar(self.table_container[tab_name], orientation="horizontal")
                tree_scroll_x.pack(side="bottom", fill="x")

                self.tree[tab_name] = ttk.Treeview(
                    self.table_container[tab_name],
                    columns=columns,
                    show="headings",
                    yscrollcommand=tree_scroll_y.set,
                    xscrollcommand=tree_scroll_x.set,
                    selectmode="extended"
                )
                self.tree[tab_name].pack(expand=True, fill="both")

                tree_scroll_y.configure(command=self.tree[tab_name].yview)
                tree_scroll_x.configure(command=self.tree[tab_name].xview)

                # Einträge laden
                max_lengths = [0] * len(columns)
                for row in self.ma_obj:
                    values = row.value()
                    self.tree[tab_name].insert("", "end", values=values)
                    for i, value in enumerate(values):
                        max_lengths[i] = max(max_lengths[i], len(str(value)), 8)

                for i, col in enumerate(columns):
                    self.tree[tab_name].heading(col, text=col)
                    self.tree[tab_name].column(col, width=int(max_lengths[i] * 10 * dpi_scaling))

                # Rechter Bereich – Anzeige für Auswertung
                self.lv_display = ctk.CTkFrame(lv_main_container)
                self.lv_display.grid(row=0, column=1, sticky="nsew")

                self.lv_textbox = ctk.CTkTextbox(self.lv_display, width=350, height=400, wrap="word")
                self.lv_textbox.pack(padx=10, pady=10, fill="both", expand=True)
                self.lv_textbox.insert("0.0", "Hier erscheinen die Auswertungen der Lohnverrechnung...")
                self.lv_textbox.configure(state="disabled")  # Nur-Lese-Modus

                self.lv_textbox.bind("<Button-1>", lambda e: "break")  # Klicks im Textfeld ignorieren
                self.lv_textbox.bind("<Key>", lambda e: "break")  # Tasteneingaben im Textfeld ignorieren


                abrechnung_btn = ctk.CTkButton(self.lv_display, text="Lohnverrechnung starten", command=self.starte_abrechnung)
                abrechnung_btn.pack(pady=10)


    def starte_abrechnung(self):
        selected_items = self.tree["Lohnverrechnung"].selection()
        mitarbeiter_daten = []

        for item in selected_items:
            werte = self.tree["Lohnverrechnung"].item(item)["values"]
            mitarbeiter_daten.append(werte)

        self.lv_textbox.delete("0.0", "end")  # Textbox leeren

        if not mitarbeiter_daten:
            self.lv_textbox.insert("end", "⚠️ Kein Mitarbeiter ausgewählt.\n")
            return

        self.lv_textbox.configure(state="normal")  # Schreibmodus aktivieren
        self.lv_textbox.insert("end", f"🔍 Lohnverrechnung gestartet für {len(mitarbeiter_daten)} Mitarbeiter:innen\n\n")

        for werte in mitarbeiter_daten:
            self.ma_obj : employee.mitarbeiter = employee.mitarbeiter.select_specific(dbms=self.db_ms, id=int(werte[0]))[0]

            print(self.ma_obj.salary)
            string2print = Abrechnung.calc_brutto2netto(monat=dt.datetime.now().month, jahr=dt.datetime.now().year, stundensatz=38.5, brutto=self.ma_obj.salary)

            self.lv_textbox.insert("end", string2print + "\n\n")
        self.lv_textbox.configure(state="disabled")  # Schreibmodus deaktivieren
    def check_tab_change(self):
        """Erkennt, wenn der Tab gewechselt wurde"""
        current_tab = self.tab_view.get()
        if current_tab != self.last_tab:
            #print(f"📢 Tab gewechselt zu: {current_tab}")
            self.hide_entry_fields()
            self.last_tab = current_tab

        # Überprüfe jede 100ms auf Tab-Wechsel
        self.after(100, self.check_tab_change)
        
    def get_dpi_scaling(self):
        # Ermittelt die DPI-Skalierung
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        dpi = ctypes.windll.shcore.GetScaleFactorForDevice(0)
        return dpi / 100.0

    def reload_trees(self):
        """Lädt die Daten für alle Tabs neu in die Treeview-Tabellen."""
        for tab_name, columns in self.tabs.items():  # ✅ Korrekte Methode, um die Tab-Namen zu erhalten
            
            # Bestimme die richtige Datenquelle basierend auf dem Tab-Namen
            if tab_name == "Personalstammblatt":
                item_list = person.person.select_all(db_ms=self.db_ms)
            elif tab_name == "Mitarbeiterdaten":
                item_list = employee.mitarbeiter.select_all(dbms=self.db_ms)
            else:
                continue  # Falls es weitere Tabs gibt, die keine Tabelle enthalten
            
            # Lösche alte Einträge im Treeview
            self.tree[tab_name].delete(*self.tree[tab_name].get_children())
            
            # Füge die neuen Daten hinzu
            for row in item_list:
                self.tree[tab_name].insert("", "end", values=row.value())

        print("🔄 Alle Tabs wurden aktualisiert!")

                   
    def show_entry_fields(self, dict_item : dict [str, List [str]], mode : str, tab_name : str = None):
        """Zeigt die Eingabefelder im rechten Frame und passt das Layout an"""
        self.geometry("1440x800")
        self.main_frame.grid_columnconfigure(0, weight=3)  # Tabelle kleiner machen
        self.main_frame.grid_columnconfigure(1, weight=2)  # Eingabe-Feld sichtbar machen
        self.entry_frame.grid()  # Frame sichtbar machen

        # Alte Widgets löschen
        for widget in self.entry_frame.winfo_children():
            widget.destroy()

        self.entry_fields.clear()
        
        self.tree : dict [str, ttk.Treeview]

        # Titel für das Eingabe-Panel
        title = "Neuen Eintrag erstellen" if mode == "create" else "Eintrag aktualisieren"
        title_label = ctk.CTkLabel(self.entry_frame, text=title, font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        selected_item = self.tree[tab_name].selection()
        item_values = self.tree[tab_name].item(selected_item, "values")
        
        # Dynamische Felder erstellen
        if mode == "create":
            for col in dict_item[tab_name]:
                label = ctk.CTkLabel(self.entry_frame, text=col)
                label.pack()
                entry = ctk.CTkEntry(self.entry_frame)
                entry.pack()
                self.entry_fields[col] = entry  # Speichert die Eingabefelder
        elif mode == "update" and item_values:
            for i, col in enumerate(dict_item[tab_name]):
                label = ctk.CTkLabel(self.entry_frame, text=col)
                label.pack()
                placeholder = item_values[i] if i < len(item_values) else ""
                entry = ctk.CTkEntry(self.entry_frame)
                entry.insert(0, placeholder)
                entry.pack()
                self.entry_fields[col] = entry  # Speichert die Eingabefelder
        elif mode == "update":
            for col in dict_item[tab_name]:
                label = ctk.CTkLabel(self.entry_frame, text=col)
                label.pack()
                entry = ctk.CTkEntry(self.entry_frame)
                entry.pack()
                self.entry_fields[col] = entry  # Speichert die Eingabefelder
        else:
            print("WARNUNG: Unbekannter Modus!")

        # Speichern- und Abbrechen-Buttons
        save_btn = ctk.CTkButton(self.entry_frame, text="Speichern", command=lambda: self.save_entry(mode=mode, columnlist=dict_item[tab_name],tab_name=tab_name))
        save_btn.pack(pady=5)

        cancel_btn = ctk.CTkButton(self.entry_frame, text="Abbrechen", fg_color="gray", command=self.hide_entry_fields)
        cancel_btn.pack(pady=5)

    def hide_entry_fields(self):
        """Versteckt das Eingabe-Frame und vergrößert die Tabelle wieder"""
        self.geometry("1200x640")
        self.entry_frame.grid_remove()
        self.main_frame.grid_columnconfigure(0, weight=3)  # Tabelle wieder groß
        self.main_frame.grid_columnconfigure(1, weight=0)  # Eingabe-Feld unsichtbar

    def save_entry(self, mode : str, columnlist : List[str], tab_name : str = None):
        """Speichert neue oder geänderte Daten"""
        values = [self.entry_fields[col].get() for col in columnlist]
        print(values)

        if mode == "create":
            #db speichern
            #db laden & tree aktualisieren
            try:
                if tab_name == "Personalstammblatt":
                    result = next((obj for obj in self.pers_obj if obj.obj_id == int(values[0])), None)
                    if result is None:
                        new_entry = person.person(id=values[0], nachname=values[1], vorname=values[2], geburtsdatum=values[3], straße=values[4], hausnr=values[5], stiege_top_etc=values[6], plz=values[7], ort=values[8])
                        new_entry.insert(self.db_ms)
                        self.reload_trees()
                    else: 
                        print("WARNUNG: Person mit ID: ", result.obj_id, " existiert bereits!")
                elif tab_name == "Mitarbeiterdaten":
                    result = next((obj for obj in self.ma_obj if obj.empolyee_ID == int(values[0])), None)
                    pers_result = next((obj for obj in self.pers_obj if obj.obj_id == int(values[1])), None)
                    if result is None:
                        new_entry = employee.mitarbeiter(vorname=pers_result.name, nachname=pers_result.surname, geburtsdatum=pers_result.birthdate, eintrittsdatum=values[2], gehalt=values[3], persid=values[1], straße=pers_result.street, hausnr=pers_result.housenr, stiege_top_etc=pers_result.floor, plz=pers_result.zip, ort=pers_result.place, ma_id=values[0])
                        new_entry.insert(self.db_ms)
                        self.reload_trees()
                    else: 
                        print("WARNUNG: Person mit ID: ", result.obj_id, " existiert bereits!")
                else:
                    print("WARNUNG: Nicht existenter Tab-Name!")
            except Exception as e:
                error_message = f"""
            🚨 **Fehler während des Einfügens eines neuen Datensatzes in `{tab_name}`** 🚨
            🔹 **Fehlermeldung:** {e}
            🔹 **Aktiver GUI-Tab:** {tab_name}
            🔹 **Werte, die eingefügt werden sollten:** {values}

            📌 **Stack Trace:** 
            {traceback.format_exc()}
            """
                print(error_message)

                
            #self.tree.insert("", "end", values=values)
        elif mode == "update":
            selected_item = self.tree[tab_name].selection()
            item_values = self.tree[tab_name].item(selected_item, "values")
            if selected_item:
                try:
                    if tab_name == "Personalstammblatt":
                        selcted_pers = next((obj for obj in self.pers_obj if obj.obj_id == int(item_values[0])), None)
                        # print(selcted_pers)
                        if selcted_pers is not None:
                            print("Lösche...")
                            selcted_pers.update(self.db_ms, values)
                            self.reload_trees()
                    elif tab_name == "Mitarbeiterdaten":
                        selcted_ma = next((obj for obj in self.ma_obj if obj.empolyee_ID == int(item_values[0])), None)
                        if selcted_ma is not None:
                            print("Lösche...")
                            selcted_ma.update(self.db_ms, values)
                            self.reload_trees()
                    else:
                        print("WARNUNG: Nicht existenter Tab-Name!")
                except Exception as e:
                    error_message = f"""
                🚨 **Fehler während des Löschens eines Datensatzes in `{tab_name}`** 🚨
                🔹 **Fehlermeldung:** {e}
                🔹 **Aktiver GUI-Tab:** {tab_name}
                🔹 **Werte, die gelöscht werden sollten:** {selected_item}

                📌 **Stack Trace:** 
                {traceback.format_exc()}
                """
                    print(error_message)

        self.hide_entry_fields()  # Felder wieder verstecken

    def delete_entry(self, tab_name : str = None):
        """Löscht den ausgewählten Eintrag"""
        print("Probiere Eintrag aus ", tab_name, "zu Löschen...")
        #print(tab_name, self.tree, self.table_container)
        selected_item = self.tree[tab_name].selection()

        # print(self.pers_obj[50].obj_id)
        if selected_item:
            item_values = self.tree[tab_name].item(selected_item, "values")
            print(f"Ausgewählte Zeile: {item_values}")
            try:
                if tab_name == "Personalstammblatt":
                    selcted_pers = next((obj for obj in self.pers_obj if obj.obj_id == int(item_values[0])), None)
                    # print(selcted_pers)
                    if selcted_pers is not None:
                        print("Lösche...")
                        selcted_pers.delete(self.db_ms)
                        self.reload_trees()
                elif tab_name == "Mitarbeiterdaten":
                    selcted_ma = next((obj for obj in self.ma_obj if obj.empolyee_ID == int(item_values[0])), None)
                    if selcted_ma is not None:
                        print("Lösche...")
                        selcted_ma.delete(self.db_ms)
                        self.reload_trees()
                else:
                    print("WARNUNG: Nicht existenter Tab-Name!")
            except Exception as e:
                error_message = f"""
            🚨 **Fehler während des Löschens eines Datensatzes in `{tab_name}`** 🚨
            🔹 **Fehlermeldung:** {e}
            🔹 **Aktiver GUI-Tab:** {tab_name}
            🔹 **Werte, die gelöscht werden sollten:** {selected_item}

            📌 **Stack Trace:** 
            {traceback.format_exc()}
            """
                print(error_message)


if __name__ == "__main__":
    print("test")
    #app = MyGUI()
    #app.mainloop()
