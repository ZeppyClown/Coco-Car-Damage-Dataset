# Car Damage Detector

This repository contains a complete pipeline to train and run a Mask R-CNN model for detecting car damage and identifying which part of the car is damaged.

## Prerequisites

Ensure you have Python 3.8+ installed.

### 1. Install Dependencies
Install the required libraries (PyTorch, Torchvision, PIL, Matplotlib).

```bash
pip install torch torchvision numpy matplotlib pillow
```

### For NVIDIA GPUs (CUDA)
If you are switching to a Windows or Linux machine with an NVIDIA GPU, use this command to install the CUDA version:

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```
*(Note: Change `cu118` to `cu121` if you have a newer driver)*

## Quick Start Guide

Follow these steps in order to build and run the system.

### Step 1: Prepare the Data
The dataset comes with separate files for "Parts" and "Damage". We need to merge them first.

```bash
python merge_dataset.py
```
*   **Input**: `COCO_mul_train_annos.json` (Parts) & `COCO_train_annos.json` (Damage)
*   **Output**: `COCO_merged_annos.json` (Ready for training)

### Step 2: Train the Model
Train the Mask R-CNN model on the merged dataset.

```bash
python train_model.py
```
*   **Action**: Trains for 10 epochs. 
*   **Output**: Saves the trained brain to `model_final.pth`.
*   *Note: This script automatically detects if you have a GPU (CUDA/MPS) and uses it.*

### Step 3: Verify & Test
Run the trained model on hidden validation images to see if it works.

```bash
python verify_model.py
```
*   **Action**: Loads `model_final.pth`, detects damage on validation images, and saves the results.
*   **Output**: Images like `val_res_0.jpg` with red boxes (Damage) and blue boxes (Parts).

### Optional: Exploratory Data Analysis (EDA)
If you want to visualize the raw dataset before training:
```bash
python eda.py
```

## Files Overview
*   `merge_dataset.py`: scripts to fix ID conflicts and merge JSONs.
*   `train_model.py`: Main training loop using PyTorch Mask R-CNN.
*   `verify_model.py`: Inference script for testing.
*   `eda.py`: Visualization tool for raw data.
