"""
Payroll module for managing salary calculations and payroll records
Works with the new database schema (lohnverrechnung_dn table)
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from modules import dbms

class PayrollManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = dbms.dbms(db_path)
    
    def get_employee_payroll_history(self, empl_id: int) -> List[Dict]:
        """Get payroll history for an employee using EMPL_ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT l.*, p.PERS_FIRSTNAME, p.PERS_SURNAME
            FROM lohnverrechnung_dn l
            JOIN MITARBEITER m ON l.lv_dn_empl_id = m.EMPL_ID
            JOIN PERSON p ON m.PERS_ID = p.PERS_ID
            WHERE l.lv_dn_empl_id = ?
            ORDER BY l.lv_dn_monat DESC
        '''
        cursor.execute(query, (empl_id,))
        results = cursor.fetchall()
        conn.close()
        
        columns = [
            'lv_dn_id', 'lv_dn_empl_id', 'lv_dn_monat', 'lv_dn_stundensatz', 'lv_dn_wochenstunden', 'lv_dn_brutto',
            'lv_dn_mehrstunden0', 'lv_dn_mehrstunden25', 'lv_dn_mehrstunden50', 'lv_dn_ueberstunden50', 'lv_dn_ueberstunden100',
            'lv_dn_sonderzahlungen', 'lv_dn_sachbezug', 'lv_dn_diäten', 'lv_dn_reisekosten', 'lv_dn_jahressechstel',
            'FIRSTNAME', 'SURNAME'
        ]
        
        return [dict(zip(columns, row)) for row in results]
    
    def get_tax_benefits(self, empl_id: int) -> Dict:
        """Get tax benefits for an employee"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT stv_freibetrag, stv_pendlerpauschale, stv_pendlereuro, 
                   stv_anzahl_kinder_avab, stv_anspruch_fabo, stv_gewerkschaft
            FROM steuerliche_vorteile
            WHERE stv_empl_id = ?
        ''', (empl_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'freibetrag': result[0] or 0,
                'pendlerpauschale': result[1] or 0,
                'pendlereuro': result[2] or 0,
                'anzahl_kinder_avab': result[3] or 0,
                'anspruch_fabo': result[4] or 0,
                'gewerkschaft': result[5] or 0
            }
        return {
            'freibetrag': 0,
            'pendlerpauschale': 0,
            'pendlereuro': 0,
            'anzahl_kinder_avab': 0,
            'anspruch_fabo': 0,
            'gewerkschaft': 0
        }
    
    def save_tax_benefits(self, empl_id: int, benefits: Dict) -> bool:
        """Save or update tax benefits for an employee"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute('SELECT stv_id FROM steuerliche_vorteile WHERE stv_empl_id = ?', (empl_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update
                cursor.execute('''
                    UPDATE steuerliche_vorteile SET
                        stv_freibetrag = ?,
                        stv_pendlerpauschale = ?,
                        stv_pendlereuro = ?,
                        stv_anzahl_kinder_avab = ?,
                        stv_anspruch_fabo = ?,
                        stv_gewerkschaft = ?
                    WHERE stv_empl_id = ?
                ''', (
                    benefits.get('freibetrag', 0),
                    benefits.get('pendlerpauschale', 0),
                    benefits.get('pendlereuro', 0),
                    benefits.get('anzahl_kinder_avab', 0),
                    benefits.get('anspruch_fabo', 0),
                    benefits.get('gewerkschaft', 0),
                    empl_id
                ))
            else:
                # Insert
                cursor.execute('''
                    INSERT INTO steuerliche_vorteile (
                        stv_empl_id, stv_freibetrag, stv_pendlerpauschale, stv_pendlereuro,
                        stv_anzahl_kinder_avab, stv_anspruch_fabo, stv_gewerkschaft
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    empl_id,
                    benefits.get('freibetrag', 0),
                    benefits.get('pendlerpauschale', 0),
                    benefits.get('pendlereuro', 0),
                    benefits.get('anzahl_kinder_avab', 0),
                    benefits.get('anspruch_fabo', 0),
                    benefits.get('gewerkschaft', 0)
                ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving tax benefits: {e}")
            return False
    
    def create_payroll_record(self, payroll_data: Dict) -> bool:
        """Create a new payroll record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if record already exists for this employee and month
            cursor.execute('''
                SELECT COUNT(*) FROM lohnverrechnung_dn 
                WHERE lv_dn_empl_id = ? AND lv_dn_monat = ?
            ''', (payroll_data['lv_dn_empl_id'], payroll_data['lv_dn_monat']))
            
            if cursor.fetchone()[0] > 0:
                conn.close()
                return False  # Record already exists
            
            query = '''
                INSERT INTO lohnverrechnung_dn (
                    lv_dn_empl_id, lv_dn_monat, lv_dn_stundensatz, lv_dn_wochenstunden, lv_dn_brutto,
                    lv_dn_mehrstunden0, lv_dn_mehrstunden25, lv_dn_mehrstunden50, 
                    lv_dn_ueberstunden50, lv_dn_ueberstunden100,
                    lv_dn_sonderzahlungen, lv_dn_sachbezug, lv_dn_diäten, 
                    lv_dn_reisekosten, lv_dn_jahressechstel
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            values = (
                payroll_data['lv_dn_empl_id'], 
                payroll_data['lv_dn_monat'], 
                payroll_data.get('lv_dn_stundensatz', 38.5),
                payroll_data.get('lv_dn_wochenstunden', 38.5), 
                payroll_data['lv_dn_brutto'],
                payroll_data.get('lv_dn_mehrstunden0', 0), 
                payroll_data.get('lv_dn_mehrstunden25', 0),
                payroll_data.get('lv_dn_mehrstunden50', 0), 
                payroll_data.get('lv_dn_ueberstunden50', 0),
                payroll_data.get('lv_dn_ueberstunden100', 0), 
                payroll_data.get('lv_dn_sonderzahlungen', 0),
                payroll_data.get('lv_dn_sachbezug', 0), 
                payroll_data.get('lv_dn_diäten', 0),
                payroll_data.get('lv_dn_reisekosten', 0), 
                payroll_data.get('lv_dn_jahressechstel', 0)
            )
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error creating payroll record: {e}")
            return False
    
    def update_payroll_record(self, lv_dn_id: int, payroll_data: Dict) -> bool:
        """Update an existing payroll record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                UPDATE lohnverrechnung_dn SET
                    lv_dn_stundensatz = ?, lv_dn_wochenstunden = ?, lv_dn_brutto = ?,
                    lv_dn_mehrstunden0 = ?, lv_dn_mehrstunden25 = ?, lv_dn_mehrstunden50 = ?,
                    lv_dn_ueberstunden50 = ?, lv_dn_ueberstunden100 = ?, lv_dn_sonderzahlungen = ?,
                    lv_dn_sachbezug = ?, lv_dn_diäten = ?, lv_dn_reisekosten = ?,
                    lv_dn_jahressechstel = ?
                WHERE lv_dn_id = ?
            '''
            
            values = (
                payroll_data.get('lv_dn_stundensatz', 38.5), 
                payroll_data.get('lv_dn_wochenstunden', 38.5),
                payroll_data['lv_dn_brutto'], 
                payroll_data.get('lv_dn_mehrstunden0', 0),
                payroll_data.get('lv_dn_mehrstunden25', 0), 
                payroll_data.get('lv_dn_mehrstunden50', 0),
                payroll_data.get('lv_dn_ueberstunden50', 0), 
                payroll_data.get('lv_dn_ueberstunden100', 0),
                payroll_data.get('lv_dn_sonderzahlungen', 0), 
                payroll_data.get('lv_dn_sachbezug', 0),
                payroll_data.get('lv_dn_diäten', 0), 
                payroll_data.get('lv_dn_reisekosten', 0),
                payroll_data.get('lv_dn_jahressechstel', 0), 
                lv_dn_id
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
            WHERE m.EMPL_VALID_TO > datetime('now')
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
            FROM lohnverrechnung_dn l
            JOIN MITARBEITER m ON l.lv_dn_empl_id = m.EMPL_ID
            JOIN PERSON p ON m.PERS_ID = p.PERS_ID
            WHERE l.lv_dn_monat = ?
            ORDER BY p.PERS_SURNAME, p.PERS_FIRSTNAME
        '''
        cursor.execute(query, (month,))
        results = cursor.fetchall()
        conn.close()
        
        columns = [
            'lv_dn_id', 'lv_dn_empl_id', 'lv_dn_monat', 'lv_dn_stundensatz', 'lv_dn_wochenstunden', 'lv_dn_brutto',
            'lv_dn_mehrstunden0', 'lv_dn_mehrstunden25', 'lv_dn_mehrstunden50', 'lv_dn_ueberstunden50', 'lv_dn_ueberstunden100',
            'lv_dn_sonderzahlungen', 'lv_dn_sachbezug', 'lv_dn_diäten', 'lv_dn_reisekosten', 'lv_dn_jahressechstel',
            'FIRSTNAME', 'SURNAME'
        ]
        
        return [dict(zip(columns, row)) for row in results]