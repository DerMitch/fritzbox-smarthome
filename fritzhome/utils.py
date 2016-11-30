# -*- coding: utf-8 -*-

def c_from_hkr_temperature(val):
    '''Temperatur-Wert in 0,5 °C
    Wertebereich: 16 – 56, 8°C bis 28°C
    16 <= 8°C, 17 = 8,5°C...... 56 >= 28°C
    254 = ON , 253 = OFF
    '''
    val = int(val)
    assert val in range(16, 57) + [253, 254]

    if val == 253:
        return False
    elif val == 254:
        return True
    else:
        return val / 2.0

def c_to_hkr_temperature(val):
    val = int(round(val * 2))
    assert val in range(16, 57)
    return val
