from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


class Organization(MPTTModel):
    """조직/부서 트리 구조"""
    name = models.CharField(max_length=100, verbose_name='조직명')
    code = models.CharField(max_length=20, unique=True, verbose_name='조직코드')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                           related_name='children', verbose_name='상위조직')

    # 조직 정보
    level = models.IntegerField(default=1, verbose_name='조직레벨')
    description = models.TextField(blank=True, verbose_name='설명')
    organization_type = models.CharField(max_length=20, choices=[
        ('본부', '본부'),
        ('부서', '부서'),
        ('팀', '팀'),
        ('파트', '파트'),
        ('그룹', '그룹'),
    ], default='부서', verbose_name='조직유형')

    # 책임자
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='managed_organizations',
                               verbose_name='조직장')
    assistant_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='assistant_organizations',
                                        verbose_name='차장')

    # 위치 정보
    location = models.CharField(max_length=100, blank=True, verbose_name='위치')
    floor = models.CharField(max_length=20, blank=True, verbose_name='층')

    # 상태
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    employee_count = models.PositiveIntegerField(default=0, verbose_name='직원수')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '조직'
        verbose_name_plural = '조직들'
        ordering = ['tree_id', 'lft']

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def get_all_employees(self):
        """해당 조직의 모든 직원 반환"""
        return settings.AUTH_USER_MODEL.objects.filter(
            models.Q(organization=self) |
            models.Q(organization__in=self.get_descendants())
        ).distinct()

    def update_employee_count(self):
        """직원수 업데이트"""
        self.employee_count = self.get_all_employees().count()
        self.save(update_fields=['employee_count'])

    def get_ancestors_names(self):
        """상위 조직들의 이름 반환"""
        return [org.name for org in self.get_ancestors()]

    def get_full_path(self):
        """전체 경로 반환"""
        return ' > '.join(self.get_ancestors_names() + [self.name])


class Position(models.Model):
    """직위/직급 모델"""
    name = models.CharField(max_length=50, unique=True, verbose_name='직위명')
    code = models.CharField(max_length=20, unique=True, verbose_name='직위코드')
    level = models.IntegerField(verbose_name='직위레벨')  # 숫자가 높을수록 상급
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    class Meta:
        verbose_name = '직위'
        verbose_name_plural = '직위들'
        ordering = ['-level', 'name']

    def __str__(self):
        return f"{self.name} ({self.level})"


class JobTitle(models.Model):
    """직책 모델"""
    name = models.CharField(max_length=50, unique=True, verbose_name='직책명')
    code = models.CharField(max_length=20, unique=True, verbose_name='직책코드')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    class Meta:
        verbose_name = '직책'
        verbose_name_plural = '직책들'
        ordering = ['name']

    def __str__(self):
        return self.name


class EmployeeOrganization(models.Model):
    """직원-조직 관계 (발령이력)"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='organization_history', verbose_name='직원')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                   related_name='employee_history', verbose_name='조직')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True,
                                verbose_name='직위')
    job_title = models.ForeignKey(JobTitle, on_delete=models.SET_NULL, null=True,
                                 verbose_name='직책')

    # 발령 정보
    appointment_type = models.CharField(max_length=20, choices=[
        ('입사', '입사'),
        ('승진', '승진'),
        ('전보', '전보'),
        ('겸직', '겸직'),
        ('파견', '파견'),
        ('복귀', '복귀'),
        ('퇴사', '퇴사'),
    ], default='입사', verbose_name='발령유형')

    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(blank=True, null=True, verbose_name='종료일')

    # 급여 정보
    base_salary = models.PositiveIntegerField(blank=True, null=True, verbose_name='기본급')
    allowances = models.JSONField(default=dict, blank=True, verbose_name='수당')

    # 상태
    is_primary = models.BooleanField(default=True, verbose_name='주요발령')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '직원 조직이력'
        verbose_name_plural = '직원 조직이력들'
        ordering = ['-start_date']
        unique_together = ['employee', 'organization', 'start_date']

    def __str__(self):
        return f"{self.employee} - {self.organization} ({self.start_date})"

    @property
    def is_current(self):
        """현재 발령인지 확인"""
        return self.is_active and (self.end_date is None or self.end_date >= models.date.today())

    def get_duration_months(self):
        """발령 기간 (개월)"""
        if not self.end_date:
            from django.utils import timezone
            end_date = timezone.now().date()
        else:
            end_date = self.end_date

        months = (end_date.year - self.start_date.year) * 12 + (end_date.month - self.start_date.month)
        return max(months, 1)


class OrganizationChangeRequest(models.Model):
    """조직개편 요청"""
    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(verbose_name='설명')

    # 요청자
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='org_change_requests', verbose_name='요청자')

    # 변경 내용
    change_type = models.CharField(max_length=20, choices=[
        ('조직생성', '조직생성'),
        ('조직폐지', '조직폐지'),
        ('조직이동', '조직이동'),
        ('조직통합', '조직통합'),
        ('조직분할', '조직분할'),
    ], verbose_name='변경유형')

    # 관련 조직
    target_organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                           null=True, blank=True, verbose_name='대상조직')
    new_parent_organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                              null=True, blank=True, related_name='child_change_requests',
                                              verbose_name='새 상위조직')

    # 세부 정보
    change_details = models.JSONField(default=dict, blank=True, verbose_name='변경세부사항')
    effective_date = models.DateField(verbose_name='시행일')

    # 결재 정보
    status = models.CharField(max_length=20, choices=[
        ('작성중', '작성중'),
        ('검토중', '검토중'),
        ('승인', '승인'),
        ('반려', '반려'),
        ('시행완료', '시행완료'),
    ], default='작성중', verbose_name='상태')

    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='approved_org_changes',
                                verbose_name='승인자')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='승인일시')
    approval_notes = models.TextField(blank=True, verbose_name='승인비고')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='요청일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        verbose_name = '조직개편 요청'
        verbose_name_plural = '조직개편 요청들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.change_type})"


# 감사로그 등록
auditlog.register(Organization)
auditlog.register(Position)
auditlog.register(JobTitle)
auditlog.register(EmployeeOrganization)
auditlog.register(OrganizationChangeRequest)
