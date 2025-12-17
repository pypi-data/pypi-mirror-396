"""
PhysLab - Библиотека для обработки лабораторных работ по физике
"""
from .__version__ import __version__
from .core import phys, LabProcessor, graph, sin, cos, tg, ctg, exp, ln, log10, sqrt, arcsin, arccos, arctg

__author__ = "Vsevolod Filippov"
__email__ = "filippov.va@phystech.edu"

__all__ = [
    'phys',
    'LabProcessor',
    'graph',
    'cos',
    'sin',
    'tg',
    'ctg',
    'exp',
    'ln',
    'log10',
    'sqrt',
    'arcsin',
    'arccos',
    'arctg'
]

# Создаём удобный экземпляр по умолчанию
lab = LabProcessor()