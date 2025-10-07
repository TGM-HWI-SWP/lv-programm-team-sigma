"""
Payroll module for managing salary calculations and payroll records
Works with the existing LOHNABRECHNUNG table structure
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from modules import dbms

class PayrollManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = dbms.dbms(db_path)
    
    def get_employee_payroll_history(self, pers_id: int) -> List[Dict]:
        """Get payroll history for an employee"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT l.*, p.PERS_FIRSTNAME, p.PERS_SURNAME
            FROM LOHNABRECHNUNG l
            JOIN PERSON p ON l.PERS_ID = p.PERS_ID
            WHERE l.PERS_ID = ?
            ORDER BY l.MONAT DESC
        '''
        cursor.execute(query, (pers_id,))
        results = cursor.fetchall()
        conn.close()
        
        columns = [
            'LOHN_ID', 'PERS_ID', 'MONAT', 'STUNDENSATZ', 'WOCHENSTUNDEN', 'BRUTTO',
            'MEHRSTUNDEN0', 'MEHRSTUNDEN25', 'MEHRSTUNDEN50', 'ÜBERSTUNDEN50', 'ÜBERSTUNDEN100',
            'SONDERZAHLUNGEN', 'SACHBEZUG', 'DIÄTEN', 'REISEKOSTEN', 'FREIBETRAGSBESCHEID',
            'PENDLERPAUSCHALE', 'PENDLEREURO', 'ANZAHL_KINDER_AVAB', 'ANSPRUCH_FABO',
            'GEWERKSCHAFTSMITGLIED', 'JAHRESSECHSTEL', 'FIRSTNAME', 'SURNAME'
        ]
        
        return [dict(zip(columns, row)) for row in results]
    
    def create_payroll_record(self, payroll_data: Dict) -> bool:
        """Create a new payroll record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if record already exists for this person and month
            cursor.execute('''
                SELECT COUNT(*) FROM LOHNABRECHNUNG 
                WHERE PERS_ID = ? AND MONAT = ?
            ''', (payroll_data['PERS_ID'], payroll_data['MONAT']))
            
            if cursor.fetchone()[0] > 0:
                conn.close()
                return False  # Record already exists
            
            query = '''
                INSERT INTO LOHNABRECHNUNG (
                    PERS_ID, MONAT, STUNDENSATZ, WOCHENSTUNDEN, BRUTTO,
                    MEHRSTUNDEN0, MEHRSTUNDEN25, MEHRSTUNDEN50, ÜBERSTUNDEN50, ÜBERSTUNDEN100,
                    SONDERZAHLUNGEN, SACHBEZUG, DIÄTEN, REISEKOSTEN, FREIBETRAGSBESCHEID,
                    PENDLERPAUSCHALE, PENDLEREURO, ANZAHL_KINDER_AVAB, ANSPRUCH_FABO,
                    GEWERKSCHAFTSMITGLIED, JAHRESSECHSTEL
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                payroll_data['PERS_ID'], payroll_data['MONAT'], payroll_data.get('STUNDENSATZ', 38.5),
                payroll_data.get('WOCHENSTUNDEN', 38.5), payroll_data['BRUTTO'],
                payroll_data.get('MEHRSTUNDEN0', 0), payroll_data.get('MEHRSTUNDEN25', 0),
                payroll_data.get('MEHRSTUNDEN50', 0), payroll_data.get('ÜBERSTUNDEN50', 0),
                payroll_data.get('ÜBERSTUNDEN100', 0), payroll_data.get('SONDERZAHLUNGEN', 0),
                payroll_data.get('SACHBEZUG', 0), payroll_data.get('DIÄTEN', 0),
                payroll_data.get('REISEKOSTEN', 0), payroll_data.get('FREIBETRAGSBESCHEID', 0),
                payroll_data.get('PENDLERPAUSCHALE', 0), payroll_data.get('PENDLEREURO', 0),
                payroll_data.get('ANZAHL_KINDER_AVAB', 0), payroll_data.get('ANSPRUCH_FABO', 0),
                payroll_data.get('GEWERKSCHAFTSMITGLIED', 0), payroll_data.get('JAHRESSECHSTEL', 0)
            )
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error creating payroll record: {e}")
            return False
    
    def update_payroll_record(self, lohn_id: int, payroll_data: Dict) -> bool:
        """Update an existing payroll record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                UPDATE LOHNABRECHNUNG SET
                    STUNDENSATZ = ?, WOCHENSTUNDEN = ?, BRUTTO = ?,
                    MEHRSTUNDEN0 = ?, MEHRSTUNDEN25 = ?, MEHRSTUNDEN50 = ?,
                    ÜBERSTUNDEN50 = ?, ÜBERSTUNDEN100 = ?, SONDERZAHLUNGEN = ?,
                    SACHBEZUG = ?, DIÄTEN = ?, REISEKOSTEN = ?,
                    FREIBETRAGSBESCHEID = ?, PENDLERPAUSCHALE = ?, PENDLEREURO = ?,
                    ANZAHL_KINDER_AVAB = ?, ANSPRUCH_FABO = ?, GEWERKSCHAFTSMITGLIED = ?,
                    JAHRESSECHSTEL = ?
                WHERE LOHN_ID = ?
            '''
            
            values = (
                payroll_data.get('STUNDENSATZ', 38.5), payroll_data.get('WOCHENSTUNDEN', 38.5),
                payroll_data['BRUTTO'], payroll_data.get('MEHRSTUNDEN0', 0),
                payroll_data.get('MEHRSTUNDEN25', 0), payroll_data.get('MEHRSTUNDEN50', 0),
                payroll_data.get('ÜBERSTUNDEN50', 0), payroll_data.get('ÜBERSTUNDEN100', 0),
                payroll_data.get('SONDERZAHLUNGEN', 0), payroll_data.get('SACHBEZUG', 0),
                payroll_data.get('DIÄTEN', 0), payroll_data.get('REISEKOSTEN', 0),
                payroll_data.get('FREIBETRAGSBESCHEID', 0), payroll_data.get('PENDLERPAUSCHALE', 0),
                payroll_data.get('PENDLEREURO', 0), payroll_data.get('ANZAHL_KINDER_AVAB', 0),
                payroll_data.get('ANSPRUCH_FABO', 0), payroll_data.get('GEWERKSCHAFTSMITGLIED', 0),
                payroll_data.get('JAHRESSECHSTEL', 0), lohn_id
            )
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating payroll record: {e}")
            return False
    
    def get_all_employees_for_payroll(self) -> List[Dict]:
        """Get all employees with their current salary information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT m.EMPL_ID, m.PERS_ID, p.PERS_FIRSTNAME, p.PERS_SURNAME, 
                   m.EMPL_BRUTTOGEHALT, m.EMPL_ENTRYDATE
            FROM MITARBEITER m
            JOIN PERSON p ON m.PERS_ID = p.PERS_ID
            ORDER BY p.PERS_SURNAME, p.PERS_FIRSTNAME
        '''
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        employees = []
        for row in results:
            employees.append({
                'EMPL_ID': row[0],
                'PERS_ID': row[1],
                'FIRSTNAME': row[2],
                'SURNAME': row[3],
                'SALARY': self._convert_salary(row[4]),
                'ENTRY_DATE': row[5],
                'FULL_NAME': f"{row[2]} {row[3]}"
            })
        
        return employees
    
    def _convert_salary(self, salary) -> float:
        """Convert salary from string format to float"""
        try:
            if isinstance(salary, str):
                # Handle German number format (comma as decimal separator)
                salary = salary.replace(',', '.')
                return float(salary)
            return float(salary)
        except:
            return 0.0
    
    def get_monthly_payroll_summary(self, month: str) -> List[Dict]:
        """Get payroll summary for a specific month"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT l.*, p.PERS_FIRSTNAME, p.PERS_SURNAME
            FROM LOHNABRECHNUNG l
            JOIN PERSON p ON l.PERS_ID = p.PERS_ID
            WHERE l.MONAT = ?
            ORDER BY p.PERS_SURNAME, p.PERS_FIRSTNAME
        '''
        cursor.execute(query, (month,))
        results = cursor.fetchall()
        conn.close()
        
        columns = [
            'LOHN_ID', 'PERS_ID', 'MONAT', 'STUNDENSATZ', 'WOCHENSTUNDEN', 'BRUTTO',
            'MEHRSTUNDEN0', 'MEHRSTUNDEN25', 'MEHRSTUNDEN50', 'ÜBERSTUNDEN50', 'ÜBERSTUNDEN100',
            'SONDERZAHLUNGEN', 'SACHBEZUG', 'DIÄTEN', 'REISEKOSTEN', 'FREIBETRAGSBESCHEID',
            'PENDLERPAUSCHALE', 'PENDLEREURO', 'ANZAHL_KINDER_AVAB', 'ANSPRUCH_FABO',
            'GEWERKSCHAFTSMITGLIED', 'JAHRESSECHSTEL', 'FIRSTNAME', 'SURNAME'
        ]
        
        return [dict(zip(columns, row)) for row in results]