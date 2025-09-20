from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render  # 기존에 있으면 생략

# 기존 뷰들...

def org_action_api(request, action):
    html = ''
    if action == 'create':
        html = render_to_string('organization/create_form.html', {})  # 별도 템플릿 필요 (아래 단계)
    elif action == 'move':
        html = '<h2>조직 이동 폼</h2><form>...</form>'  # 임시, 실제 폼으로 교체
    elif action == 'delete':
        html = '<h2>조직 삭제 확인</h2><button>삭제</button>'
    elif action == 'assign':
        html = '<h2>인원 배치 폼</h2><select>...</select>'
    return JsonResponse({'html': html})