from iWom import iWom
from datetime import datetime
import os

# Rellenar el archivo 'holidays.json' con los días de vacaciones y el archivo 'others.json' con una equivalencia a la siguiente matriz:
# 02 - Baja médica -> 15
# 03 - Maternidad / paternidad -> 16
# 04 - Permiso retribuido -> 17
# 05 - Excedencia -> 18
# 06 - Permiso autorizado no retribuido -> 19
# 07 - Descanso semanal (trunos) -> 20
# 08 - Compensación de horas -> 21
# 09 - Huelga -> 9

#Ejecutar el script como está para registrar el día en curso, cambiar la linea comentada para registrar desde una fecha

if __name__ == "__main__":
    reg = iWom(os.getenv('endpoint'), os.getenv('username'), os.getenv('password'), datetime.now().strftime('%d/%m/%Y'))
    #reg = iWom(os.getenv('endpoint'), os.getenv('username'), os.getenv('password'), '01/01/2022')
    if (datetime.now().date() - reg.initial_date).days >= 365:
        print('Can not record dates earlier to 365 days')  
    else:  
        if len(reg.dates_list) > 0:
            print('Starting the time register process')
            reg.first_step()
        else:
            print('Nothing to do here')