import os
import json
import torch
import torchvision
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision import transforms as T
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

DATASET_DIR = '/Volumes/T9/Kaggle/car detection/Coco Car Damage Dataset'
VAL_DIR = os.path.join(DATASET_DIR, 'val')
MODEL_PATH = os.path.join(DATASET_DIR, 'model_final.pth')

# Categories (merged)
CATEGORIES = {
    1: 'headlamp', 2: 'rear_bumper', 3: 'door', 4: 'hood', 5: 'front_bumper', 6: 'damage'
}
DAMAGE_ID = 6

def get_model(num_classes):
    model = maskrcnn_resnet50_fpn(weights=None) # Load structure
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, hidden_layer, num_classes)
    return model

def get_transform():
    return T.Compose([T.ToTensor()])

def compute_iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou, interArea

def main():
    # Use generic device
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu')
    print(f"Using device: {device}")

    num_classes = 7
    model = get_model(num_classes)
    
    if not os.path.exists(MODEL_PATH):
        print(f"Model file {MODEL_PATH} not found. Waiting for training...")
        return

    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.to(device)
    model.eval()

    # Get sample images from val
    val_files = [f for f in os.listdir(VAL_DIR) if f.endswith('.jpg')]
    sample_files = random.sample(val_files, min(5, len(val_files)))

    for i, file_name in enumerate(sample_files):
        print(f"\nVerifying {file_name}...")
        img_path = os.path.join(VAL_DIR, file_name)
        img = Image.open(img_path).convert("RGB")
        transform = get_transform()
        img_tensor = transform(img).to(device)
        
        with torch.no_grad():
            prediction = model([img_tensor])[0]
            
        # Filter low confidence
        THRESHOLD = 0.5
        
        boxes = prediction['boxes'].cpu().numpy()
        labels = prediction['labels'].cpu().numpy()
        scores = prediction['scores'].cpu().numpy()
        masks = prediction['masks'].cpu().numpy()
        
        keep = scores > THRESHOLD
        boxes = boxes[keep]
        labels = labels[keep]
        scores = scores[keep]
        masks = masks[keep]
        
        print(f"Detected {len(boxes)} objects.")
        
        # Analyze Damage
        damage_indices = [idx for idx, label in enumerate(labels) if label == DAMAGE_ID]
        part_indices = [idx for idx, label in enumerate(labels) if label != DAMAGE_ID]
        
        results = []
        
        if not damage_indices:
            print("No damage detected.")
        else:
            for d_idx in damage_indices:
                d_box = boxes[d_idx]
                d_score = scores[d_idx]
                found_part = False
                
                for p_idx in part_indices:
                    p_box = boxes[p_idx]
                    p_label = labels[p_idx]
                    iou, intersect = compute_iou(d_box, p_box)
                    
                    # If intersection is significant (e.g. damage is inside part)
                    if intersect > 0: # Simple check: any overlap
                        part_name = CATEGORIES.get(p_label, 'unknown')
                        res_str = f"Damage detected on {part_name} (conf {d_score:.2f})"
                        results.append(res_str)
                        print(f"  -> {res_str}")
                        found_part = True
                
                if not found_part:
                    print(f"  -> Damage detected but no specific part overlap (conf {d_score:.2f})")

        # Visualize
        draw = ImageDraw.Draw(img)
        # Draw parts first (blue)
        for idx in part_indices:
            box = boxes[idx]
            label = labels[idx]
            name = CATEGORIES.get(label, 'part')
            draw.rectangle(box, outline='blue', width=3)
            draw.text((box[0], box[1]), name, fill='blue')
            
        # Draw damage (red)
        for idx in damage_indices:
            box = boxes[idx]
            draw.rectangle(box, outline='red', width=3)
            draw.text((box[0], box[1]-10), "DAMAGE", fill='red')

        save_path = os.path.join(DATASET_DIR, f'val_res_{i}.jpg')
        img.save(save_path)
        print(f"Saved result to {save_path}")

if __name__ == "__main__":
    main()
