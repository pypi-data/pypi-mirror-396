from typing import Optional, Type, Dict
from rest_framework.serializers import BaseSerializer

class ReadWriteSerializerMixin:

    # Choose read/write serializers with optional per-action overrides.
    # Resolution order:
    #  - If called with `data=...`  -> write serializer for action (if any) else default write else default read.
    # - If called with `instance=...` -> read serializer for action (if any) else default read else default write.
    # - If neither `data` nor `instance` provided:
    #      * if action is known -> prefer read serializer for action (fallback to defaults)
    #      * else -> default read (fallback to default write)
    # Define in your view:
    # read_serializer_class: Type[BaseSerializer]         # default read
    # write_serializer_class: Type[BaseSerializer]        # default write
    # action_read_serializer_classes: Dict[str, Type[BaseSerializer]]   # optional per-action read
    # action_write_serializer_classes: Dict[str, Type[BaseSerializer]]  # optional per-action write

    # Defaults (override in subclasses)
    read_serializer_class: Optional[Type[BaseSerializer]] = None
    write_serializer_class: Optional[Type[BaseSerializer]] = None

    # Per-action overrides (override in subclasses)
    action_read_serializer_classes: Optional[Dict[str, Type[BaseSerializer]]] = None
    action_write_serializer_classes: Optional[Dict[str, Type[BaseSerializer]]] = None

    # ------- helpers ---------------------------------------------------------

    def _drf_serializer_cls(self) -> Optional[Type[BaseSerializer]]:
        """
        Try to use DRF / GenericAPIView.get_serializer_class(), including any
        override you defined on the view.

        Returns None if DRF cannot determine a serializer (e.g. it would
        raise AssertionError because no serializer is configured).
        """
        get_sc = getattr(type(self), "get_serializer_class", None)
        if get_sc is None:
            return None

        try:
            cls = get_sc(self)  # call the class's get_serializer_class(self)
        except AssertionError:
            # DRF uses AssertionError when serializer_class is not set
            return None

        return cls

    def _default_read_cls(self) -> Type[BaseSerializer]:
        """
              Default read serializer resolution.

              Order:
                1) read_serializer_class
                2) DRF get_serializer_class()
                3) serializer_class attribute

              Raises AssertionError if none of the above are configured.
        """
        cls = (
                self.read_serializer_class
                or self._drf_serializer_cls()
                or getattr(self, "serializer_class", None)
        )

        if cls is None:
            raise AssertionError(
                "Read serializer is not configured. "
                "Set `read_serializer_class`, implement `get_serializer_class`, "
                "or set `serializer_class` on the view."
            )
        return cls

    def _default_write_cls(self) -> Type[BaseSerializer]:
        """
        Default write serializer resolution.

        Order:
          1) write_serializer_class
          2) fallback to default read serializer
        """
        return self.write_serializer_class or self._default_read_cls()

    def _action_read_cls(self, action: Optional[str]) -> Optional[Type[BaseSerializer]]:
        """
        Return a per-action read serializer class if configured for this action.
        """
        if not action or not self.action_read_serializer_classes:
            return None
        return self.action_read_serializer_classes.get(action)

    def _action_write_cls(self, action: Optional[str]) -> Optional[Type[BaseSerializer]]:
        """
        Return a per-action write serializer class if configured for this action.
        """
        if not action or not self.action_write_serializer_classes:
            return None
        return self.action_write_serializer_classes.get(action)

    # ------- main hook -------------------------------------------------------
    def get_serializer(self, *args, **kwargs) -> BaseSerializer:
        """
        Main entry point for DRF.

        DRF calls this for:
          - Validation: usually with `data=...`
          - Serialization: usually with `instance=...` or positional instance

        We decide whether it's a read or write scenario and choose the
        appropriate serializer class according to the rules above.
        """
        kwargs.setdefault("context", self.get_serializer_context())
        action = getattr(self, "action", None)

        has_data = "data" in kwargs
        has_instance_kw = "instance" in kwargs
        # DRF sometimes passes the instance positionally: get_serializer(obj, many=True)
        has_positional_instance = bool(args) and not has_data

        if has_data:
            # Write path
            serializer_class = self._action_write_cls(action) or self._default_write_cls()
        elif has_instance_kw or has_positional_instance:
            # Read path
            serializer_class = self._action_read_cls(action) or self._default_read_cls()
        else:
            # Indeterminate (e.g. get_serializer() with no data/instance)
            # Prefer read serializer for this action, falling back to default read.
            serializer_class = (
                self._action_read_cls(action)
                or self._default_read_cls()
            )

        return serializer_class(*args, **kwargs)