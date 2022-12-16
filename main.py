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
    #reg = iWom('Pablo Banuelos', 'super_password', '28/10/2022')
    reg.first_step()