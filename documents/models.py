from django.db import models
from django.conf import settings
from django.utils import timezone
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


class DocumentTemplate(models.Model):
    """문서 템플릿"""
    name = models.CharField(max_length=100, verbose_name='템플릿명')
    description = models.TextField(blank=True, verbose_name='설명')

    document_type = models.CharField(max_length=30, choices=[
        ('재직증명서', '재직증명서'),
        ('경력증명서', '경력증명서'),
        ('퇴직증명서', '퇴직증명서'),
        ('급여명세서', '급여명세서'),
        ('원천징수영수증', '원천징수영수증'),
        ('근로소득원천징수부', '근로소득원천징수부'),
        ('고용보험피보험자격취득확인서', '고용보험피보험자격취득확인서'),
        ('건강보험자격득실확인서', '건강보험자격득실확인서'),
        ('국민연금가입증명서', '국민연금가입증명서'),
        ('기타', '기타'),
    ], verbose_name='문서유형')

    # 템플릿 내용
    template_content = models.TextField(verbose_name='템플릿내용')
    variables = models.JSONField(default=list, blank=True, verbose_name='변수목록')

    # 설정
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    is_default = models.BooleanField(default=False, verbose_name='기본템플릿')
    requires_approval = models.BooleanField(default=False, verbose_name='승인필요')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '문서 템플릿'
        verbose_name_plural = '문서 템플릿들'
        ordering = ['document_type', 'name']

    def __str__(self):
        return f"{self.document_type} - {self.name}"


class DocumentRequest(models.Model):
    """제증명 신청"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='document_requests', verbose_name='신청자')

    document_type = models.CharField(max_length=30, choices=[
        ('재직증명서', '재직증명서'),
        ('경력증명서', '경력증명서'),
        ('퇴직증명서', '퇴직증명서'),
        ('급여명세서', '급여명세서'),
        ('원천징수영수증', '원천징수영수증'),
        ('근로소득원천징수부', '근로소득원천징수부'),
        ('고용보험피보험자격취득확인서', '고용보험피보험자격취득확인서'),
        ('건강보험자격득실확인서', '건강보험자격득실확인서'),
        ('국민연금가입증명서', '국민연금가입증명서'),
        ('기타', '기타'),
    ], verbose_name='문서유형')

    # 신청 정보
    title = models.CharField(max_length=200, verbose_name='제목')
    purpose = models.TextField(verbose_name='용도')
    quantity = models.PositiveIntegerField(default=1, verbose_name='수량')

    # 기간 지정 (해당하는 문서에만)
    start_date = models.DateField(blank=True, null=True, verbose_name='시작일')
    end_date = models.DateField(blank=True, null=True, verbose_name='종료일')

    # 추가 정보
    additional_info = models.JSONField(default=dict, blank=True, verbose_name='추가정보')
    special_instructions = models.TextField(blank=True, verbose_name='특별지시사항')

    # 상태
    status = models.CharField(max_length=20, choices=[
        ('신청', '신청완료'),
        ('검토중', '검토중'),
        ('승인', '승인'),
        ('발급완료', '발급완료'),
        ('수령완료', '수령완료'),
        ('반려', '반려'),
        ('취소', '취소'),
    ], default='신청', verbose_name='상태')

    # 결재 정보
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='approved_documents',
                                verbose_name='승인자')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='승인일시')
    approval_notes = models.TextField(blank=True, verbose_name='승인비고')

    # 발급 정보
    issued_at = models.DateTimeField(blank=True, null=True, verbose_name='발급일시')
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='issued_documents',
                                 verbose_name='발급자')

    # 파일
    document_file = models.FileField(upload_to='documents/', blank=True, null=True,
                                   verbose_name='문서파일')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='신청일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '제증명 신청'
        verbose_name_plural = '제증명 신청들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.document_type} ({self.status})"

    @property
    def is_approved(self):
        return self.status == '승인'

    @property
    def is_completed(self):
        return self.status == '수령완료'

    def approve(self, approver):
        """신청 승인"""
        self.status = '승인'
        self.approver = approver
        self.approved_at = timezone.now()
        self.save()

    def reject(self, approver, notes=""):
        """신청 반려"""
        self.status = '반려'
        self.approver = approver
        self.approved_at = timezone.now()
        self.approval_notes = notes
        self.save()

    def issue(self, issuer):
        """문서 발급"""
        self.status = '발급완료'
        self.issued_by = issuer
        self.issued_at = timezone.now()
        self.save()


class Certificate(models.Model):
    """자격증/수료증"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='certificates', verbose_name='직원')

    certificate_type = models.CharField(max_length=30, choices=[
        ('자격증', '자격증'),
        ('수료증', '수료증'),
        ('이수증', '이수증'),
        ('면허증', '면허증'),
        ('기타', '기타'),
    ], default='자격증', verbose_name='증명서유형')

    name = models.CharField(max_length=100, verbose_name='증명서명')
    issuing_organization = models.CharField(max_length=100, verbose_name='발급기관')

    # 발급 정보
    certificate_number = models.CharField(max_length=50, blank=True, verbose_name='증서번호')
    issue_date = models.DateField(verbose_name='발급일')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='만료일')

    # 성적 정보
    grade = models.CharField(max_length=20, blank=True, verbose_name='등급')
    score = models.CharField(max_length=20, blank=True, verbose_name='점수')

    # 파일
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True,
                                      verbose_name='증명서파일')

    # 상태
    is_verified = models.BooleanField(default=False, verbose_name='검증완료')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='verified_certificates',
                                   verbose_name='검증자')
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name='검증일시')

    notes = models.TextField(blank=True, verbose_name='비고')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '자격증/수료증'
        verbose_name_plural = '자격증/수료증들'
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.employee} - {self.name}"

    @property
    def is_expired(self):
        """만료되었는지 확인"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    def verify(self, verifier):
        """검증 완료 처리"""
        self.is_verified = True
        self.verified_by = verifier
        self.verified_at = timezone.now()
        self.save()


class TrainingRecord(models.Model):
    """교육이수기록"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='training_records', verbose_name='직원')

    training_name = models.CharField(max_length=200, verbose_name='교육명')
    training_type = models.CharField(max_length=30, choices=[
        ('내부교육', '내부교육'),
        ('외부교육', '외부교육'),
        ('온라인교육', '온라인교육'),
        ('워크숍', '워크숍'),
        ('세미나', '세미나'),
        ('기타', '기타'),
    ], default='내부교육', verbose_name='교육유형')

    # 교육 기관
    organization = models.CharField(max_length=100, verbose_name='교육기관')
    instructor = models.CharField(max_length=50, blank=True, verbose_name='강사')

    # 기간
    start_date = models.DateField(verbose_name='교육시작일')
    end_date = models.DateField(verbose_name='교육종료일')
    total_hours = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='총교육시간')

    # 비용
    training_cost = models.PositiveIntegerField(default=0, verbose_name='교육비')
    company_cost = models.PositiveIntegerField(default=0, verbose_name='회사부담금')
    personal_cost = models.PositiveIntegerField(default=0, verbose_name='개인부담금')

    # 결과
    completion_status = models.CharField(max_length=20, choices=[
        ('수료', '수료'),
        ('수료예정', '수료예정'),
        ('미수료', '미수료'),
        ('취소', '취소'),
    ], default='수료예정', verbose_name='수료상태')

    grade = models.CharField(max_length=20, blank=True, verbose_name='성적')
    certificate_number = models.CharField(max_length=50, blank=True, verbose_name='수료번호')

    # 파일
    certificate_file = models.FileField(upload_to='training_certificates/', blank=True, null=True,
                                      verbose_name='수료증파일')

    # 평가
    satisfaction_rating = models.IntegerField(blank=True, null=True, verbose_name='만족도')  # 1-5
    usefulness_rating = models.IntegerField(blank=True, null=True, verbose_name='유용도')  # 1-5
    feedback = models.TextField(blank=True, verbose_name='교육피드백')

    # 상태
    is_mandatory = models.BooleanField(default=False, verbose_name='필수교육')
    is_approved = models.BooleanField(default=False, verbose_name='승인완료')

    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='approved_trainings',
                                   verbose_name='승인자')
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='승인일시')

    notes = models.TextField(blank=True, verbose_name='비고')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '교육이수기록'
        verbose_name_plural = '교육이수기록들'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee} - {self.training_name}"

    @property
    def duration_days(self):
        """교육 기간 (일)"""
        return (self.end_date - self.start_date).days + 1

    def approve(self, approver):
        """교육 승인 처리"""
        self.is_approved = True
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()


class Contract(models.Model):
    """계약서/협약서"""
    title = models.CharField(max_length=200, verbose_name='계약명')
    contract_type = models.CharField(max_length=30, choices=[
        ('근로계약', '근로계약서'),
        ('업무협약', '업무협약서'),
        ('비밀유지', '비밀유지계약'),
        ('경업금지', '경업금지계약'),
        ('기타', '기타'),
    ], default='근로계약', verbose_name='계약유형')

    # 계약 당사자
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='contracts', verbose_name='직원')
    counterparty = models.CharField(max_length=100, blank=True, verbose_name='계약상대방')

    # 계약 내용
    content = models.TextField(verbose_name='계약내용')
    key_terms = models.JSONField(default=list, blank=True, verbose_name='주요조항')

    # 기간
    start_date = models.DateField(verbose_name='계약시작일')
    end_date = models.DateField(blank=True, null=True, verbose_name='계약종료일')

    # 금액
    contract_amount = models.PositiveIntegerField(blank=True, null=True, verbose_name='계약금액')
    payment_terms = models.TextField(blank=True, verbose_name='지급조건')

    # 파일
    contract_file = models.FileField(upload_to='contracts/', blank=True, null=True,
                                   verbose_name='계약서파일')

    # 상태
    status = models.CharField(max_length=20, choices=[
        ('작성중', '작성중'),
        ('검토중', '검토중'),
        ('서명완료', '서명완료'),
        ('진행중', '진행중'),
        ('종료', '종료'),
        ('해지', '해지'),
    ], default='작성중', verbose_name='상태')

    # 서명
    employee_signature = models.ImageField(upload_to='signatures/', blank=True, null=True,
                                         verbose_name='직원서명')
    company_signature = models.ImageField(upload_to='signatures/', blank=True, null=True,
                                        verbose_name='회사서명')

    signed_at = models.DateTimeField(blank=True, null=True, verbose_name='서명일시')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '계약서'
        verbose_name_plural = '계약서들'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee} - {self.title}"

    @property
    def is_active(self):
        """현재 유효한 계약인지 확인"""
        today = timezone.now().date()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today

    def sign(self, signature_image, is_employee=True):
        """서명 처리"""
        if is_employee:
            self.employee_signature = signature_image
        else:
            self.company_signature = signature_image

        if self.employee_signature and self.company_signature:
            self.status = '서명완료'
            self.signed_at = timezone.now()

        self.save()


# 감사로그 등록
auditlog.register(DocumentTemplate)
auditlog.register(DocumentRequest)
auditlog.register(Certificate)
auditlog.register(TrainingRecord)
auditlog.register(Contract)
