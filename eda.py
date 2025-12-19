import json
import os
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
from matplotlib.path import Path

# Paths
DATASET_DIR = '/Volumes/T9/Kaggle/car detection/Coco Car Damage Dataset'
TRAIN_DIR = os.path.join(DATASET_DIR, 'train')
VAL_DIR = os.path.join(DATASET_DIR, 'val')

# Annotation Files
PARTS_ANN_FILE = os.path.join(TRAIN_DIR, 'COCO_mul_train_annos.json') # check which carp art damage
DAMAGE_ANN_FILE = os.path.join(TRAIN_DIR, 'COCO_train_annos.json') # if the car is damage or not 

def load_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def get_img_anns(coco_data, img_id):
    return [ann for ann in coco_data['annotations'] if ann['image_id'] == img_id]

def draw_annotations(ax, anns, categories, color_map, title):
    ax.set_title(title)
    if not anns:
        return

    # Sort by area (large first) so small ones aren't covered, though standard usually transparency handles this
    anns = sorted(anns, key=lambda x: x['area'], reverse=True)

    for ann in anns:
        cat_id = ann['category_id']
        cat_name = categories[cat_id]
        color = color_map.get(cat_id, 'red')
        
        # Draw BBox
        x, y, w, h = ann['bbox']
        rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor=color, facecolor='none', linestyle='--')
        ax.add_patch(rect)
        
        # Draw Text
        ax.text(x, y - 5, cat_name, color=color, fontsize=10, weight='bold', bbox=dict(facecolor='white', alpha=0.7, pad=1))

        # Draw Segmentation
        for seg in ann['segmentation']:
            poly = np.array(seg).reshape((-1, 2))
            patch = patches.Polygon(poly, closed=True, edgecolor=color, facecolor=color, alpha=0.3)
            ax.add_patch(patch)

def main():
    print("Loading annotations...")
    parts_data = load_json(PARTS_ANN_FILE)
    damage_data = load_json(DAMAGE_ANN_FILE)
    
    # Create category maps
    parts_cats = {c['id']: c['name'] for c in parts_data['categories']}
    damage_cats = {c['id']: c['name'] for c in damage_data['categories']}
    
    print(f"Parts Categories: {parts_cats}")
    print(f"Damage Categories: {damage_cats}")

    # Pick a random image that exists in both (assuming IDs match mostly, but let's check filenames)
    # Map filenames to IDs
    parts_img_map = {img['file_name']: img for img in parts_data['images']}
    damage_img_map = {img['file_name']: img for img in damage_data['images']}
    
    # find same files in the data set
    common_files = list(set(parts_img_map.keys()) & set(damage_img_map.keys()))
    print(f"Found {len(common_files)} common images between datasets.")
    
    sample_files = random.sample(common_files, min(3, len(common_files)))
    
    for i, file_name in enumerate(sample_files):
        # checks if image path exists
        print(f"Visualizing {file_name}...")
        img_path = os.path.join(TRAIN_DIR, file_name)
        if not os.path.exists(img_path):
            print(f"Image {img_path} not found, skipping.")
            continue
        
        # retrieving the meta data of the image
        parts_img_info = parts_img_map[file_name]
        damage_img_info = damage_img_map[file_name]
        
        # retrieving the annotations of the image
        parts_anns = get_img_anns(parts_data, parts_img_info['id'])
        damage_anns = get_img_anns(damage_data, damage_img_info['id'])
        
        # Setup plot
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        img = Image.open(img_path)
        
        # Color maps
        parts_colors = {
            1: 'cyan', 2: 'blue', 3: 'green', 4: 'orange', 5: 'purple' 
        } # Adjust based on actual IDs if needed
        damage_colors = {
            1: 'red'
        }
        
        # Original Image
        axes[0].imshow(img)
        axes[0].set_title(f"Original: {file_name}")
        axes[0].axis('off')

        # Parts
        axes[1].imshow(img)
        draw_annotations(axes[1], parts_anns, parts_cats, parts_colors, "Car Parts")
        axes[1].axis('off')

        # Damage
        axes[2].imshow(img)
        draw_annotations(axes[2], damage_anns, damage_cats, damage_colors, "Damage")
        axes[2].axis('off')
        
        out_path = os.path.join(DATASET_DIR, f'eda_vis_{i}.png')
        plt.tight_layout()
        plt.savefig(out_path)
        print(f"Saved visualization to {out_path}")
        plt.close()

if __name__ == "__main__":
    main()
