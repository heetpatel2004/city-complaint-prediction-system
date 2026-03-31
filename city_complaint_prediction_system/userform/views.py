from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from .models import Complaint
from .ml_model import predict
import pandas as pd
from django.core.paginator import Paginator
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncDate



import re

def home(request):
    return render(request, "userform/landing.html")


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        conf_password = request.POST.get("conf_password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("userform:signup")

           # Minimum length check
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return redirect("userform:signup")

        # Lowercase check
        if not re.search(r"[a-z]", password):
            messages.error(request, "Password must contain at least one lowercase letter")
            return redirect("userform:signup")

        # Uppercase check
        if not re.search(r"[A-Z]", password):
            messages.error(request, "Password must contain at least one uppercase letter")
            return redirect("userform:signup")

        # Number check
        if not re.search(r"[0-9]", password):
            messages.error(request, "Password must contain at least one number")
            return redirect("userform:signup")

        # Special character check
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            messages.error(request, "Password must contain at least one special character")
            return redirect("userform:signup")

        if password != conf_password:
            messages.error(request, "Passwords do not match")
            return redirect("userform:signup")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        messages.success(request, "Account created successfully")
        return redirect("userform:login")

    return render(request, "userform/signup.html")


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("userform:home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("userform:login")

    return render(request, "userform/login.html")


def user_logout(request):
    logout(request)
    return redirect("userform:home")


def about_us(request):
    return render(request, "userform/about_us.html")

def contact(request):
    return render(request, "userform/contact.html")

# submit complaint
def submit_complaint(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")

        date = request.POST.get("complaint_date")
        date = pd.to_datetime(date)
        month = date.month
        day_of_week = date.dayofweek
        is_weekend = 1 if day_of_week >= 5 else 0
        category = request.POST.get("category")
        area = request.POST.get("area")
        severity = (request.POST.get('severity')   or 'Medium').capitalize()
        affected_people = int(request.POST.get('affected_people'))
        # title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        
        print("CATEGORY RECEIVED:", category)
        
        priority, resolution_time = predict(
                category,
                area,
                severity,
                affected_people,
                month,
                day_of_week,
                is_weekend
                
               )
        print("PREDICT OUTPUT:", priority, resolution_time)

        complaint = Complaint.objects.create(
            name=name,
            email=email,
            mobile=mobile,
            # month=month,
            # day_of_week=day_of_week,
            # is_weekend=is_weekend,
            category=category,
            area=area,
            severity=severity,
            affected_people=affected_people,
            priority=priority or "Low",
            resolution_time=resolution_time or "1",
            # complaint_title=title,
            description=description,
            status="Pending",
            image=image
        )

        # messages.success(request, "Complaint submitted successfully!")
        return redirect("userform:home")   # name of your home URL

    return render(request, "userform/complaint.html")


# ✅ TRACK COMPLAINT
def track_complaint(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    
    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        status = request.POST.get("status")

        if complaint_id:
            complaints = complaints.filter(complaint_id__icontains=complaint_id)

        if status and status != "all":
            complaints = complaints.filter(status=status)

    return render(request, "userform/track_complaint.html", {"complaints": complaints})

def complaint_dashboard_data(request):

    # Status Data
    status_data = Complaint.objects.values('status').annotate(count=Count('status'))

    # Category Data
    category_data = Complaint.objects.values('category').annotate(count=Count('category'))

    # Trend Data (date wise)
    trend_data = Complaint.objects.annotate(date=TruncDate('created_at')) \
        .values('date').annotate(count=Count('id')).order_by('date')

    return JsonResponse({
        "status": list(status_data),
        "category": list(category_data),
        "trend": list(trend_data),
    })
  



# admin dashboard
# ✅ ADMIN DASHBOARD
# def admin_dashboard(request):
#     if request.method == "POST":
#         complaint_id = request.POST.get("complaint_id")
#         new_status = request.POST.get("status")

#         complaint = Complaint.objects.get(id=complaint_id)
#         complaint.status = new_status
#         complaint.save()

#         return redirect("userform:admin_dashboard")

#     complaints = Complaint.objects.all().order_by('-created_at')
#     return render(request, "userform/admin_dashboard.html", {"complaints": complaints})

def admin_check(user):
    return user.is_superuser  # OR user.is_staff


@user_passes_test(admin_check)
def dashboard(request):
    complaints = Complaint.objects.all() # 🔥 Fetch from DB

    area = request.GET.get('area')
    category = request.GET.get('category')
    priority = request.GET.get('priority')
    search = request.GET.get('search')

    # Apply filters
    if area:
        complaints = complaints.filter(area=area)

    if category:
        complaints = complaints.filter(category=category)

    if priority:
        complaints = complaints.filter(priority=priority)

    if search:
        complaints = complaints.filter(description__icontains=search)
        
    paginator = Paginator(complaints, 10)  # 10 per page

    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)

    return render(request, 'userform/dashboard.html', {'complaints': complaints})

@user_passes_test(admin_check, login_url='/login/')  
def analysis_page(request):
      return render(request, 'userform/analysis.html')



# def submit_complaint(request):

#     if request.method == "POST":

#         category = request.POST['category']
#         area = request.POST['area']
#         severity = request.POST['severity']
#         affected_people = int(request.POST['affected_people'])
#         # department = request.POST['department']

#         # 🔥 Call ML function
#         priority, days = predict(category, area, severity, affected_people, department)

#         # Save to DB
#         Complaint.objects.create(
#             category=category,
#             area=area,
#             severity=severity,
#             affected_people=affected_people,
#             # department=department,
#             priority=priority,
#             resolution_days=days,
#             status="Pending"
#         )

#         return redirect('dashboard')
#     return render(request, "userform/complaint.html")
from django.contrib.auth.decorators import user_passes_test

# Check admin
def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def update_status(request):
    if request.method == "POST":
        complaint_id = request.POST.get("id")
        new_status = request.POST.get("status")

        complaint = Complaint.objects.get(id=complaint_id)
        complaint.status = new_status
        complaint.save()

    return redirect("userform:dashboard")


@user_passes_test(is_admin)
def delete_complaint(request):
    if request.method == "POST":
        complaint_id = request.POST.get("id")

        complaint = Complaint.objects.get(id=complaint_id)
        complaint.delete()

    return redirect("userform:dashboard")