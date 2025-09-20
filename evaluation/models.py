from django.db import models
from django.conf import settings
from django.utils import timezone
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


class EvaluationPeriod(models.Model):
    """평가 기간"""
    name = models.CharField(max_length=100, verbose_name='평가명')
    year = models.IntegerField(verbose_name='년도')
    period_type = models.CharField(max_length=20, choices=[
        ('상반기', '상반기'),
        ('하반기', '하반기'),
        ('연간', '연간'),
        ('분기', '분기'),
        ('월간', '월간'),
    ], default='상반기', verbose_name='평가유형')

    start_date = models.DateField(verbose_name='평가시작일')
    end_date = models.DateField(verbose_name='평가종료일')
    evaluation_start = models.DateField(verbose_name='평가시작일')
    evaluation_end = models.DateField(verbose_name='평가종료일')

    is_active = models.BooleanField(default=True, verbose_name='활성화')
    description = models.TextField(blank=True, verbose_name='설명')

    class Meta:
        verbose_name = '평가 기간'
        verbose_name_plural = '평가 기간들'
        unique_together = ['year', 'period_type']
        ordering = ['-year', '-start_date']

    def __str__(self):
        return f"{self.year}년 {self.period_type} - {self.name}"

    @property
    def is_evaluation_open(self):
        """평가 진행 중인지 확인"""
        today = timezone.now().date()
        return self.evaluation_start <= today <= self.evaluation_end


class EvaluationTemplate(models.Model):
    """평가 템플릿"""
    name = models.CharField(max_length=100, verbose_name='템플릿명')
    description = models.TextField(blank=True, verbose_name='설명')

    # 평가 항목 (JSON)
    evaluation_items = models.JSONField(verbose_name='평가항목')

    # 설정
    max_score = models.DecimalField(max_digits=3, decimal_places=1, default=5.0, verbose_name='최고점수')
    min_score = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, verbose_name='최저점수')
    weight_total = models.DecimalField(max_digits=4, decimal_places=1, default=100.0, verbose_name='가중치합계')

    is_active = models.BooleanField(default=True, verbose_name='활성화')
    is_default = models.BooleanField(default=False, verbose_name='기본템플릿')

    class Meta:
        verbose_name = '평가 템플릿'
        verbose_name_plural = '평가 템플릿들'
        ordering = ['name']

    def __str__(self):
        return self.name


class Evaluation(models.Model):
    """성과 평가"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='evaluations', verbose_name='피평가자')
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='given_evaluations', verbose_name='평가자')

    evaluation_period = models.ForeignKey(EvaluationPeriod, on_delete=models.CASCADE,
                                        verbose_name='평가기간')
    template = models.ForeignKey(EvaluationTemplate, on_delete=models.CASCADE,
                               verbose_name='평가템플릿')

    # 평가 내용 (JSON)
    scores = models.JSONField(verbose_name='점수')
    comments = models.JSONField(verbose_name='코멘트')
    strengths = models.TextField(blank=True, verbose_name='강점')
    improvements = models.TextField(blank=True, verbose_name='개선사항')

    # 종합 평가
    overall_score = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True,
                                      verbose_name='종합점수')
    overall_grade = models.CharField(max_length=10, choices=[
        ('S', 'S 등급'),
        ('A', 'A 등급'),
        ('B', 'B 등급'),
        ('C', 'C 등급'),
        ('D', 'D 등급'),
    ], blank=True, verbose_name='종합등급')

    # 목표 설정
    goals = models.JSONField(default=list, blank=True, verbose_name='목표')
    development_plan = models.TextField(blank=True, verbose_name='발전계획')

    # 상태
    status = models.CharField(max_length=20, choices=[
        ('작성중', '작성중'),
        ('제출', '제출완료'),
        ('검토중', '검토중'),
        ('확정', '확정'),
        ('공유', '공유완료'),
    ], default='작성중', verbose_name='상태')

    submitted_at = models.DateTimeField(blank=True, null=True, verbose_name='제출일시')
    reviewed_at = models.DateTimeField(blank=True, null=True, verbose_name='검토일시')
    confirmed_at = models.DateTimeField(blank=True, null=True, verbose_name='확정일시')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '성과 평가'
        verbose_name_plural = '성과 평가들'
        unique_together = ['employee', 'evaluator', 'evaluation_period']
        ordering = ['-evaluation_period__start_date']

    def __str__(self):
        return f"{self.employee} - {self.evaluation_period} (평가자: {self.evaluator})"

    def calculate_overall_score(self):
        """종합 점수 계산"""
        if not self.scores:
            return

        total_score = 0
        total_weight = 0

        for item_id, score in self.scores.items():
            # 각 항목의 가중치 찾기
            for item in self.template.evaluation_items:
                if str(item.get('id')) == item_id:
                    weight = item.get('weight', 1)
                    total_score += float(score) * weight
                    total_weight += weight
                    break

        if total_weight > 0:
            self.overall_score = round(total_score / total_weight, 1)
            self.save()

    def determine_grade(self):
        """등급 결정"""
        if not self.overall_score:
            return

        score = float(self.overall_score)
        if score >= 4.5:
            self.overall_grade = 'S'
        elif score >= 3.5:
            self.overall_grade = 'A'
        elif score >= 2.5:
            self.overall_grade = 'B'
        elif score >= 1.5:
            self.overall_grade = 'C'
        else:
            self.overall_grade = 'D'

        self.save()


class OneOnOneMeeting(models.Model):
    """1 on 1 면담"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='one_on_one_as_employee', verbose_name='직원')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='one_on_one_as_manager', verbose_name='매니저')

    meeting_date = models.DateField(verbose_name='면담일')
    meeting_type = models.CharField(max_length=20, choices=[
        ('정기면담', '정기면담'),
        ('상황면담', '상황면담'),
        ('성과면담', '성과면담'),
        ('경력면담', '경력면담'),
    ], default='정기면담', verbose_name='면담유형')

    # 면담 내용
    agenda = models.TextField(verbose_name='안건')
    discussion_points = models.JSONField(default=list, blank=True, verbose_name='논의사항')
    action_items = models.JSONField(default=list, blank=True, verbose_name='액션아이템')

    # 결과
    key_takeaways = models.TextField(blank=True, verbose_name='주요내용')
    follow_up_date = models.DateField(blank=True, null=True, verbose_name='후속면담일')
    follow_up_items = models.JSONField(default=list, blank=True, verbose_name='후속사항')

    # 상태
    status = models.CharField(max_length=20, choices=[
        ('예정', '예정'),
        ('진행중', '진행중'),
        ('완료', '완료'),
        ('취소', '취소'),
    ], default='예정', verbose_name='상태')

    notes = models.TextField(blank=True, verbose_name='비고')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '1 on 1 면담'
        verbose_name_plural = '1 on 1 면담들'
        ordering = ['-meeting_date']

    def __str__(self):
        return f"{self.employee} - {self.manager} ({self.meeting_date})"


class Feedback(models.Model):
    """피드백"""
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='received_feedback', verbose_name='수신자')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='sent_feedback', verbose_name='발신자')

    feedback_type = models.CharField(max_length=20, choices=[
        ('칭찬', '칭찬'),
        ('개선', '개선사항'),
        ('제안', '제안사항'),
        ('고객피드백', '고객피드백'),
        ('기타', '기타'),
    ], default='칭찬', verbose_name='피드백유형')

    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')

    # 상황 정보
    situation = models.TextField(blank=True, verbose_name='상황설명')
    impact = models.TextField(blank=True, verbose_name='영향도')

    # 중요도
    priority = models.CharField(max_length=10, choices=[
        ('높음', '높음'),
        ('중간', '중간'),
        ('낮음', '낮음'),
    ], default='중간', verbose_name='중요도')

    # 상태
    is_anonymous = models.BooleanField(default=False, verbose_name='익명')
    is_read = models.BooleanField(default=False, verbose_name='읽음')
    requires_action = models.BooleanField(default=False, verbose_name='조치필요')

    action_taken = models.TextField(blank=True, verbose_name='조치내용')
    action_date = models.DateField(blank=True, null=True, verbose_name='조치일')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '피드백'
        verbose_name_plural = '피드백들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient} - {self.title} ({self.feedback_type})"


class Goal(models.Model):
    """목표 관리"""
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                related_name='goals', verbose_name='직원')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='managed_goals', verbose_name='매니저')

    title = models.CharField(max_length=200, verbose_name='목표제목')
    description = models.TextField(verbose_name='목표설명')

    # 목표 설정
    goal_type = models.CharField(max_length=20, choices=[
        ('업무', '업무 목표'),
        ('개인', '개인 목표'),
        ('발전', '발전 목표'),
        ('조직', '조직 목표'),
    ], default='업무', verbose_name='목표유형')

    priority = models.CharField(max_length=10, choices=[
        ('높음', '높음'),
        ('중간', '중간'),
        ('낮음', '낮음'),
    ], default='중간', verbose_name='우선순위')

    # 기간
    start_date = models.DateField(verbose_name='시작일')
    target_date = models.DateField(verbose_name='목표일')
    completed_date = models.DateField(blank=True, null=True, verbose_name='완료일')

    # 측정 기준
    success_criteria = models.TextField(verbose_name='성공기준')
    measurement_method = models.TextField(blank=True, verbose_name='측정방법')

    # 진행 상황
    progress = models.IntegerField(default=0, verbose_name='진행률')  # 0-100
    status = models.CharField(max_length=20, choices=[
        ('진행중', '진행중'),
        ('완료', '완료'),
        ('보류', '보류'),
        ('취소', '취소'),
    ], default='진행중', verbose_name='상태')

    # 결과
    result = models.TextField(blank=True, verbose_name='결과')
    achievement_level = models.CharField(max_length=20, choices=[
        ('초과달성', '초과달성'),
        ('달성', '달성'),
        ('부분달성', '부분달성'),
        ('미달성', '미달성'),
    ], blank=True, verbose_name='달성도')

    notes = models.TextField(blank=True, verbose_name='비고')

    # 메타정보
    history = AuditlogHistoryField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '목표'
        verbose_name_plural = '목표들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.title}"

    @property
    def is_overdue(self):
        """기한 초과 여부"""
        return self.target_date < timezone.now().date() and self.status == '진행중'

    @property
    def days_remaining(self):
        """남은 일수"""
        if self.status != '진행중':
            return 0
        return (self.target_date - timezone.now().date()).days


# 감사로그 등록
auditlog.register(EvaluationPeriod)
auditlog.register(EvaluationTemplate)
auditlog.register(Evaluation)
auditlog.register(OneOnOneMeeting)
auditlog.register(Feedback)
auditlog.register(Goal)
