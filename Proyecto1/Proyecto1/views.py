from django.http import HttpResponse
import datetime

def saludos(request):
    
    documento="""<html>
    <body>

    <h1>
        <strong>
            <span style="color: darkblue;">Bienvenido a </span>
            <span style="color: darkgreen;">Django</span>
            👋🚀🐍
        </strong>
    </h1>

    <hr> <h1 style="color: purple;">
        <b>¡Hola Django! 😎✨</b>
    </h1>

</body>
    
    </html>"""
    
    return HttpResponse(documento)

def despedida(request):
    return HttpResponse("¡nos vemos luego con Django!")

def dameFecha(request):
    fecha_actual= datetime.datetime.now()
    
    documento="""<html>
    <body>

    <h1>
        <strong>
            <span style="color: darkblue;">Bienvenido a </span>
            <span style="color: darkgreen;">Django</span>
            👋🚀🐍
        </strong>
    </h1>

    <hr> <h1 style="color: purple;">
        Fecha y hora actuales %s
    </h1>

</body>
    
    </html>""" %fecha_actual
    
    return HttpResponse (documento)

def calcularEdad (request, agno):
    edadActual =37
    periodo= agno-2025
    edadFutura = edadActual + periodo
    documento="""<html>
    <body>

    <h1>
        <strong>
            <span style="color: darkblue;">Bienvenido a </span>
            <span style="color: darkgreen;">Django</span>
            👋🚀🐍
        </strong>
    </h1>

    <hr> <h1 style="color: purple;">
        <b>En el año %s tendras %s años😎✨</b>
    </h1>

</body>
    
    </html>""" %(agno,edadFutura)
    
    return  HttpResponse(documento)