from email.policy import default
from django.db import models


class WorkPosition(models.Model):
    name = models.CharField(max_length=50)


class WoodType(models.Model):
    id = models.AutoField(primary_key=True)
    wood_name = models.CharField(max_length=50)


class Package(models.Model):

    W1 = 26
    W2 = 32
    W3 = 38
    W4 = 50
    W5 = 60
    BoardHeightChoices=[
        (W1, str(W1)),
        (W2, str(W2)),
        (W3, str(W3)),
        (W4, str(W4)),
        (W5, str(W5)),
    ]

    UNUTAR_KOSINE = 'UK'
    POLA_KOSINE = 'PK'
    JEDNA_KOSINA = 'JK'
    PUNA_SIRINA = 'PS'
    DVIJE_SIRINE = 'DS'
    BoardMeasurementTypeChoices=[
        (UNUTAR_KOSINE, 'Unutar kosine'),
        (POLA_KOSINE, 'Pola kosine'),
        (JEDNA_KOSINA, 'Jedna kosina'),
        (PUNA_SIRINA, 'Puna sirina'),
        (DVIJE_SIRINE, 'Dvije sirine')
    ]


    S1 = 'S1'
    S2 = 'S2'
    PackageStockChoices = [
        (S1, 'Sjekac 1'),
        (S2, 'Sjeka 2')
    ]

    MIX = 'MIX'
    SAMICA = 'SAMICA'
    POLUSAMICA = 'POLUSAMICA'
    OKRAJCENA = 'OKRAJCENA'
    BoardTypes=[
        (MIX, 'Mix'),
        (SAMICA, 'Samica'),
        (POLUSAMICA, 'Polusamica'),
        (OKRAJCENA, 'Okrajcena'),
    ]

    P1 = 'Sjekac 1'
    P2 = 'Sjekac 2'
    S = 'Skladiste'
    Stocks=[
        (P1, P1),
        (P2, P2),
        (S, S),
    ]

    WORK_POSITION_STOCK_MAP = {
        1: P1,
        2: P2,
    }

    OPEN = 'Open'
    CLOSED = 'Closed'
    UNFINISHED = 'Unfinished'
    PackageOpenChoices = [
        (OPEN, OPEN),
        (CLOSED, CLOSED),
        (UNFINISHED, UNFINISHED)
    ]

    id = models.AutoField(primary_key=True)
    wood_type = models.ForeignKey(WoodType, on_delete=models.RESTRICT)
    board_height = models.PositiveIntegerField(choices=BoardHeightChoices)
    board_class = models.CharField(max_length=10)#TODO, restrict to choices
    stock = models.CharField(max_length=50, choices=Stocks, default=Stocks[-1])
    board_lengths = models.CharField(max_length=100, default="[]")
    board_measurement_type = models.CharField(max_length=30, choices=BoardMeasurementTypeChoices)
    board_type = models.CharField(max_length=30, choices=BoardTypes)

    closed = models.CharField(max_length=20, choices=PackageOpenChoices, default=OPEN)
    last_change_date = models.DateTimeField(auto_now_add=True)#update on every change

    BOARD_CLASSES_REST=['A', 'I-III', 'AB', 'I-IV', 'ABC', 'CD']
    BOARD_CLASSES_OAK=['I-III', 'I-V', 'IV-V', 'dorada']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        oak_object_id=WoodType.objects.filter(wood_name='Hrast')[0]

        if self.wood_type == oak_object_id and self.board_class in Package.BOARD_CLASSES_OAK:
            super(Package, self).save(force_insert, force_update, using, update_fields)
        elif self.wood_type != oak_object_id and self.board_class in Package.BOARD_CLASSES_REST:
            super(Package, self).save(force_insert, force_update, using, update_fields)
        else:
            raise Exception('Unable to save package object to database. Incompatible wood type and board class.')

class PackageBoardLengthWidth(models.Model):
    #id created automatically
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True)
    length = models.PositiveIntegerField(default=200)#TODO, add choices
    width = models.PositiveIntegerField()
    width2 = models.PositiveIntegerField(null=True)
