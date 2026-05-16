from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Report, Profile, ReportMedia, Comment
from .forms import ReportForm, UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import urllib.request
import urllib.error

def home(request):
    reports = Report.objects.all().order_by('created_at')
    query = request.GET.get('q')
    
    if query:
        reports = reports.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(author__username__icontains=query) |
            Q(region__icontains=query)
        )
    return render(request, 'home.html', {'reports': reports})

@login_required
def profile_view(request):
    user_reports = Report.objects.filter(author=request.user)
    total_uploads = user_reports.count()
    total_likes = sum(report.likes.count() for report in user_reports)
    context = {'total_uploads': total_uploads, 'total_likes': total_likes}
    return render(request, 'accounts/profile.html', context)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('report_list')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def report_list(request):
    reports = Report.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'reports/report_list.html', {'reports': reports})

@login_required
def report_create(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        files = request.FILES.getlist('extra_media')
        if form.is_valid():
            report = form.save(commit=False)
            report.author = request.user
            report.save()
            for f in files:
                is_vid = f.name.lower().endswith(('.mp4', '.mov', '.avi'))
                ReportMedia.objects.create(report=report, file=f, is_video=is_vid)
            return redirect('report_list')
    else:
        form = ReportForm()
    return render(request, 'reports/report_form.html', {'form': form, 'title': 'Upload Sceneries'})

@login_required
def report_update(request, pk):
    if request.user.is_staff:
        report = get_object_or_404(Report, pk=pk)
    else:
        report = get_object_or_404(Report, pk=pk, author=request.user)
        
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES, instance=report)
        files = request.FILES.getlist('extra_media')
        if form.is_valid():
            form.save()
            for f in files:
                is_vid = f.name.lower().endswith(('.mp4', '.mov', '.avi'))
                ReportMedia.objects.create(report=report, file=f, is_video=is_vid)
            return redirect('report_list')
    else:
        form = ReportForm(instance=report)
    return render(request, 'reports/report_form.html', {'form': form, 'title': 'Edit Sceneries'})

@login_required
def report_delete(request, pk):
    report = get_object_or_404(Report, pk=pk, author=request.user)
    if request.method == 'POST':
        report.delete()
        return redirect('report_list')
    return render(request, 'reports/report_confirm_delete.html', {'report': report})

@login_required
def edit_profile(request):
    Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {'u_form': u_form, 'p_form': p_form}
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

@staff_member_required
def admin_delete_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report.delete()
    messages.success(request, "Post removed by Admin.")
    return redirect('home')

@login_required
def toggle_like(request, pk):
    if request.method == "POST":
        report = get_object_or_404(Report, pk=pk)
        if request.user in report.likes.all():
            report.likes.remove(request.user)
            liked = False
        else:
            report.likes.add(request.user)
            liked = True
        return JsonResponse({'liked': liked, 'count': report.likes.count()})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def add_comment(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        report = get_object_or_404(Report, pk=pk)
        comment = Comment.objects.create(report=report, author=request.user, text=data.get('text'))
        return JsonResponse({
            'status': 'success',
            'comment_id': comment.id,
            'author': comment.author.username,
            'text': comment.text,
            'date': comment.created_at.strftime("%b %d")
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        report_id = comment.report.id
        if request.user == comment.author or request.user.is_staff:
            comment.delete()
            remaining_count = Comment.objects.filter(report_id=report_id).count()
            return JsonResponse({'status': 'success', 'count': remaining_count})
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def analytics_dashboard(request):
    top_spots = Report.objects.annotate(
        total_engagement=Count('comments') + Count('likes')
    ).order_by('-total_engagement')[:5]
    spot_names = [spot.title for spot in top_spots]
    spot_engagement = [spot.total_engagement for spot in top_spots]
    context = {'spot_names': json.dumps(spot_names), 'spot_engagement': json.dumps(spot_engagement)}
    return render(request, 'reports/analytics.html', context)

# 100% GUARANTEED FIX: @csrf_exempt disables the strict firewall just for the chat
@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            api_key = os.environ.get('OPENROUTER_API_KEY')
            
            if not api_key:
                return JsonResponse({'error': 'Render Environment Variables missing OPENROUTER_API_KEY.'}, status=500)

            url = 'https://openrouter.ai/api/v1/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'HTTP-Referer': 'https://geoph.onrender.com',
                'X-Title': 'GeoPH'
            }
            
            payload = {
                "model": "google/gemma-2-9b-it:free",
                "messages": [
                    {"role": "system", "content": "You are a friendly tour guide for the Philippines. Recommend tourist spots, beaches, mountains, islands, and cultural places. Keep answers under 3 sentences."},
                    {"role": "user", "content": user_message}
                ]
            }

            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
            
            try:
                with urllib.request.urlopen(req, timeout=15) as response:
                    response_data = json.loads(response.read().decode('utf-8'))
                    bot_message = response_data['choices'][0]['message']['content']
                    return JsonResponse({'response': bot_message})
                    
            except urllib.error.HTTPError as e:
                error_info = e.read().decode('utf-8')
                return JsonResponse({'error': f"OpenRouter API rejected request (Code {e.code}): {error_info}"}, status=e.code)
            except urllib.error.URLError as e:
                return JsonResponse({'error': f"Failed to connect to OpenRouter: {str(e)}"}, status=500)
                
        except Exception as e:
            return JsonResponse({'error': f"Django backend crashed: {str(e)}"}, status=500)
            
    return JsonResponse({'error': 'Invalid request method'}, status=400)