from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Teacher, AdminUser, Attendance
from .forms import StudentForm, TeacherForm, AdminForm


def portal(request):
    return render(request, "portal.html")

def home(request):
    return render(request, 'home.html')

def register(request):

    role = request.GET.get("role")

    if role == "student":
        form = StudentForm(request.POST or None)

        if form.is_valid():
            form.save()
            return redirect("/login?role=student")

    elif role == "teacher":
        form = TeacherForm(request.POST or None)

        if form.is_valid():
            form.save()
            return redirect("/login?role=teacher")

    elif role == "admin":
        form = AdminForm(request.POST or None)

        if form.is_valid():
            form.save()
            return redirect("/login?role=admin")

    else:
        form = None

    return render(request, "register.html", {"form": form, "role": role})



def login_view(request):

    role = request.GET.get("role")
    error = None

    if request.method == "POST":

        name = request.POST.get("name", "")
        password = request.POST.get("password", "")

        if not name or not password:
            error = "Please enter both name and password"
        elif role == "student":
            user = Student.objects.filter(name=name, password=password).first()

            if user and user.is_approved:
                request.session["student_id"] = user.id
                return redirect("/student")
            elif user:
                error = "Account not approved by admin"
            else:
                error = "Invalid student credentials"

        elif role == "teacher":
            user = Teacher.objects.filter(name=name, password=password).first()

            if user:
                request.session["teacher_id"] = user.id
                return redirect("/teacher")
            else:
                error = "Invalid teacher credentials"

        elif role == "admin":
            user = AdminUser.objects.filter(name=name, password=password).first()

            if user:
                request.session["admin_id"] = user.id
                return redirect("/admin_dashboard")
            else:
                error = "Invalid admin credentials"
        else:
            error = "Please select a role"

    return render(request, "login.html", {"role": role, "error": error})

@csrf_exempt
def approve_student(request,student_id):
    try:
        student = Student.objects.get(id=student_id)
        student.is_approved = True
        student.save()
    except Student.DoesNotExist:
        pass
    return redirect('/admin_dashboard')
def student_dashboard(request):

    student_id = request.session.get("student_id")
    
    if not student_id:
        return redirect("/login/?role=student")

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        request.session.flush()
        return redirect("/login/?role=student")

    present = Attendance.objects.filter(student=student, status="Present").count()
    absent = Attendance.objects.filter(student=student, status="Absent").count()

    return render(request, "student.html", {
        "student": student,
        "present": present,
        "absent": absent
    })



@csrf_exempt
def teacher_dashboard(request):

    teacher_id = request.session.get("teacher_id")
    
    if not teacher_id:
        return redirect("/login/?role=teacher")

    try:
        teacher = Teacher.objects.get(id=teacher_id)
    except Teacher.DoesNotExist:
        request.session.flush()
        return redirect("/login/?role=teacher")

    students = Student.objects.all()

    if request.method == "POST":

        student_id = request.POST.get("student_id")
        status = request.POST.get("status")

        if student_id and status:
            try:
                student = Student.objects.get(id=student_id)
                Attendance.objects.create(
                    student=student,
                    status=status
                )
            except Student.DoesNotExist:
                pass

    data = []

    for s in students:
        present = Attendance.objects.filter(student=s, status="Present").count()
        absent = Attendance.objects.filter(student=s, status="Absent").count()

        data.append({
            "student": s,
            "present": present,
            "absent": absent,
            "is_approved":s.is_approved
        })

    return render(request, "teacher.html", {"data": data})




def admin_dashboard(request):

    admin_id = request.session.get("admin_id")
    
    if not admin_id:
        return redirect("/login/?role=admin")

    try:
        admin = AdminUser.objects.get(id=admin_id)
    except AdminUser.DoesNotExist:
        request.session.flush()
        return redirect("/login/?role=admin")

    teachers = Teacher.objects.all()
    
    
    students_data = []
    students = Student.objects.all()
    
    for s in students:
        present = Attendance.objects.filter(student=s, status="Present").count()
        absent = Attendance.objects.filter(student=s, status="Absent").count()
        total = present + absent
        
        if total > 0:
            percentage = round((present / total) * 100, 1)
        else:
            percentage = 0
            
        students_data.append({
            "student": s,
            "present": present,
            "absent": absent,
            "percentage": percentage,
            "is_approved": s.is_approved
        })

    return render(request, "admin_dashboard.html", {
        "students_data": students_data,
        "teachers": teachers
    })
def logout_view(request):
   
    Attendance.objects.all().delete()
    

    Student.objects.all().delete()
    
   
    Teacher.objects.all().delete()
    
    AdminUser.objects.all().delete()
    
    
    request.session.flush()
    
    return redirect('home')



@csrf_exempt
def delete_student(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
       
        Attendance.objects.filter(student=student).delete()
        student.delete()
    except Student.DoesNotExist:
        pass
    return redirect('/admin_dashboard/')



@csrf_exempt
def delete_teacher(request, teacher_id):
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.delete()
    except Teacher.DoesNotExist:
        pass
    return redirect('/admin_dashboard/')
