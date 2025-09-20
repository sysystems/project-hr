from django.db import models
from django.conf import settings
from django.utils import timezone
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


class SalaryGrade(models.Model):
    """호봉/급여등급"""
    grade = models.CharField(max_length=20, unique=True, verbose_name='등급')
    name = models.CharField(max_length=50, verbose_name='등급명')
    base_salary = models.PositiveIntegerField(verbose_name='기본급')
    min_salary = models.PositiveIntegerField(verbose_name='최저급')
    max_salary = models.PositiveIntegerField(verbose_name='최고급')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    class Meta:
        verbose_name = '급여등급'
        verbose_name_plural = '급여등급들'
        ordering = ['grade']

    def __str__(self):
        return f"{self.grade} - {self.name}"


class Allowance(models.Model):
    """수당 항목"""
    name = models.CharField(max_length=50, unique=True, verbose_name='수당명')
    code = models.CharField(max_length=20, unique=True, verbose_name='수당코드')
    allowance_type = models.CharField(max_length=20, choices=[
        ('기본수당', '기본수당'),
        ('직무수당', '직무수당'),
        ('성과수당', '성과수당'),
        ('복리후생', '복리후생'),
        ('기타', '기타'),
    ], default='기본수당', verbose_name='수당유형')

    calculation_method = models.CharField(max_length=20, choices=[
        ('정액', '정액'),
        ('기본급비율', '기본급비율'),
        ('시급', '시급'),
        ('일급', '일급'),
        ('월급', '월급'),
    ], default='정액', verbose_name='계산방법')

    default_amount = models.PositiveIntegerField(default=0, verbose_name='기본금액')
    is_taxable = models.BooleanField(default=True, verbose_name='과세대상')
    is_mandatory = models.BooleanField(default=False, verbose_name='필수지급')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    class Meta:
        verbose_name = '수당'
        verbose_name_plural = '수당들'
        ordering = ['name']

    def __str__(self):
        return self.name


class Deduction(models.Model):
    """공제 항목"""
    name = models.CharField(max_length=50, unique=True, verbose_name='공제명')
    code = models.CharField(max_length=20, unique=True, verbose_name='공제코드')
    deduction_type = models.CharField(max_length=20, choices=[
        ('법정공제', '법정공제'),
        ('임의공제', '임의공제'),
        ('기타', '기타'),
    ], default='법정공제', verbose_name='공제유형')

    calculation_method = models.CharField(max_length=20, choices=[
        ('정률', '정률'),
        ('정액', '정액'),
        ('기본급비율', '기본급비율'),
    ], default='정률', verbose_name='계산방법')

    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='비율')
    default_amount = models.PositiveIntegerField(default=0, verbose_name='기본금액')
    is_mandatory = models.BooleanField(default=True, verbose_name='필수공제')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    class Meta:
        verbose_name = '공제'
        verbose_name_plural = '공제들'
        ordering = ['name']

    def __str__(self):
        return self.name


class Payroll(models.Model):
    """급여대장"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='payrolls', verbose_name='직원')
    year = models.IntegerField(verbose_name='년도')
    month = models.IntegerField(verbose_name='월')

    # 급여 정보
    salary_grade = models.ForeignKey(SalaryGrade, on_delete=models.SET_NULL, null=True,
                                   verbose_name='급여등급')
    base_salary = models.PositiveIntegerField(verbose_name='기본급')
    total_allowances = models.PositiveIntegerField(default=0, verbose_name='총수당')
    total_deductions = models.PositiveIntegerField(default=0, verbose_name='총공제')
    gross_pay = models.PositiveIntegerField(verbose_name='지급총액')
    net_pay = models.PositiveIntegerField(verbose_name='실지급액')

    # 상세 내역 (JSON)
    allowances_detail = models.JSONField(default=dict, blank=True, verbose_name='수당내역')
    deductions_detail = models.JSONField(default=dict, blank=True, verbose_name='공제내역')

    # 지급 정보
    payment_date = models.DateField(verbose_name='지급일')
    payment_method = models.CharField(max_length=20, choices=[
        ('계좌이체', '계좌이체'),
        ('현금', '현금'),
        ('기타', '기타'),
    ], default='계좌이체', verbose_name='지급방법')

    bank_name = models.CharField(max_length=50, blank=True, verbose_name='은행명')
    account_number = models.CharField(max_length=50, blank=True, verbose_name='계좌번호')

    # 상태
    status = models.CharField(max_length=20, choices=[
        ('작성중', '작성중'),
        ('확정', '확정'),
        ('지급완료', '지급완료'),
        ('취소', '취소'),
    ], default='작성중', verbose_name='상태')

    notes = models.TextField(blank=True, verbose_name='비고')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '급여대장'
        verbose_name_plural = '급여대장들'
        unique_together = ['employee', 'year', 'month']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee} - {self.year}년 {self.month}월"

    @property
    def tax_amount(self):
        """세금 총액"""
        return sum(amount for code, amount in self.deductions_detail.items()
                  if code.startswith('tax_'))

    @property
    def insurance_amount(self):
        """보험료 총액"""
        return sum(amount for code, amount in self.deductions_detail.items()
                  if code.startswith('insurance_'))


class Bonus(models.Model):
    """상여금"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='bonuses', verbose_name='직원')
    bonus_type = models.CharField(max_length=20, choices=[
        ('성과상여', '성과상여'),
        ('명절상여', '명절상여'),
        ('특별상여', '특별상여'),
        ('퇴직상여', '퇴직상여'),
        ('기타', '기타'),
    ], verbose_name='상여종류')

    year = models.IntegerField(verbose_name='년도')
    quarter = models.IntegerField(blank=True, null=True, verbose_name='분기')

    amount = models.PositiveIntegerField(verbose_name='상여금액')
    payment_date = models.DateField(verbose_name='지급일')
    reason = models.TextField(blank=True, verbose_name='지급사유')

    # 결재 정보
    status = models.CharField(max_length=20, choices=[
        ('신청', '신청'),
        ('검토중', '검토중'),
        ('승인', '승인'),
        ('지급완료', '지급완료'),
        ('취소', '취소'),
    ], default='신청', verbose_name='상태')

    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='approved_bonuses',
                                verbose_name='승인자')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='승인일시')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='신청일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '상여금'
        verbose_name_plural = '상여금들'
        ordering = ['-year', '-quarter', '-payment_date']

    def __str__(self):
        return f"{self.employee} - {self.bonus_type} ({self.amount:,}원)"


class RetirementPension(models.Model):
    """퇴직연금"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='retirement_pensions', verbose_name='직원')

    # 퇴직 정보
    retirement_date = models.DateField(verbose_name='퇴직일')
    reason = models.TextField(verbose_name='퇴직사유')

    # 연금 정보
    pension_type = models.CharField(max_length=20, choices=[
        ('확정급여형', '확정급여형 (DB)'),
        ('확정기여형', '확정기여형 (DC)'),
        ('개인퇴직연금', '개인퇴직연금 (IRP)'),
    ], default='확정기여형', verbose_name='연금유형')

    total_contribution = models.PositiveIntegerField(verbose_name='총납입금')
    employee_contribution = models.PositiveIntegerField(verbose_name='본인납입금')
    company_contribution = models.PositiveIntegerField(verbose_name='회사납입금')

    # 지급 정보
    payout_amount = models.PositiveIntegerField(blank=True, null=True, verbose_name='지급금액')
    payout_date = models.DateField(blank=True, null=True, verbose_name='지급일')
    payout_method = models.CharField(max_length=20, choices=[
        ('일시금', '일시금'),
        ('연금', '연금'),
        ('혼합', '혼합'),
    ], default='일시금', verbose_name='지급방법')

    # 상태
    status = models.CharField(max_length=20, choices=[
        ('계산중', '계산중'),
        ('확정', '확정'),
        ('지급완료', '지급완료'),
    ], default='계산중', verbose_name='상태')

    notes = models.TextField(blank=True, verbose_name='비고')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '퇴직연금'
        verbose_name_plural = '퇴직연금들'
        ordering = ['-retirement_date']

    def __str__(self):
        return f"{self.employee} - 퇴직연금 ({self.pension_type})"

    def calculate_payout(self):
        """지급금액 계산 (간단한 계산식)"""
        # 실제로는 복잡한 계산식이 적용되어야 함
        if self.pension_type == '확정기여형':
            self.payout_amount = self.total_contribution
        elif self.pension_type == '확정급여형':
            # 근속연수와 평균급여에 기반한 계산
            self.payout_amount = self.total_contribution * 1.2  # 예시
        else:
            self.payout_amount = self.total_contribution

        self.status = '확정'
        self.save()


# 감사로그 등록
auditlog.register(SalaryGrade)
auditlog.register(Allowance)
auditlog.register(Deduction)
auditlog.register(Payroll)
auditlog.register(Bonus)
auditlog.register(RetirementPension)
