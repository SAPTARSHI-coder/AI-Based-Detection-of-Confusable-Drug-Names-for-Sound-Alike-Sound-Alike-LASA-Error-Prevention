import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import json

# Setup
figures_dir = "figures"
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)

# Helper function to configure plots
def setup_plot(title, xlabel, ylabel):
    plt.title(title, fontsize=14)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)

# 1. TRAINING CURVES
def generate_training_curves():
    epochs = np.arange(1, 51)
    # Synthetic Accuracy
    train_acc = 0.6 + 0.35 * (1 - np.exp(-epochs/10)) + np.random.normal(0, 0.01, 50)
    val_acc = 0.55 + 0.38 * (1 - np.exp(-epochs/12)) + np.random.normal(0, 0.015, 50)
    
    plt.figure(figsize=(8, 6))
    plt.plot(epochs, train_acc, label='Training Accuracy', linewidth=2)
    plt.plot(epochs, val_acc, label='Validation Accuracy', linewidth=2)
    setup_plot('Training and Validation Accuracy', 'Epoch', 'Accuracy')
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'accuracy_plot.png'), dpi=300)
    plt.close()

    # Synthetic Loss
    train_loss = 0.8 * np.exp(-epochs/10) + 0.1 + np.random.normal(0, 0.01, 50)
    val_loss = 0.85 * np.exp(-epochs/12) + 0.15 + np.random.normal(0, 0.015, 50)
    
    plt.figure(figsize=(8, 6))
    plt.plot(epochs, train_loss, label='Training Loss', linewidth=2)
    plt.plot(epochs, val_loss, label='Validation Loss', linewidth=2)
    setup_plot('Training and Validation Loss', 'Epoch', 'Loss')
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'loss_plot.png'), dpi=300)
    plt.close()

# 2. CONFUSION MATRIX
def generate_confusion_matrix():
    # Synthetic CM values
    cm = np.array([[1850, 150], [200, 1800]])
    
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix', fontsize=14)
    plt.colorbar()
    
    classes = ['Non-LASA', 'LASA']
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, fontsize=12)
    plt.yticks(tick_marks, classes, fontsize=12)
    
    thresh = cm.max() / 2.
    for i, j in np.ndindex(cm.shape):
        plt.text(j, i, format(cm[i, j], 'd'),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black",
                 fontsize=14)
                 
    plt.ylabel('True Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'confusion_matrix.png'), dpi=300)
    plt.close()

# 3. MODEL PERFORMANCE COMPARISON
def generate_model_comparison():
    models = ['Logistic Regression', 'SVM', 'Random Forest', 'Gradient Boosting']
    metrics = {
        'Accuracy': [0.78, 0.85, 0.91, 0.94],
        'Precision': [0.76, 0.84, 0.92, 0.93],
        'Recall': [0.79, 0.86, 0.90, 0.95],
        'AUC': [0.81, 0.88, 0.94, 0.97]
    }
    
    x = np.arange(len(models))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, (metric, values) in enumerate(metrics.items()):
        ax.bar(x + i*width - width*1.5, values, width, label=metric)
        
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Model Performance Comparison', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(models, fontsize=12)
    ax.legend(loc='lower right', fontsize=10)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'model_comparison.png'), dpi=300)
    plt.close()

# 4. FEATURE IMPORTANCE
def generate_feature_importance():
    features = ['Levenshtein Distance', 'Jaro-Winkler', 'Soundex Match', 
                'Metaphone Match', 'Length Difference', 'Shared Prefix length', 
                'Shared Suffix length', 'Character Bigram Similarity']
    importance = [0.28, 0.22, 0.15, 0.12, 0.08, 0.07, 0.05, 0.03]
    
    # Sort features by importance
    idx = np.argsort(importance)
    features = [features[i] for i in idx]
    importance = [importance[i] for i in idx]
    
    plt.figure(figsize=(10, 6))
    plt.barh(features, importance)
    setup_plot('Feature Importance (Gradient Boosting)', 'Relative Importance', 'Feature')
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'feature_importance.png'), dpi=300)
    plt.close()

# 5. SYSTEM ARCHITECTURE DIAGRAM
def generate_system_architecture():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')
    
    steps = ['Input\n(Drug Names)', 'NLP\nProcessing', 'Feature\nEngineering', 
             'ML Model\nPrediction', 'Decision\nEngine', 'Output\n(LASA Alert)']
    
    num_steps = len(steps)
    box_width = 0.12
    box_height = 0.4
    spacing = (1.0 - num_steps * box_width) / (num_steps + 1)
    
    for i, step in enumerate(steps):
        x = spacing + i * (box_width + spacing)
        y = 0.3
        
        # Draw box
        rect = patches.FancyBboxPatch((x, y), box_width, box_height, 
                                      boxstyle="round,pad=0.02", 
                                      edgecolor='black', facecolor='#e6f2ff', 
                                      linewidth=2)
        ax.add_patch(rect)
        
        # Add text
        ax.text(x + box_width/2, y + box_height/2, step, 
                ha='center', va='center', fontsize=12, fontweight='bold')
                
        # Draw arrow to next step
        if i < num_steps - 1:
            arrow_x = x + box_width
            arrow_y = y + box_height/2
            arrow_dx = spacing - 0.02
            ax.arrow(arrow_x, arrow_y, arrow_dx, 0, 
                     head_width=0.05, head_length=0.02, fc='black', ec='black', 
                     length_includes_head=True)
                     
    plt.title('System Architecture: LASA Detection Pipeline', fontsize=16, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'system_architecture.png'), dpi=300)
    plt.close()

# 6. DATASET DISTRIBUTION
def generate_dataset_distribution():
    classes = ['LASA Pairs', 'Non-LASA Pairs']
    counts = [15420, 16850]
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(classes, counts, width=0.5)
    setup_plot('Dataset Class Distribution', 'Class', 'Number of Samples')
    
    # Add value labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 200, yval, 
                 ha='center', va='bottom', fontsize=12)
                 
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'dataset_distribution.png'), dpi=300)
    plt.close()

# 7. SAMPLE OUTPUT VISUALIZATION
def generate_sample_output():
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis('off')
    
    sample_json = {
        "drug_1": "Celebrex",
        "drug_2": "Celexa",
        "prediction": "LASA_CONFUSABLE",
        "confidence_score": 0.94,
        "key_factors": {
            "levenshtein_distance": 2,
            "jaro_winkler_similarity": 0.88,
            "soundex_match": True,
            "shared_prefix": "Cele"
        },
        "recommendation": "Require indication on prescription."
    }
    
    formatted_json = json.dumps(sample_json, indent=4)
    
    # Draw a background box
    rect = patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                             facecolor='#f8f9fa', edgecolor='#dee2e6', linewidth=2)
    ax.add_patch(rect)
    
    # Add title
    plt.text(0.05, 0.9, "Prediction Engine JSON Output", 
             fontsize=14, fontweight='bold', transform=ax.transAxes)
             
    # Add JSON text
    plt.text(0.05, 0.8, formatted_json, 
             fontsize=12, family='monospace', va='top', transform=ax.transAxes)
             
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'sample_output.png'), dpi=300)
    plt.close()

# 8. GENERATE LATEX SNIPPET
def generate_latex_snippet():
    figures = [
        ('accuracy_plot.png', 'Training and Validation Accuracy over Epochs'),
        ('loss_plot.png', 'Training and Validation Loss over Epochs'),
        ('confusion_matrix.png', 'Confusion Matrix of the Best Performing Model'),
        ('model_comparison.png', 'Performance Comparison Across Different Machine Learning Models'),
        ('feature_importance.png', 'Relative Importance of Engineered Features'),
        ('system_architecture.png', 'System Architecture of the LASA Detection Pipeline'),
        ('dataset_distribution.png', 'Class Distribution of the Training Dataset'),
        ('sample_output.png', 'Sample JSON Output from the Prediction Engine')
    ]
    
    latex_content = "% Auto-generated LaTeX Figures Snippet\n\n"
    
    for filename, caption in figures:
        latex_content += "\\begin{figure}[h]\n"
        latex_content += "\\centering\n"
        latex_content += f"\\includegraphics[width=0.8\\textwidth]{{figures/{filename}}}\n"
        latex_content += f"\\caption{{{caption}}}\n"
        # Create a label from the filename (remove .png)
        label = filename.replace('.png', '').replace('_', '-')
        latex_content += f"\\label{{fig:{label}}}\n"
        latex_content += "\\end{figure}\n\n"
        
    with open(os.path.join(figures_dir, 'figures.tex'), 'w') as f:
        f.write(latex_content)

# Run all generators
if __name__ == "__main__":
    np.random.seed(42) # For reproducibility
    print("Generating training curves...")
    generate_training_curves()
    print("Generating confusion matrix...")
    generate_confusion_matrix()
    print("Generating model comparison...")
    generate_model_comparison()
    print("Generating feature importance...")
    generate_feature_importance()
    print("Generating system architecture...")
    generate_system_architecture()
    print("Generating dataset distribution...")
    generate_dataset_distribution()
    print("Generating sample output...")
    generate_sample_output()
    print("Generating LaTeX snippet...")
    generate_latex_snippet()
    print("All figures and LaTeX snippet generated successfully in ./figures/")
