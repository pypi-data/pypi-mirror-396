from kuaijs import node, action, device
from typing import Union

NodeSelector = node.NodeSelector


class Selector:
    def __init__(self):
        self.selector: NodeSelector = node.createNodeSelector()
        self.clickNode = False
        self.brotherIndex = None
        self.inputValue = None
        self.scrollMode = None
        self.scrollDistance = None
        self.childIndex = None
        self.parentIndex = None

    def find(self, timeout: int = 120) -> Union[node.NodeInfo, None]:
        base = self.selector.getOneNodeInfo(timeout * 1000)
        if base is None:
            return None
        self.exec_action(base)
        if self.childIndex is not None:
            children = base.allChildren()
            idx = self.childIndex
            if idx == 0:
                return children[0] if len(children) > 0 else None
            if isinstance(idx, (int, float)) and idx > 0:
                i = int(idx) - 1
                return children[i] if 0 <= i < len(children) else None
            if idx == -1:
                i = len(children) - 2
                return children[i] if 0 <= i < len(children) else None
            # 其他负值默认返回最后一个
            return children[-1] if len(children) > 0 else None
        if self.parentIndex is not None:
            idx = int(self.parentIndex)
            if idx == 0:
                return base.parent()
            cur = base
            for _ in range(idx):
                p = cur.parent()
                if p is None:
                    return None
                cur = p
            return cur
        if self.brotherIndex is not None:
            sibs = base.siblings()
            val = self.brotherIndex
            if val == 0:
                return sibs[0] if len(sibs) > 0 else None
            if val == 1:
                return sibs[0] if len(sibs) > 0 else None
            if val == 2:
                return sibs[1] if len(sibs) > 1 else None
            if val == -1:
                return sibs[-1] if len(sibs) > 0 else None
            if val == 0.1:
                prev = base.previousSiblings()
                return prev[-1] if len(prev) > 0 else None
            if val == -0.1:
                nxt = base.nextSiblings()
                return nxt[0] if len(nxt) > 0 else None
        return base

    def find_all(self, timeout: int = 120) -> list[node.NodeInfo]:
        nodes = self.selector.getNodeInfo(timeout * 1000)
        for n in nodes:
            self.exec_action(n)
        if self.childIndex is not None:
            out = []
            idx = self.childIndex
            for n in nodes:
                children = n.allChildren()
                if idx == 0:
                    out.extend(children)
                elif isinstance(idx, (int, float)) and idx > 0:
                    i = int(idx) - 1
                    if 0 <= i < len(children):
                        out.append(children[i])
                elif idx == -1:
                    i = len(children) - 2
                    if 0 <= i < len(children):
                        out.append(children[i])
                else:
                    if len(children) > 0:
                        out.append(children[-1])
            return out
        if self.parentIndex is not None:
            out = []
            idx = int(self.parentIndex)
            for n in nodes:
                if idx == 0:
                    cur = n
                    while True:
                        p = cur.parent()
                        if p is None:
                            break
                        out.append(p)
                        cur = p
                else:
                    cur = n
                    ok = True
                    for _ in range(idx):
                        p = cur.parent()
                        if p is None:
                            ok = False
                            break
                        cur = p
                    if ok:
                        out.append(cur)
            return out
        if self.brotherIndex is not None:
            out = []
            val = self.brotherIndex
            for n in nodes:
                if val == 0:
                    out.extend(n.siblings())
                elif val == 1:
                    sibs = n.siblings()
                    if len(sibs) > 0:
                        out.append(sibs[0])
                elif val == 2:
                    sibs = n.siblings()
                    if len(sibs) > 1:
                        out.append(sibs[1])
                elif val == -1:
                    sibs = n.siblings()
                    if len(sibs) > 0:
                        out.append(sibs[-1])
                elif val == 0.1:
                    prev = n.previousSiblings()
                    if len(prev) > 0:
                        out.append(prev[-1])
                elif val == -0.1:
                    nxt = n.nextSiblings()
                    if len(nxt) > 0:
                        out.append(nxt[0])
            return out
        return nodes

    def exec_action(self, one: node.NodeInfo):
        if self.clickNode or self.inputValue is not None:
            one.clickRandom()
            if self.inputValue is not None:
                action.input(self.inputValue)
        if self.scrollMode is not None and self.scrollDistance is not None:
            mode = self.scrollMode
            distance = self.scrollDistance
            s = device.getScreenRealSize()
            w = s.width
            h = s.height
            cx = int(w // 2)
            cy = int(h // 2)
            if one is not None:
                cx = int(one.bounds.centerX)
                cy = int(one.bounds.centerY)
            if distance <= 1:
                dx = int(w * float(distance))
                dy = int(h * float(distance))
            else:
                dx = int(distance)
                dy = int(distance)
            if mode == "left":
                action.swipe(cx + dx, cy, cx - dx, cy, 300)
                return self
            if mode == "right":
                action.swipe(cx - dx, cy, cx + dx, cy, 300)
                return self
            if mode == "up":
                action.swipe(cx, cy + dy, cx, cy - dy, 300)
                return self
            if mode == "down":
                action.swipe(cx, cy - dy, cx, cy + dy, 300)
                return self
            for _ in range(8):
                cur = self.selector.loadNode().getOneNodeInfo()
                if cur is not None and cur.visible:
                    return self
                action.swipe(cx, int(h * 0.75), cx, int(h * 0.25), 500)
            for _ in range(8):
                cur = self.selector.loadNode().getOneNodeInfo()
                if cur is not None and cur.visible:
                    return self
                action.swipe(cx, int(h * 0.25), cx, int(h * 0.75), 500)

    @staticmethod
    def xml() -> str:
        return node.createNodeSelector().xml()

    def value(self, value, mode=0) -> "Selector":
        if mode == 0:
            self.selector.value(value)
        else:
            self.selector.valueMatch(f".*{value}.*")
        return self

    def name(self, value: str, mode=0) -> "Selector":
        if mode == 0:
            self.selector.identifier(value)
        else:
            self.selector.identifierMatch(f".*{value}.*")
        return self

    def label(self, value: str, mode=0) -> "Selector":
        if mode == 0:
            self.selector.label(value)
        else:
            self.selector.labelMatch(f".*{value}.*")
        return self

    def type(self, value: str, mode=0) -> "Selector":
        if mode == 0:
            self.selector.type(value)
        else:
            self.selector.typeMatch(f".*{value}.*")
        return self

    def visible(self, value: bool) -> "Selector":
        self.selector.visible(value)
        return self

    def enabled(self, value: bool) -> "Selector":
        self.selector.enabled(value)
        return self

    def accessible(self, value: bool) -> "Selector":
        self.selector.accessible(value)
        return self

    def index(self, value: int) -> "Selector":
        self.selector.index(value)
        return self

    def x(self, value: int, mode: int = 0) -> "Selector":
        if mode == 0:
            self.selector.x(value)
        elif mode == 3:
            self.selector.x(f">{value}")
        elif mode == 4:
            self.selector.x(f"<{value}")
        return self

    def y(self, value: int, mode: int = 0) -> "Selector":
        if mode == 0:
            self.selector.y(value)
        elif mode == 3:
            self.selector.y(f">{value}")
        elif mode == 4:
            self.selector.y(f"<{value}")
        return self

    def width(self, value: int, mode: int = 0) -> "Selector":
        if mode == 0:
            self.selector.width(value)
        elif mode == 3:
            self.selector.width(f">{value}")
        elif mode == 4:
            self.selector.width(f"<{value}")
        return self

    def height(self, value: int, mode: int = 0) -> "Selector":
        if mode == 0:
            self.selector.height(value)
        elif mode == 3:
            self.selector.height(f">{value}")
        elif mode == 4:
            self.selector.height(f"<{value}")
        return self

    def child(self, value: float = 0) -> "Selector":
        self.childIndex = value
        self.parentIndex = None
        self.brotherIndex = None
        return self

    def parent(self, value: float = 0) -> "Selector":
        self.parentIndex = value
        self.childIndex = None
        self.brotherIndex = None
        return self

    def brother(self, value: float = 0) -> "Selector":
        self.brotherIndex = value
        self.childIndex = None
        self.parentIndex = None
        return self

    def xpath(self, value: str) -> "Selector":
        self.selector.xpath(value)
        return self

    def click(self, mode: int = 0) -> "Selector":
        self.clickNode = True
        return self

    def scroll(self, mode: str = "visible", distance: float = 1.0) -> "Selector":
        self.scrollMode = mode
        self.scrollDistance = distance
        return self

    def input(self, value: str) -> "Selector":
        self.inputValue = value
        return self
