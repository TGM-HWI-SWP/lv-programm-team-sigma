import ctypes
import modules.dbms as dbms
import modules.employee as emp
import modules.person as p
import modules.gui as gui

def set_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception as e:
        print(f"Error setting DPI awareness: {e}")

if __name__ == "__main__":

    set_dpi_awareness()
    print("Hello World!")
    db_name = "stammdatenverwaltung.db"
    db_ms = dbms.dbms(db_name)


    
    p.person.initialize_db_table(db_ms=db_ms)
    emp.mitarbeiter.initialize_db_table(dbms=db_ms)


    GUI = gui.MyGUI(db_ms=db_ms)

    GUI.mainloop()
    
