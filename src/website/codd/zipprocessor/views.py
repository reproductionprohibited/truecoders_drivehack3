# from codd.settings import MEDIA_ROOT

from django.views.generic import TemplateView, View
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, request
from django.shortcuts import render
from datetime import datetime, UTC
import zipfile
import pathlib
import random
from .forms import UploadFileForm


def generate_mock_data() -> list[dict]:
    return [
            {
                'num': 2 * i + 1,
                'display': [random.randint(10000, 20000) for _ in range(3)],
                'mismatch_percentage': random.randint(0, 10 ** 9) / 10 ** 9
            } for i in range(20)
        ]


def handle_uploaded_file(f) -> str:
    timestamp = str(int(datetime.now(UTC).timestamp() * (10 ** 6)))
    zip_path = f"media/{timestamp}.zip"

    with open(zip_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(f"media/{timestamp}")

    pathlib.Path.unlink(zip_path)

    return timestamp


class HomepageView(View):
    def get(self, request):
        form = UploadFileForm()
        return render(request, 'zipprocessor/home.html', {'form': form})

    def post(self, request):
        if not request.user.is_authenticated:
            form = UploadFileForm()
            return render(request, 'zipprocessor/home.html', {'form': form, 'errormessage': 'Вы не авторизованы'})

        form = UploadFileForm(request.POST, request.FILES)
        print(request.FILES)
        if form.is_valid():
            filename = handle_uploaded_file(request.FILES["file"])
            return HttpResponseRedirect(reverse_lazy('zipprocessor:processing_id', kwargs={'filename': filename}))
        else:
            return render(request, 'zipprocessor/home.html', {'form': form, 'errormessage': 'Произошла ошибка загрузки'})


class ProcessingView(View):
    def get(self, request, *args, **kwargs):
        filename = kwargs['filename']
        return render(request, 'zipprocessor/processing.html')
    
    def post(self, request, *args, **kwargs):
        print(args, kwargs)
        
        # HERE WE DO THE PROCESSING...
        result_data = generate_mock_data()
        request.session['result_data'] = result_data
        return HttpResponseRedirect(reverse_lazy('zipprocessor:result'))


class ResultView(View):
    template_name = 'zipprocessor/result.html'
  
    def get(self, request, *args, **kwargs):
        print(args, kwargs)
        result_data = request.session.get('result_data', None)
        del request.session['result_data']
        print(result_data)
        return render(request, 'zipprocessor/result.html', context={'result_data': result_data})
