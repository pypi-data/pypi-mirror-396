## Paica

A TensorFlow-based package for generating **Saliency Maps** and **Grad-CAM** visualizations for convolutional neural networks.

This package helps interpret deep learning models by highlighting the regions of an image that most influence model predictions.

---

## Features

- Easy image preprocessing & visualization
- Saliency map generation & visualization
- Grad-CAM++ generation & visualization
- Works with TensorFlow / Keras models
- Supports pretrained models (e.g. VGG16)

---

## Installation

```bash
pip install paica
```
---

## Sample Code

1. Saliency Maps

```python
import tensorflow as tf
from paica import create_image_tensors, smoothgrad_saliency
from paica import visualize_saliency_maps

# Load model
model = tf.keras.models.load_model(model_path)

# Create image tensors
dog_orig, dog_tensor = create_image_tensors(dog_img_path)
cat_orig, cat_tensor = create_image_tensors(cat_image_path)

# Define variables
alpha = 0.5
images = [dog_orig, cat_orig]
image_titles = ['Dog', 'Cat']

# Generate SmoothGrad Saliency Maps
saliency_map_dog = smoothgrad_saliency(model, dog_tensor, class_index=None, n_samples=25, noise_level=0.1)
saliency_map_cat = smoothgrad_saliency(model, cat_tensor, class_index=None, n_samples=25, noise_level=0.1)
saliency_maps = [saliency_map_dog, saliency_map_cat]

# Visualize Saliency Maps
visualize_saliency_maps(image_titles, images, saliency_maps, alpha)
```
---

2. GradCAM++ 

```python
import tensorflow as tf
from paica import create_image_tensors, gradcam_plus_plus
from paica import visualize_grad_cams

# Load model
model = tf.keras.models.load_model(model_path)

# Create image tensors
dog_orig, dog_tensor = create_image_tensors(dog_img_path)
cat_orig, cat_tensor = create_image_tensors(cat_image_path)

# Define variables
alpha = 0.5
images = [dog_orig, cat_orig]
image_titles = ['Dog', 'Cat']

# Find last conv layer name
for layer in model.layers[::-1]:
  if isinstance(layer, tf.keras.layers.Conv2D):
    last_conv_layer_name = str(layer.name)
    break

# Create GradCAM heatmaps
heatmap_dog = gradcam_plus_plus(model, dog_tensor, last_conv_layer_name=last_conv_layer_name,
                            class_index=None, smoothgrad=True, n_samples=15, noise_level=0.1)
heatmap_cat = gradcam_plus_plus(model, cat_tensor, last_conv_layer_name=last_conv_layer_name,
                            class_index=None, smoothgrad=True, n_samples=15, noise_level=0.1)

# Create heatmap list
heatmaps = [heatmap_dog, heatmap_cat]

# Visualize GradCAMs
visualize_grad_cams(image_titles, images, heatmaps, alpha)
```

