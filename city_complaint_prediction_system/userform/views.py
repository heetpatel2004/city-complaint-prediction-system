from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from .models import Complaint
from .ml_model import predict
import pandas as pd



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
        severity = request.POST.get('severity')   or 'Medium'
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


# admin dashboard
# ✅ ADMIN DASHBOARD
def admin_dashboard(request):
    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        new_status = request.POST.get("status")

        complaint = Complaint.objects.get(id=complaint_id)
        complaint.status = new_status
        complaint.save()

        return redirect("userform:admin_dashboard")

    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, "userform/admin_dashboard.html", {"complaints": complaints})



def dashboard(request):
    complaints = Complaint.objects.all() # 🔥 Fetch from DB
    
    for c in complaints:
            print(c.severity, c.priority, c.status)
    return render(request, 'userform/dashboard.html', {'complaints': complaints})



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