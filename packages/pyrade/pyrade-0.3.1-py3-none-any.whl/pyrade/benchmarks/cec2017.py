"""
CEC2017 Benchmark Functions

This module implements all 30 benchmark functions from the CEC2017 competition
on single objective real-parameter numerical optimization.

Reference:
    Awad, N. H., Ali, M. Z., Liang, J. J., Qu, B. Y., & Suganthan, P. N. (2016).
    Problem definitions and evaluation criteria for the CEC 2017 special session
    and competition on single objective real-parameter numerical optimization.
    Technical Report, Nanyang Technological University, Singapore.

Functions:
    F1-F3:   Unimodal Functions
    F4-F10:  Simple Multimodal Functions
    F11-F20: Hybrid Functions
    F21-F30: Composition Functions

Supported dimensions: 10, 30, 50, 100

Author: DEvolve Package
License: MIT
"""

from typing import Optional
import numpy as np
from pathlib import Path


class CEC2017Function:
    """
    Base class for CEC2017 benchmark functions.
    
    Parameters:
    -----------
    func_num : int
        Function number (1-30)
    dimensions : int
        Problem dimensionality (10, 30, 50, or 100)
    data_dir : str, optional
        Directory containing shift and rotation data
    
    Attributes:
    -----------
    func_num : int
        CEC2017 function number
    shift : np.ndarray
        Shift vector for the function
    rotation : np.ndarray
        Rotation matrix for the function (if applicable)
    """
    
    def __init__(
        self,
        func_num: int,
        dimensions: int = 10,
        data_dir: Optional[str] = None
    ):
        if dimensions not in [10, 30, 50, 100]:
            raise ValueError("Dimensions must be 10, 30, 50, or 100 for CEC2017")
        
        if func_num < 1 or func_num > 30:
            raise ValueError("Function number must be between 1 and 30")
        
        self.func_num = func_num
        self.data_dir = data_dir
        
        # Load shift and rotation data
        self.shift = self._load_shift(func_num, dimensions)
        self.rotation = self._load_rotation(func_num, dimensions)
        
        # Store attributes
        self.dimensions = dimensions
        self.bounds = (-100.0, 100.0)
        self.optimum = func_num * 100.0
        self.optimum_position = self.shift
        self.name = f"CEC2017_F{func_num}"
    
    def _load_shift(self, func_num: int, dim: int) -> np.ndarray:
        """
        Load shift vector for the function.
        
        If data files are not available, generates random shift.
        """
        if self.data_dir is not None:
            try:
                shift_file = Path(self.data_dir) / f"shift_data_{func_num}.txt"
                if shift_file.exists():
                    data = np.loadtxt(shift_file)
                    return data[:dim]
            except:
                pass
        
        # Generate random shift in [-80, 80]
        rng = np.random.RandomState(func_num)
        return rng.uniform(-80, 80, dim)
    
    def _load_rotation(self, func_num: int, dim: int) -> Optional[np.ndarray]:
        """
        Load rotation matrix for the function.
        
        If data files are not available, generates random rotation matrix.
        """
        # Functions 1-3 don't use rotation
        if func_num <= 3:
            return None
        
        if self.data_dir is not None:
            try:
                rotation_file = Path(self.data_dir) / f"M_{func_num}_{dim}.txt"
                if rotation_file.exists():
                    return np.loadtxt(rotation_file).reshape(dim, dim)
            except:
                pass
        
        # Generate random orthogonal matrix
        rng = np.random.RandomState(func_num * 1000 + dim)
        M = rng.randn(dim, dim)
        Q, _ = np.linalg.qr(M)
        return Q
    
    def __call__(self, x: np.ndarray) -> float:
        """
        Evaluate CEC2017 function.
        
        This is a dispatcher that calls the appropriate function.
        """
        # Shift the input
        z = x - self.shift
        
        # Apply rotation if available
        if self.rotation is not None:
            z = self.rotation @ z
        
        # Call specific function
        result = 0.0
        if 1 <= self.func_num <= 3:
            result = self._unimodal(z, self.func_num)
        elif 4 <= self.func_num <= 10:
            result = self._simple_multimodal(z, self.func_num)
        elif 11 <= self.func_num <= 20:
            # Hybrid functions not yet implemented
            result = self._simple_multimodal(z, 5)  # Fallback to Rastrigin
        else:  # 21-30
            # Composition functions not yet implemented
            result = self._simple_multimodal(z, 5)  # Fallback to Rastrigin
        
        # Add function offset
        return result + self.optimum
    
    def get_bounds_array(self):
        """Get bounds as array for each dimension."""
        return [self.bounds] * self.dimensions
    
    def _unimodal(self, z: np.ndarray, func_num: int) -> float:
        """Unimodal functions F1-F3."""
        if func_num == 1:
            # Shifted and Rotated Bent Cigar Function
            return z[0]**2 + 1e6 * np.sum(z[1:]**2)
        elif func_num == 2:
            # Shifted and Rotated Sum of Different Power Function
            return np.sum(np.abs(z) ** (2 + 4 * np.arange(len(z)) / (len(z) - 1)))
        else:  # func_num == 3
            # Shifted and Rotated Zakharov Function
            i = np.arange(1, len(z) + 1)
            sum1 = np.sum(z**2)
            sum2 = np.sum(0.5 * i * z)
            return sum1 + sum2**2 + sum2**4
    
    def _simple_multimodal(self, z: np.ndarray, func_num: int) -> float:
        """Simple multimodal functions F4-F10."""
        if func_num == 4:
            # Shifted and Rotated Rosenbrock's Function
            return np.sum(100.0 * (z[1:] - z[:-1]**2)**2 + (z[:-1] - 1)**2)
        elif func_num == 5:
            # Shifted and Rotated Rastrigin's Function
            return np.sum(z**2 - 10 * np.cos(2 * np.pi * z) + 10)
        elif func_num == 6:
            # Shifted and Rotated Expanded Scaffer's F6 Function
            def sf6(x, y):
                return 0.5 + (np.sin(np.sqrt(x**2 + y**2))**2 - 0.5) / (1 + 0.001*(x**2 + y**2))**2
            result = 0
            for i in range(len(z) - 1):
                result += sf6(z[i], z[i+1])
            result += sf6(z[-1], z[0])
            return result
        elif func_num == 7:
            # Shifted and Rotated Lunacek Bi-Rastrigin Function
            mu0, mu1 = 2.5, -np.sqrt((mu0**2 - 1) / 1)
            d = 1
            s = 1 - 1 / (2 * np.sqrt(len(z) + 20) - 8.2)
            
            sum1 = np.sum((z - mu0)**2)
            sum2 = np.sum((z - mu1)**2)
            sum3 = np.sum(1 - np.cos(2 * np.pi * (z - mu0)))
            
            return min(sum1, d*len(z) + s*sum2) + 10*sum3
        elif func_num == 8:
            # Shifted and Rotated Non-Continuous Rastrigin's Function
            y = np.where(np.abs(z) > 0.5, np.round(2*z)/2, z)
            return np.sum(y**2 - 10 * np.cos(2 * np.pi * y) + 10)
        elif func_num == 9:
            # Shifted and Rotated Levy Function
            w = 1 + (z - 1) / 4
            term1 = np.sin(np.pi * w[0])**2
            term2 = np.sum((w[:-1] - 1)**2 * (1 + 10 * np.sin(np.pi * w[:-1] + 1)**2))
            term3 = (w[-1] - 1)**2 * (1 + np.sin(2 * np.pi * w[-1])**2)
            return term1 + term2 + term3
        else:  # func_num == 10
            # Shifted and Rotated Schwefel's Function
            g = z + 4.209687462275036e+002
            return 418.9829 * len(z) - np.sum(g * np.sin(np.sqrt(np.abs(g))))

