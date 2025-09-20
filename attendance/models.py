from django.db import models
from django.conf import settings
from django.utils import timezone
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


class Attendance(models.Model):
    """출퇴근 기록"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='attendance_records', verbose_name='직원')
    date = models.DateField(verbose_name='날짜')

    # 출근 정보
    check_in_time = models.DateTimeField(verbose_name='출근시간')
    check_in_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='출근 IP')
    check_in_location = models.CharField(max_length=200, blank=True, verbose_name='출근 위치')

    # 퇴근 정보
    check_out_time = models.DateTimeField(blank=True, null=True, verbose_name='퇴근시간')
    check_out_ip = models.GenericIPAddressField(blank=True, null=True, verbose_name='퇴근 IP')
    check_out_location = models.CharField(max_length=200, blank=True, verbose_name='퇴근 위치')

    # 근무 정보
    work_hours = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True,
                                   verbose_name='근무시간')
    overtime_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0,
                                       verbose_name='연장근무시간')
    break_hours = models.DecimalField(max_digits=3, decimal_places=1, default=0,
                                    verbose_name='휴게시간')

    # 상태
    status = models.CharField(max_length=20, choices=[
        ('정상', '정상출근'),
        ('지각', '지각'),
        ('조퇴', '조퇴'),
        ('결근', '결근'),
        ('휴가', '휴가'),
        ('외근', '외근'),
        ('재택', '재택근무'),
    ], default='정상', verbose_name='근태상태')

    notes = models.TextField(blank=True, verbose_name='비고')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '출퇴근 기록'
        verbose_name_plural = '출퇴근 기록들'
        unique_together = ['employee', 'date']
        ordering = ['-date', '-check_in_time']

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"

    @property
    def is_late(self):
        """지각 여부 확인"""
        if self.status == '지각':
            return True
        # 9시 이후 출근 시 지각
        if self.check_in_time and self.check_in_time.time() > timezone.datetime.strptime('09:00', '%H:%M').time():
            return True
        return False

    @property
    def is_early_leave(self):
        """조퇴 여부 확인"""
        if self.status == '조퇴':
            return True
        # 18시 이전 퇴근 시 조퇴
        if self.check_out_time and self.check_out_time.time() < timezone.datetime.strptime('18:00', '%H:%M').time():
            return True
        return False

    def calculate_work_hours(self):
        """근무시간 계산"""
        if not self.check_in_time or not self.check_out_time:
            return 0

        work_time = self.check_out_time - self.check_in_time
        hours = work_time.total_seconds() / 3600
        self.work_hours = round(hours - self.break_hours, 2)
        return self.work_hours

    def save(self, *args, **kwargs):
        if self.check_in_time and self.check_out_time:
            self.calculate_work_hours()
        super().save(*args, **kwargs)


class LeaveRequest(models.Model):
    """휴가 신청"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='leave_requests', verbose_name='직원')

    leave_type = models.CharField(max_length=20, choices=[
        ('연차', '연차휴가'),
        ('반차', '반차휴가'),
        ('병가', '병가'),
        ('경조사', '경조사휴가'),
        ('출산휴가', '출산휴가'),
        ('육아휴가', '육아휴가'),
        ('기타', '기타휴가'),
    ], verbose_name='휴가종류')

    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')
    days_requested = models.DecimalField(max_digits=3, decimal_places=1, verbose_name='신청일수')

    reason = models.TextField(verbose_name='사유')
    emergency_contact = models.CharField(max_length=100, blank=True, verbose_name='비상연락처')

    # 결재 정보
    status = models.CharField(max_length=20, choices=[
        ('대기', '승인대기'),
        ('승인', '승인'),
        ('반려', '반려'),
        ('취소', '취소'),
    ], default='대기', verbose_name='상태')

    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='approved_leaves',
                                verbose_name='승인자')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='승인일시')
    approval_notes = models.TextField(blank=True, verbose_name='승인비고')

    # 첨부파일
    attachment = models.FileField(upload_to='leave_attachments/', blank=True, null=True,
                                 verbose_name='첨부파일')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='신청일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        verbose_name = '휴가 신청'
        verbose_name_plural = '휴가 신청들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date})"

    @property
    def is_approved(self):
        return self.status == '승인'

    @property
    def is_pending(self):
        return self.status == '대기'

    @property
    def is_rejected(self):
        return self.status == '반려'

    def approve(self, approver):
        """휴가 승인"""
        self.status = '승인'
        self.approver = approver
        self.approved_at = timezone.now()
        self.save()

    def reject(self, approver, notes=""):
        """휴가 반려"""
        self.status = '반려'
        self.approver = approver
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.save()


class LeaveBalance(models.Model):
    """연차 잔여일수"""
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='leave_balance', verbose_name='직원')
    year = models.IntegerField(verbose_name='연도')

    # 연차 정보
    total_days = models.DecimalField(max_digits=4, decimal_places=1, default=15,
                                   verbose_name='총 연차일수')
    used_days = models.DecimalField(max_digits=4, decimal_places=1, default=0,
                                  verbose_name='사용일수')
    remaining_days = models.DecimalField(max_digits=4, decimal_places=1, default=15,
                                      verbose_name='잔여일수')

    # 상세 사용내역
    annual_leave_used = models.DecimalField(max_digits=3, decimal_places=1, default=0,
                                          verbose_name='연차 사용')
    sick_leave_used = models.DecimalField(max_digits=3, decimal_places=1, default=0,
                                       verbose_name='병가 사용')
    other_leave_used = models.DecimalField(max_digits=3, decimal_places=1, default=0,
                                         verbose_name='기타휴가 사용')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '연차 잔여일수'
        verbose_name_plural = '연차 잔여일수들'
        unique_together = ['employee', 'year']

    def __str__(self):
        return f"{self.employee} - {self.year}년 ({self.remaining_days}일)"

    @property
    def available_days(self):
        """사용 가능한 일수"""
        return self.remaining_days

    def use_leave(self, days, leave_type='연차'):
        """휴가 사용 처리"""
        if self.remaining_days < days:
            raise ValueError("잔여 휴가일수가 부족합니다.")

        self.used_days += days
        self.remaining_days -= days

        if leave_type == '연차':
            self.annual_leave_used += days
        elif leave_type == '병가':
            self.sick_leave_used += days
        else:
            self.other_leave_used += days

        self.save()

    def calculate_total_days(self):
        """총 연차일수 계산 (근속연수에 따라)"""
        from core.models import EmployeeProfile
        try:
            profile = self.employee.profile
            tenure_years = profile.tenure_years

            # 근속연수에 따른 연차일수 계산
            if tenure_years < 1:
                self.total_days = 11  # 입사 첫해
            elif tenure_years < 3:
                self.total_days = 15
            elif tenure_years < 5:
                self.total_days = 20
            else:
                self.total_days = 25

            self.remaining_days = self.total_days - self.used_days
            self.save()
        except:
            pass


class WorkSchedule(models.Model):
    """근무 스케줄"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='work_schedules', verbose_name='직원')
    date = models.DateField(verbose_name='날짜')
    schedule_type = models.CharField(max_length=20, choices=[
        ('정상근무', '정상근무'),
        ('휴일근무', '휴일근무'),
        ('야간근무', '야간근무'),
        ('특별근무', '특별근무'),
    ], default='정상근무', verbose_name='근무유형')

    start_time = models.TimeField(verbose_name='근무시작')
    end_time = models.TimeField(verbose_name='근무종료')
    break_start = models.TimeField(blank=True, null=True, verbose_name='휴게시작')
    break_end = models.TimeField(blank=True, null=True, verbose_name='휴게종료')

    notes = models.TextField(blank=True, verbose_name='비고')
    is_flexible = models.BooleanField(default=False, verbose_name='탄력근무')

    class Meta:
        verbose_name = '근무 스케줄'
        verbose_name_plural = '근무 스케줄들'
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.schedule_type})"


# 감사로그 등록
auditlog.register(Attendance)
auditlog.register(LeaveRequest)
auditlog.register(LeaveBalance)
auditlog.register(WorkSchedule)
