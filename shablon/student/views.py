from django.contrib.auth.mixins import (
    LoginRequiredMixin, 
    UserPassesTestMixin
)

from io import BytesIO
from docxtpl import DocxTemplate
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views import View

from django.shortcuts import get_object_or_404

from django.views.generic import (
    ListView,
    DetailView,
    View,
    CreateView,
    UpdateView,
    DeleteView,
    ListView
)

import csv
from io import TextIOWrapper

from registration.permission import isStudent

from user.models import (
    PracticeStudent,
    Practice,
    StudentProductionTasks,
)

from django.shortcuts import render, get_object_or_404

from django.urls import (
    reverse_lazy,
    reverse,
)

from django.http import HttpResponseRedirect

from .utils import practice_student_test_func

from .forms import (
    CSVFileUploadForm,
)

import csv

def practice_student_test_func(practice_student, student):
    return practice_student.student == student



class StudentMixin(LoginRequiredMixin, UserPassesTestMixin):

    def extra_test_func(self):
        return True
    
    def test_func(self):
        return isStudent(self.request.user) and self.extra_test_func()



class PracticeListView(ListView, StudentMixin):
    template_name = 'student/practice_list.html' 
    context_object_name = 'practices'
    paginate_by = 1

    def get_queryset(self):
        return Practice.objects.filter(group=self.request.user.student.group)
    

class PracticeDetailView(View, StudentMixin):
    template_name = 'student/practice_detail.html' 

    
    def get(self, request, pk):
        practice = get_object_or_404(Practice, pk=pk)
        context = {}
        context['practice'] = practice

        try:
            practice_student = PracticeStudent.objects.get(practice=practice, student=self.request.user.student)
            
        except PracticeStudent.DoesNotExist:
            practice_student = None

        context['practice_student'] = practice_student
        return render(request, self.template_name, context)
    

    def post(self, request, pk):
        practice = get_object_or_404(Practice, pk=pk)
        context = {}
        context['practice'] = practice

        try:
            practice_student = PracticeStudent.objects.get(practice=practice)

        except PracticeStudent.DoesNotExist:
            return HttpResponseBadRequest("Нет отчета")
        
        if not practice_student.ratingpracticestudent:
            return HttpResponseBadRequest("Нет оценки отчета")
        
        
        context = {
            'practice': practice, 
            'practice_student': practice_student,
        }

        tpl = DocxTemplate("C://Users//79828//Desktop//docShablon//shablon//student//shablon//practice_diary_template.docx")
        tpl.render(context)
        output = BytesIO()
        tpl.save(output)
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = f'attachment; filename="generated_report.docx"'

        return response
    
    def extra_test_func(self):
        return practice_student_test_func(self.object, self.request.user.student)



class StudentProductionTasksCreateView(View, StudentMixin):
    model = StudentProductionTasks
    form_class = CSVFileUploadForm

    def post(self, request, *args, **kwargs):
        practice_id = self.kwargs['practice_id']
        practice = get_object_or_404(Practice, pk=practice_id)
        practice_student, created = PracticeStudent.objects.get_or_create(practice=practice, student=self.request.user.student)
        StudentProductionTasks.objects.filter(practice_student=practice_student).delete()
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['csv_file']
            csv_text = TextIOWrapper(uploaded_file, encoding='utf-8')
            csv_reader = csv.DictReader(csv_text)

            for row in csv_reader:
                title = row.get('Subject')
                data_str = row.get('Closed')

                if not data_str or not title or title == "" or data_str == "":
                    return HttpResponseRedirect(self.get_success_url())
                
                data = datetime.strptime(data_str, '%d/%m/%Y %I:%M %p').date()
                
                StudentProductionTasks.objects.create(title=title, data=data, practice_student=practice_student)

        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        practice_id = self.kwargs['practice_id']
        return reverse('student-practice-detail', kwargs={'pk': practice_id})

    def extra_test_func(self):
        return practice_student_test_func(self.object, self.request.user.student)
    


    


