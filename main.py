from iWom import iWom
from datetime import datetime
import os

# Los archivos bank_holidays y reduced_hours_days están completados con el calendario laboral de Las Rozas

# Rellenar el archivo 'holidays.json' con los días de vacaciones y el archivo 'others.json' con una equivalencia a la siguiente matriz:
# - Baja médica -> 15
# - Maternidad / paternidad -> 16
# - Permiso retribuido -> 17
# - Excedencia -> 18
# - Permiso autorizado no retribuido -> 19
# - Descanso semanal (turnos) -> 20
# - Compensación de horas -> 21
# - Huelga -> 9

#Ejecutar el script como está para registrar el día en curso, cambiar la linea comentada para registrar desde una fecha
#Ejecutar de la siguiente forma para imputar desde una fecha en concreto:
#iwom = iWom(os.getenv('username'), os.getenv('password'), '01/01/2022')

if __name__ == "__main__":
    iwom = iWom(os.getenv('username'), os.getenv('password'))