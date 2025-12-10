import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras import regularizers
from tensorflow.keras.losses import CategoricalCrossentropy
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import class_weight
import matplotlib.pyplot as plt
import numpy as np
import os

# Configuración
DATASET_DIR = 'dataset'
IMG_SIZE = (224, 224)
BATCH_SIZE = 16 
EPOCHS = 40 
MODEL_PATH = 'mango_model.h5'

def plot_history(history):
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    
    epochs_range = range(len(acc))

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label='Training Accuracy')
    plt.plot(epochs_range, val_acc, label='Validation Accuracy')
    plt.legend(loc='lower right')
    plt.title('Training and Validation Accuracy')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label='Training Loss')
    plt.plot(epochs_range, val_loss, label='Validation Loss')
    plt.legend(loc='upper right')
    plt.title('Training and Validation Loss')
    plt.grid(True)
    plt.savefig('training_results_efficientnet.png')
    print("Gráfica guardada como 'training_results_efficientnet.png'")

def train():
    print("Iniciando preparación de datos...")
    
    if not os.path.exists(DATASET_DIR):
        print(f"Error: No se encuentra la carpeta '{DATASET_DIR}'.")
        return

    # IMPORTANTE: EfficientNet espera inputs [0-255], NO rescalamos aquí
    train_datagen = ImageDataGenerator(
        # rescale=1./255,  <-- REMOVIDO para EfficientNet
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.7, 1.3],
        fill_mode='nearest',
        validation_split=0.2
    )

    print("Cargando imágenes de ENTRENAMIENTO (80%)...")
    train_generator = train_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )

    print("Cargando imágenes de PRUEBA/VALIDACIÓN (20%)...")
    validation_generator = train_datagen.flow_from_directory(
        DATASET_DIR,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )

    if train_generator.samples == 0:
        print("Error: No se encontraron imágenes.")
        return

    # Pesos de clase
    print("Calculando pesos de clase...")
    class_weights_list = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_generator.classes),
        y=train_generator.classes
    )
    class_weights = dict(enumerate(class_weights_list))
    print(f"Pesos de clase: {class_weights}")

    # --- MODELO EFFICIENTNET B0 ---
    print("\n=== Entrenando EfficientNetB0 (Transfer Learning) ===")
    
    # EfficientNetB0 incluye su propio preprocesamiento
    base_model = EfficientNetB0(weights='imagenet', include_top=False, input_shape=IMG_SIZE + (3,))
    base_model.trainable = False # Congelar base

    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x) 
    
    x = Dense(128, activation='relu', kernel_regularizer=regularizers.l2(0.02))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.4)(x)
    
    predictions = Dense(5, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    # Label Smoothing ayuda a la generalización
    model.compile(optimizer=Adam(learning_rate=0.001),
                  loss=CategoricalCrossentropy(label_smoothing=0.1),
                  metrics=['accuracy'])

    # Callbacks
    early_stopping = EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True, verbose=1)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=4, min_lr=1e-6, verbose=1)

    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // BATCH_SIZE,
        validation_data=validation_generator,
        validation_steps=validation_generator.samples // BATCH_SIZE,
        epochs=EPOCHS,
        class_weight=class_weights,
        callbacks=[early_stopping, reduce_lr]
    )

    # Guardar modelo final
    model.save(MODEL_PATH)
    print(f"Modelo optimizado guardado en {MODEL_PATH}")
    
    # Guardar etiquetas
    with open("class_indices.txt", "w") as f:
        f.write(str(train_generator.class_indices))

    # --- EVALUACIÓN FINAL ---
    print("\n--- Evaluando Modelo Final ---")
    validation_generator.reset()
    Y_pred = model.predict(validation_generator)
    y_pred = np.argmax(Y_pred, axis=1)
    
    print('Matriz de Confusión')
    print(confusion_matrix(validation_generator.classes, y_pred))
    
    print('Reporte de Clasificación')
    target_names = list(train_generator.class_indices.keys())
    print(classification_report(validation_generator.classes, y_pred, target_names=target_names))

    plot_history(history)

if __name__ == "__main__":
    train()
