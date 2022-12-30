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

if __name__ == "__main__":
    iwom = iWom(os.getenv('username'), os.getenv('password'), datetime.now().strftime('%d/%m/%Y'))
    #iwom = iWom(os.getenv('username'), os.getenv('password'), '01/01/2022')
    if (datetime.now().date() - iwom.initial_date).days >= 365:
        print('Can not record dates earlier than 365 days')  
    else:  
        if len(iwom.dates_list) > 0:
            print('Starting the time register process')
            iwom.first_step()
        else:
            print('Nothing to do here')