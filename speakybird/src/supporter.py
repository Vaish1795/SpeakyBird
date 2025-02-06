import csv
import json
import math
import os
import numpy as np
import pygame as pg
import global_var


def repeat_image(settings, image: pg.Surface, scroll_speed: float = 0):
    # Calculate the number of tiles needed
    tiles = math.ceil(settings.game_screen_width / image.get_width()) + 1
    # Create a surface to hold the tiled image
    tiled_image = pg.Surface((tiles * image.get_width(), image.get_height()), pg.SRCALPHA)

    # Tile the image
    x_position = scroll_speed
    for _ in range(tiles):
        tiled_image.blit(image, (x_position, 0))
        x_position += image.get_width()

    return tiled_image


def show_score(settings, score):
    score_text = settings.font.render(f'{score}', True, (255, 255, 255))
    settings.screen.blit(score_text, (settings.game_screen_width / 2, 20))


def render_message(settings, message):
    while global_var.render_message:
        margin = 50
        available_width = settings.game_screen_width - 2 * margin
        x_start = margin

        lines = []
        current_line = ""
        words = message.split()

        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_surface = settings.calibration_font.render(test_line, True, (255, 255, 255))
            if test_surface.get_width() > available_width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        if current_line:
            lines.append(current_line)

        y = (settings.game_screen_height - len(lines) * settings.calibration_font.get_height()) // 2
        for line in lines:
            message_surface = settings.calibration_font.render(line, True, (255, 255, 255))
            message_rect = message_surface.get_rect(x=x_start, y=y)
            settings.screen.blit(message_surface, message_rect)
            y += settings.calibration_font.get_height() + 10
        global_var.render_message = False
    pg.display.flip()
    pg.display.update()

def calculate_loudness(data):
    if data.size == 0:
        print("No data")
    stream_array = data.astype(np.float64)
    rms = np.sqrt((stream_array * stream_array).sum() / len(stream_array)) / 32767
    db = 20 * np.log10(rms)

    return rms, db


def draw_arc(surf, color, center, radius, width, end_angle_degrees):
    if global_var.calibrate_screen_state:
        arc_rect = pg.Rect(0, 0, radius * 2, radius * 2)
        arc_rect.center = center
        end_angle_radians = math.radians(end_angle_degrees)  # Convert degrees to radians
        pg.draw.arc(surf, color, arc_rect, 0, end_angle_radians, width)


def save_to_csv(json_file_path, csv_file_path):
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)

    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def get_next_counter(counter_file):
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as f:
            counter = int(f.read().strip()) + 1
    else:
        counter = 1

    # Save the updated counter back to the file
    with open(counter_file, 'w') as f:
        f.write(str(counter))

    return counter

def save_data_to_csv(directory, base_file_name, data, headers):
    # Define the directory for saving CSV files
    output_dir = os.path.join(os.getcwd(), directory)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the next available counter for this type of data
    counter_file = os.path.join(output_dir, f"{base_file_name}_counter.txt")
    counter = get_next_counter(counter_file)

    # Generate file name with incremented counter
    file_name = f"{base_file_name}_{counter}.csv"
    csv_path = os.path.join(output_dir, file_name)

    # Write the data to the CSV file
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)

    print(f"Data saved to {csv_path}")
    return csv_path

def display_word(settings, text, color):
    text = text.upper()
    text_surface = settings.command_font.render(text, True, color)
    margin_bottom = 20
    text_rect = text_surface.get_rect(center=(settings.game_screen_width // 2, settings.game_screen_height - margin_bottom - text_surface.get_height() // 2))
    settings.screen.blit(text_surface, text_rect)

def calculate_number_of_words(text):
    return len(text.split())

def load_avatar(avatar_path):
    try:
        avatar = pg.image.load(avatar_path).convert_alpha()
        return pg.transform.scale(avatar, (50, 50))
    except Exception as e:
        print(f"Error loading avatar: {e}")
        return None

def load_leaderboard(settings):
    leaderboard = []
    with open(settings.csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            leaderboard.append({
                "name": row["player_name"],
                "score": int(row["score"]),
                "avatar": row['avatar_path']
            })
    leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)
    return leaderboard