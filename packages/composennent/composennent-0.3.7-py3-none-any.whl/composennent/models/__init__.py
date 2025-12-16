"""Models module with shared capabilities.

Usage:
    from composennent.models import BaseModel
    
    class MyModel(BaseModel):
        def forward(self, x):
            return self.layers(x)
"""

from .base import BaseModel

__all__ = ["BaseModel"]
