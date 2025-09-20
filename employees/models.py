from django.db import models
from django.conf import settings
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


class Skill(models.Model):
    """기술/역량 모델"""
    name = models.CharField(max_length=100, unique=True, verbose_name='기술명')
    category = models.CharField(max_length=50, choices=[
        ('기술', '기술'),
        ('언어', '언어'),
        ('자격증', '자격증'),
        ('기타', '기타'),
    ], default='기술', verbose_name='카테고리')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    class Meta:
        verbose_name = '기술'
        verbose_name_plural = '기술들'

    def __str__(self):
        return self.name


class Certification(models.Model):
    """자격증 모델"""
    name = models.CharField(max_length=100, verbose_name='자격증명')
    issuing_organization = models.CharField(max_length=100, verbose_name='발급기관')
    description = models.TextField(blank=True, verbose_name='설명')
    is_active = models.BooleanField(default=True, verbose_name='활성화')

    class Meta:
        verbose_name = '자격증'
        verbose_name_plural = '자격증들'
        unique_together = ['name', 'issuing_organization']

    def __str__(self):
        return f"{self.name} ({self.issuing_organization})"


class EmployeeSkill(models.Model):
    """직원 기술/자격증"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='skills', verbose_name='직원')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, verbose_name='기술')
    proficiency_level = models.CharField(max_length=20, choices=[
        ('초급', '초급'),
        ('중급', '중급'),
        ('고급', '고급'),
        ('전문가', '전문가'),
    ], default='중급', verbose_name='숙련도')
    years_of_experience = models.PositiveIntegerField(default=0, verbose_name='경험연수')
    obtained_date = models.DateField(blank=True, null=True, verbose_name='취득일')
    notes = models.TextField(blank=True, verbose_name='비고')

    class Meta:
        verbose_name = '직원 기술'
        verbose_name_plural = '직원 기술들'
        unique_together = ['employee', 'skill']

    def __str__(self):
        return f"{self.employee} - {self.skill}"


class EmployeeCertification(models.Model):
    """직원 자격증"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='certifications', verbose_name='직원')
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, verbose_name='자격증')
    certificate_number = models.CharField(max_length=50, blank=True, verbose_name='증서번호')
    issue_date = models.DateField(verbose_name='발급일')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='만료일')
    issuing_organization = models.CharField(max_length=100, blank=True, verbose_name='발급기관')
    notes = models.TextField(blank=True, verbose_name='비고')

    class Meta:
        verbose_name = '직원 자격증'
        verbose_name_plural = '직원 자격증들'
        unique_together = ['employee', 'certification', 'certificate_number']

    def __str__(self):
        return f"{self.employee} - {self.certification}"

    @property
    def is_expired(self):
        """만료되었는지 확인"""
        if self.expiry_date:
            from django.utils import timezone
            return self.expiry_date < timezone.now().date()
        return False


class WorkExperience(models.Model):
    """경력사항"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='work_experiences', verbose_name='직원')
    company_name = models.CharField(max_length=100, verbose_name='회사명')
    department = models.CharField(max_length=50, blank=True, verbose_name='부서')
    position = models.CharField(max_length=50, verbose_name='직위')
    job_description = models.TextField(verbose_name='업무 내용')
    start_date = models.DateField(verbose_name='입사일')
    end_date = models.DateField(blank=True, null=True, verbose_name='퇴사일')
    reason_for_leaving = models.TextField(blank=True, verbose_name='퇴사사유')
    salary = models.PositiveIntegerField(blank=True, null=True, verbose_name='연봉')
    is_current = models.BooleanField(default=False, verbose_name='현재 재직중')

    class Meta:
        verbose_name = '경력사항'
        verbose_name_plural = '경력사항들'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee} - {self.company_name}"

    @property
    def duration_months(self):
        """근무 기간 (개월)"""
        if not self.end_date:
            from django.utils import timezone
            end_date = timezone.now().date()
        else:
            end_date = self.end_date

        months = (end_date.year - self.start_date.year) * 12 + (end_date.month - self.start_date.month)
        return max(months, 1)  # 최소 1개월


class Education(models.Model):
    """학력사항"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='education', verbose_name='직원')
    institution = models.CharField(max_length=100, verbose_name='교육기관')
    major = models.CharField(max_length=50, blank=True, verbose_name='전공')
    degree = models.CharField(max_length=20, choices=[
        ('고등학교', '고등학교'),
        ('전문대학', '전문대학'),
        ('대학교', '대학교'),
        ('석사', '석사'),
        ('박사', '박사'),
        ('기타', '기타'),
    ], default='대학교', verbose_name='학위')
    start_date = models.DateField(verbose_name='입학일')
    end_date = models.DateField(blank=True, null=True, verbose_name='졸업일')
    gpa = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, verbose_name='학점')
    status = models.CharField(max_length=20, choices=[
        ('졸업', '졸업'),
        ('재학', '재학중'),
        ('중퇴', '중퇴'),
        ('수료', '수료'),
    ], default='졸업', verbose_name='상태')

    class Meta:
        verbose_name = '학력사항'
        verbose_name_plural = '학력사항들'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee} - {self.institution}"


class EmergencyContact(models.Model):
    """비상연락망"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='emergency_contacts', verbose_name='직원')
    name = models.CharField(max_length=50, verbose_name='이름')
    relationship = models.CharField(max_length=20, verbose_name='관계')
    phone = models.CharField(max_length=20, verbose_name='전화번호')
    address = models.CharField(max_length=200, blank=True, verbose_name='주소')
    is_primary = models.BooleanField(default=False, verbose_name='주요연락처')

    class Meta:
        verbose_name = '비상연락망'
        verbose_name_plural = '비상연락망들'

    def __str__(self):
        return f"{self.employee} - {self.name} ({self.relationship})"


# 감사로그 등록
auditlog.register(Skill)
auditlog.register(Certification)
auditlog.register(EmployeeSkill)
auditlog.register(EmployeeCertification)
auditlog.register(WorkExperience)
auditlog.register(Education)
auditlog.register(EmergencyContact)
