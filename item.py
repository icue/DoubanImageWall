from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    """A Douban item"""
    name: str
    img_url: str
    rating: int
    img_used: bool = False

    @property
    def is_high_rating(self) -> bool:
        return self.rating == 5


def get_next_img_url(items: list[Item], sort_by_time: bool, need_large_img: bool) -> str:
    exhausted = all(i.img_used for i in items)
    if exhausted:
        return None
    if not sort_by_time:
        # Rating does not matter
        item = next(i for i in items if not i.img_used)
    elif need_large_img:
        # Prioritizes high rating items
        item = next((i for i in items if not i.img_used and i.is_high_rating),
                    next((i for i in items if not i.img_used and not i.is_high_rating), None))
    else:
        # Prioritizes low rating items
        item = next((i for i in items if not i.img_used and not i.is_high_rating),
                    next((i for i in items if not i.img_used and i.is_high_rating), None))
    # item should never be None here, as exhausted already did the check
    item.img_used = True
    return item.img_url
