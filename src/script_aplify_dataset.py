#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aumentar un dataset de imágenes mediante diversas transformaciones.
Mantiene la estructura jerárquica original y permite personalizar numeración
de sets y aplicación consistente de filtros.
"""

import os
import cv2
import numpy as np
import argparse
from concurrent.futures import ProcessPoolExecutor
import random
from tqdm import tqdm
import shutil
from collections import defaultdict

def parse_arguments():
    """Define y procesa los argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(description='Aumenta un dataset de imágenes manteniendo la estructura jerárquica.')
    parser.add_argument('--input_dir', type=str, default='data/dataset', 
                        help='Directorio de entrada con las imágenes originales')
    parser.add_argument('--output_dir', type=str, default='data/dataset', 
                        help='Directorio de salida para las imágenes aumentadas')
    parser.add_argument('--augmentations', type=int, default=5, 
                        help='Número de versiones aumentadas a generar por imagen')
    parser.add_argument('--workers', type=int, default=os.cpu_count(), 
                        help='Número de procesos en paralelo a utilizar')
    parser.add_argument('--start_set', type=int, default=31, 
                        help='Número inicial para la numeración de sets (ej: 31)')
    parser.add_argument('--consistent_filters', action='store_true',
                        help='Aplicar filtros consistentemente por set (mismo filtro para todo el set)')
    return parser.parse_args()

def apply_rotation(image, angle=None):
    """Aplica una rotación aleatoria entre -15 y 15 grados."""
    if angle is None:
        angle = random.uniform(-15, 15)
    
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, rotation_matrix, (width, height), 
                             borderMode=cv2.BORDER_REFLECT)
    return rotated

def apply_gaussian_blur(image, kernel_size=None):
    """Aplica un desenfoque gaussiano con un kernel aleatorio entre 3x3 y 7x7."""
    if kernel_size is None:
        # Aseguramos que el kernel size sea impar
        kernel_size = random.choice([3, 5, 7])
    
    blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
    return blurred

def apply_stretch(image, scale_x=None, scale_y=None):
    """Aplica un estiramiento aleatorio entre 0.8 y 1.2 en x o y."""
    if scale_x is None:
        scale_x = random.uniform(0.8, 1.2)
    if scale_y is None:
        scale_y = random.uniform(0.8, 1.2)
    
    height, width = image.shape[:2]
    new_width = int(width * scale_x)
    new_height = int(height * scale_y)
    
    stretched = cv2.resize(image, (new_width, new_height))
    
    # Si la imagen es más grande, recortamos el centro
    if new_width > width or new_height > height:
        start_x = (new_width - width) // 2 if new_width > width else 0
        start_y = (new_height - height) // 2 if new_height > height else 0
        stretched = stretched[start_y:start_y+height, start_x:start_x+width]
    
    # Si la imagen es más pequeña, rellenamos con reflejo de bordes
    if new_width < width or new_height < height:
        top = (height - new_height) // 2 if new_height < height else 0
        bottom = height - new_height - top if new_height < height else 0
        left = (width - new_width) // 2 if new_width < width else 0
        right = width - new_width - left if new_width < width else 0
        stretched = cv2.copyMakeBorder(stretched, top, bottom, left, right, 
                                      cv2.BORDER_REFLECT)
    
    return stretched

def apply_brightness_contrast(image, alpha=None, beta=None):
    """Aplica cambios en brillo y contraste.
    alpha: contraste (1.0 - sin cambio, >1 más contraste, <1 menos contraste)
    beta: brillo (0 - sin cambio, >0 más brillo, <0 menos brillo)
    """
    if alpha is None:
        alpha = random.uniform(0.8, 1.5)
    if beta is None:
        beta = random.randint(-30, 30)
    
    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return adjusted

def apply_color_filters(image, filter_type=None):
    """Aplica diferentes filtros de color (HSV, CLAHE, etc)."""
    if filter_type is None:
        filter_type = random.randint(0, 3)
    
    if filter_type == 0:
        # Aplicar ajuste HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Ajustar el tono (H), saturación (S), y valor (V)
        h, s, v = cv2.split(hsv)
        
        # Random shift en el tono (-10 a 10)
        h = np.mod(h + random.randint(-10, 10), 180).astype(np.uint8)
        
        # Random ajuste de saturación (0.8 a 1.2)
        s = cv2.convertScaleAbs(s, alpha=random.uniform(0.8, 1.2))
        
        # Random ajuste de valor/brillo (0.8 a 1.2)
        v = cv2.convertScaleAbs(v, alpha=random.uniform(0.8, 1.2))
        
        hsv_adjusted = cv2.merge([h, s, v])
        filtered = cv2.cvtColor(hsv_adjusted, cv2.COLOR_HSV2BGR)
    
    elif filter_type == 1:
        # Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clahe = cv2.createCLAHE(clipLimit=random.uniform(1.0, 4.0), 
                               tileGridSize=(8, 8))
        cl = clahe.apply(l)
        
        lab_adjusted = cv2.merge([cl, a, b])
        filtered = cv2.cvtColor(lab_adjusted, cv2.COLOR_LAB2BGR)
    
    elif filter_type == 2:
        # Aplicar un balance de color aleatorio
        b, g, r = cv2.split(image)
        
        # Ajusta el balance entre canales
        r_scale = random.uniform(0.9, 1.1)
        g_scale = random.uniform(0.9, 1.1)
        b_scale = random.uniform(0.9, 1.1)
        
        r = cv2.convertScaleAbs(r, alpha=r_scale)
        g = cv2.convertScaleAbs(g, alpha=g_scale)
        b = cv2.convertScaleAbs(b, alpha=b_scale)
        
        filtered = cv2.merge([b, g, r])
    
    else:  # filter_type == 3
        # Aplicar ajuste de gamma
        gamma = random.uniform(0.8, 1.2)
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255
                         for i in np.arange(0, 256)]).astype("uint8")
        filtered = cv2.LUT(image, table)
    
    return filtered

def generate_augmentation_params():
    """Genera parámetros aleatorios para todas las transformaciones."""
    params = {
        'rotation': {
            'apply': random.random() > 0.3,  # 70% de probabilidad
            'angle': random.uniform(-15, 15)
        },
        'blur': {
            'apply': random.random() > 0.5,  # 50% de probabilidad
            'kernel_size': random.choice([3, 5, 7])
        },
        'stretch': {
            'apply': random.random() > 0.5,  # 50% de probabilidad
            'scale_x': random.uniform(0.8, 1.2),
            'scale_y': random.uniform(0.8, 1.2)
        },
        'brightness_contrast': {
            'apply': random.random() > 0.3,  # 70% de probabilidad
            'alpha': random.uniform(0.8, 1.5),
            'beta': random.randint(-30, 30)
        },
        'color': {
            'apply': random.random() > 0.5,  # 50% de probabilidad
            'filter_type': random.randint(0, 3)
        }
    }
    
    # Aseguramos que al menos se aplique una transformación
    if not any(params[k]['apply'] for k in params):
        # Aplicamos al menos una transformación aleatoria
        random_transform = random.choice(list(params.keys()))
        params[random_transform]['apply'] = True
    
    return params

def augment_image(image, aug_params=None):
    """Aplica una combinación de transformaciones a la imagen según los parámetros dados."""
    if aug_params is None:
        aug_params = generate_augmentation_params()
    
    # Aplicamos las transformaciones en orden
    augmented = image.copy()
    
    if aug_params['rotation']['apply']:
        augmented = apply_rotation(augmented, aug_params['rotation']['angle'])
    
    if aug_params['blur']['apply']:
        augmented = apply_gaussian_blur(augmented, aug_params['blur']['kernel_size'])
    
    if aug_params['stretch']['apply']:
        augmented = apply_stretch(augmented, 
                                 aug_params['stretch']['scale_x'], 
                                 aug_params['stretch']['scale_y'])
    
    if aug_params['brightness_contrast']['apply']:
        augmented = apply_brightness_contrast(
            augmented, 
            aug_params['brightness_contrast']['alpha'], 
            aug_params['brightness_contrast']['beta']
        )
    
    if aug_params['color']['apply']:
        augmented = apply_color_filters(augmented, aug_params['color']['filter_type'])
    
    return augmented

def process_image(args):
    """Procesa una imagen, aplica aumentación y guarda las versiones aumentadas."""
    img_path, output_path, aug_params = args
    
    # Crear directorio de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Leer la imagen
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error al leer la imagen: {img_path}")
        return
    
    # Generar versión aumentada con los parámetros dados
    aug_img = augment_image(img, aug_params)
    
    # Guardar la imagen aumentada
    cv2.imwrite(output_path, aug_img)

def parse_path_structure(path, input_dir):
    """Extrae la estructura class/set/seq de la ruta del archivo."""
    rel_path = os.path.relpath(path, input_dir)
    parts = rel_path.split(os.sep)
    
    if len(parts) >= 3:
        class_name = parts[0]  # class_X
        set_name = parts[1]    # set_Y
        seq_name = parts[2]    # seq_Z
        
        # El último elemento puede ser el nombre del archivo
        if len(parts) > 3:
            file_name = parts[-1]
        else:
            file_name = ""
            
        return {
            'class': class_name,
            'set': set_name,
            'seq': seq_name,
            'file': file_name
        }
    
    return None

def group_by_structure(image_paths, input_dir):
    """Agrupa las imágenes según su estructura class/set/seq."""
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for img_path in image_paths:
        structure = parse_path_structure(img_path, input_dir)
        if structure:
            class_name = structure['class']
            set_name = structure['set']
            seq_name = structure['seq']
            grouped[class_name][set_name][seq_name].append(img_path)
    
    return grouped

def find_images(input_dir):
    """Encuentra todas las imágenes en el directorio de entrada."""
    image_paths = []
    
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_paths.append(os.path.join(root, file))
    
    return image_paths

def main():
    """Función principal del script."""
    args = parse_arguments()
    
    print(f"Buscando imágenes en: {args.input_dir}")
    image_paths = find_images(args.input_dir)
    
    if not image_paths:
        print("No se encontraron imágenes en el directorio especificado.")
        return
    
    print(f"Se encontraron {len(image_paths)} imágenes.")
    
    # Agrupar imágenes por class/set/seq
    grouped_images = group_by_structure(image_paths, args.input_dir)
    
    # Para cada tipo de augmentación
    for aug_idx in range(args.augmentations):
        print(f"\nGenerando augmentación {aug_idx+1}/{args.augmentations}...")
        
        process_args = []
        current_set_id = args.start_set
        
        # Para cada clase
        for class_name, sets in grouped_images.items():
            # Para cada set en la clase
            for set_name, sequences in sets.items():
                # Generar parámetros de augmentación consistentes para todo el set
                # si la opción está activada
                set_aug_params = generate_augmentation_params() if args.consistent_filters else None
                
                # Nuevo nombre de set con numeración incremental
                new_set_name = f"set_{current_set_id}"
                
                # Para cada secuencia en el set
                for seq_name, images in sequences.items():
                    # Para cada imagen en la secuencia
                    for img_path in images:
                        # Obtener el nombre base del archivo
                        base_name = os.path.basename(img_path)
                        name, ext = os.path.splitext(base_name)
                        
                        # Construir ruta de salida con la nueva estructura
                        output_path = os.path.join(
                            args.output_dir,
                            class_name,
                            new_set_name,
                            seq_name,
                            f"{name}_aug{aug_idx+1}{ext}"
                        )
                        
                        # Si no se usa filtro consistente por set, generar nuevos parámetros
                        img_aug_params = set_aug_params if args.consistent_filters else generate_augmentation_params()
                        
                        process_args.append((img_path, output_path, img_aug_params))
                
                # Incrementar el ID del set para la siguiente iteración
                current_set_id += 1
        
        # Procesar imágenes en paralelo para esta augmentación
        num_workers = min(args.workers, len(process_args))
        print(f"Procesando imágenes con {num_workers} workers...")
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            list(tqdm(executor.map(process_image, process_args), total=len(process_args)))
    
    print(f"Proceso completado. Imágenes aumentadas guardadas en: {args.output_dir}")

if __name__ == "__main__":
    main()
