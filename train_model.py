import os
import json
import torch
import torch.utils.data
from PIL import Image
import numpy as np
import torchvision
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
from torchvision import transforms as T

DATASET_DIR = '/Volumes/T9/Kaggle/car detection/Coco Car Damage Dataset'

class CarDamageDataset(torch.utils.data.Dataset):
    def __init__(self, root, ann_file, transforms=None):
        self.root = root
        self.transforms = transforms
        with open(ann_file, 'r') as f:
            self.coco = json.load(f)
        
        self.categories = {c['id']: c['name'] for c in self.coco['categories']}
        self.img_map = {img['id']: img for img in self.coco['images']}
        self.ids = list(self.img_map.keys())
        
        # Group annotations by image_id for faster access
        self.anns = {}
        for ann in self.coco['annotations']:
            img_id = ann['image_id']
            if img_id not in self.anns:
                self.anns[img_id] = []
            self.anns[img_id].append(ann)

    def __getitem__(self, index):
        img_id = self.ids[index]
        img_info = self.img_map[img_id]
        path = os.path.join(self.root, img_info['file_name'])
        
        img = Image.open(path).convert("RGB")
        
        anns = self.anns.get(img_id, [])
        
        num_objs = len(anns)
        boxes = []
        labels = []
        masks = []
        
        for ann in anns:
            xmin, ymin, w, h = ann['bbox']
            xmax = xmin + w
            ymax = ymin + h
            boxes.append([xmin, ymin, xmax, ymax])
            labels.append(ann['category_id'])
            
            # Create Mask from segmentation
            # Usually we use pycocotools.mask.decode, but here we only have polygons
            # We can use PIL ImageDraw to draw polygon to mask
            from PIL import ImageDraw
            width, height = img_info['width'], img_info['height']
            mask = Image.new('L', (width, height), 0)
            draw = ImageDraw.Draw(mask)
            
            for seg in ann['segmentation']:
                # segmentation is list of floats [x1, y1, x2, y2, ...]
                poly = seg # already flat list
                draw.polygon(poly, outline=1, fill=1)
                
            masks.append(np.array(mask))

        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)
        if masks:
            masks = torch.as_tensor(np.array(masks), dtype=torch.uint8)
        else:
            # Handle no annotations case if any (though unlikely based on checks)
            masks = torch.zeros((0, img_info['height'], img_info['width']), dtype=torch.uint8)
            
        image_id = torch.tensor([img_id])
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
        iscrowd = torch.zeros((num_objs,), dtype=torch.int64)

        target = {}
        target["boxes"] = boxes
        target["labels"] = labels
        target["masks"] = masks
        target["image_id"] = image_id
        target["area"] = area
        target["iscrowd"] = iscrowd

        if self.transforms:
            img = self.transforms(img)
            # Resize or other transforms would need to apply to masks/boxes too
            # For simplicity, we only use ToTensor here which doesn't affect coords

        return img, target

    def __len__(self):
        return len(self.ids)

def get_model(num_classes):
    # Load instance segmentation model pre-trained on COCO
    model = maskrcnn_resnet50_fpn(weights='DEFAULT')

    # Get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    
    # Replace the pre-trained head with a new one
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    # Now get the number of input features for the mask classifier
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    
    # Replace the mask predictor with a new one
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, hidden_layer, num_classes)

    return model

def get_transform(train):
    transforms = []
    transforms.append(T.ToTensor())
    return T.Compose(transforms)

def collate_fn(batch):
    return tuple(zip(*batch))

def main():
    # Use generic device
    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('mps') if torch.backends.mps.is_available() else torch.device('cpu')
    print(f"Using device: {device}")

    # 6 classes + background = 7
    # (Background=0, Headlamp=1, Rear_bumper=2, Door=3, Hood=4, Front_bumper=5, Damage=6)
    num_classes = 7

    dataset = CarDamageDataset(
        root=os.path.join(DATASET_DIR, 'train'),
        ann_file=os.path.join(DATASET_DIR, 'train/COCO_merged_annos.json'),
        transforms=get_transform(train=True)
    )
    
    # Small dataset, num_workers=0 to avoid multiprocessing overhead issues in some envs
    data_loader = torch.utils.data.DataLoader(
        dataset, batch_size=2, shuffle=True, num_workers=0, collate_fn=collate_fn
    )

    model = get_model(num_classes)
    model.to(device)

    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
    
    # Train for 10 epochs
    num_epochs = 10
    
    print("Starting training...")
    for epoch in range(num_epochs):
        model.train()
        i = 0
        epoch_loss = 0
        for images, targets in data_loader:
            images = list(image.to(device) for image in images)
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

            loss_dict = model(images, targets)
            losses = sum(loss for loss in loss_dict.values())

            optimizer.zero_grad()
            losses.backward()
            optimizer.step()
            
            epoch_loss += losses.item()
            
            if i % 10 == 0:
                print(f"Epoch: {epoch}, Iter: {i}, Loss: {losses.item():.4f}")
            i += 1
        print(f"Epoch {epoch} finished. Avg Loss: {epoch_loss/i:.4f}")

    # Save model
    save_path = os.path.join(DATASET_DIR, 'model_final.pth')
    torch.save(model.state_dict(), save_path)
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    main()
