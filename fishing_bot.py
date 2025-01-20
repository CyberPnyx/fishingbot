import pyautogui
import math
import time
from pynput.keyboard import Controller, Listener, Key

# Initialisation du contrôleur clavier
keyboard = Controller()

# Définir les paramètres du cercle
center_x = 968
center_y = 546
radius = 72
num_points = 20  # Nombre de points à vérifier sur le cercle

# Définir la couleur cible (bleu) et la tolérance
target_color = (81, 158, 198)
tolerance = 10

# Définir les chemins des images
start_image_path = "resources/start.png"
no_place_image_path = "resources/no_place.png"
no_fish_image_path = "resources/no_fish.png"

# Variable pour quitter le programme
exit_program = False

def is_color_close(color, target_color, tolerance=10):
    """
    Vérifie si une couleur est proche d'une couleur cible avec une tolérance.
    """
    return all(abs(color[i] - target_color[i]) <= tolerance for i in range(3))

def get_circle_points(center_x, center_y, radius, num_points):
    """
    Génère les coordonnées des points sur le contour du cercle.
    """
    points = []
    angle_step = 2 * math.pi / num_points
    for i in range(num_points):
        angle = i * angle_step
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        points.append((x, y))
    return points

def detect_image_on_screen(image_path, confidence=0.8):
    """
    Détecte si une image est présente sur l'écran.
    """
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            print(f"Image trouvée à l'emplacement : {location}")
            return location
        else:
            print(f"Image {image_path} non trouvée.")
            return None
    except Exception as e:
        return None

def on_press(key):
    """
    Gestionnaire d'événements pour les appuis sur les touches.
    """
    global exit_program
    if key == Key.esc or (hasattr(key, 'char') and key.char == 'o'):
        print("Commande de sortie détectée. Fermeture du programme...")
        exit_program = True
        return False

if __name__ == "__main__":
    # Démarrer l'écouteur clavier dans un thread séparé
    listener = Listener(on_press=on_press)
    listener.start()

    while not exit_program:
        print("Lancement du programme...")

        # Vérifier l'image no_place avant de chercher start
        while not exit_program:
            start_found = detect_image_on_screen(start_image_path)
            no_fish_found = detect_image_on_screen(no_fish_image_path)
            no_place_found = detect_image_on_screen(no_place_image_path)

            if start_found:
                print("L'image de départ est détectée. Démarrage du processus...")
                break

            if no_place_found:
                print("Aucune place disponible dans l'inventaire.")
                time.sleep(1)
                exit_program = True
                break

            if no_fish_found:
                print("Aucun poisson détecté. Appui sur 'E' et attente...")
                keyboard.press('e')
                time.sleep(0.1)
                keyboard.release('e')
                time.sleep(1)  # Attendre avant de recommencer
                continue  # Revenir à la recherche de l'image start

            time.sleep(0.1)  # Attendre avant de réessayer

        if exit_program:
            break

        # Récupérer les points du cercle
        circle_points = get_circle_points(center_x, center_y, radius, num_points)

        # Initialiser les variables
        tracked_pixels = {}  # Dictionnaire des pixels surveillés {coord: couleur_initiale}

        print("Recherche de pixels bleus sur le cercle...")
        for x, y in circle_points:
            if exit_program:
                break
            try:
                color = pyautogui.pixel(x, y)
                if is_color_close(color, target_color, tolerance):
                    tracked_pixels[(x, y)] = color
                    print(f"Pixel bleu trouvé à {(x, y)} avec la couleur {color}")
            except Exception as e:
                pass

        if exit_program:
            break

        if not tracked_pixels:
            print("Aucun pixel bleu trouvé sur le cercle. Retour à la recherche de l'image de départ.")
        else:
            print(f"{len(tracked_pixels)} pixels bleus trouvés. Surveillance en cours...")

            # Surveiller les pixels pour un changement de couleur
            while not exit_program:
                pixel_changed = False
                for coord, initial_color in tracked_pixels.items():
                    try:
                        current_color = pyautogui.pixel(*coord)
                        if not is_color_close(current_color, initial_color, tolerance):
                            print(f"Le pixel à {coord} a changé de couleur : {current_color}")
                            print("Appui sur la touche E...")
                            keyboard.press('e')
                            time.sleep(0.1)
                            keyboard.release('e')
                            pixel_changed = True
                            break  # Sortir de la boucle des pixels
                    except Exception as e:
                        print(f"Erreur lors de la vérification du pixel {coord}.")

                if pixel_changed or exit_program:
                    break

        if exit_program:
            break

        time.sleep(2)  # Attendre avant de recommencer la recherche de l'image de départ
        print("Redémarrage de la boucle principale...")
        keyboard.press('e')
        time.sleep(0.1)
        keyboard.release('e')

    print("Programme terminé.")
