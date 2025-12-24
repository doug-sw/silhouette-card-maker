import math
import os
from PIL import Image, ImageDraw, ImageFont

from utilities import PaperSize

# Specify directory locations
asset_directory = 'assets'

for paper_size in PaperSize:
    base_filename = f'{paper_size.value}_blank.jpg'
    base_path = os.path.join(asset_directory, base_filename)

    # Load a base page
    with Image.open(base_path) as im:
        font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40)
        coord_font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 25)
        
        print_width = im.width
        print_height = im.height
        
        if print_height > print_width:
            im = im.rotate(90, expand=True)
            print_width = im.width
            print_height = im.height
            
        # Grid calibration pages (front/back)
        front_image = im.copy()
        front_draw = ImageDraw.Draw(front_image)
        front_draw.text((print_width - 180, print_height - 180), 'front', fill=(0, 0, 0), anchor="ra", font=font)

        back_image = im.copy()
        back_draw = ImageDraw.Draw(back_image)
        back_draw.text((print_width - 180, print_height - 180), 'back', fill=(0, 0, 0), anchor="ra", font=font)

        # Rotation-only calibration pages (no grid)
        rot_front_image = im.copy()
        rot_front_draw = ImageDraw.Draw(rot_front_image)
        rot_front_draw.text((print_width - 180, print_height - 180), 'front', fill=(0, 0, 0), anchor="ra", font=font)

        rot_back_image = im.copy()
        rot_back_draw = ImageDraw.Draw(rot_back_image)
        rot_back_draw.text((print_width - 180, print_height - 180), 'back', fill=(0, 0, 0), anchor="ra", font=font)

        test_size = 25
        test_half_size = math.floor(test_size / 2)
        test_distance = 75

        matrix_size_x = math.floor(print_width / (test_size + test_distance)) - 6
        matrix_half_size_x = math.floor(matrix_size_x / 2)
        
        matrix_size_y = math.floor(print_height / (test_size + test_distance)) - 6
        matrix_half_size_y = math.floor(matrix_size_y / 2)


        start_x = 0
        if matrix_size_x % 2 > 0:
            start_x = math.floor(print_width / 2) - (matrix_half_size_x * test_distance) - ((matrix_half_size_x + .5) * test_size)
        else:
            if matrix_size_x <= 0:
                raise Exception(f'matrix_size must be greater than 0; received: {matrix_size_x}')
            start_x = math.floor(print_width / 2) - ((matrix_half_size_x - .5) * test_distance) - (matrix_half_size_x * test_size)

        start_y = 0
        if matrix_size_y % 2 > 0:
            start_y = math.floor(print_height / 2) - (matrix_half_size_y * test_distance) - ((matrix_half_size_y + .5) * test_size)
        else:
            if matrix_size_y <= 0:
                raise Exception(f'matrix_size must be greater than 0; received: {matrix_size_y}')
            start_y = math.floor(print_height / 2) - ((matrix_half_size_y - .5) * test_distance) - (matrix_half_size_y * test_size)


        front_draw = ImageDraw.Draw(front_image)
        back_draw = ImageDraw.Draw(back_image)

        for x_index in range(matrix_size_x):
            for y_index in range(matrix_size_y):
                offset_x = x_index * (test_distance + test_size)
                offset_y = y_index * (test_distance + test_size)

                front_element_x = start_x + offset_x
                front_element_y = start_y + offset_y
                front_shape = [(front_element_x, front_element_y), (front_element_x + test_size, front_element_y + test_size)]
                
                fill="black"
                if x_index == matrix_half_size_x or y_index == matrix_half_size_y:
                    fill="blue"

                front_draw.rectangle(front_shape, fill=fill)

                back_element_x = front_element_x + x_index - matrix_half_size_x
                back_element_y = front_element_y + y_index - matrix_half_size_y
                back_shape = [(back_element_x, back_element_y), (back_element_x + test_size, back_element_y + test_size)]

                back_draw.rectangle(back_shape, fill=fill)
                
                back_draw.text((back_element_x + test_half_size, back_element_y + test_half_size + 30), f'({x_index - matrix_half_size_x}, {y_index - matrix_half_size_y})', fill="red", anchor="mm", font=coord_font)

        # Build rotation-only page: origin and centerline markers only
        center_x = math.floor(print_width / 2)
        center_y = math.floor(print_height / 2)

        marker_r = 14
        def draw_marker(draw: ImageDraw.ImageDraw, x: int, y: int, label: str):
            draw.ellipse([(x - marker_r, y - marker_r), (x + marker_r, y + marker_r)], outline=(255, 0, 0), width=3)
            draw.text((x, y - marker_r - 20), label, fill=(0, 0, 0), anchor="ma", font=coord_font)

        # Origin crosshair
        def draw_origin(draw: ImageDraw.ImageDraw):
            draw.line([(center_x - 30, center_y), (center_x + 30, center_y)], fill=(0, 0, 0), width=3)
            draw.line([(center_x, center_y - 30), (center_x, center_y + 30)], fill=(0, 0, 0), width=3)
            draw.text((center_x, center_y - 40), "ORIGIN", fill=(0, 0, 0), anchor="ma", font=coord_font)

        # Front rotation markers
        draw_origin(rot_front_draw)
        draw_marker(rot_front_draw, center_x, 60, "TOP")
        draw_marker(rot_front_draw, center_x, print_height - 60, "BOTTOM")
        draw_marker(rot_front_draw, 60, center_y, "LEFT")
        draw_marker(rot_front_draw, print_width - 60, center_y, "RIGHT")

        # Back rotation markers
        draw_origin(rot_back_draw)
        draw_marker(rot_back_draw, center_x, 60, "TOP")
        draw_marker(rot_back_draw, center_x, print_height - 60, "BOTTOM")
        draw_marker(rot_back_draw, 60, center_y, "LEFT")
        draw_marker(rot_back_draw, print_width - 60, center_y, "RIGHT")

        # Instruction overlay on rotation back page
        height_mm = round(print_height / 300 * 25.4, 2)
        width_mm = round(print_width / 300 * 25.4, 2)
        instruction = (
            f"Rotation calibration: measure horizontal offset (mm) at TOP and BOTTOM along the vertical centerline. "
            f"Angle ≈ (Δx_bottom − Δx_top) / H (radians), H={height_mm}mm. Degrees ≈ above × 57.2958. "
            f"Similarly, measure vertical offset at LEFT and RIGHT; Angle ≈ (Δy_right − Δy_left) / W, W={width_mm}mm."
        )
        rot_back_draw.text((center_x, print_height - 100), instruction, fill=(0, 0, 0), anchor="ma", font=coord_font)

        card_list = [front_image, back_image]
        pdf_path = os.path.join("calibration", f"{paper_size.value}_calibration.pdf")
        card_list[0].save(pdf_path, save_all=True, append_images=card_list[1:], resolution=300, speed=0, subsampling=0, quality=100)

        # Emit a dedicated rotation calibration PDF with no grid
        rot_card_list = [rot_front_image, rot_back_image]
        rot_pdf_path = os.path.join("calibration", f"{paper_size.value}_rotation_calibration.pdf")
        rot_card_list[0].save(rot_pdf_path, save_all=True, append_images=rot_card_list[1:], resolution=300, speed=0, subsampling=0, quality=100)