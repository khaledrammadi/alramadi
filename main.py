"""
برنامج إدارة رواتب الموظفين
الملف الرئيسي وواجهة المستخدم
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os

from database import DatabaseManager
from models import Employee, Salary, Commission, Transfer
from reports import ReportGenerator
from utils import (validate_employee_data, validate_financial_entry, 
                  format_currency, parse_date, format_date, clean_text)


class PayrollApp:
    """تطبيق إدارة الرواتب"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("برنامج إدارة رواتب الموظفين")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # إنشاء قاعدة البيانات ومولد التقارير
        self.db_manager = DatabaseManager()
        self.report_generator = ReportGenerator(self.db_manager)
        
        # المتغيرات
        self.selected_employee_id = None
        
        self.setup_ui()
        self.refresh_employee_list()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # إنشاء النوتبوك للتبويبات
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # تبويب الموظفين
        self.setup_employees_tab()
        
        # تبويب الرواتب
        self.setup_salaries_tab()
        
        # تبويب العمولات
        self.setup_commissions_tab()
        
        # تبويب الحوالات
        self.setup_transfers_tab()
        
        # تبويب التقارير
        self.setup_reports_tab()
    
    def setup_employees_tab(self):
        """إعداد تبويب الموظفين"""
        self.employees_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.employees_frame, text="الموظفين")
        
        # إطار البحث والأزرار
        search_frame = ttk.Frame(self.employees_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="البحث:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', self.search_employees)
        
        ttk.Button(search_frame, text="موظف جديد", 
                  command=self.add_employee_dialog).pack(side=tk.RIGHT, padx=5)
        
        # قائمة الموظفين
        list_frame = ttk.Frame(self.employees_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # إنشاء Treeview
        columns = ("ID", "الاسم", "رقم الموظف", "المنصب", "القسم", "الراتب الأساسي")
        self.employees_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # تعيين عناوين الأعمدة
        for col in columns:
            self.employees_tree.heading(col, text=col)
            self.employees_tree.column(col, width=150)
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.employees_tree.yview)
        self.employees_tree.configure(yscrollcommand=scrollbar.set)
        
        self.employees_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ربط الأحداث
        self.employees_tree.bind('<Double-1>', self.edit_employee_dialog)
        self.employees_tree.bind('<Button-1>', self.select_employee)
        
        # إطار الأزرار
        buttons_frame = ttk.Frame(self.employees_frame)
        buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(buttons_frame, text="تعديل", 
                  command=self.edit_employee_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="حذف", 
                  command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="تحديث", 
                  command=self.refresh_employee_list).pack(side=tk.LEFT, padx=5)
    
    def setup_salaries_tab(self):
        """إعداد تبويب الرواتب"""
        self.salaries_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.salaries_frame, text="الرواتب")
        
        # إطار اختيار الموظف
        employee_frame = ttk.LabelFrame(self.salaries_frame, text="اختيار الموظف")
        employee_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.salary_employee_var = tk.StringVar()
        self.salary_employee_combo = ttk.Combobox(employee_frame, textvariable=self.salary_employee_var, 
                                                 state="readonly", width=50)
        self.salary_employee_combo.pack(padx=10, pady=10)
        
        # إطار إدخال الراتب
        input_frame = ttk.LabelFrame(self.salaries_frame, text="إضافة راتب جديد")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # الصف الأول
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1, text="المبلغ:").pack(side=tk.LEFT, padx=5)
        self.salary_amount_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.salary_amount_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="الشهر:").pack(side=tk.LEFT, padx=5)
        self.salary_month_var = tk.StringVar(value=str(datetime.now().month))
        ttk.Entry(row1, textvariable=self.salary_month_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="السنة:").pack(side=tk.LEFT, padx=5)
        self.salary_year_var = tk.StringVar(value=str(datetime.now().year))
        ttk.Entry(row1, textvariable=self.salary_year_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # الصف الثاني
        row2 = ttk.Frame(input_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2, text="تاريخ الدفع:").pack(side=tk.LEFT, padx=5)
        self.salary_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(row2, textvariable=self.salary_date_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="ملاحظات:").pack(side=tk.LEFT, padx=5)
        self.salary_notes_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.salary_notes_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row2, text="إضافة راتب", 
                  command=self.add_salary).pack(side=tk.RIGHT, padx=5)
        
        # قائمة الرواتب
        list_frame = ttk.LabelFrame(self.salaries_frame, text="رواتب الموظف المحدد")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("التاريخ", "الشهر", "السنة", "المبلغ", "ملاحظات")
        self.salaries_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.salaries_tree.heading(col, text=col)
            self.salaries_tree.column(col, width=120)
        
        scrollbar2 = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.salaries_tree.yview)
        self.salaries_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.salaries_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ربط تغيير الموظف
        self.salary_employee_combo.bind('<<ComboboxSelected>>', self.load_employee_salaries)
    
    def setup_commissions_tab(self):
        """إعداد تبويب العمولات"""
        self.commissions_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.commissions_frame, text="العمولات")
        
        # إطار اختيار الموظف
        employee_frame = ttk.LabelFrame(self.commissions_frame, text="اختيار الموظف")
        employee_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.commission_employee_var = tk.StringVar()
        self.commission_employee_combo = ttk.Combobox(employee_frame, textvariable=self.commission_employee_var, 
                                                     state="readonly", width=50)
        self.commission_employee_combo.pack(padx=10, pady=10)
        
        # إطار إدخال العمولة
        input_frame = ttk.LabelFrame(self.commissions_frame, text="إضافة عمولة جديدة")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # الصف الأول
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row1, text="المبلغ:").pack(side=tk.LEFT, padx=5)
        self.commission_amount_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.commission_amount_var, width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="النوع:").pack(side=tk.LEFT, padx=5)
        self.commission_type_var = tk.StringVar(value="sales")
        type_combo = ttk.Combobox(row1, textvariable=self.commission_type_var, 
                                 values=["sales", "performance", "bonus"], width=12)
        type_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row1, text="التاريخ:").pack(side=tk.LEFT, padx=5)
        self.commission_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(row1, textvariable=self.commission_date_var, width=15).pack(side=tk.LEFT, padx=5)
        
        # الصف الثاني
        row2 = ttk.Frame(input_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(row2, text="الوصف:").pack(side=tk.LEFT, padx=5)
        self.commission_desc_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.commission_desc_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(row2, text="ملاحظات:").pack(side=tk.LEFT, padx=5)
        self.commission_notes_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.commission_notes_var, width=25).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(row2, text="إضافة عمولة", 
                  command=self.add_commission).pack(side=tk.RIGHT, padx=5)
        
        # قائمة العمولات
        list_frame = ttk.LabelFrame(self.commissions_frame, text="عمولات الموظف المحدد")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("التاريخ", "النوع", "الوصف", "المبلغ", "ملاحظات")
        self.commissions_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.commissions_tree.heading(col, text=col)
            self.commissions_tree.column(col, width=120)
        
        scrollbar3 = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.commissions_tree.yview)
        self.commissions_tree.configure(yscrollcommand=scrollbar3.set)
        
        self.commissions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar3.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ربط تغيير الموظف
        self.commission_employee_combo.bind('<<ComboboxSelected>>', self.load_employee_commissions)

    def setup_transfers_tab(self):
        """إعداد تبويب الحوالات"""
        self.transfers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.transfers_frame, text="الحوالات")

        # إطار اختيار الموظف
        employee_frame = ttk.LabelFrame(self.transfers_frame, text="اختيار الموظف")
        employee_frame.pack(fill=tk.X, padx=5, pady=5)

        self.transfer_employee_var = tk.StringVar()
        self.transfer_employee_combo = ttk.Combobox(employee_frame, textvariable=self.transfer_employee_var,
                                                   state="readonly", width=50)
        self.transfer_employee_combo.pack(padx=10, pady=10)

        # إطار إدخال الحوالة
        input_frame = ttk.LabelFrame(self.transfers_frame, text="إضافة حوالة جديدة")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        # الصف الأول
        row1 = ttk.Frame(input_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row1, text="المبلغ:").pack(side=tk.LEFT, padx=5)
        self.transfer_amount_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.transfer_amount_var, width=15).pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="اسم المرسل:").pack(side=tk.LEFT, padx=5)
        self.transfer_sender_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.transfer_sender_var, width=20).pack(side=tk.LEFT, padx=5)

        ttk.Label(row1, text="التاريخ:").pack(side=tk.LEFT, padx=5)
        self.transfer_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(row1, textvariable=self.transfer_date_var, width=15).pack(side=tk.LEFT, padx=5)

        # الصف الثاني
        row2 = ttk.Frame(input_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row2, text="رقم المرجع:").pack(side=tk.LEFT, padx=5)
        self.transfer_ref_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.transfer_ref_var, width=20).pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="النوع:").pack(side=tk.LEFT, padx=5)
        self.transfer_type_var = tk.StringVar(value="bank")
        type_combo = ttk.Combobox(row2, textvariable=self.transfer_type_var,
                                 values=["bank", "cash", "online"], width=12)
        type_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="ملاحظات:").pack(side=tk.LEFT, padx=5)
        self.transfer_notes_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.transfer_notes_var, width=20).pack(side=tk.LEFT, padx=5)

        ttk.Button(row2, text="إضافة حوالة",
                  command=self.add_transfer).pack(side=tk.RIGHT, padx=5)

        # قائمة الحوالات
        list_frame = ttk.LabelFrame(self.transfers_frame, text="حوالات الموظف المحدد")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("التاريخ", "المرسل", "رقم المرجع", "النوع", "المبلغ", "ملاحظات")
        self.transfers_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.transfers_tree.heading(col, text=col)
            self.transfers_tree.column(col, width=100)

        scrollbar4 = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.transfers_tree.yview)
        self.transfers_tree.configure(yscrollcommand=scrollbar4.set)

        self.transfers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar4.pack(side=tk.RIGHT, fill=tk.Y)

        # ربط تغيير الموظف
        self.transfer_employee_combo.bind('<<ComboboxSelected>>', self.load_employee_transfers)

    def setup_reports_tab(self):
        """إعداد تبويب التقارير"""
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="التقارير")

        # إطار اختيار الموظف والفترة
        selection_frame = ttk.LabelFrame(self.reports_frame, text="إعدادات التقرير")
        selection_frame.pack(fill=tk.X, padx=5, pady=5)

        # الصف الأول - اختيار الموظف
        row1 = ttk.Frame(selection_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row1, text="الموظف:").pack(side=tk.LEFT, padx=5)
        self.report_employee_var = tk.StringVar()
        self.report_employee_combo = ttk.Combobox(row1, textvariable=self.report_employee_var,
                                                 state="readonly", width=40)
        self.report_employee_combo.pack(side=tk.LEFT, padx=5)

        # الصف الثاني - الفترة الزمنية
        row2 = ttk.Frame(selection_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row2, text="من تاريخ:").pack(side=tk.LEFT, padx=5)
        self.report_start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        ttk.Entry(row2, textvariable=self.report_start_date_var, width=15).pack(side=tk.LEFT, padx=5)

        ttk.Label(row2, text="إلى تاريخ:").pack(side=tk.LEFT, padx=5)
        self.report_end_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(row2, textvariable=self.report_end_date_var, width=15).pack(side=tk.LEFT, padx=5)

        ttk.Button(row2, text="إنتاج كشف الحساب",
                  command=self.generate_account_statement).pack(side=tk.RIGHT, padx=5)
        ttk.Button(row2, text="معاينة",
                  command=self.preview_statement).pack(side=tk.RIGHT, padx=5)

        # إطار المعاينة
        preview_frame = ttk.LabelFrame(self.reports_frame, text="معاينة كشف الحساب")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # منطقة النص للمعاينة
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, font=('Arial', 10))
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)

        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # وظائف الموظفين
    def refresh_employee_list(self):
        """تحديث قائمة الموظفين"""
        # مسح القائمة الحالية
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)

        # جلب الموظفين من قاعدة البيانات
        employees = self.db_manager.get_all_employees()

        # إضافة الموظفين للقائمة
        for emp in employees:
            self.employees_tree.insert('', 'end', values=(
                emp.id, emp.name, emp.employee_id, emp.position,
                emp.department, format_currency(emp.base_salary)
            ))

        # تحديث قوائم الموظفين في التبويبات الأخرى
        self.update_employee_combos()

    def update_employee_combos(self):
        """تحديث قوائم الموظفين في جميع التبويبات"""
        employees = self.db_manager.get_all_employees()
        employee_list = [f"{emp.id} - {emp.name}" for emp in employees]

        self.salary_employee_combo['values'] = employee_list
        self.commission_employee_combo['values'] = employee_list
        self.transfer_employee_combo['values'] = employee_list
        self.report_employee_combo['values'] = employee_list

    def search_employees(self, event=None):
        """البحث في الموظفين"""
        search_term = self.search_var.get().lower()

        # مسح القائمة الحالية
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)

        # جلب الموظفين من قاعدة البيانات
        employees = self.db_manager.get_all_employees()

        # تصفية النتائج
        for emp in employees:
            if (search_term in emp.name.lower() or
                search_term in emp.employee_id.lower() or
                search_term in emp.position.lower() or
                search_term in emp.department.lower()):

                self.employees_tree.insert('', 'end', values=(
                    emp.id, emp.name, emp.employee_id, emp.position,
                    emp.department, format_currency(emp.base_salary)
                ))

    def select_employee(self, event=None):
        """اختيار موظف من القائمة"""
        selection = self.employees_tree.selection()
        if selection:
            item = self.employees_tree.item(selection[0])
            self.selected_employee_id = item['values'][0]

    def add_employee_dialog(self):
        """حوار إضافة موظف جديد"""
        dialog = EmployeeDialog(self.root, "إضافة موظف جديد")
        if dialog.result:
            employee_data = dialog.result

            # التحقق من البيانات
            errors = validate_employee_data(
                employee_data['name'], employee_data['employee_id'],
                employee_data['email'], employee_data['phone'],
                employee_data['base_salary']
            )

            if errors:
                messagebox.showerror("خطأ في البيانات", "\n".join(errors))
                return

            # إنشاء كائن الموظف
            employee = Employee(
                name=clean_text(employee_data['name']),
                employee_id=clean_text(employee_data['employee_id']),
                position=clean_text(employee_data['position']),
                department=clean_text(employee_data['department']),
                base_salary=float(employee_data['base_salary']) if employee_data['base_salary'] else 0,
                phone=clean_text(employee_data['phone']),
                email=clean_text(employee_data['email'])
            )

            try:
                self.db_manager.add_employee(employee)
                messagebox.showinfo("نجح", "تم إضافة الموظف بنجاح")
                self.refresh_employee_list()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في إضافة الموظف: {str(e)}")

    def edit_employee_dialog(self, event=None):
        """حوار تعديل موظف"""
        if not self.selected_employee_id:
            messagebox.showwarning("تحذير", "يرجى اختيار موظف للتعديل")
            return

        # جلب بيانات الموظف
        employee = self.db_manager.get_employee(self.selected_employee_id)
        if not employee:
            messagebox.showerror("خطأ", "الموظف غير موجود")
            return

        dialog = EmployeeDialog(self.root, "تعديل بيانات الموظف", employee)
        if dialog.result:
            employee_data = dialog.result

            # التحقق من البيانات
            errors = validate_employee_data(
                employee_data['name'], employee_data['employee_id'],
                employee_data['email'], employee_data['phone'],
                employee_data['base_salary']
            )

            if errors:
                messagebox.showerror("خطأ في البيانات", "\n".join(errors))
                return

            # تحديث بيانات الموظف
            employee.name = clean_text(employee_data['name'])
            employee.position = clean_text(employee_data['position'])
            employee.department = clean_text(employee_data['department'])
            employee.base_salary = float(employee_data['base_salary']) if employee_data['base_salary'] else 0
            employee.phone = clean_text(employee_data['phone'])
            employee.email = clean_text(employee_data['email'])

            try:
                self.db_manager.update_employee(employee)
                messagebox.showinfo("نجح", "تم تحديث بيانات الموظف بنجاح")
                self.refresh_employee_list()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في تحديث الموظف: {str(e)}")

    def delete_employee(self):
        """حذف موظف"""
        if not self.selected_employee_id:
            messagebox.showwarning("تحذير", "يرجى اختيار موظف للحذف")
            return

        result = messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من حذف هذا الموظف؟")
        if result:
            try:
                employee = self.db_manager.get_employee(self.selected_employee_id)
                employee.is_active = False
                self.db_manager.update_employee(employee)
                messagebox.showinfo("نجح", "تم حذف الموظف بنجاح")
                self.refresh_employee_list()
                self.selected_employee_id = None
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل في حذف الموظف: {str(e)}")

    # وظائف الرواتب
    def get_selected_employee_id(self, combo_var):
        """استخراج معرف الموظف من النص المحدد"""
        selected = combo_var.get()
        if selected and " - " in selected:
            return int(selected.split(" - ")[0])
        return None

    def add_salary(self):
        """إضافة راتب جديد"""
        employee_id = self.get_selected_employee_id(self.salary_employee_var)
        if not employee_id:
            messagebox.showwarning("تحذير", "يرجى اختيار موظف")
            return

        # التحقق من البيانات
        errors = validate_financial_entry(
            self.salary_amount_var.get(),
            self.salary_date_var.get()
        )

        if errors:
            messagebox.showerror("خطأ في البيانات", "\n".join(errors))
            return

        try:
            # إنشاء كائن الراتب
            salary = Salary(
                employee_id=employee_id,
                amount=float(self.salary_amount_var.get()),
                month=int(self.salary_month_var.get()),
                year=int(self.salary_year_var.get()),
                payment_date=parse_date(self.salary_date_var.get()),
                notes=clean_text(self.salary_notes_var.get())
            )

            self.db_manager.add_salary(salary)
            messagebox.showinfo("نجح", "تم إضافة الراتب بنجاح")

            # مسح الحقول
            self.salary_amount_var.set("")
            self.salary_notes_var.set("")

            # تحديث القائمة
            self.load_employee_salaries()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة الراتب: {str(e)}")

    def load_employee_salaries(self, event=None):
        """تحميل رواتب الموظف المحدد"""
        employee_id = self.get_selected_employee_id(self.salary_employee_var)
        if not employee_id:
            return

        # مسح القائمة الحالية
        for item in self.salaries_tree.get_children():
            self.salaries_tree.delete(item)

        # جلب الرواتب
        salaries = self.db_manager.get_employee_salaries(employee_id)

        # إضافة الرواتب للقائمة
        for salary in salaries:
            self.salaries_tree.insert('', 'end', values=(
                format_date(salary.payment_date),
                salary.month,
                salary.year,
                format_currency(salary.amount),
                salary.notes or ""
            ))

    # وظائف العمولات
    def add_commission(self):
        """إضافة عمولة جديدة"""
        employee_id = self.get_selected_employee_id(self.commission_employee_var)
        if not employee_id:
            messagebox.showwarning("تحذير", "يرجى اختيار موظف")
            return

        # التحقق من البيانات
        errors = validate_financial_entry(
            self.commission_amount_var.get(),
            self.commission_date_var.get()
        )

        if errors:
            messagebox.showerror("خطأ في البيانات", "\n".join(errors))
            return

        try:
            # إنشاء كائن العمولة
            commission = Commission(
                employee_id=employee_id,
                amount=float(self.commission_amount_var.get()),
                description=clean_text(self.commission_desc_var.get()),
                commission_date=parse_date(self.commission_date_var.get()),
                commission_type=self.commission_type_var.get(),
                notes=clean_text(self.commission_notes_var.get())
            )

            self.db_manager.add_commission(commission)
            messagebox.showinfo("نجح", "تم إضافة العمولة بنجاح")

            # مسح الحقول
            self.commission_amount_var.set("")
            self.commission_desc_var.set("")
            self.commission_notes_var.set("")

            # تحديث القائمة
            self.load_employee_commissions()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة العمولة: {str(e)}")

    def load_employee_commissions(self, event=None):
        """تحميل عمولات الموظف المحدد"""
        employee_id = self.get_selected_employee_id(self.commission_employee_var)
        if not employee_id:
            return

        # مسح القائمة الحالية
        for item in self.commissions_tree.get_children():
            self.commissions_tree.delete(item)

        # جلب العمولات
        commissions = self.db_manager.get_employee_commissions(employee_id)

        # إضافة العمولات للقائمة
        for commission in commissions:
            self.commissions_tree.insert('', 'end', values=(
                format_date(commission.commission_date),
                commission.commission_type,
                commission.description,
                format_currency(commission.amount),
                commission.notes or ""
            ))

    # وظائف الحوالات
    def add_transfer(self):
        """إضافة حوالة جديدة"""
        employee_id = self.get_selected_employee_id(self.transfer_employee_var)
        if not employee_id:
            messagebox.showwarning("تحذير", "يرجى اختيار موظف")
            return

        # التحقق من البيانات
        errors = validate_financial_entry(
            self.transfer_amount_var.get(),
            self.transfer_date_var.get()
        )

        if errors:
            messagebox.showerror("خطأ في البيانات", "\n".join(errors))
            return

        try:
            # إنشاء كائن الحوالة
            transfer = Transfer(
                employee_id=employee_id,
                amount=float(self.transfer_amount_var.get()),
                sender_name=clean_text(self.transfer_sender_var.get()),
                transfer_date=parse_date(self.transfer_date_var.get()),
                reference_number=clean_text(self.transfer_ref_var.get()),
                transfer_type=self.transfer_type_var.get(),
                notes=clean_text(self.transfer_notes_var.get())
            )

            self.db_manager.add_transfer(transfer)
            messagebox.showinfo("نجح", "تم إضافة الحوالة بنجاح")

            # مسح الحقول
            self.transfer_amount_var.set("")
            self.transfer_sender_var.set("")
            self.transfer_ref_var.set("")
            self.transfer_notes_var.set("")

            # تحديث القائمة
            self.load_employee_transfers()

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إضافة الحوالة: {str(e)}")

    def load_employee_transfers(self, event=None):
        """تحميل حوالات الموظف المحدد"""
        employee_id = self.get_selected_employee_id(self.transfer_employee_var)
        if not employee_id:
            return

        # مسح القائمة الحالية
        for item in self.transfers_tree.get_children():
            self.transfers_tree.delete(item)

        # جلب الحوالات
        transfers = self.db_manager.get_employee_transfers(employee_id)

        # إضافة الحوالات للقائمة
        for transfer in transfers:
            self.transfers_tree.insert('', 'end', values=(
                format_date(transfer.transfer_date),
                transfer.sender_name,
                transfer.reference_number,
                transfer.transfer_type,
                format_currency(transfer.amount),
                transfer.notes or ""
            ))

    # وظائف التقارير
    def preview_statement(self):
        """معاينة كشف الحساب"""
        employee_id = self.get_selected_employee_id(self.report_employee_var)
        if not employee_id:
            messagebox.showwarning("تحذير", "يرجى اختيار موظف")
            return

        try:
            start_date = parse_date(self.report_start_date_var.get())
            end_date = parse_date(self.report_end_date_var.get())

            # جلب البيانات
            employee = self.db_manager.get_employee(employee_id)
            salaries = self.db_manager.get_employee_salaries(employee_id, start_date, end_date)
            commissions = self.db_manager.get_employee_commissions(employee_id, start_date, end_date)
            transfers = self.db_manager.get_employee_transfers(employee_id, start_date, end_date)

            # إنشاء كشف الحساب
            from models import AccountStatement
            statement = AccountStatement(
                employee=employee,
                salaries=salaries,
                commissions=commissions,
                transfers=transfers,
                start_date=start_date,
                end_date=end_date
            )

            # إنشاء النص للمعاينة
            preview_text = self._generate_preview_text(statement)

            # عرض المعاينة
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_text)

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إنشاء المعاينة: {str(e)}")

    def _generate_preview_text(self, statement):
        """إنتاج نص المعاينة"""
        text = f"""
كشف حساب الموظف
==================

معلومات الموظف:
- الاسم: {statement.employee.name}
- رقم الموظف: {statement.employee.employee_id}
- المنصب: {statement.employee.position}
- القسم: {statement.employee.department}
- فترة التقرير: {format_date(statement.start_date)} إلى {format_date(statement.end_date)}

الرواتب:
--------
"""

        if statement.salaries:
            for salary in statement.salaries:
                text += f"- {format_date(salary.payment_date)}: {format_currency(salary.amount)} (شهر {salary.month}/{salary.year})\n"
        else:
            text += "لا توجد رواتب في هذه الفترة\n"

        text += f"\nالعمولات:\n--------\n"

        if statement.commissions:
            for commission in statement.commissions:
                text += f"- {format_date(commission.commission_date)}: {format_currency(commission.amount)} ({commission.description})\n"
        else:
            text += "لا توجد عمولات في هذه الفترة\n"

        text += f"\nالحوالات:\n--------\n"

        if statement.transfers:
            for transfer in statement.transfers:
                text += f"- {format_date(transfer.transfer_date)}: {format_currency(transfer.amount)} من {transfer.sender_name}\n"
        else:
            text += "لا توجد حوالات في هذه الفترة\n"

        text += f"""
الملخص المالي:
==============
- إجمالي الرواتب: {format_currency(statement.total_salary)}
- إجمالي العمولات: {format_currency(statement.total_commissions)}
- إجمالي الحوالات: {format_currency(statement.total_transfers)}
- المجموع الكلي: {format_currency(statement.grand_total)}
"""

        return text

    def generate_account_statement(self):
        """إنتاج كشف حساب PDF"""
        employee_id = self.get_selected_employee_id(self.report_employee_var)
        if not employee_id:
            messagebox.showwarning("تحذير", "يرجى اختيار موظف")
            return

        try:
            start_date = parse_date(self.report_start_date_var.get())
            end_date = parse_date(self.report_end_date_var.get())

            # اختيار مكان الحفظ
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="حفظ كشف الحساب"
            )

            if filename:
                # إنتاج التقرير
                output_path = self.report_generator.generate_account_statement(
                    employee_id, start_date, end_date, filename
                )

                messagebox.showinfo("نجح", f"تم إنتاج كشف الحساب بنجاح:\n{output_path}")

                # فتح الملف
                import subprocess
                import platform

                if platform.system() == 'Darwin':  # macOS
                    subprocess.call(('open', output_path))
                elif platform.system() == 'Windows':  # Windows
                    os.startfile(output_path)
                else:  # Linux
                    subprocess.call(('xdg-open', output_path))

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في إنتاج كشف الحساب: {str(e)}")

    def run(self):
        """تشغيل التطبيق"""
        self.root.mainloop()


class EmployeeDialog:
    """حوار إضافة/تعديل موظف"""

    def __init__(self, parent, title, employee=None):
        self.result = None

        # إنشاء النافذة
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # جعل النافذة modal

        # توسيط النافذة
        self.dialog.transient(parent)

        # المتغيرات
        self.name_var = tk.StringVar(value=employee.name if employee else "")
        self.employee_id_var = tk.StringVar(value=employee.employee_id if employee else "")
        self.position_var = tk.StringVar(value=employee.position if employee else "")
        self.department_var = tk.StringVar(value=employee.department if employee else "")
        self.base_salary_var = tk.StringVar(value=str(employee.base_salary) if employee else "")
        self.phone_var = tk.StringVar(value=employee.phone if employee else "")
        self.email_var = tk.StringVar(value=employee.email if employee else "")

        self.setup_ui()

        # انتظار إغلاق النافذة
        self.dialog.wait_window()

    def setup_ui(self):
        """إعداد واجهة الحوار"""
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # الحقول
        fields = [
            ("الاسم *:", self.name_var),
            ("رقم الموظف *:", self.employee_id_var),
            ("المنصب:", self.position_var),
            ("القسم:", self.department_var),
            ("الراتب الأساسي:", self.base_salary_var),
            ("الهاتف:", self.phone_var),
            ("البريد الإلكتروني:", self.email_var)
        ]

        for i, (label, var) in enumerate(fields):
            ttk.Label(main_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Entry(main_frame, textvariable=var, width=30).grid(row=i, column=1, sticky=tk.W, padx=10, pady=5)

        # الأزرار
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)

        ttk.Button(buttons_frame, text="حفظ", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="إلغاء", command=self.cancel).pack(side=tk.LEFT, padx=5)

    def save(self):
        """حفظ البيانات"""
        self.result = {
            'name': self.name_var.get(),
            'employee_id': self.employee_id_var.get(),
            'position': self.position_var.get(),
            'department': self.department_var.get(),
            'base_salary': self.base_salary_var.get(),
            'phone': self.phone_var.get(),
            'email': self.email_var.get()
        }
        self.dialog.destroy()

    def cancel(self):
        """إلغاء"""
        self.result = None
        self.dialog.destroy()


def main():
    """الدالة الرئيسية"""
    app = PayrollApp()
    app.run()


if __name__ == "__main__":
    main()
