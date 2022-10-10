import os

import json
from tkinter import Pack
import qrcode

from django.shortcuts import render
from django.db.models import Count
from django.http import (HttpResponse, HttpResponseBadRequest, 
                         HttpResponseForbidden)
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer

from .models import WorkPosition, WoodType, Package, PackageBoardLengthWidth

from .serializers import WorkPositionSerializer, WoodTypeSerializer, PackageSerializer
from .util import print_label

class HelloView(APIView):

    def get(self, request):
        return 'Hello world'

class PositionView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        work_positions = WorkPosition.objects.all()
        serializer = WorkPositionSerializer(work_positions, many=True)
        
        print(serializer.data)

        return Response(serializer.data)


class PackageAddView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        wood_types = WoodTypeSerializer(WoodType.objects.all(), many=True).data
        board_classes = {'oak': Package.BOARD_CLASSES_OAK, 'rest': Package.BOARD_CLASSES_REST}
        board_heights = Package.BoardHeightChoices
        board_lengths = [i for i in range(200, 400, 10)],
        board_measurement_type = Package.BoardMeasurementTypeChoices
        board_widths = [i for i in range(1, 11)]
        board_widths_second = [i for i in range(1, 11)]


        resp = {
            'wood_types': wood_types,
            'board_classes': board_classes,
            'board_heights': board_heights,
            'board_lengths': board_lengths,
            'board_measurement_type': board_measurement_type,
            'board_widths': board_widths,
            'board_widths_second': board_widths_second
        }

        return Response(resp)

    def post(self, request):

        data = json.loads(request.body)

        package = Package(
            wood_type = WoodType.objects.get(wood_name=data['wood_type']),
            board_height = int(data['board_height']),
            board_class = data['board_type'],
            board_measurement_type = data['board_measurement_type'],
            board_lengths = json.dumps(sorted(data['board_length'])),
            board_type = Package.SAMICA,
            stock = Package.WORK_POSITION_STOCK_MAP[int(data['work_position'])]
        )

        package.save()

        serializer = PackageSerializer(package)

        return Response(serializer.data)

class PackagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        work_position = request.GET.get('work_position', None)
        if work_position is None:
            return HttpResponseBadRequest('Work position must not be null')

        packages = Package.objects.all().filter(stock = Package.WORK_POSITION_STOCK_MAP[int(work_position)], closed = Package.OPEN).order_by('board_class', 'board_height').all()

        serializer =PackageSerializer(packages, many=True)
        
        return Response(serializer.data)

class BoardsWidthView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        package_id = request.GET.get('package_id', None)
        length = request.GET.get('length', None)

        if package_id == None:
            return HttpResponseBadRequest('Package id parameter is missing')

        package = Package.objects.all().filter(id = package_id).first()
        if package is None:
            return HttpResponseBadRequest('Package with id={} does not exist'.format(package_id))

        package_boards = PackageBoardLengthWidth.objects.filter(package_id=package_id, length=length).values('width', 'width2') \
            .annotate(width_comb_count=Count('width'))

        return Response(package_boards)

class BoardsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        package_id = request.GET.get('package_id', None)

        if package_id == None:
            return HttpResponseBadRequest('Package id parameter is missing')

        package = Package.objects.all().filter(id = package_id).first()
        if package is None:
            return HttpResponseBadRequest('Package with id={} does not exist'.format(package_id))

        package_boards = PackageBoardLengthWidth.objects.filter(package_id = package_id).values('length') \
            .annotate(length_count=Count('length'))

        package_board_lengths_cnt = {}
        for board_length in json.loads(package.board_lengths):
            package_board_lengths_cnt[board_length] = 0
        for el in package_boards:
            board_length, cnt = el['length'], el['length_count']
            package_board_lengths_cnt[board_length] = cnt

        return Response(package_board_lengths_cnt)

    def post(self, request):
        data = json.loads(request.body)
        print(data)

        package = Package.objects.all().filter(id = data['package_id']).first()

        if data['operation'] == 'add':
            #TODO check for compatibility between board length and package id
            package_board_length_width = PackageBoardLengthWidth(
                package = package,
                length = int(data['board_length']),
                width = data['width_1'],
                width2 = data['width_2'] if data['width_2'] else None
            )
            package_board_length_width.save()
        else:
            cnt = PackageBoardLengthWidth.objects.all().filter(
                    package=package, 
                    length=data['board_length'],
                    width=data['width_1'],
                    width2=data['width_2']).count()

            if cnt == 0:
                return HttpResponseBadRequest(
                    'Board with given length {}, width {}, width2 {} and package id {} does not exits'.format(
                        data['board_length'], data['width_1'], data['width_2'], data['package_id']
                    )
                )

            package_board_length_width = PackageBoardLengthWidth.objects.all().filter(
                    package=package, 
                    length=data['board_length'],
                    width=data['width_1'],
                    width2=data['width_2']).first()
            package_board_length_width.delete()


        package_boards = PackageBoardLengthWidth.objects.filter(package_id = data['package_id']).values('length') \
            .annotate(length_count=Count('length'))

        package_board_lengths_cnt = {}
        for board_length in json.loads(package.board_lengths):
            package_board_lengths_cnt[board_length] = 0
        for el in package_boards:
            board_length, cnt = el['length'], el['length_count']
            package_board_lengths_cnt[board_length] = cnt


        print(package_board_lengths_cnt)
        return Response(package_board_lengths_cnt)

class PackagesCloseView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = json.loads(request.body)

        id = data['id']

        if id == None:
            return HttpResponseBadRequest('Package id parameter is missing')

        package = Package.objects.all().filter(id = id).first()
        if package is None:
            return HttpResponseBadRequest('Package with id={} does not exist'.format(id))

        package.closed = Package.CLOSED
        package.save()

        img = qrcode.make(id)

        qr_file_name = "/Users/leonardokokot/dev/pilana_proj/web/some_file_{}.jpg".format(id)
        img.save(qr_file_name)

        #send image to printer
        #os.system("lpr -P YOUR_PRINTER {}".format(qr_file_name))

        #delete image
        os.remove(qr_file_name)

        return HttpResponse('')

class ClosedPackagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        work_position = request.GET.get('work_position', None)
        if work_position is None:
            return HttpResponseBadRequest('Work position must not be null')

        packages = Package.objects.all().filter(stock = Package.WORK_POSITION_STOCK_MAP[int(work_position)], closed = Package.CLOSED).all()

        serializer =PackageSerializer(packages, many=True)
        
        return Response(serializer.data)

class PackagesOpenView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = json.loads(request.body)

        id = data['id']

        if id == None:
            return HttpResponseBadRequest('Package id parameter is missing')

        package = Package.objects.all().filter(id = id).first()
        if package is None:
            return HttpResponseBadRequest('Package with id={} does not exist'.format(id))

        package.closed = Package.OPEN
        package.save()

        serializer = PackageSerializer(package)

        return Response(serializer.data)

class PackagesUnfinishView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = json.loads(request.body)

        id = data['id']

        if id == None:
            return HttpResponseBadRequest('Package id parameter is missing')

        package = Package.objects.all().filter(id = id).first()
        if package is None:
            return HttpResponseBadRequest('Package with id={} does not exist'.format(id))

        package.closed = Package.UNFINISHED
        package.save()

        print_label(id)

        return HttpResponse('')

class UnfinishedPackagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        work_position = request.GET.get('work_position', None)
        if work_position is None:
            return HttpResponseBadRequest('Work position must not be null')

        packages = Package.objects.all().filter(stock = Package.WORK_POSITION_STOCK_MAP[int(work_position)], closed = Package.UNFINISHED).all()

        serializer =PackageSerializer(packages, many=True)
        
        return Response(serializer.data)

class PrintLabel(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = json.loads(request.body)

        id = data['id']

        if id == None:
            return HttpResponseBadRequest('Package id parameter is missing')

        package = Package.objects.all().filter(id = id).first()
        if package is None:
            return HttpResponseBadRequest('Package with id={} does not exist'.format(id))

        print_label(id)

        return HttpResponse('')