"""
Stunning Visualization for Aizawa Attractor.

Creates beautiful dark-themed 3D visualizations and animations
with professional aesthetics and comprehensive metrics display.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import warnings
import io

from PIL import Image, ImageFilter, ImageEnhance
from tqdm import tqdm

warnings.filterwarnings('ignore')


class Animator:
    """
    Create stunning visualizations for Aizawa attractor.
    
    Features professional dark-themed aesthetics with neon accents,
    smooth camera motion, and glow effects.
    """
    
    # Cyberpunk/Neon dark theme color palette
    COLOR_BG = '#0A0E14'
    COLOR_BG_LIGHTER = '#11151C'
    COLOR_BG_PANEL = '#151A23'
    COLOR_ACCENT_CYAN = '#00F5D4'
    COLOR_ACCENT_MAGENTA = '#FF6B9D'
    COLOR_ACCENT_YELLOW = '#FFE66D'
    COLOR_ACCENT_BLUE = '#00D9FF'
    COLOR_ACCENT_ORANGE = '#FF9F1C'
    COLOR_GRID = '#1E2633'
    COLOR_TEXT = '#E6EDF3'
    COLOR_TITLE = '#FFFFFF'
    
    # Colormaps for trajectories
    TRAJECTORY_CMAPS = ['plasma', 'viridis', 'cividis', 'inferno']
    
    def __init__(self, fps: int = 30, dpi: int = 150):
        """
        Initialize animator.
        
        Args:
            fps: Frames per second for animations
            dpi: Resolution for output images
        """
        self.fps = fps
        self.dpi = dpi
        self._setup_style()
    
    def _setup_style(self):
        """Setup matplotlib dark theme styling."""
        plt.style.use('dark_background')
        plt.rcParams.update({
            'figure.facecolor': self.COLOR_BG,
            'axes.facecolor': self.COLOR_BG_LIGHTER,
            'axes.edgecolor': self.COLOR_GRID,
            'axes.labelcolor': self.COLOR_TEXT,
            'axes.titlecolor': self.COLOR_TITLE,
            'xtick.color': self.COLOR_TEXT,
            'ytick.color': self.COLOR_TEXT,
            'text.color': self.COLOR_TEXT,
            'grid.color': self.COLOR_GRID,
            'grid.alpha': 0.4,
            'legend.facecolor': self.COLOR_BG_PANEL,
            'legend.edgecolor': self.COLOR_GRID,
            'font.family': 'sans-serif',
            'font.size': 11,
            'axes.labelsize': 13,
            'axes.titlesize': 15,
            'mathtext.fontset': 'cm',
            'lines.antialiased': True,
        })
    
    def _add_glow_effect(
        self,
        image: Image.Image,
        intensity: float = 1.5
    ) -> Image.Image:
        """Add subtle glow effect to image."""
        glow = image.filter(ImageFilter.GaussianBlur(radius=3))
        enhancer = ImageEnhance.Brightness(glow)
        glow = enhancer.enhance(0.5)
        return Image.blend(image, glow, alpha=0.15)
    
    def _create_custom_cmap(self, color: str) -> LinearSegmentedColormap:
        """Create a custom colormap from dark to specified color."""
        return LinearSegmentedColormap.from_list(
            'custom', ['#000000', color, '#FFFFFF'], N=256
        )
    
    def create_static_plot(
        self,
        result: Dict[str, Any],
        filepath: str,
        title: str = "Aizawa Attractor",
        metrics: Optional[Dict[str, Any]] = None,
        multi_trajectory: bool = False
    ):
        """
        Create comprehensive static visualization.
        
        Args:
            result: Simulation result dictionary
            filepath: Output file path
            title: Plot title
            metrics: Optional chaos metrics
            multi_trajectory: Whether result contains multiple trajectories
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Create figure with subplots
        fig = plt.figure(figsize=(20, 12), facecolor=self.COLOR_BG)
        
        fig.suptitle(
            f'{title}\nStrange Attractor Dynamics',
            fontsize=22, fontweight='bold', color=self.COLOR_TITLE, y=0.98
        )
        
        # Layout: 2 rows, 3 columns
        # Row 1: 3D view, XY projection, XZ projection
        # Row 2: YZ projection, Time series, Metrics panel
        
        ax1 = fig.add_subplot(231, projection='3d', facecolor=self.COLOR_BG)
        ax2 = fig.add_subplot(232, facecolor=self.COLOR_BG_LIGHTER)
        ax3 = fig.add_subplot(233, facecolor=self.COLOR_BG_LIGHTER)
        ax4 = fig.add_subplot(234, facecolor=self.COLOR_BG_LIGHTER)
        ax5 = fig.add_subplot(235, facecolor=self.COLOR_BG_LIGHTER)
        ax6 = fig.add_subplot(236, facecolor=self.COLOR_BG_LIGHTER)
        
        # Get trajectory data
        if multi_trajectory:
            trajectories = result['trajectories']
            n_traj = len(trajectories)
        else:
            trajectories = [result['trajectory']]
            n_traj = 1
        
        time_array = result['time']
        
        # Plot 1: 3D Attractor
        for i, traj in enumerate(trajectories):
            x, y, z = traj[:, 0], traj[:, 1], traj[:, 2]
            cmap = plt.cm.get_cmap(self.TRAJECTORY_CMAPS[i % len(self.TRAJECTORY_CMAPS)])
            colors = cmap(np.linspace(0.2, 0.9, len(x)))
            ax1.scatter(x, y, z, c=colors, s=0.1, alpha=0.6)
        
        ax1.set_xlabel('X', fontsize=12, fontweight='bold', labelpad=8)
        ax1.set_ylabel('Y', fontsize=12, fontweight='bold', labelpad=8)
        ax1.set_zlabel('Z', fontsize=12, fontweight='bold', labelpad=8)
        ax1.set_title('3D Phase Space', fontsize=14, fontweight='bold', pad=10)
        
        # Style 3D axes
        ax1.xaxis.pane.fill = True
        ax1.yaxis.pane.fill = True
        ax1.zaxis.pane.fill = True
        ax1.xaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
        ax1.yaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
        ax1.zaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
        ax1.tick_params(colors=self.COLOR_TEXT, labelsize=9)
        ax1.view_init(elev=25, azim=45)
        
        # Plot 2: XY Projection
        for i, traj in enumerate(trajectories):
            x, y = traj[:, 0], traj[:, 1]
            cmap = plt.cm.get_cmap(self.TRAJECTORY_CMAPS[i % len(self.TRAJECTORY_CMAPS)])
            colors = cmap(np.linspace(0.2, 0.9, len(x)))
            ax2.scatter(x, y, c=colors, s=0.1, alpha=0.5)
        
        ax2.set_xlabel('X', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Y', fontsize=12, fontweight='bold')
        ax2.set_title('XY Projection', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        self._style_2d_axes(ax2)
        
        # Plot 3: XZ Projection
        for i, traj in enumerate(trajectories):
            x, z = traj[:, 0], traj[:, 2]
            cmap = plt.cm.get_cmap(self.TRAJECTORY_CMAPS[i % len(self.TRAJECTORY_CMAPS)])
            colors = cmap(np.linspace(0.2, 0.9, len(x)))
            ax3.scatter(x, z, c=colors, s=0.1, alpha=0.5)
        
        ax3.set_xlabel('X', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Z', fontsize=12, fontweight='bold')
        ax3.set_title('XZ Projection', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        self._style_2d_axes(ax3)
        
        # Plot 4: YZ Projection
        for i, traj in enumerate(trajectories):
            y, z = traj[:, 1], traj[:, 2]
            cmap = plt.cm.get_cmap(self.TRAJECTORY_CMAPS[i % len(self.TRAJECTORY_CMAPS)])
            colors = cmap(np.linspace(0.2, 0.9, len(y)))
            ax4.scatter(y, z, c=colors, s=0.1, alpha=0.5)
        
        ax4.set_xlabel('Y', fontsize=12, fontweight='bold')
        ax4.set_ylabel('Z', fontsize=12, fontweight='bold')
        ax4.set_title('YZ Projection', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        self._style_2d_axes(ax4)
        
        # Plot 5: Time Series
        traj = trajectories[0]
        n_show = min(10000, len(time_array))
        ax5.plot(time_array[:n_show], traj[:n_show, 0], 
                color=self.COLOR_ACCENT_CYAN, lw=0.5, alpha=0.8, label='x')
        ax5.plot(time_array[:n_show], traj[:n_show, 1], 
                color=self.COLOR_ACCENT_MAGENTA, lw=0.5, alpha=0.8, label='y')
        ax5.plot(time_array[:n_show], traj[:n_show, 2], 
                color=self.COLOR_ACCENT_YELLOW, lw=0.5, alpha=0.8, label='z')
        
        ax5.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax5.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax5.set_title('Time Series', fontsize=14, fontweight='bold')
        ax5.legend(loc='upper right', fontsize=10)
        ax5.grid(True, alpha=0.3)
        self._style_2d_axes(ax5)
        
        # Plot 6: Metrics Panel or Parameters
        ax6.axis('off')
        
        # Get system info
        system = result.get('system')
        
        # Build info text
        info_lines = []
        info_lines.append("SYSTEM PARAMETERS")
        info_lines.append("─" * 30)
        
        if system is not None:
            info_lines.append(f"a = {system.a:.4f}")
            info_lines.append(f"b = {system.b:.4f}")
            info_lines.append(f"c = {system.c:.4f}")
            info_lines.append(f"d = {system.d:.4f}")
            info_lines.append(f"e = {system.e:.4f}")
            info_lines.append(f"f = {system.f:.4f}")
        
        info_lines.append("")
        info_lines.append("INTEGRATION")
        info_lines.append("─" * 30)
        info_lines.append(f"dt = {result.get('dt', 0.01)}")
        info_lines.append(f"Points = {len(trajectories[0]):,}")
        
        if metrics is not None:
            info_lines.append("")
            info_lines.append("CHAOS METRICS")
            info_lines.append("─" * 30)
            
            if 'lyapunov_1' in metrics:
                info_lines.append(f"λ₁ = {metrics['lyapunov_1']:.4f}")
                info_lines.append(f"λ₂ = {metrics['lyapunov_2']:.4f}")
                info_lines.append(f"λ₃ = {metrics['lyapunov_3']:.4f}")
            
            if 'kaplan_yorke_dim' in metrics:
                info_lines.append(f"D_KY = {metrics['kaplan_yorke_dim']:.4f}")
            
            if 'correlation_dim' in metrics:
                info_lines.append(f"D₂ = {metrics['correlation_dim']:.4f}")
            
            if 'ks_entropy' in metrics:
                info_lines.append(f"h_KS = {metrics['ks_entropy']:.4f}")
            
            if 'is_chaotic' in metrics:
                status = "CHAOTIC" if metrics['is_chaotic'] else "NON-CHAOTIC"
                info_lines.append(f"Status: {status}")
        
        info_text = "\n".join(info_lines)
        
        ax6.text(
            0.1, 0.95, info_text,
            transform=ax6.transAxes,
            fontsize=11,
            fontweight='normal',
            color=self.COLOR_TEXT,
            family='monospace',
            verticalalignment='top',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor=self.COLOR_BG_PANEL,
                edgecolor=self.COLOR_GRID,
                alpha=0.9
            )
        )
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        
        # Save
        plt.savefig(
            filepath, dpi=self.dpi,
            facecolor=self.COLOR_BG, edgecolor='none',
            bbox_inches='tight'
        )
        plt.close(fig)
    
    def _style_2d_axes(self, ax):
        """Apply consistent styling to 2D axes."""
        for spine in ax.spines.values():
            spine.set_color(self.COLOR_GRID)
    
    def create_animation(
        self,
        result: Dict[str, Any],
        filepath: str,
        title: str = "Aizawa Attractor",
        n_frames: int = 180,
        duration_seconds: float = 15.0,
        multi_trajectory: bool = False
    ):
        """
        Create stunning animated 3D visualization.
        
        Args:
            result: Simulation result dictionary
            filepath: Output file path
            title: Animation title
            n_frames: Number of frames
            duration_seconds: Target duration
            multi_trajectory: Whether result contains multiple trajectories
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Get trajectory data
        if multi_trajectory:
            trajectories = result['trajectories']
        else:
            trajectories = [result['trajectory']]
        
        system = result.get('system')
        
        # Parameter info
        if system is not None:
            param_text = (
                f"a={system.a:.2f}  b={system.b:.2f}  c={system.c:.2f}\n"
                f"d={system.d:.2f}  e={system.e:.2f}  f={system.f:.2f}"
            )
        else:
            param_text = ""
        
        print(f"      Generating {n_frames} frames...")
        
        anim_dpi = 100
        frames = []
        
        # Camera motion: smooth 360° rotation
        t_norm = np.linspace(0, 1, n_frames)
        azims = 360 * t_norm
        elevs = 20 + 15 * np.sin(2 * np.pi * t_norm)
        
        for frame_idx in tqdm(range(n_frames), desc="      Rendering", ncols=70):
            fig = plt.figure(figsize=(12, 10), facecolor=self.COLOR_BG, dpi=anim_dpi)
            ax = fig.add_subplot(111, projection='3d', facecolor=self.COLOR_BG)
            
            # Plot trajectories
            for i, traj in enumerate(trajectories):
                x, y, z = traj[:, 0], traj[:, 1], traj[:, 2]
                cmap = plt.cm.get_cmap(self.TRAJECTORY_CMAPS[i % len(self.TRAJECTORY_CMAPS)])
                colors = cmap(np.linspace(0.2, 0.9, len(x)))
                ax.scatter(x, y, z, c=colors, s=0.08, alpha=0.5)
            
            # Camera position
            ax.view_init(elev=elevs[frame_idx], azim=azims[frame_idx])
            
            # Labels
            ax.set_xlabel('X', fontsize=12, fontweight='bold', color=self.COLOR_TEXT)
            ax.set_ylabel('Y', fontsize=12, fontweight='bold', color=self.COLOR_TEXT)
            ax.set_zlabel('Z', fontsize=12, fontweight='bold', color=self.COLOR_TEXT)
            
            # Title
            ax.set_title(title, fontsize=18, fontweight='bold', 
                        color=self.COLOR_TITLE, pad=20)
            
            # Style panes
            ax.xaxis.pane.fill = True
            ax.yaxis.pane.fill = True
            ax.zaxis.pane.fill = True
            ax.xaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
            ax.yaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
            ax.zaxis.pane.set_facecolor(self.COLOR_BG_PANEL)
            ax.xaxis.pane.set_edgecolor(self.COLOR_GRID)
            ax.yaxis.pane.set_edgecolor(self.COLOR_GRID)
            ax.zaxis.pane.set_edgecolor(self.COLOR_GRID)
            ax.tick_params(colors=self.COLOR_TEXT, labelsize=9)
            
            # Hide tick labels for cleaner look
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.set_zticklabels([])
            
            # Parameter box
            if param_text:
                ax.text2D(
                    0.02, 0.98, param_text,
                    transform=ax.transAxes,
                    fontsize=10, fontweight='bold',
                    color=self.COLOR_TEXT,
                    family='monospace',
                    verticalalignment='top',
                    bbox=dict(
                        boxstyle='round,pad=0.4',
                        facecolor=self.COLOR_BG_PANEL,
                        edgecolor=self.COLOR_GRID,
                        alpha=0.9
                    )
                )
            
            # Equations
            eq_text = (
                r"$\dot{x}=(z-b)x-dy$" + "\n" +
                r"$\dot{y}=dx+(z-b)y$" + "\n" +
                r"$\dot{z}=c+az-\frac{z^3}{3}-(x^2+y^2)(1+ez)+fzx^3$"
            )
            ax.text2D(
                0.98, 0.02, eq_text,
                transform=ax.transAxes,
                fontsize=9,
                color='#888888',
                family='serif',
                horizontalalignment='right',
                verticalalignment='bottom',
                alpha=0.8
            )
            
            fig.tight_layout()
            
            # Render to buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=anim_dpi,
                       facecolor=self.COLOR_BG, edgecolor='none')
            buf.seek(0)
            frame_img = Image.open(buf).copy()
            
            # Add glow effect
            frame_img = self._add_glow_effect(frame_img)
            
            frames.append(frame_img)
            buf.close()
            plt.close(fig)
        
        # Save GIF
        frame_duration_ms = int(duration_seconds * 1000 / n_frames)
        
        print(f"      Saving GIF ({n_frames} frames)...")
        
        frames[0].save(
            str(filepath),
            save_all=True,
            append_images=frames[1:],
            duration=frame_duration_ms,
            loop=0,
            optimize=True
        )
        
        print(f"      ✓ Saved to {filepath.name}")
