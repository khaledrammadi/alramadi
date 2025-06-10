"""
إدارة قاعدة البيانات لبرنامج رواتب الموظفين
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from models import Employee, Salary, Commission, Transfer


class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self, db_path: str = "employee_payroll.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """إنشاء اتصال بقاعدة البيانات"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """إنشاء جداول قاعدة البيانات"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # جدول الموظفين
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    employee_id TEXT UNIQUE NOT NULL,
                    position TEXT,
                    department TEXT,
                    base_salary REAL DEFAULT 0,
                    hire_date TEXT,
                    phone TEXT,
                    email TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # جدول الرواتب
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS salaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    amount REAL NOT NULL,
                    month INTEGER,
                    year INTEGER,
                    payment_date TEXT,
                    notes TEXT,
                    created_at TEXT,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            """)
            
            # جدول العمولات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS commissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    amount REAL NOT NULL,
                    description TEXT,
                    commission_date TEXT,
                    commission_type TEXT DEFAULT 'sales',
                    notes TEXT,
                    created_at TEXT,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            """)
            
            # جدول الحوالات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER,
                    amount REAL NOT NULL,
                    sender_name TEXT,
                    transfer_date TEXT,
                    reference_number TEXT,
                    transfer_type TEXT DEFAULT 'bank',
                    notes TEXT,
                    created_at TEXT,
                    FOREIGN KEY (employee_id) REFERENCES employees (id)
                )
            """)
            
            conn.commit()
    
    # وظائف الموظفين
    def add_employee(self, employee: Employee) -> int:
        """إضافة موظف جديد"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO employees (name, employee_id, position, department, 
                                     base_salary, hire_date, phone, email, 
                                     is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee.name, employee.employee_id, employee.position,
                employee.department, employee.base_salary,
                employee.hire_date.isoformat(), employee.phone, employee.email,
                employee.is_active, employee.created_at.isoformat(),
                employee.updated_at.isoformat()
            ))
            return cursor.lastrowid
    
    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """الحصول على بيانات موظف"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_employee(row)
            return None
    
    def get_all_employees(self) -> List[Employee]:
        """الحصول على جميع الموظفين"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees WHERE is_active = 1 ORDER BY name")
            rows = cursor.fetchall()
            return [self._row_to_employee(row) for row in rows]
    
    def update_employee(self, employee: Employee):
        """تحديث بيانات موظف"""
        employee.updated_at = datetime.now()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE employees SET name=?, position=?, department=?, 
                                   base_salary=?, phone=?, email=?, updated_at=?
                WHERE id=?
            """, (
                employee.name, employee.position, employee.department,
                employee.base_salary, employee.phone, employee.email,
                employee.updated_at.isoformat(), employee.id
            ))
    
    def _row_to_employee(self, row) -> Employee:
        """تحويل صف قاعدة البيانات إلى كائن موظف"""
        return Employee(
            id=row[0], name=row[1], employee_id=row[2], position=row[3],
            department=row[4], base_salary=row[5],
            hire_date=datetime.fromisoformat(row[6]) if row[6] else None,
            phone=row[7], email=row[8], is_active=bool(row[9]),
            created_at=datetime.fromisoformat(row[10]) if row[10] else None,
            updated_at=datetime.fromisoformat(row[11]) if row[11] else None
        )

    # وظائف الرواتب
    def add_salary(self, salary: Salary) -> int:
        """إضافة راتب"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO salaries (employee_id, amount, month, year,
                                    payment_date, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                salary.employee_id, salary.amount, salary.month, salary.year,
                salary.payment_date.isoformat(), salary.notes,
                salary.created_at.isoformat()
            ))
            return cursor.lastrowid

    def get_employee_salaries(self, employee_id: int, start_date: datetime = None,
                            end_date: datetime = None) -> List[Salary]:
        """الحصول على رواتب موظف"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM salaries WHERE employee_id = ?"
            params = [employee_id]

            if start_date:
                query += " AND payment_date >= ?"
                params.append(start_date.isoformat())
            if end_date:
                query += " AND payment_date <= ?"
                params.append(end_date.isoformat())

            query += " ORDER BY payment_date DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_salary(row) for row in rows]

    def _row_to_salary(self, row) -> Salary:
        """تحويل صف قاعدة البيانات إلى كائن راتب"""
        return Salary(
            id=row[0], employee_id=row[1], amount=row[2], month=row[3],
            year=row[4],
            payment_date=datetime.fromisoformat(row[5]) if row[5] else None,
            notes=row[6],
            created_at=datetime.fromisoformat(row[7]) if row[7] else None
        )

    # وظائف العمولات
    def add_commission(self, commission: Commission) -> int:
        """إضافة عمولة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO commissions (employee_id, amount, description,
                                       commission_date, commission_type, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                commission.employee_id, commission.amount, commission.description,
                commission.commission_date.isoformat(), commission.commission_type,
                commission.notes, commission.created_at.isoformat()
            ))
            return cursor.lastrowid

    def get_employee_commissions(self, employee_id: int, start_date: datetime = None,
                               end_date: datetime = None) -> List[Commission]:
        """الحصول على عمولات موظف"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM commissions WHERE employee_id = ?"
            params = [employee_id]

            if start_date:
                query += " AND commission_date >= ?"
                params.append(start_date.isoformat())
            if end_date:
                query += " AND commission_date <= ?"
                params.append(end_date.isoformat())

            query += " ORDER BY commission_date DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_commission(row) for row in rows]

    def _row_to_commission(self, row) -> Commission:
        """تحويل صف قاعدة البيانات إلى كائن عمولة"""
        return Commission(
            id=row[0], employee_id=row[1], amount=row[2], description=row[3],
            commission_date=datetime.fromisoformat(row[4]) if row[4] else None,
            commission_type=row[5], notes=row[6],
            created_at=datetime.fromisoformat(row[7]) if row[7] else None
        )

    # وظائف الحوالات
    def add_transfer(self, transfer: Transfer) -> int:
        """إضافة حوالة"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transfers (employee_id, amount, sender_name,
                                     transfer_date, reference_number, transfer_type,
                                     notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transfer.employee_id, transfer.amount, transfer.sender_name,
                transfer.transfer_date.isoformat(), transfer.reference_number,
                transfer.transfer_type, transfer.notes, transfer.created_at.isoformat()
            ))
            return cursor.lastrowid

    def get_employee_transfers(self, employee_id: int, start_date: datetime = None,
                             end_date: datetime = None) -> List[Transfer]:
        """الحصول على حوالات موظف"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM transfers WHERE employee_id = ?"
            params = [employee_id]

            if start_date:
                query += " AND transfer_date >= ?"
                params.append(start_date.isoformat())
            if end_date:
                query += " AND transfer_date <= ?"
                params.append(end_date.isoformat())

            query += " ORDER BY transfer_date DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_transfer(row) for row in rows]

    def _row_to_transfer(self, row) -> Transfer:
        """تحويل صف قاعدة البيانات إلى كائن حوالة"""
        return Transfer(
            id=row[0], employee_id=row[1], amount=row[2], sender_name=row[3],
            transfer_date=datetime.fromisoformat(row[4]) if row[4] else None,
            reference_number=row[5], transfer_type=row[6], notes=row[7],
            created_at=datetime.fromisoformat(row[8]) if row[8] else None
        )
