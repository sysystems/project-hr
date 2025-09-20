from django.db import models
from django.contrib.auth.models import AbstractUser
from encrypted_model_fields.fields import EncryptedCharField
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
import uuid

class User(AbstractUser):
    """사용자 모델 (MS365 계정 연동)"""
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name='사번')
    phone = models.CharField(max_length=20, blank=True, verbose_name='전화번호')
    department = models.CharField(max_length=100, blank=True, verbose_name='부서')
    position = models.CharField(max_length=50, blank=True, verbose_name='직위')
    is_hr_manager = models.BooleanField(default=False, verbose_name='인사담당자')
    is_admin = models.BooleanField(default=False, verbose_name='관리자')
    hire_date = models.DateField(blank=True, null=True, verbose_name='입사일')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="core_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="core_user_set",
        related_query_name="user",
    )

    class Meta:
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'

    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"

    @property
    def is_management(self):
        """관리자 또는 인사담당자인지 확인"""
        return self.is_admin or self.is_hr_manager


class Department(models.Model):
    """부서/조직 모델"""
    name = models.CharField(max_length=100, verbose_name='부서명')
    code = models.CharField(max_length=20, unique=True, verbose_name='부서코드', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                              related_name='children', verbose_name='상위부서')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='managed_departments', verbose_name='부서장')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '부서'
        verbose_name_plural = '부서들'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_all_employees(self):
        """해당 부서의 모든 직원 반환"""
        return User.objects.filter(department=self.name, is_active=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(uuid.uuid4())[:8]
        super().save(*args, **kwargs)


class EmployeeProfile(models.Model):
    """직원 상세 프로필"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',
                               verbose_name='사용자')

    # 개인정보 (암호화)
    resident_id = EncryptedCharField(max_length=14, verbose_name='주민등록번호')
    birth_date = models.DateField(verbose_name='생년월일')
    address = EncryptedCharField(max_length=200, blank=True, verbose_name='주소')

    # 인사정보
    employee_type = models.CharField(max_length=20, choices=[
        ('정규직', '정규직'),
        ('계약직', '계약직'),
        ('인턴', '인턴'),
        ('파견', '파견직'),
    ], default='정규직', verbose_name='고용형태')

    work_type = models.CharField(max_length=20, choices=[
        ('전일제', '전일제'),
        ('시간제', '시간제'),
        ('재택근무', '재택근무'),
    ], default='전일제', verbose_name='근무형태')

    # 발령이력 (JSON으로 저장)
    position_history = models.JSONField(default=list, blank=True, verbose_name='발령이력')
    department_history = models.JSONField(default=list, blank=True, verbose_name='부서이력')

    # 상태
    status = models.CharField(max_length=20, choices=[
        ('재직', '재직중'),
        ('휴직', '휴직중'),
        ('퇴사', '퇴사'),
        ('정년퇴직', '정년퇴직'),
    ], default='재직', verbose_name='재직상태')

    resignation_date = models.DateField(blank=True, null=True, verbose_name='퇴사일')
    resignation_reason = models.TextField(blank=True, verbose_name='퇴사사유')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '직원 프로필'
        verbose_name_plural = '직원 프로필들'

    def __str__(self):
        return f"{self.user.get_full_name()} 프로필"

    @property
    def age(self):
        """나이 계산"""
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    @property
    def tenure_years(self):
        """근속연수 계산"""
        from datetime import date
        if not self.user.hire_date:
            return 0
        today = date.today()
        return today.year - self.user.hire_date.year - ((today.month, today.day) < (self.user.hire_date.month, self.user.hire_date.day))


# 감사로그 등록
auditlog.register(User)
auditlog.register(EmployeeProfile)
auditlog.register(Department)
