from typing import Optional


class Slot:
    def __init__(self, name):
        self.name = name
        self.bean = None
        self.creating = True


def _make_finished_slot(name, bean):
    slot = Slot(name)
    slot.bean = bean
    slot.creating = False
    return slot


class ContextBase:
    def __init__(self, parent=None):
        self.path = []
        self.slots = dict()
        self.parent = parent

    def _get_factory(self, name):
        raise NotImplementedError()

    def __getitem__(self, item):
        return self.get(item, RAISE_IF_MISSING)

    def get(self, item, default=None):
        self.path.append(item)
        try:
            slot = self._get_finished_slot(item)
            if slot is not None:
                return slot.bean
            slot = self._make_new_slot(item)
            if slot is not None:
                return slot.bean
            slot = self._slot_from_parent(item)
            if slot is not None:
                return slot.bean
            if default is RAISE_IF_MISSING:
                raise KeyError(f"{item!r} is not found in context_def ({self._path_str()})")
            return default
        finally:
            self.path.pop()

    def _slot_from_parent(self, name):
        if self.parent is None:
            return None
        result = self.parent.get(name, _MISSING_MARKER)
        if result is _MISSING_MARKER:
            return None
        slot = _make_finished_slot(name=name, bean=result)
        self.slots[name] = slot
        return slot

    def _make_new_slot(self, name):
        fn = self._get_factory(name)
        if fn is None:
            return None
        slot = Slot(name)
        self.slots[name] = slot
        bean = fn(self)
        slot.bean = bean
        slot.creating = False
        return slot

    def _get_finished_slot(self, name) -> Optional[Slot]:
        slot = self.slots.get(name, None)
        if slot is not None and slot.creating:
            raise ContextError(f"Circular dependency: {self._path_str()}")
        return slot

    def _path_str(self):
        return ' -> '.join(self.path)


class Context(ContextBase):
    def __init__(self, context_def, context_def_prefix=None, parent=None):
        if context_def_prefix is None:
            context_def_prefix = 'bean_'
        super().__init__(parent=parent)
        self.context_def = context_def
        self.context_def_prefix = context_def_prefix

    def _get_factory(self, name):
        return getattr(self.context_def, self.context_def_prefix + name, None)


class ContextError(Exception):
    pass


RAISE_IF_MISSING = object()
_MISSING_MARKER = object()
