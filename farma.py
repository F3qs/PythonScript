import os, sys
import minescript
import random
import time
import aim.player_aim
import pyautogui
import threading
import lib_nbt
import java
from minescript_plus import Gui
from minescript_plus import Util

# Dodajemy globalne zmienne
x_monitoring = True
running = True
stop_event = threading.Event()
POSITION_CHANGE_THRESHOLD = 2.0
LAYER_Y_POSITIONS = [67] # dostosuj do swoich potrzeb
START_POS = [47.3, 67, -238.7] # dostosuj współrzędne początkowe

def forw():
    minescript.player_press_forward(True)
    time.sleep(random.uniform(0.2,0.5))
    minescript.player_press_forward(False)
def rand_between(min_val: float, max_val: float) -> float:
    return random.uniform(min_val, max_val)

def moveright():
    minescript.player_press_right(True)
    forw()
    offset = random.uniform(0.4,0.5)
    time.sleep(2)
    while minescript.player_position()[2] < (-49 + offset):
        time.sleep(random.uniform(0.01,0.013))
    else:
        minescript.player_press_right(False)
        time.sleep(1)
def moveleft():
    minescript.player_press_left(True)
    forw()
    offset = random.uniform(0.31,0.65)
    time.sleep(2)
    while minescript.player_position()[2] > (-239 + offset):
        time.sleep(random.uniform(0.01,0.013))
        
    else:
        minescript.player_press_left(False)
        time.sleep(1)
def walknext():
    global x_monitoring, running
    offset = random.uniform(0.8,1)
    walkto = minescript.player_position()[0] + 5 + offset
    
    # Wyłącz monitoring X przed ruchem
    x_monitoring = False
    
    while minescript.player_position()[0] < walkto:
        time.sleep(0.01)
        minescript.player_press_forward(True)
    
    minescript.player_press_forward(False)
    time.sleep(0.1)
    
    # Włącz monitoring X z nową pozycją bazową
    x_monitoring = True


def main():
    global running
    minescript.player_press_attack(True)
    if running and not stop_event.is_set():
        moveright()
        walknext()
        moveleft()
        walknext()
    minescript.player_press_attack(False)

licznik = 0
def ors():
    yaw = -90
    pitch = 0
    aim.player_aim.smooth_rotate_to(yaw, pitch, duration=rand_between(0.5, 0.8))

# Uruchamiamy monitory bezpieczeństwa
def safety_monitor():
    """Monitoruje nagłe zmiany pozycji i orientacji"""
    global running
    prev_pos = minescript.player_position()
    prev_pitch = minescript.player_orientation()[1]
    prev_yaw = minescript.player_orientation()[0]

    while running and not stop_event.is_set():
        current_pos = minescript.player_position()
        current_yaw, current_pitch = minescript.player_orientation()
        dx = abs(current_pos[0] - prev_pos[0])
        dy = abs(current_pos[1] - prev_pos[1])
        dz = abs(current_pos[2] - prev_pos[2])

        if (dx > POSITION_CHANGE_THRESHOLD or dy > POSITION_CHANGE_THRESHOLD or dz > POSITION_CHANGE_THRESHOLD):
            minescript.echo("Sudden position change detected! Stopping.")
            running = False
            stop_event.set()
            break

        pitch_change = abs(current_pitch - prev_pitch)
        if pitch_change > 15:
            Util.play_sound(Util.get_soundevents().BELL_BLOCK)
            Gui.set_title("MACRO CHECK UWAGA")
            Gui.set_subtitle("MYSZKE CI PRZESUNELI")
            running = False
            stop_event.set()
            break

        yaw_change = abs(current_yaw - prev_yaw)
        if yaw_change > 20:
            Util.play_sound(Util.get_soundevents().BELL_BLOCK)
            Gui.set_title("MACRO CHECK UWAGA")
            Gui.set_subtitle("MYSZKE CI PRZESUNELI")
            running = False
            stop_event.set()
            break

        prev_pos = current_pos
        prev_pitch = current_pitch
        prev_yaw = current_yaw
        stop_event.wait(0.05)

def check_blocked():
    """Sprawdza czy gracz jest zablokowany"""
    global running
    last_pos = minescript.player_position()
    stuck_count = 0
    STUCK_THRESHOLD = 0.05
    MAX_STUCK_TIME = 6

    while running and not stop_event.is_set():
        try:
            time.sleep(0.5)
            current_pos = minescript.player_position()
            
            dx = abs(current_pos[0] - last_pos[0])
            dz = abs(current_pos[2] - last_pos[2])
            total_movement = dx + dz

            if total_movement < STUCK_THRESHOLD:
                stuck_count += 1
                minescript.echo(f"Możliwe zablokowanie: {stuck_count}/{MAX_STUCK_TIME*2}")
                if stuck_count >= MAX_STUCK_TIME * 2:
                    Util.play_sound(Util.get_soundevents().BELL_BLOCK)
                    minescript.print("\\suspend")
                    Gui.set_title("MACRO CHECK UWAGA")
                    Gui.set_subtitle("ZOSTAŁEŚ ZABLOKOWANY")
                    minescript.echo("STOP: Wykryto zablokowanie!")
                    minescript.player_press_forward(False)
                    minescript.player_press_attack(False)
                    running = False
                    minescript.print("\\suspend")
                    stop_event.set()
                    return  
            else:
                stuck_count = 0
                
            last_pos = current_pos
        except:
            return

def check_y_level():
    """Monitoruje poziom Y aby wykryć nieoczekiwane spadki"""
    global running
    expected_y_levels = set(LAYER_Y_POSITIONS)
    Y_THRESHOLD = 3  # Maksymalna dozwolona zmiana Y
    
    try:
        last_y = minescript.player_position()[1]
        minescript.echo(f"Start monitorowania Y na poziomie: {last_y:.2f}")

        while running and not stop_event.is_set():
            try:
                time.sleep(0.5)
                current_y = minescript.player_position()[1]
                y_diff = abs(current_y - last_y)
                
                if y_diff > Y_THRESHOLD:
                    minescript.echo(f"Wykryto zmianę wysokości! Różnica: {y_diff:.2f}")
                    Util.play_sound(Util.get_soundevents().BELL_BLOCK)
                    minescript.print("\\suspend")
                    time.sleep(random.uniform(1.5, 2.5))  # Losowe opóźnienie
                    minescript.player_press_forward(False)
                    minescript.player_press_attack(False)
                    minescript.player_press_left(False)
                    minescript.player_press_right(False)
                    running = False
                    Gui.set_title("MACRO CHECK UWAGA")
                    Gui.set_subtitle("PRZESUNAL CIE SIĘ ZA DUŻO W OSI Y")
                    time.sleep(2)
                    minescript.print("\\suspend")
                    stop_event.set()
                    return
                    
                last_y = current_y
                
            except Exception as e:
                minescript.echo(f"Błąd w check_y_level: {str(e)}")
                return
                
    except Exception as e:
        minescript.echo(f"Nie można rozpocząć monitorowania Y: {str(e)}")
        return
                
    except Exception as e:
        minescript.echo(f"Nie można rozpocząć monitorowania Y: {str(e)}")
        return

def check_x_cord():
    """Sprawdza czy gracz nie zboczył z kursu X"""
    global running, x_monitoring
    baseline = minescript.player_position()[0]
    minescript.echo(f"Bazowa pozycja X: {baseline:.2f}")
    
    while running and not stop_event.is_set():
        try:
            stop_event.wait(0.5)
            
            if x_monitoring:
                current_x = minescript.player_position()[0]
                diff = abs(current_x - baseline)
                
                if diff > 1.63:
                    minescript.echo(f"STOP: Zbyt duże odchylenie od linii! (różnica: {diff:.2f})")
                    Gui.set_title("MACRO CHECK UWAGA")
                    Gui.set_subtitle("PRZESUNAL CIE SIĘ ZA BARDZO W OSI X")
                    Util.play_sound(Util.get_soundevents().BELL_BLOCK)
                    time.sleep(random.uniform(1.5, 2.5))  # Losowe opóźnienie
                    minescript.player_press_forward(False)
                    minescript.player_press_attack(False)
                    minescript.player_press_left(False)
                    minescript.player_press_right(False)
                    minescript.print("\\killjob -1")
                    running = False

                    stop_event.set()
                    return
            else:
                baseline = minescript.player_position()[0]
        except:
            return

# Modyfikujemy główną pętlę
def start_safety_threads():
    """Uruchamia wszystkie monitory bezpieczeństwa w osobnych wątkach"""
    threads = []
    monitors = [safety_monitor, check_blocked, check_y_level, check_x_cord]
    
    for monitor in monitors:
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        threads.append(thread)
    return threads
ors()
running = True
safety_threads = start_safety_threads()

while licznik < 99999999 and running and not stop_event.is_set():
    main()
    licznik += 1
    if licznik % 7 == 0:
        running = False
        stop_event.set()
        minescript.chat("/warp garden")
        time.sleep(2)
        ors()
        time.sleep(1)
        stop_event.clear()
        running = True
        safety_threads = start_safety_threads()
        ors()
        time.sleep(1)
    elif licznik % 2 == 0:
        pyautogui.press('f3')
        time.sleep(0.9)
        pyautogui.press('f3')
    
    if stop_event.is_set():
        minescript.echo("Program zatrzymany przez monitor bezpieczeństwa")
        break

# Czyszczenie po zakończeniu
running = False
stop_event.set()
for thread in safety_threads:
    thread.join(timeout=1.0)