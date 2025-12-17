from typing import Optional, Tuple, Callable, List, Dict
from .container_node import ContainerNode
from .node import Node
from ..models import VerticalAlignment, HorizontalDistribution, SizeValueMode
import skia
import math

class RowNode(ContainerNode):

    def _set_width_constraint(self, width_constraint: Optional[int]) -> None:
        children = self._get_positionable_children()
        width_style_prop = self.computed_styles.width.get()
        is_auto_width = not width_style_prop or width_style_prop.mode == SizeValueMode.AUTO
        width_constraint = width_constraint if is_auto_width else self.content_width
        if width_constraint is None:
            for child in children:
                child._set_width_constraint(None)
            return
        
        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(children) - 1) if len(children) > 0 else 0
        available_for_children = max(width_constraint - total_gap, 0)
        children_with_flexible_width: List[Node] = []
        fixed_width_total = 0

        for child in children:
            child_width_property = child.computed_styles.width.get()
            if not child_width_property or child_width_property.mode in ['auto', 'fit-content']:
                children_with_flexible_width.append(child)
            else:
                child._set_width_constraint(None)
                fixed_width_total += child.margin_bounds.width()

        available_for_children = max(available_for_children - fixed_width_total, 0)
        if not children_with_flexible_width:
            return

        bases: Dict[Node, float] = {}
        mins: Dict[Node, int] = {}
        for child in children_with_flexible_width:
            basis = float(child.margin_bounds.width())
            if basis <= 0:
                basis = 1.0
            bases[child] = basis
            mins[child] = int(round(child.compute_min_width() or 0))

        remaining = set(children_with_flexible_width)
        remaining_available = int(available_for_children)

        while remaining:
            total_basis = sum(bases[c] for c in remaining)
            raw_allocs = {c: (bases[c] / total_basis) * remaining_available for c in remaining}
            allocations = {c: int(math.floor(raw_allocs[c])) for c in remaining}

            allocated_sum = sum(allocations.values())
            leftover = remaining_available - allocated_sum
            if leftover > 0:
                residuals = sorted(
                    remaining,
                    key=lambda c: (raw_allocs[c] - math.floor(raw_allocs[c])),
                    reverse=True
                )
                for c in residuals[:leftover]:
                    allocations[c] += 1

            bumped = False
            to_fix = []
            for c in list(remaining):
                alloc = allocations.get(c, 0)
                minw = mins[c]
                if alloc < minw:
                    to_fix.append((c, minw))
                    bumped = True

            if not bumped:
                for c in remaining:
                    child_alloc = int(allocations[c])
                    c._set_width_constraint(child_alloc)
                break
            else:
                for (c, minw) in to_fix:
                    c._set_width_constraint(int(minw))
                    remaining_available = max(remaining_available - int(minw), 0)
                    remaining.remove(c)
    
    def compute_min_width(self) -> int:
        children = self._get_positionable_children()
        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(children) - 1) if len(children) > 1 else 0
        min_width = total_gap
        for child in children:
            min_width += child.compute_min_width()
        
        margin = self.computed_styles.margin.get()
        padding = self.computed_styles.padding.get()
        border = self.computed_styles.border.get()
        border_width = border.width if border else 0
        horizontal_spacing = padding.left + padding.right + (border_width * 2) + margin.left + margin.right
        return min_width + horizontal_spacing

    def compute_intrinsic_width(self) -> int:
        children = self._get_positionable_children()
        if not children:
            return 0

        gap = self.computed_styles.gap.get()
        total_gap = gap * (len(children) - 1)
        total_children_width = 0
        
        for child in children:
            width_style = child.computed_styles.width.get()
            if width_style and width_style.mode in [SizeValueMode.PERCENT, SizeValueMode.FILL_AVAILABLE]:
                continue
            total_children_width += child.margin_bounds.width()

        return total_children_width + total_gap
    
    def compute_intrinsic_height(self) -> int:
        children = self._get_positionable_children()
        if not children:
            return 0

        max_height = 0
        for child in children:
            height_style = child.computed_styles.height.get()
            if height_style and height_style.mode in [SizeValueMode.PERCENT, SizeValueMode.FILL_AVAILABLE]:
                continue
            max_height = max(max_height, child.margin_bounds.height())
            
        return max_height
    
    def _apply_stretch_constraints(self):
        """
        Apply vertical stretch constraints to children with auto height.
        """
        alignment = self.computed_styles.vertical_alignment.get()
        if alignment != VerticalAlignment.STRETCH:
            return
        
        children = self._get_positionable_children()
        for child in children:
            child_height = child.computed_styles.height.get()
            if child_height and child_height.mode != SizeValueMode.AUTO:
                continue

            child._forced_size = (child._forced_size[0], self.content_height)

    def _apply_fill_available_constraints(self):
        """
        Apply width constraints to children with fill-available.
        """
        children = self._get_positionable_children()
        fixed_children_width = 0
        flexible_children: list[Node] = []
        user_gap = self.computed_styles.gap.get()

        for child in children:
            child_width_style = child.computed_styles.width.get()
            if child_width_style and child_width_style.mode == SizeValueMode.FILL_AVAILABLE:
                flexible_children.append(child)
            else:
                fixed_children_width += child.size[0]

        if not flexible_children:
            return

        total_gap_space = user_gap * (len(children) - 1) if len(children) > 1 else 0
        remaining_space = self.content_width - fixed_children_width - total_gap_space
        space_per_flexible_child = max(0, remaining_space / len(flexible_children))

        for child in flexible_children:
            child._forced_size = (space_per_flexible_child, child._forced_size[1])

    def _calculate_children_relative_positions(self, children: list[Node], get_child_bounds: Callable[[Node], skia.Rect]) -> list[Tuple[float, float]]:
        positions = []
        alignment = self.computed_styles.vertical_alignment.get()
        user_gap = self.computed_styles.gap.get()
        distribution_gap, start_x = self._distribute_horizontally(user_gap, children)

        final_gap = user_gap + distribution_gap
        current_x = start_x
        for child in children:
            child_bounds = get_child_bounds(child)
            child_height = child_bounds.height()
            container_height = self.content_bounds.height()
            child_y = self.content_bounds.top()

            if alignment == VerticalAlignment.CENTER:
                child_y += (container_height - child_height) / 2
            elif alignment == VerticalAlignment.BOTTOM:
                child_y += container_height - child_height

            positions.append((current_x, child_y))
            current_x += child_bounds.width() + final_gap

        return positions

    def _distribute_horizontally(self, user_gap: float, children: list[Node]) -> Tuple[float, float]:
        distribution = self.computed_styles.horizontal_distribution.get()
        container_width = self.content_bounds.width()
        children_total_width = sum(child.margin_bounds.width() for child in children)
        total_gap_space = user_gap * (len(children) - 1)
        extra_space = container_width - children_total_width - total_gap_space

        start_x = self.content_bounds.left()
        distribution_gap = 0
        if distribution == HorizontalDistribution.RIGHT:
            start_x += extra_space
        elif distribution == HorizontalDistribution.CENTER:
            start_x += extra_space / 2
        elif distribution == HorizontalDistribution.SPACE_BETWEEN and len(children) > 1:
            distribution_gap = extra_space / (len(children) - 1)
        elif distribution == HorizontalDistribution.SPACE_AROUND:
            distribution_gap = extra_space / len(children)
            start_x += distribution_gap / 2
        elif distribution == HorizontalDistribution.SPACE_EVENLY:
            distribution_gap = extra_space / (len(children) + 1)
            start_x += distribution_gap

        return distribution_gap, start_x
