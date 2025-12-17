from typing import Tuple, Callable
from .node import Node
from ..painters import Painter, BackgroundPainter, BorderPainter
from ..models import Style
import skia

class ContainerNode(Node):

    def __init__(self, style: Style, children: list[Node]) -> None:
        super().__init__(style)
        self._set_children(children)
        self.clear()

    def _calculate_children_relative_positions(self, children: list[Node], get_child_bounds: Callable[[Node], skia.Rect]) -> list[Tuple[float, float]]:
        raise NotImplementedError()
    
    def _compute_paint_bounds(self) -> skia.Rect:
        paint_bounds = skia.Rect.MakeEmpty()

        children = self._get_positionable_children()
        positions = self._calculate_children_relative_positions(children, lambda node: node.margin_bounds)
        for i, child in enumerate(children):
            position = positions[i]
            child_bounds_shifted = child.paint_bounds.makeOffset(position[0], position[1])
            paint_bounds.join(child_bounds_shifted)

        paint_bounds.join(self._compute_shadow_bounds(self.border_bounds, self.computed_styles.box_shadows.get()))
        paint_bounds.join(self.margin_bounds)
        return paint_bounds

    def _get_painters(self) -> list[Painter]:
        if not self._render_props:
            raise RuntimeError("Unexpected error: self._render_props is not defined. Parent node should initialize this dependency.")

        return [
            BackgroundPainter(self.computed_styles, self.border_bounds, self._render_props.is_svg),
            BorderPainter(self.computed_styles, self.border_bounds),
        ]

    def _setup_absolute_position(self, x: float = 0, y: float = 0) -> None:
        super()._setup_absolute_position(x, y)
        absolute_position = self._absolute_position
        if not absolute_position:
            raise RuntimeError("Unexpected error: node doesn't have a position defined but it should have.")
        
        x, y = absolute_position
        positionable_children = self._get_positionable_children()
        positions = self._calculate_children_relative_positions(positionable_children, lambda node: node.margin_bounds)
        for i, child in enumerate(positionable_children):
            position = positions[i]
            child._setup_absolute_position(x + position[0], y + position[1])

        non_positionable_children = self._get_non_positionable_children()
        for child in non_positionable_children:
            child._setup_absolute_position()

    def _before_calculating_bounds(self) -> None:
        self._apply_stretch_constraints()
        self._apply_fill_available_constraints()

        super()._before_calculating_bounds()

    def _apply_stretch_constraints(self):
        """
        Apply stretch-specific constraints to children that have auto sizing.
        This is overridden by RowNode and ColumnNode with specific stretch logic.
        """
        pass

    def _apply_fill_available_constraints(self):
        """
        Apply fill-available constraints to children that use fill-available sizing.
        This is overridden by RowNode and ColumnNode with specific fill-available logic.
        """
        pass
