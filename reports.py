"""
إنتاج التقارير وكشوفات الحساب
"""
from datetime import datetime
from typing import List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

from models import AccountStatement, Employee
from database import DatabaseManager


class ReportGenerator:
    """مولد التقارير"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.setup_fonts()
    
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        try:
            # يمكن إضافة خط عربي هنا إذا كان متوفراً
            # pdfmetrics.registerFont(TTFont('Arabic', 'path/to/arabic/font.ttf'))
            pass
        except:
            pass
    
    def generate_account_statement(self, employee_id: int, start_date: datetime, 
                                 end_date: datetime, output_path: str = None) -> str:
        """إنتاج كشف حساب موظف"""
        
        # جمع البيانات
        employee = self.db_manager.get_employee(employee_id)
        if not employee:
            raise ValueError(f"الموظف غير موجود: {employee_id}")
        
        salaries = self.db_manager.get_employee_salaries(employee_id, start_date, end_date)
        commissions = self.db_manager.get_employee_commissions(employee_id, start_date, end_date)
        transfers = self.db_manager.get_employee_transfers(employee_id, start_date, end_date)
        
        # إنشاء كشف الحساب
        statement = AccountStatement(
            employee=employee,
            salaries=salaries,
            commissions=commissions,
            transfers=transfers,
            start_date=start_date,
            end_date=end_date
        )
        
        # إنتاج PDF
        if output_path is None:
            output_path = f"account_statement_{employee.employee_id}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
        
        self._create_pdf_report(statement, output_path)
        return output_path
    
    def _create_pdf_report(self, statement: AccountStatement, output_path: str):
        """إنشاء تقرير PDF"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # عنوان التقرير
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # وسط
        )
        
        story.append(Paragraph("كشف حساب الموظف", title_style))
        story.append(Spacer(1, 20))
        
        # معلومات الموظف
        employee_info = [
            ["اسم الموظف:", statement.employee.name],
            ["رقم الموظف:", statement.employee.employee_id],
            ["المنصب:", statement.employee.position],
            ["القسم:", statement.employee.department],
            ["فترة التقرير:", f"{statement.start_date.strftime('%Y-%m-%d')} إلى {statement.end_date.strftime('%Y-%m-%d')}"]
        ]
        
        employee_table = Table(employee_info, colWidths=[2*inch, 3*inch])
        employee_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(employee_table)
        story.append(Spacer(1, 30))
        
        # جدول الرواتب
        if statement.salaries:
            story.append(Paragraph("الرواتب", styles['Heading2']))
            salary_data = [["التاريخ", "الشهر", "السنة", "المبلغ", "ملاحظات"]]
            
            for salary in statement.salaries:
                salary_data.append([
                    salary.payment_date.strftime('%Y-%m-%d'),
                    str(salary.month),
                    str(salary.year),
                    f"{salary.amount:,.2f}",
                    salary.notes or ""
                ])
            
            salary_table = Table(salary_data, colWidths=[1.2*inch, 0.8*inch, 0.8*inch, 1.2*inch, 2*inch])
            salary_table.setStyle(self._get_table_style())
            story.append(salary_table)
            story.append(Spacer(1, 20))
        
        # جدول العمولات
        if statement.commissions:
            story.append(Paragraph("العمولات", styles['Heading2']))
            commission_data = [["التاريخ", "النوع", "الوصف", "المبلغ", "ملاحظات"]]
            
            for commission in statement.commissions:
                commission_data.append([
                    commission.commission_date.strftime('%Y-%m-%d'),
                    commission.commission_type,
                    commission.description,
                    f"{commission.amount:,.2f}",
                    commission.notes or ""
                ])
            
            commission_table = Table(commission_data, colWidths=[1.2*inch, 1*inch, 1.5*inch, 1.2*inch, 1.1*inch])
            commission_table.setStyle(self._get_table_style())
            story.append(commission_table)
            story.append(Spacer(1, 20))
        
        # جدول الحوالات
        if statement.transfers:
            story.append(Paragraph("الحوالات", styles['Heading2']))
            transfer_data = [["التاريخ", "المرسل", "رقم المرجع", "النوع", "المبلغ"]]
            
            for transfer in statement.transfers:
                transfer_data.append([
                    transfer.transfer_date.strftime('%Y-%m-%d'),
                    transfer.sender_name,
                    transfer.reference_number,
                    transfer.transfer_type,
                    f"{transfer.amount:,.2f}"
                ])
            
            transfer_table = Table(transfer_data, colWidths=[1.2*inch, 1.5*inch, 1.2*inch, 1*inch, 1.1*inch])
            transfer_table.setStyle(self._get_table_style())
            story.append(transfer_table)
            story.append(Spacer(1, 20))
        
        # الملخص المالي
        summary_data = [
            ["إجمالي الرواتب:", f"{statement.total_salary:,.2f}"],
            ["إجمالي العمولات:", f"{statement.total_commissions:,.2f}"],
            ["إجمالي الحوالات:", f"{statement.total_transfers:,.2f}"],
            ["المجموع الكلي:", f"{statement.grand_total:,.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('BACKGROUND', (0, 3), (1, 3), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("الملخص المالي", styles['Heading2']))
        story.append(summary_table)
        
        # إنشاء PDF
        doc.build(story)
    
    def _get_table_style(self):
        """نمط الجداول الافتراضي"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
