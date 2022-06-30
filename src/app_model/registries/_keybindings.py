from __future__ import annotations

from typing import TYPE_CHECKING, Callable, NamedTuple, Optional

from psygnal import Signal

if TYPE_CHECKING:
    from typing import Iterator, List, TypeVar

    from .. import expressions
    from ..types import CommandIdStr, KeybindingRule, KeyCodeStr

    DisposeCallable = Callable[[], None]
    CommandDecorator = Callable[[Callable], Callable]
    CommandCallable = TypeVar("CommandCallable", bound=Callable)


class _RegisteredKeyBinding(NamedTuple):
    """Internal object representing a fully registered keybinding."""

    keybinding: KeyCodeStr  # the keycode to bind to
    command_id: CommandIdStr  # the command to run
    weight: int  # the weight of the binding, for prioritization
    when: Optional[expressions.Expr] = None  # condition to enable keybinding


class KeybindingsRegistry:

    registered = Signal()
    __instance: Optional[KeybindingsRegistry] = None

    def __init__(self) -> None:
        self._coreKeybindings: List[_RegisteredKeyBinding] = []

    @classmethod
    def instance(cls) -> KeybindingsRegistry:
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def register_keybinding_rule(
        self, id: CommandIdStr, rule: KeybindingRule
    ) -> Optional[DisposeCallable]:
        if bound_keybinding := rule._bind_to_current_platform():
            entry = _RegisteredKeyBinding(
                keybinding=bound_keybinding,
                command_id=id,
                weight=rule.weight,
                when=rule.when,
            )
            self._coreKeybindings.append(entry)
            self.registered.emit()

            def _dispose() -> None:
                self._coreKeybindings.remove(entry)

            return _dispose
        return None  # pragma: no cover

    def __iter__(self) -> Iterator[_RegisteredKeyBinding]:
        yield from self._coreKeybindings

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"<{name} at {hex(id(self))} ({len(self._coreKeybindings)} bindings)>"