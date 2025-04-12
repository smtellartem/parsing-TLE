import requests
import math



print("""

                                           _                    _ _     __    ___ 
  __ _   _  _   _ __    _ _    __ _   ___ (_)  _  _   _ __     | | |   /  \  |_  )
 / _` | | || | | '  \  | ' \  / _` | (_-< | | | || | | '  \    |_  _| | () |  / / 
 \__, |  \_, | |_|_|_| |_||_| \__,_| /__/ |_|  \_,_| |_|_|_|     |_|   \__/  /___|
 |___/   |__/                                                                     

""")





url = "https://celestrak.org/NORAD/elements/gp.php?CATNR=61777"

response = requests.get(url)


# Разделение данных на строки
tle_lines = response.text.strip().split('\n')


# Парсинг второй строки TLE
line2 = tle_lines[2].strip().split()


# Извлечение параметров
eccentricity = float(line2[4]) / 1e7 # Эксцентриситет
mean_anomaly = float(line2[6])  # Средняя аномалия
inclination = float(line2[2])  # Наклонение
raan = float(line2[3])  # Долгота восходящего узла
arg_perigee = float(line2[5])   # Аргумент перигея
mean_motion = float(line2[7])  # Среднее движение


print(f"Эксцентриситет {eccentricity}, Средняя аномалия: {mean_anomaly}, Наклонение: {inclination}, Долгота восходящего узла: {raan},  Аргумент перигея: {arg_perigee}, Среднее движение: {mean_motion} " )

e = eccentricity
M = mean_anomaly
M = math.radians(M)

w = arg_perigee

v1 = M + ((2*e * math.sin(M))/ (1 - e * math.cos(M)))
v1 = math.degrees(v1)


u = (w + v1) % 360





true_anomaly = v1
argument_of_latitude = u
E = M





# Результаты расчетов
params = {
    'inclination': inclination,
    'raan': raan,
    'eccentricity': eccentricity,
    'arg_perigee': arg_perigee,
    'mean_anomaly': mean_anomaly,
    'mean_motion': mean_motion,
    'true_anomaly': true_anomaly,
    'argument_of_latitude': argument_of_latitude,
    'eccentric_anomaly': math.degrees(E)
}


print(f"истинная аномалия = {v1}  аргумент широты = {u} ")

