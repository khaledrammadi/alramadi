"""
نماذج البيانات لبرنامج رواتب الموظفين
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Employee:
    """نموذج بيانات الموظف"""
    id: Optional[int] = None
    name: str = ""
    employee_id: str = ""
    position: str = ""
    department: str = ""
    base_salary: float = 0.0
    hire_date: datetime = None
    phone: str = ""
    email: str = ""
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.hire_date is None:
            self.hire_date = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class Salary:
    """نموذج بيانات الراتب"""
    id: Optional[int] = None
    employee_id: int = 0
    amount: float = 0.0
    month: int = 0
    year: int = 0
    payment_date: datetime = None
    notes: str = ""
    created_at: datetime = None

    def __post_init__(self):
        if self.payment_date is None:
            self.payment_date = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Commission:
    """نموذج بيانات العمولة"""
    id: Optional[int] = None
    employee_id: int = 0
    amount: float = 0.0
    description: str = ""
    commission_date: datetime = None
    commission_type: str = "sales"  # sales, performance, bonus
    notes: str = ""
    created_at: datetime = None

    def __post_init__(self):
        if self.commission_date is None:
            self.commission_date = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class Transfer:
    """نموذج بيانات الحوالة"""
    id: Optional[int] = None
    employee_id: int = 0
    amount: float = 0.0
    sender_name: str = ""
    transfer_date: datetime = None
    reference_number: str = ""
    transfer_type: str = "bank"  # bank, cash, online
    notes: str = ""
    created_at: datetime = None

    def __post_init__(self):
        if self.transfer_date is None:
            self.transfer_date = datetime.now()
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class AccountStatement:
    """نموذج كشف الحساب"""
    employee: Employee
    salaries: List[Salary]
    commissions: List[Commission]
    transfers: List[Transfer]
    start_date: datetime
    end_date: datetime
    total_salary: float = 0.0
    total_commissions: float = 0.0
    total_transfers: float = 0.0
    grand_total: float = 0.0

    def __post_init__(self):
        self.calculate_totals()

    def calculate_totals(self):
        """حساب المجاميع"""
        self.total_salary = sum(salary.amount for salary in self.salaries)
        self.total_commissions = sum(commission.amount for commission in self.commissions)
        self.total_transfers = sum(transfer.amount for transfer in self.transfers)
        self.grand_total = self.total_salary + self.total_commissions + self.total_transfers
