import json
import os

DATASET_DIR = '/Volumes/T9/Kaggle/car detection/Coco Car Damage Dataset'

def merge_annotations(parts_path, damage_path, output_path):
    print(f"Merging {parts_path} and {damage_path}...")
    with open(parts_path, 'r') as f:
        parts_data = json.load(f)
    with open(damage_path, 'r') as f:
        damage_data = json.load(f)

    # 1. Categories
    # Parts: 1-5 (keep)
    # Damage: 1 -> 6 (remap)
    new_categories = parts_data['categories'][:] # copy
    
    # Check if damage category exists (it does, id=1, name='damage')
    # We create a new category for it
    damage_category = {'id': 6, 'name': 'damage', 'supercategory': 'damage'}
    new_categories.append(damage_category)
    
    print("New Categories:", new_categories)

    # 2. Images
    # Create a dictionary by file_name to avoid duplicates and ensure consistent metadata
    img_map = {}
    for img in parts_data['images']:
        img_map[img['file_name']] = img
    
    for img in damage_data['images']:
        if img['file_name'] not in img_map:
            img_map[img['file_name']] = img
        # else: ensure IDs match? They should if they come from same source. 
        # But let's verify or enforce one ID map.
    
    # We will regenerate image_id map to be safe: file_name -> new_image_id
    new_images = []
    filename_to_id = {}
    for idx, (filename, img_data) in enumerate(img_map.items()):
        new_id = idx
        img_data['id'] = new_id
        new_images.append(img_data)
        filename_to_id[filename] = new_id
        
    print(f"Total Images: {len(new_images)}")

    # 3. Annotations
    new_annotations = []
    ann_id_counter = 0

    # Process Parts (keep category_id)
    for ann in parts_data['annotations']:
        # Update image_id
        # Find filename for this old image_id
        # Takes time to lookup, better to build map first
        # But wait, original files might have different image_ids for same file?
        # Let's map old_image_id -> filename -> new_image_id
        pass 
    
    # Efficient Mapping Strategy
    # Parts: old_img_id -> filename
    parts_id_to_filename = {img['id']: img['file_name'] for img in parts_data['images']}
    # Damage: old_img_id -> filename
    damage_id_to_filename = {img['id']: img['file_name'] for img in damage_data['images']}
    
    # Add Parts Annotations
    for ann in parts_data['annotations']:
        old_img_id = ann['image_id']
        if old_img_id not in parts_id_to_filename:
            continue # Should not happen
        filename = parts_id_to_filename[old_img_id]
        new_img_id = filename_to_id[filename]
        
        new_ann = ann.copy()
        new_ann['id'] = ann_id_counter
        new_ann['image_id'] = new_img_id
        # category_id stays same (1-5)
        new_annotations.append(new_ann)
        ann_id_counter += 1
        
    # Add Damage Annotations
    for ann in damage_data['annotations']:
        old_img_id = ann['image_id']
        if old_img_id not in damage_id_to_filename:
            continue
        filename = damage_id_to_filename[old_img_id]
        new_img_id = filename_to_id[filename]
        
        new_ann = ann.copy()
        new_ann['id'] = ann_id_counter
        new_ann['image_id'] = new_img_id
        new_ann['category_id'] = 6 # Remap 1 -> 6
        new_annotations.append(new_ann)
        ann_id_counter += 1
        
    print(f"Total Annotations: {len(new_annotations)}")

    merged_data = {
        'info': parts_data.get('info', {}),
        'licenses': parts_data.get('licenses', []),
        'images': new_images,
        'annotations': new_annotations,
        'categories': new_categories
    }

    with open(output_path, 'w') as f:
        json.dump(merged_data, f)
    print(f"Saved merged annotations to {output_path}")

def main():
    # Train
    merge_annotations(
        os.path.join(DATASET_DIR, 'train/COCO_mul_train_annos.json'),
        os.path.join(DATASET_DIR, 'train/COCO_train_annos.json'),
        os.path.join(DATASET_DIR, 'train/COCO_merged_annos.json')
    )
    # Val
    merge_annotations(
        os.path.join(DATASET_DIR, 'val/COCO_mul_val_annos.json'),
        os.path.join(DATASET_DIR, 'val/COCO_val_annos.json'),
        os.path.join(DATASET_DIR, 'val/COCO_merged_annos.json')
    )

if __name__ == '__main__':
    main()
