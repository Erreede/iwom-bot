from iWom import iWom
from datetime import datetime
import os

# Los archivos bank_holidays y reduced_hours_days están completados con el calendario laboral de Las Rozas

# Rellenar el archivo 'holidays.json' con los días de vacaciones y el archivo 'others.json' con una equivalencia a la siguiente matriz:
# - Baja médica -> 41
# - Maternidad / paternidad -> 42
# - Permiso retribuido -> 43
# - Excedencia -> 44
# - Permiso autorizado no retribuido -> 78
# - Descanso semanal (turnos) -> 46
# - Compensación de horas -> 47
# - Huelga -> 48

#Ejecutar el script como está para registrar el día en curso, cambiar la linea comentada para registrar desde una fecha
#Ejecutar de la siguiente forma para imputar desde una fecha en concreto:
#iwom = iWom(os.getenv('username'), os.getenv('password'), '01/01/2022')

if __name__ == "__main__":
    iwom = iWom(os.getenv('username'), os.getenv('password'), datetime.now().strftime('%d/%m/%Y'))