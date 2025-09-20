from django.shortcuts import render

def home(request):
    return render(request, 'core/home.html')

def org_chart(request):
    return render(request, 'core/org_chart.html')
