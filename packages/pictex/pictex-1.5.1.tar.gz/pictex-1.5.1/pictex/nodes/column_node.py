from typing import Optional, Tuple, Callable
from .node import Node
from .container_node import ContainerNode
from ..models import HorizontalAlignment, VerticalDistribution, SizeValueMode
import skia

class ColumnNode(ContainerNode):

    def _set_width_constraint(self, width_constraint: Optional[int]) -> None:
        children = self._get_positionable_children()
        width_style_prop = self.computed_styles.width.get()
        is_auto_width = not width_style_prop or width_style_prop.mode == SizeValueMode.AUTO
        width_constraint = width_constraint if is_auto_width else self.content_width
        for child in children:
            child._set_width_constraint(width_constraint)

    def compute_min_width(self) -> int:
        children = self._get_positionable_children()
        margin = self.computed_styles.margin.get()
        padding = self.computed_styles.padding.get()
        border = self.computed_styles.border.get()
        border_width = border.width if border else 0
        horizontal_spacing = padding.left + padding.right + (border_width * 2) + margin.left + margin.right

        if not children:
            return horizontal_spacing
        
        min_width = max([child.compute_min_width() for child in children])
        return min_width + horizontal_spacing

    def _apply_stretch_constraints(self):
        """
        Apply horizontal stretch constraints to children with auto width.
        """
        alignment = self.computed_styles.horizontal_alignment.get()
        if alignment != HorizontalAlignment.STRETCH:
            return

        children = self._get_positionable_children()
        for child in children:
            child_width = child.computed_styles.width.get()
            if child_width and child_width.mode != SizeValueMode.AUTO:
                continue

            child._forced_size = (self.content_width, self._forced_size[1])

    def _apply_fill_available_constraints(self):
        """
        Apply height constraints to children with fill-available height.
        """
        children = self._get_positionable_children()
        fixed_children_height = 0
        flexible_children: list[Node] = []
        user_gap = self.computed_styles.gap.get()

        for child in children:
            child_height_style = child.computed_styles.height.get()
            if child_height_style and child_height_style.mode == SizeValueMode.FILL_AVAILABLE:
                flexible_children.append(child)
            else:
                fixed_children_height += child.size[1]

        if not flexible_children:
            return

        total_gap_space = user_gap * (len(children) - 1) if len(children) > 1 else 0
        remaining_space = self.content_height - fixed_children_height - total_gap_space
        space_per_flexible_child = max(0, remaining_space / len(flexible_children))

        for child in flexible_children:
            child._forced_size = (self._forced_size[0], space_per_flexible_child)

    def compute_intrinsic_width(self) -> int:
        children = self._get_positionable_children()
        if not children:
            return 0

        max_width = 0
        for child in children:
            width_style = child.computed_styles.width.get()
            if width_style and width_style.mode in [SizeValueMode.PERCENT, SizeValueMode.FILL_AVAILABLE]:
                continue
            max_width = max(max_width, child.margin_bounds.width())
            
        return max_width
    
    def compute_intrinsic_height(self) -> int:
        children = self._get_positionable_children()
        if not children:
            return 0

        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(children) - 1)
        
        total_children_height = 0
        for child in children:
            height_style = child.computed_styles.height.get()
            if height_style and height_style.mode in [SizeValueMode.PERCENT, SizeValueMode.FILL_AVAILABLE]:
                continue
            total_children_height += child.margin_bounds.height()
            
        return total_children_height + total_gap

    def _calculate_children_relative_positions(self, children: list[Node], get_child_bounds: Callable[[Node], skia.Rect]) -> list[Tuple[float, float]]:
        positions = []
        user_gap = self.computed_styles.gap.get()
        alignment = self.computed_styles.horizontal_alignment.get()
        start_y, distribution_gap = self._distribute_vertically(user_gap, children)

        final_gap = user_gap + distribution_gap
        current_y = start_y
        for child in children:
            child_bounds = get_child_bounds(child)
            child_width = child_bounds.width()
            container_width = self.content_bounds.width()
            child_x = self.content_bounds.left()

            if alignment == HorizontalAlignment.CENTER:
                child_x += (container_width - child_width) / 2
            elif alignment == HorizontalAlignment.RIGHT:
                child_x += container_width - child_width

            positions.append((child_x, current_y))
            current_y += child_bounds.height() + final_gap

        return positions

    def _distribute_vertically(self, user_gap: float, children: list[Node]) -> Tuple[float, float]:
        distribution = self.computed_styles.vertical_distribution.get()
        container_height = self.content_bounds.height()
        children_total_height = sum(child.margin_bounds.height() for child in children)
        total_gap_space = user_gap * (len(children) - 1)
        extra_space = container_height - children_total_height - total_gap_space

        start_y = self.content_bounds.top()
        distribution_gap = 0
        if distribution == VerticalDistribution.BOTTOM:
            start_y += extra_space
        elif distribution == VerticalDistribution.CENTER:
            start_y += extra_space / 2
        elif distribution == VerticalDistribution.SPACE_BETWEEN and len(children) > 1:
            distribution_gap = extra_space / (len(children) - 1)
        elif distribution == VerticalDistribution.SPACE_AROUND:
            distribution_gap = extra_space / len(children)
            start_y += distribution_gap / 2
        elif distribution == VerticalDistribution.SPACE_EVENLY:
            distribution_gap = extra_space / (len(children) + 1)
            start_y += distribution_gap

        return start_y, distribution_gap
