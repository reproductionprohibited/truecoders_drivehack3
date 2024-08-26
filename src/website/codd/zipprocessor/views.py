from datetime import datetime, UTC, timedelta
import io
import pathlib
import random
import zipfile

from django.urls import reverse_lazy
from django.views.generic import View
from django.http import HttpResponseRedirect, FileResponse
from django.shortcuts import render, get_object_or_404
import pandas

from .image_processing import run_image_processing
from .forms import UploadFileForm
from .models import Record, InvalidImage, ValidImage, ContentImage


def generate_mock_data() -> list[dict]:
    return [
            {
                'num': 2 * i + 1,
                'display': [str(random.randint(10000, 20000)) for _ in range(random.randint(0, 3))],
                'mismatch_percentage': random.randint(0, 10 ** 2) / 10 ** 2
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
        return render(request, 'zipprocessor/processing.html')
    
    def post(self, request, *args, **kwargs):
        filename = kwargs['filename']
        result_data = run_image_processing(filepath=f'media/{filename}')
        print(result_data)
        # result_data = generate_mock_data()
        request.session['result_data'] = result_data
        return HttpResponseRedirect(reverse_lazy('zipprocessor:result'))


class ResultView(View):
    template_name = 'zipprocessor/result.html'

    def get(self, request, *args, **kwargs):
        result_data = request.session.get('result_data', None)
        new_result_data = [
            {
                'num': chunk['num'],
                'display': chunk['display'],
                'mismatch_percentage': chunk['mismatch_percentage'] * 100
            } for chunk in result_data
        ]
        # del request.session['result_data']
        print(result_data)
        for chunk in result_data:
            num = chunk['num']
            mismatch_count = len(chunk['display'])
            mismatch_percentage = chunk['mismatch_percentage'] * 100
            record, created = Record.objects.update_or_create(
                num=num,
                defaults={
                    'mismatch_count': mismatch_count,
                    'mismatch_percentage': mismatch_percentage
                }
            )
            record.invalid_images.clear()
            record.content_images.clear()
            record.valid_images.clear()
            for invalid_image_id in chunk['display']:
                inst = InvalidImage.objects.create(image_id=invalid_image_id)
                record.invalid_images.add(inst)
            for valid_image_id in chunk['valid_images']:
                inst = ValidImage.objects.create(image_id=valid_image_id)
                record.valid_images.add(inst)
            for content_image_id in chunk['content']:
                inst = ContentImage.objects.create(image_id=content_image_id)
                record.content_images.add(inst)

        return render(request, 'zipprocessor/result.html', context={'result_data': new_result_data})

    def post(self, request, *args, **kwargs):
        session_data = request.session.get('result_data', None)
        result_data = [
            {
                'num': row['num'],
                'mismatch_cnt': len(row['display']),
                'mismatch_percentage': row['mismatch_percentage'],
                'mismatch_images': ','.join(row['display'])
            } for row in session_data
        ]

        df = pandas.DataFrame(result_data)

        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, sep=';')
        buffer.seek(0)

        response = FileResponse(
            buffer, 
            content_type='text/csv',
            as_attachment=True,
            filename='result.csv'
        )
        return response


class CameraDataView(View):
    def get(self, request):
        records = Record.objects.all().order_by('-mismatch_count', '-mismatch_percentage', '-last_modified', 'num')
        data = [
            {
                'num': str(record.num).zfill(3),
                'last_updated': record.last_modified,
                'mismatch_cnt': record.mismatch_count,
                'mismatch_percentage': round(record.mismatch_percentage, 2),
                'mismatch_img_ids': ','.join([img.image_id for img in record.invalid_images.all()])
            } for record in records
        ]
        return render(request, 'zipprocessor/camera_data.html', context={'result_data': data})

    def post(self, request):
        records = Record.objects.all().order_by('-mismatch_count', '-mismatch_percentage', '-last_modified', 'num')
        data = []
        data = [
            {
                'num': str(record.num).zfill(3),
                'last_updated': (record.last_modified + timedelta(hours=3)).strftime("%d/%m/%Y %H:%M:%S"),
                'mismatch_cnt': record.mismatch_count,
                'mismatch_percentage': round(record.mismatch_percentage, 2),
                'mismatch_img_ids': ','.join([img.image_id for img in record.invalid_images.all()])
            } for record in records
        ]
        df = pandas.DataFrame(data)
        buffer = io.BytesIO()
        df.to_csv(buffer, index=False, sep=';')
        buffer.seek(0)

        response = FileResponse(
            buffer,
            content_type='text/csv',
            as_attachment=True,
            filename='result.csv'
        )
        return response


class CameraDetailsView(View):
    def get(self, request, *args, **kwargs):
        camera_id = kwargs['num']
        camera_record = get_object_or_404(Record, num=camera_id)
        image_urls = [
            image.image_id for image in camera_record.invalid_images.all()
        ]
        valid_image_urls = [
            image.image_id for image in camera_record.valid_images.all()
        ]
        content_urls = list(set([
            '/'.join(image.image_id.split('/')[1:]) for image in camera_record.content_images.all()
        ]))
        return render(
            request,
            'zipprocessor/detail_camera_photos.html',
            context={
                'num': camera_id,
                'images': image_urls,
                'content': content_urls,
                'valid_images': valid_image_urls
            }
        )
