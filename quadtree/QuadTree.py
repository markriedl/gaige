from pygame import Rect

class QuadTree(object):
    """An implementation of a quad-tree.

    This QuadTree started life as a version of [1] but found a life of its own
    when I realised it wasn't doing what I needed. It is intended for static
    geometry, ie, items such as the landscape that don't move.

    This implementation inserts items at the current level if they overlap all
    4 sub-quadrants, otherwise it inserts them recursively into the one or two
    sub-quadrants that they overlap.

    Items being stored in the tree must be a pygame.Rect or have have a
    .rect (pygame.Rect) attribute that is a pygame.Rect
        ...and they must be hashable.

    Acknowledgements:
    [1] http://mu.arete.cc/pcr/syntax/quadtree/1/quadtree.py
    """

    def __init__(self, items, depth=8, bounding_rect=None):
        """Creates a quad-tree.

        @param items:
            A sequence of items to store in the quad-tree. Note that these
            items must be a pygame.Rect or have a .rect attribute.

        @param depth:
            The maximum recursion depth.

        @param bounding_rect:
            The bounding rectangle of all of the items in the quad-tree. For
            internal use only.
        """

        # The sub-quadrants are empty to start with.
        self.nw = self.ne = self.se = self.sw = None

        # If we've reached the maximum depth then insert all items into this
        # quadrant.
        depth -= 1
        if depth == 0 or not items:
            self.items = items
            return

        # Find this quadrant's centre.
        if bounding_rect:
            bounding_rect = Rect( bounding_rect )
        else:
            # If there isn't a bounding rect, then calculate it from the items.
            bounding_rect = Rect( items[0] )
            for item in items[1:]:
                bounding_rect.union_ip( item )
        cx = self.cx = bounding_rect.centerx
        cy = self.cy = bounding_rect.centery

        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item.rect.left <= cx and item.rect.top <= cy
            in_sw = item.rect.left <= cx and item.rect.bottom >= cy
            in_ne = item.rect.right >= cx and item.rect.top <= cy
            in_se = item.rect.right >= cx and item.rect.bottom >= cy

            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)

        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = QuadTree(nw_items, depth, (bounding_rect.left, bounding_rect.top, cx, cy))
        if ne_items:
            self.ne = QuadTree(ne_items, depth, (cx, bounding_rect.top, bounding_rect.right, cy))
        if se_items:
            self.se = QuadTree(se_items, depth, (cx, cy, bounding_rect.right, bounding_rect.bottom))
        if sw_items:
            self.sw = QuadTree(sw_items, depth, (bounding_rect.left, cy, cx, bounding_rect.bottom))


    def hit(self, rect):
        """Returns the items that overlap a bounding rectangle.

        Returns the set of all items in the quad-tree that overlap with a
        bounding rectangle.

        @param rect:
            The bounding rectangle being tested against the quad-tree. This
            must possess left, top, right and bottom attributes.
        """

        # Find the hits at the current level.
        hits = set( [ self.items[n] for n in rect.collidelistall( self.items ) ] )

        # Recursively check the lower quadrants.
        if self.nw and rect.left <= self.cx and rect.top <= self.cy:
            hits |= self.nw.hit(rect)
        if self.sw and rect.left <= self.cx and rect.bottom >= self.cy:
            hits |= self.sw.hit(rect)
        if self.ne and rect.right >= self.cx and rect.top <= self.cy:
            hits |= self.ne.hit(rect)
        if self.se and rect.right >= self.cx and rect.bottom >= self.cy:
            hits |= self.se.hit(rect)

        return hits