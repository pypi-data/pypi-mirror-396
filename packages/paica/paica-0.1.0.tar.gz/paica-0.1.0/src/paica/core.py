import os
import sys
import cv2
import shutil
import numpy as np
import tensorflow as tf
from matplotlib import cm
import matplotlib.pyplot as plt
from PIL import Image, ImageEnhance
from tensorflow.keras.models import Model
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.vgg16 import preprocess_input, decode_predictions


#................Generate Maps.................#

# Create Image tensors
def create_image_tensors(img_path):
    img_orig = load_img(img_path, target_size=(224,224))
    img_array_orig = img_to_array(img_orig)
    img_tensor = preprocess_input(np.expand_dims(img_array_orig.copy(), 0))  # shape (1,224,224,3)
    return img_orig, img_tensor


# Guided Backprop ReLU modification
@tf.custom_gradient
def guided_relu(x):
    def grad(dy):
        return tf.cast(dy > 0, dy.dtype) * tf.cast(x > 0, dy.dtype) * dy
    return tf.nn.relu(x), grad


# Replace ReLU activations in the model with Guided ReLU
def make_guided_model(model):
    guided_model = tf.keras.models.clone_model(model)
    for layer in guided_model.layers:
        if hasattr(layer, 'activation') and layer.activation == tf.keras.activations.relu:
            layer.activation = guided_relu
    guided_model.set_weights(model.get_weights())
    return guided_model


# Compute SmoothGrad saliency map
def smoothgrad_saliency(model, img_tensor, class_index=None, n_samples=25, noise_level=0.1):
    """
    Args:
        model: Keras model
        img_tensor: preprocessed image batch, shape (1,H,W,3)
        class_index: index of class to explain. If None, takes predicted class
        n_samples: number of noisy samples for averaging
        noise_level: fraction of image range to add as Gaussian noise
    Returns:
        saliency_map: shape (H,W), normalized 0-1
    """
    guided_model = make_guided_model(model)

    if class_index is None:
        preds = model(img_tensor)
        class_index = tf.argmax(preds[0])

    saliency_accum = tf.zeros_like(img_tensor, dtype=tf.float32)

    for _ in range(n_samples):
        noise = tf.random.normal(img_tensor.shape) * noise_level
        img_noisy = img_tensor + noise

        with tf.GradientTape() as tape:
            tape.watch(img_noisy)
            logits = guided_model(img_noisy)
            loss = logits[:, class_index]

        grads = tape.gradient(loss, img_noisy)
        saliency_accum += grads

    saliency = tf.reduce_mean(tf.abs(saliency_accum / n_samples), axis=-1)[0]  # shape (H,W)

    # Normalize to 0-1
    saliency = (saliency - tf.reduce_min(saliency)) / (tf.reduce_max(saliency) - tf.reduce_min(saliency) + 1e-8)

    return saliency


# Compute Grad-CAM++
def gradcam_plus_plus(model, img_tensor, last_conv_layer_name,
                      class_index=None, smoothgrad=False, n_samples=10, noise_level=0.1):
    """
    Grad-CAM++ with SmoothGrad, fixed resizing for multi-size layers.
    """
    def compute_gradcam(inp):
        conv_layer = model.get_layer(last_conv_layer_name)
        base_model = tf.keras.Model(model.inputs, [conv_layer.output, model.output])

        with tf.GradientTape() as tape:
            conv_outputs, predictions = base_model(inp)
            conv_outputs = tf.cast(conv_outputs, tf.float32)
            tape.watch(conv_outputs)

            if class_index is None:
                class_idx = int(tf.argmax(predictions[0]).numpy())
            else:
                class_idx = class_index

            loss = tf.reduce_sum(predictions[:, class_idx])

        grads = tape.gradient(loss, conv_outputs)
        weights = tf.reduce_mean(grads, axis=(1,2), keepdims=True)
        cam = tf.reduce_sum(weights * conv_outputs, axis=-1)
        cam = tf.nn.relu(cam)
        cam = cam / (tf.reduce_max(cam) + 1e-8)
        # Resize to input image size before returning
        cam_resized = cv2.resize(cam[0].numpy(), (img_tensor.shape[2], img_tensor.shape[1]))
        return cam_resized

    if smoothgrad:
        heatmap_accum = np.zeros((img_tensor.shape[1], img_tensor.shape[2]), dtype=np.float32)
        for _ in range(n_samples):
            noise = noise_level * tf.random.normal(img_tensor.shape)
            heatmap_accum += compute_gradcam(img_tensor + noise)
        heatmap = heatmap_accum / n_samples
    else:
        heatmap = compute_gradcam(img_tensor)

    return np.clip(heatmap, 0, 1)


#................Visualizations.................#

def visualize_raw_images(image_titles, images):
  f, ax = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
  for i, title in enumerate(image_titles):
    ax[i].set_title(title, fontsize=16)
    ax[i].imshow(images[i])
    ax[i].axis('off')
  plt.tight_layout()
  plt.show()

def visualize_saliency_maps(image_titles, images, saliency_map, alpha):
  f, ax = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
  for i, title in enumerate(image_titles):
    ax[i].set_title(title, fontsize=14)
    ax[i].imshow(images[i])
    ax[i].imshow(saliency_map[i], cmap='jet', alpha=alpha)
    ax[i].axis('off')
  plt.tight_layout()
  plt.savefig(f'saliency_map_alpha_{alpha}.png')
  plt.show()

def visualize_grad_cams(image_titles, images, heatmaps, alpha):
  f, ax = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
  for i, title in enumerate(image_titles):
    ax[i].set_title(title, fontsize=14)
    ax[i].imshow(images[i])
    ax[i].imshow(heatmaps[i], cmap='jet', alpha=alpha)
    ax[i].axis('off')
  plt.tight_layout()
  plt.savefig(f'gramcam_alpha_{alpha}.png')
  plt.show()