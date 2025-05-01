from django.db import models

class MQS(models.Model):
    Date             = models.DateField()
    Time             = models.TimeField()
    Line             = models.CharField(max_length=50)
    Family           = models.CharField(max_length=50)
    Model            = models.CharField(max_length=50)
    Process          = models.CharField(max_length=100)
    Station          = models.CharField(max_length=100)
    Fixture          = models.CharField(max_length=100)
    TrackId          = models.CharField(max_length=100)
    NTF              = models.BooleanField()
    Prime            = models.BooleanField()
    Testcode         = models.CharField(max_length=100)
    Testcode_Desc    = models.CharField(max_length=200)
    Fail_Desc        = models.CharField(max_length=200)
    TestTime         = models.FloatField()
    Test_Val         = models.FloatField()
    LL               = models.FloatField()
    UL               = models.FloatField()

    class Meta:
        constraints = [
            # un único registro por fecha, hora, línea y testcode
            models.UniqueConstraint(
                fields=['Date','Time','Line','Testcode'],
                name='uq_mqs_date_time_line_testcode'
            )
        ]

class MES(models.Model):
    FECHA_REPARACION    = models.DateField()
    HORA_REPARACION     = models.TimeField()
    FECHA_RECHAZO       = models.DateField()
    HORA_RECHAZO        = models.TimeField()
    POSICION            = models.CharField(max_length=100)
    FUNCION             = models.CharField(max_length=100)
    CODIGO_FALLA        = models.CharField(max_length=200)
    CAUSA               = models.CharField(max_length=200)
    ACCION              = models.CharField(max_length=200)
    ORIGEN              = models.CharField(max_length=50)
    IMAGEN              = models.TextField()
    REPARADOR           = models.CharField(max_length=100)
    COMENTARIO          = models.TextField()
    TrackID             = models.CharField(max_length=100)
    TestCode            = models.CharField(max_length=100)

    class Meta:
        constraints = [
            # único por reparación y rechazo para evitar reimportar el mismo evento
            models.UniqueConstraint(
                fields=[
                    'FECHA_REPARACION','HORA_REPARACION',
                    'FECHA_RECHAZO','HORA_RECHAZO',
                    'CODIGO_FALLA'
                ],
                name='uq_mes_reparacion_rechazo_codigo'
            )
        ]

class Pendiente(models.Model):
    MODELO         = models.CharField(max_length=50)
    NS             = models.CharField(max_length=100)
    FECHA_RECHAZO  = models.DateField()
    HORA_RECHAZO   = models.TimeField()
    FUNCION        = models.CharField(max_length=100)
    CODIGO_FALLA   = models.CharField(max_length=200)
    CAUSA          = models.CharField(max_length=200)
    ORIGEN         = models.CharField(max_length=50)
    REPARADOR      = models.CharField(max_length=100)

    class Meta:
        constraints = [
            # único por serie y código de falla en esa fecha/hora
            models.UniqueConstraint(
                fields=['NS','FECHA_RECHAZO','HORA_RECHAZO','CODIGO_FALLA'],
                name='uq_pendiente_ns_fecha_hora_codigo'
            )
        ]

class YieldTurno(models.Model):
    Date               = models.DateField()
    Jornada            = models.CharField(max_length=50)
    Turno              = models.CharField(max_length=50)
    Line               = models.CharField(max_length=50)
    Family             = models.CharField(max_length=50)
    Process            = models.CharField(max_length=100)
    Prime_Pass         = models.FloatField()
    Prime_Fail         = models.FloatField()
    Prime_Handle       = models.FloatField()
    Prime_NTF_Count    = models.IntegerField()
    Prime_Defect_Count = models.IntegerField()

    class Meta:
        constraints = [
            # único por fecha, turno, línea y proceso
            models.UniqueConstraint(
                fields=['Date','Turno','Line','Process'],
                name='uq_yieldturno_date_turno_line_process'
            )
        ]

class Sampling(models.Model):
    tipo     = models.CharField(max_length=20)
    Fecha    = models.DateField(null=True)
    Hora     = models.TimeField(null=True)
    dato     = models.TextField()

    class Meta:
        constraints = [
            # evite duplicar el mismo tipo-fecha-hora-dato
            models.UniqueConstraint(
                fields=['tipo','Fecha','Hora','dato'],
                name='uq_sampling_tipo_fecha_hora_dato'
            )
        ]
