import numpy as np
import logging

logger = logging.getLogger("ParadoxViz")

class LatentVisualizer:
    def __init__(self, engine):
        self.engine = engine

    def reduce_dimensions(self, method="pca", n_components=2):
        """
        Reduce latent vectors to 2D/3D for visualization.
        Requires scikit-learn.
        """
        vectors = self.engine.vectors
        
        # Handle Torch tensors
        if hasattr(vectors, 'cpu'):
            vectors = vectors.cpu().detach().numpy()
            
        if len(vectors) < n_components:
            logger.warning("Not enough data to perform reduction.")
            return vectors

        try:
            from sklearn.decomposition import PCA
            from sklearn.manifold import TSNE
        except ImportError:
            logger.error("scikit-learn is required for visualization. pip install scikit-learn")
            return None

        if method == "pca":
            reducer = PCA(n_components=n_components)
        elif method == "tsne":
            reducer = TSNE(n_components=n_components)
        else:
            raise ValueError("Unknown method. Use 'pca' or 'tsne'.")

        return reducer.fit_transform(vectors)

    def plot_2d(self, method="pca", labels=None, output_file=None):
        """
        Generate a 2D scatter plot of the memory.
        Requires matplotlib.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logger.error("matplotlib is required for plotting. pip install matplotlib")
            return

        points = self.reduce_dimensions(method=method, n_components=2)
        if points is None:
            return

        plt.figure(figsize=(10, 8))
        plt.scatter(points[:, 0], points[:, 1], alpha=0.7, c='cyan', edgecolors='k')
        
        # Add labels if provided (list of strings matching indices)
        if labels:
            for i, txt in enumerate(labels):
                if i < len(points):
                    plt.annotate(txt, (points[i, 0], points[i, 1]), fontsize=8)

        plt.title(f"Paradox Latent Space ({method.upper()})")
        plt.xlabel("Dim 1")
        plt.ylabel("Dim 2")
        plt.grid(True, linestyle='--', alpha=0.3)
        plt.style.use('dark_background')
        
        if output_file:
            plt.savefig(output_file)
            logger.info(f"Plot saved to {output_file}")
        else:
            plt.show()
