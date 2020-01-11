from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.db.models import Q
from django.contrib import messages
from user.forms import CreateForm
from .models import Project
from project.paginations import pagination

# Create your views here.

def project(request):

    template = "project.html"
    object_list = Project.objects.filter(project_status__contains=1).order_by('-project_time')

    pages = pagination(request, object_list, 2)

    context={
        'items': pages[0],
        'page_range': pages[1],
        'nbar': 'project',
    }
    if request.user.is_authenticated:
        return render(request, template, context)
    else:
        return redirect('message:welcome')

def details(request, project_id):
    template = "details.html"
    try:
        details = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist.")
    context = {
        'details': details,
        'nbar': 'project',
    }
    if request.user.is_authenticated:
        return render(request, template, context)
    else:
        return redirect('welcome')

def search(request):
    template = "project.html"
    query = request.GET.get('q')
    if query:
        results = Project.objects.filter(Q(project_title__icontains=query) | Q(project_description__icontains=query))
    else:
        results = Project.objects.filter(project_status__contains=1)
    pages = pagination(request, results, 1)
    context = {
        'items': pages[0], 
        'page_range': pages[1],
        'query': query,
        'nbar': 'project',
    }
    if request.user.is_authenticated:
        return render(request, template, context)
    else:
        return redirect('message:welcome')
    
def create(request):
    if request.method == "POST":
        create_form = CreateForm(request.POST)
        if create_form.is_valid():
            cform = create_form.save(commit=False)
            cform.user = request.user
            cform.save()
            messages.success(request, f'Post successfully created!')
            return redirect('project:project')
    else:
        create_form = CreateForm()
    context={
        "create_form": create_form
    }
    if request.user.is_authenticated:
        return render(request, 'create.html', context)
    else:
        return redirect('user:login')

def update(request, project_id):
    project=Project()
    project_obj = Project.objects.get(pk=project_id)
    context = {
        'project': project_obj,
    }
    uid = request.user.id
    pid = project_obj.user_id
    if uid == pid:
        return render(request, 'update.html', context)
    else:
        return redirect('project:project')

def update_db(request, project_id):
    project_obj = Project.objects.get(pk=project_id)
    project_data = request.POST
    project_obj.project_title = request.POST['title']
    project_obj.project_description = request.POST['description']
    project_obj.project_type = request.POST['pr_type']
    project_obj.save()
    messages.success(request, f'Post updated.')
    return redirect('project:project')
    

def delete(request, project_id):
    project_obj = Project.objects.get(pk = project_id)
    uid = request.user.id
    pid = project_obj.user_id
    if uid == pid:
        project_obj.delete()
        messages.success(request, f'Your post has been deleted.')
        return redirect('project:project')
    else:
        messages.warning(request, f'Cannot delete this post')
        return redirect('project:project')