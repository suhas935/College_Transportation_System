from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import HttpResponse
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from .models import StudentProfile, BusRoute, Notification, Payment


# ---------------------------- SIGNUP ----------------------------
def signup_view(request):
    if request.method == "POST":
        usn = request.POST['usn']
        password = request.POST['password']
        name = request.POST['name']
        sem = request.POST['sem']
        branch = request.POST['branch']
        email = request.POST['email']
        phone = request.POST['phone']
        emergency_phone = request.POST['emergency_phone']
        photo = request.FILES['photo']

        # ✅ Prevent duplicate user
        if User.objects.filter(username=usn).exists():
            messages.error(request, "USN already registered. Please log in instead.")
            return redirect('signup')

        # Create new user
        user = User.objects.create_user(
            username=usn,
            password=password,
            email=email,
            first_name=name
        )

        # Create Student Profile
        StudentProfile.objects.create(
            user=user,
            usn=usn,
            sem=sem,
            branch=branch,
            phone=phone,
            emergency_phone=emergency_phone,
            photo=photo
        )

        messages.success(request, "Account created successfully! Please log in.")
        return redirect('login')

    return render(request, "signup.html")


# ---------------------------- LOGIN ----------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            # ✅ Redirect based on role
            if user.is_staff:
                return redirect("admin_dashboard")
            else:
                return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


# ---------------------------- STUDENT DASHBOARD ----------------------------
@login_required
def dashboard(request):
    profile = StudentProfile.objects.get(user=request.user)
    route = BusRoute.objects.filter(student=request.user).first()
    payment = Payment.objects.filter(student=request.user).last()

    return render(request, "dashboard.html", {
        "profile": profile,
        "route": route,
        "payment": payment
    })


# ---------------------------- ROUTE REGISTRATION ----------------------------
@login_required
def register_route(request):
    if request.method == "POST":
        BusRoute.objects.create(
            student=request.user,
            location=request.POST["location"],
            route=request.POST["route"]
        )
        messages.success(request, "Bus route registered successfully!")
        return redirect("dashboard")
    return render(request, "register_route.html")


# ---------------------------- NOTIFICATIONS ----------------------------
@login_required
def notifications(request):
    notes = Notification.objects.all().order_by("-created_at")
    return render(request, "notifications.html", {"notifications": notes})


# ---------------------------- BUS TRACKING ----------------------------
@login_required
def bus_tracking(request):
    return render(request, "bus_tracking.html")


# ---------------------------- MAKE PAYMENT ----------------------------
@login_required
def make_payment(request):
    route = BusRoute.objects.filter(student=request.user).first()

    if request.method == "POST":
        Payment.objects.create(
            student=request.user,
            route_name=route.route if route else "N/A",
            amount=15000,  # ✅ Fixed fee
            status="Paid"
        )
        messages.success(request, "Payment of ₹15,000 successful! You can now download your receipt.")
        return redirect("download_receipt")

    return render(request, "make_payment.html", {"route": route})


# ---------------------------- DOWNLOAD RECEIPT ----------------------------
@login_required
def download_receipt(request):
    payment = Payment.objects.filter(student=request.user).last()

    if not payment:
        messages.error(request, "No payment record found.")
        return redirect("dashboard")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>SJB INSTITUTE OF TECHNOLOGY</b>", styles["Title"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("<b>College Transportation Fee Receipt</b>", styles["Heading2"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph(f"<b>Student:</b> {payment.student.first_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Route:</b> {payment.route_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Amount Paid:</b> ₹{payment.amount}", styles["Normal"]))
    story.append(Paragraph(f"<b>Date:</b> {payment.date.strftime('%d-%m-%Y %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Thank you for using the College Transportation Service.", styles["Italic"]))

    doc.build(story)
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


# ---------------------------- ADMIN DASHBOARD ----------------------------
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("dashboard")

    from .models import StudentProfile, BusRoute, Payment, Notification

    search = request.GET.get("search", "")
    branch_filter = request.GET.get("branch", "")
    route_filter = request.GET.get("route", "")

    # Get all students
    students = StudentProfile.objects.all()

    # Apply search and filters
    if search:
        students = students.filter(user__first_name__icontains=search) | students.filter(usn__icontains=search)
    if branch_filter:
        students = students.filter(branch=branch_filter)

    # Add route + payment info
    data = []
    for s in students:
        route = BusRoute.objects.filter(student=s.user).first()
        payment = Payment.objects.filter(student=s.user).last()
        data.append({
            "usn": s.usn,
            "user": s.user,
            "branch": s.branch,
            "sem": s.sem,
            "route_name": route.route if route else "Not Registered",
            "location": route.location if route else "-",
            "payment_status": "Paid" if payment else "Not Paid",
            "amount": payment.amount if payment else 0,
            "payment_date": payment.date if payment else None,
        })

    notifications = Notification.objects.all().order_by('-created_at')
    branches = StudentProfile.objects.values_list('branch', flat=True).distinct()
    routes = BusRoute.objects.all()

    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")
        notif_type = request.POST.get("notif_type")
        if title and message and notif_type:
            Notification.objects.create(title=title, message=message, notif_type=notif_type)
        return redirect("admin_dashboard")

    return render(request, "admin_dashboard.html", {
        "students": data,
        "notifications": notifications,
        "branches": branches,
        "routes": routes,
    })
