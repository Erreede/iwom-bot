from iWom import iWom
from datetime import datetime
import os

# Rellenar el archivo 'holidays.json' con los días de vacaciones y el archivo 'others.json' con una equivalencia a la siguiente matriz:
# 01 - Vacaciones -> 14
# 02 - Baja médica -> 15
# 03 - Maternidad / paternidad -> 16
# 04 - Permiso retribuido -> 17
# 05 - Excedencia -> 18
# 06 - Permiso autorizado no retribuido -> 19
# 07 - Descanso semanal (trunos) -> 20
# 08 - Compensación de horas -> 21
# 09 - Huelga -> 9

if __name__ == "__main__":
    reg = iWom(os.getenv('username'), os.getenv('password'), datetime.now().strftime('%d/%m/%Y'))
    #reg = iWom(os.getenv('username'), os.getenv('password'), '28/10/2022')
    if len(reg.dates_list) > 0:
        print('Starting the time register process')
        reg.first_step()
    else:
        print('Nothing to do here')