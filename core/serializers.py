import json

from rest_framework import serializers
from .models import WoodType, Package, WorkPosition, PackageBoardLengthWidth

from django.db.models import Count

class WorkPositionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkPosition

    def to_representation(self, instance):
        representation = dict()
        representation['id'] = instance.id
        representation['name'] = instance.name

        return representation


class WoodTypeSerializer(serializers.Serializer):

    class Meta:
        model = WoodType

    def to_representation(self, instance):
        representation = dict()
        representation['id'] = instance.id
        representation["wood_name"] = instance.wood_name
        
        return representation

class PackageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Package

    def to_representation(self, instance):
        representation = dict()
        representation['id'] = instance.id
        representation["wood_type"] = WoodTypeSerializer(instance.wood_type).data
        representation["board_height"] = instance.board_height
        representation["board_class"] = instance.board_class
        representation["stock"] = instance.stock
        representation["board_lengths"] = json.loads(instance.board_lengths)
        representation["board_measurement_type"] = instance.board_measurement_type
        representation["board_type"] = instance.board_type
        representation["closed"] = instance.closed
        representation["last_change_data"] = instance.last_change_date

        package_boards = PackageBoardLengthWidth.objects.filter(package_id = instance.id).values('length') \
            .annotate(length_count=Count('length'))

        package_volume = 0
        package_board_lengths_cnt = {}
        for board_length in json.loads(instance.board_lengths):
            package_board_lengths_cnt[board_length] = 0
        for el in package_boards:
            board_length, cnt = el['length'], el['length_count']
            package_board_lengths_cnt[board_length] = cnt
            package_boards_width = PackageBoardLengthWidth.objects.filter(package_id=instance.id, length=board_length).values('width', 'width2') \
                .annotate(width_comb_count=Count('width'))

            for length_width_cnt_comb in package_boards_width:
                width = length_width_cnt_comb['width']
                width2 = length_width_cnt_comb['width2']
                length_width_cnt = length_width_cnt_comb['width_comb_count']            

                if width2 != None:
                    package_volume += (instance.board_height / 100) * 0.5 * ((width/100) + (width2/100)) * (board_length / 100) * length_width_cnt
                else:
                    package_volume += (instance.board_height / 100) * (width/100) * (board_length / 100) * length_width_cnt


        representation['package_volume'] = package_volume
        representation['package_board_lengths_cnt'] = package_board_lengths_cnt
        representation['total_board_cnt'] = sum(package_board_lengths_cnt.values())

        return representation
