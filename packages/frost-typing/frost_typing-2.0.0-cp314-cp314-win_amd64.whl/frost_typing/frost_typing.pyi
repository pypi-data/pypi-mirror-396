from abc import ABCMeta
from datetime import timedelta, datetime, date, time
from typing import (
    Callable,
    Generic,
    Optional,
    TypedDict,
    Union,
    Literal,
    TypeVar,
    Type,
    Any,
    overload,
    ClassVar,
    Iterable,
    Dict,
    BinaryIO,
    IO,
    NoReturn
)
from typing_extensions import Annotated, final, ParamSpec


# from typing_extensions import dataclass_transform
# TODO: Enable after implementing a mypy plugin to support Field(default=...) inside Annotated.

_T = TypeVar("_T")
_M = TypeVar("_M")
_V = TypeVar("_V")
_R = TypeVar("_R")
_P = ParamSpec("_P")
_S = TypeVar("_S", bound=str)
_DataModel = TypeVar("_DataModel", bound="DataModel")
_ValidModel = TypeVar("_ValidModel", bound="ValidModel")
UnionString = Union[str, bytes, bytearray]
FieldValidatorModes = Literal["before", "after", "wrap"]

_UN_SET: Any = object()
_NULL = object()

HAS_JSON_SCHEMA: bool

# =========================================================================== #
#                                  DataModel                                  #
# =========================================================================== #

def copy(__obj: _T, /) -> _T:
    """Creates a recursive copy of the object.

    This function attempts to create a deep copy of the given object by calling its `__copy__` method.

    **Requirements:**
        - The user-defined class must implement a `__copy__` method.
        - The `__copy__` method should return a new instance with copied values.

    **Behavior:**
        - If the object defines `__copy__`, that method is used.
        - If the object is a built-in type (e.g., `int`, `str`, `tuple`), it is returned as-is.
        - If the object is mutable (e.g., `list`, `dict`), a new instance is created recursively.

    **Example (User-defined class with `__copy__`):**
        ```python
        class Point:
            def __init__(self, x: int, y: int) -> None:
                self.x = x
                self.y = y

            def __copy__(self: _T) -> _T:
                return type(self)(x=self.x, y=self.y)

        point1 = Point(3, 4)
        point2 = copy(point1)

        assert point1 is not point2  # Different instances
        assert point1.x == point2.x and point1.y == point2.y  # Same values
        ```

    **Example (Recursive Copy for Nested Objects):**
        ```python
        class Rectangle:
            def __init__(self, width: int, height: int, position: Point) -> None:
                self.width = width
                self.height = height
                self.position = position  # Nested object

            def __copy__(self: _T) -> _T:
                return type(self)(self.width, self.height, copy(self.position))

        rect1 = Rectangle(10, 20, Point(3, 4))
        rect2 = copy(rect1)

        assert rect1 is not rect2  # Different instances
        assert rect1.position is not rect2.position  # Nested object is also copied
        ```

    **Example (Copying Built-in Collections):**
        ```python
        data = {"a": [1, 2, 3], "b": {"x": 10, "y": 20}}
        new_data = copy(data)

        assert new_data is not data  # Different dictionary instance
        assert new_data["a"] is not data["a"]  # Lists are copied recursively
        ```
    """

class AliasGenerator:
    """A utility class for generating field aliases (`alias` and `serialization_alias`) in a data model.

    This class allows defining custom functions that transform field names into alternative representations
    used for initialization and serialization.

    Attributes:
        alias (Optional[Callable[[str], str]]): A function that generates an alias for a field name.
            - Used when initializing an instance (`__init__`).
        serialization_alias (Optional[Callable[[str], str]]): A function that generates an alias specifically
            for serialization (e.g., when calling `.as_dict(by_alias=True)` or `.as_json(by_alias=True)`).

    Example:
        ```python
        from frost_typing import ValidModel, Field, AliasGenerator

        def to_camel_case(s: str) -> str:
            return "".join(word.capitalize() if i else word for i, word in enumerate(s.split("_")))

        class Model(ValidModel, config=AliasGenerator(alias=to_camel_case, serialization_alias=to_camel_case)):
            user_name: str

        model = Model(userName="John")       # `alias` is applied here
        print(model.as_dict(by_alias=True))  # `serialization_alias` is applied here
        # Output: {"userName": "John"}
        ```

    Behavior:
        - If `alias` is defined, it transforms the field name when initializing an instance.
        - If `serialization_alias` is defined, it is used only for serialization (`as_dict`, `as_json`).
        - If `auto_alias=True`, an alias is automatically generated using `alias_generator` when no manual alias is set.
        - If `auto_alias=False`, alias generation is disabled, and only manually set aliases are used.
    """

    alias: Optional[Callable[[str], str]]
    serialization_alias: Optional[Callable[[str], str]]

    def __new__(cls, alias: Callable[[str], str] = _UN_SET, serialization_alias: Callable[[str], str] = _UN_SET) -> "AliasGenerator":
        """Creates a new alias generator with the provided functions.

       Args:
           alias (Optional[Callable[[str], str]]): A function to generate aliases for `__init__`.
           serialization_alias (Optional[Callable[[str], str]]): A function to generate aliases for `as_dict` and `as_json`.

       Returns:
           AliasGenerator: A new instance with the specified alias generation rules.
       """

class Config:
    """Configuration class for controlling data model behavior.

    Attributes:
        init (bool): Enables/disables initialization via the constructor.
        repr (bool): Includes/excludes the attribute in the string representation.
        hash (bool): Determines if the attribute is used in object hashing.
        dict (bool): Specifies if the attribute should be included in `__dict__`.
        json (bool): Specifies if the attribute should be included in JSON serialization.
        strict (bool): Enables strict validation mode, where type conversions are not allowed.
            - If `True`, input data must match the expected type exactly.
            - This setting is only applicable to subclasses of `ValidModel`.
        kw_only (bool): Allows the attribute to be set only via keyword arguments.
        frozen (bool): Makes the attribute immutable after object creation.
        comparison (bool): Determines if the attribute is considered in equality checks.
        class_lookup (bool): If `True`, looks for the attribute in the class when missing in an instance.
        validate_private (bool): Specifies whether private fields (starting with "_") should be validated.
        gc (bool):
            - If True, enables garbage collection support (default behavior in Python).
            - If False, disables GC for this model to improve performance.
            - Defaults to True.
            - **Usage notes:**
                - Disabling GC is safe **only if this model does not participate in reference cycles** (i.e., it does not directly or indirectly reference itself).
                      Models that reference other models which themselves may have cycles are safe, because GC will handle those nested objects when they are deleted.
                    - Provides a **performance boost** in tight loops or benchmarks by avoiding the overhead of GC tracking.
                    - Reduces **memory consumption**, since the object is not tracked by the garbage collector.
                    - **Do not disable GC** if the model may directly or indirectly reference itself; this can prevent Python from collecting unreachable objects and cause memory leaks.
        fail_on_extra_init (bool):
            - If True, raises TypeError on unexpected keyword arguments.
            - If False, extra arguments are ignored.
            - Defaults to True for DataModel, False for ValidModel.
        frozen_type (bool): Prevents modification of the type attributes.
        title (Optional[str]): A title for JSON schema generation.
        examples (Optional[list[Any]]): Example values for JSON schema.
        auto_alias (bool): Determines whether to generate an alias using `alias_generator` if no manual alias is set.
            - If `True` (default), an alias is automatically generated when no `alias` or `serialization_alias` is defined.
            - If `False`, alias generation is completely disabled, and only manually set aliases are used.

        alias_generator (Union[Callable[[str], str], AliasGenerator]): A function for generating field aliases.
            - If defined, it provides an alias for `alias` and `serialization_alias` based on the `auto_alias` rule.
            - If `auto_alias=True`, manually set aliases remain unchanged.
            - If `auto_alias=False`, the generator's output is used instead.

        num_to_str (bool): If `True`, allows numerical values (`int`, `float`) to be assigned to string fields.
            - Automatically converts numbers to strings when assigning them to `str`-typed fields.
            - Useful for handling input where numbers might be provided as raw values instead of strings.

        allow_inf_nan (bool): If `True` (default), allows `inf`, `-inf`, and `nan` as valid float values.
            - If `False`, raises a validation error when encountering such values.

    Inheritance:
        - When a model class inherits from another, its `Config` settings are also inherited.
        - If a field has a `Field` configuration, it takes precedence over the inherited `Config` settings.
    """

    init: bool
    repr: bool
    hash: bool
    dict: bool
    json: bool
    strict: bool
    kw_only: bool
    frozen: bool
    comparison: bool
    class_lookup: bool
    frozen_type: bool
    fail_on_extra_init: bool
    validate_private: bool
    auto_alias: bool
    num_to_str: bool
    allow_inf_nan: bool
    gc: bool
    alias_generator: Optional[Union[Callable[[str], str], AliasGenerator]]
    title: Optional[str]
    examples: Optional[list[Any]]

    def __init__(
        self,
        init: bool = True,
        repr: bool = True,
        hash: bool = False,
        dict: bool = True,
        json: bool = True,
        strict: bool = False,
        kw_only: bool = False,
        frozen: bool = False,
        comparison: bool = True,
        class_lookup: bool = True,
        frozen_type: bool = False,
        fail_on_extra_init: bool = False,
        validate_private: bool = True,
        auto_alias: bool = True,
        num_to_str: bool = False,
        allow_inf_nan: bool = True,
        gc: bool = True,
        alias_generator: Union[Callable[[str], str], AliasGenerator] = _UN_SET,
        title: str = _UN_SET,
        examples: list[Any] = _UN_SET,
    ) -> None: ...

    def update(self: _T, __c: "Config", /) -> _T:
        """Creates a copy of the current Config, updating its attributes with values from another Config.
        This method is useful for combining configurations, inheriting from base configs while overriding selectively.

        Attributes defined in `__c` take precedence over those in `self`, unless explicitly unset.

        Args:
            __c (Config): The Config instance to merge values from.

        Returns:
            Config: A new Config instance with merged values.

        Example:
            >>> base = Config(strict=True, title="Base")
            >>> cfg = Config(title="Custom").update(base)
            >>> assert cfg.strict is True
            >>> assert cfg.title == "Base"
        """

class Field:
    """A class for configuring individual fields of the data model. Inherits attributes from `Config`.

    Attributes:
        init (bool): Enables/disables initialization via the constructor.
        repr (bool): Includes/excludes the attribute in the string representation.
        hash (bool): Determines if the attribute is used in object hashing.
        dict (bool): Specifies if the attribute should be included in `__dict__`.
        json (bool): Specifies if the attribute should be included in JSON serialization.
        kw_only (bool): Allows the attribute to be set only via keyword arguments.
        frozen (bool): Makes the attribute immutable after object creation.
        comparison (bool): Determines if the attribute is considered in equality checks.
        class_lookup (bool): If `True`, looks for the attribute in the class when missing in an instance.
        frozen_type (bool): Prevents modification of the type attributes.
        title (Optional[str]): A title for JSON schema generation.
        examples (Optional[list[Any]]): Example values for JSON schema.
        default (Any): The default value for the field.
        alias (Optional[str]): A custom name for the field used during initialization (`__init__`).
        serialization_alias (Optional[str]): A custom name for the field used during serialization (`as_dict`, `as_json`).
        default_factory (Optional[Callable[[], Any]]): Factory for generating the default value.
        json_schema_extra (Optional[dict[str, Any]]): additional JSON schema data for the schema property.
        auto_alias (bool): Determines whether to generate an alias using `alias_generator` if no manual alias is set.
            - If `True` (default), an alias is automatically generated when no `alias` or `serialization_alias` is defined.
            - If `False`, alias generation is completely disabled, and only manually set aliases are used.
        diff_key (str): the attribute or key name used to compare elements within collections
            (`list`, `set`) during `diff` operations. When set, items will be matched by the value of this field
            instead of by index or full equality. Useful for comparing lists of models or dicts based on unique identifiers like `id`.
        description (str): Human-readable description.
    """

    init: bool
    repr: bool
    hash: bool
    dict: bool
    json: bool
    kw_only: bool
    frozen: bool
    comparison: bool
    class_lookup: bool
    frozen_type: bool
    title: Optional[str]
    examples: Optional[list[Any]]
    default: Any
    auto_alias: bool
    alias: Optional[str]
    serialization_alias: Optional[str]
    default_factory: Optional[Callable[[], Any]]
    json_schema_extra: Optional[Dict[str, Any]]
    description: Optional[str]
    diff_key: Optional[str]

    def __init__(
        self,
        default: Any = _NULL,
        init: bool = True,
        repr: bool = True,
        hash: bool = False,
        dict: bool = True,
        json: bool = True,
        kw_only: bool = False,
        frozen: bool = False,
        comparison: bool = True,
        class_lookup: bool = True,
        frozen_type: bool = False,
        auto_alias: bool = True,
        alias: str = _UN_SET,
        title: str = _UN_SET,
        examples: list[Any] = _UN_SET,
        serialization_alias: str = _UN_SET,
        default_factory: Callable[[], Any] = _UN_SET,
        json_schema_extra: Dict[str, Any] = _UN_SET,
        diff_key: str = _UN_SET,
        description: str = _UN_SET,
    ) -> None: ...

    def update(self: _T, __f: "Field", /) ->_T:
        """Creates a copy of the current Field, updating its attributes with values from another Field.
        This is useful for inheriting base Field settings while overriding specific parameters.

        Fields defined in `__f` take precedence over those in `self`, unless they are unset.

        Args:
            __f (Field): The Field instance to merge values from.

        Returns:
            Field: A new Field instance with combined attributes.

        Example:
            >>> base = Field(title="Base Title", default=1)
            >>> field = Field(default=0).update(base)
            >>> assert field.title == "Base Title"
            >>> assert field.default == 1
        """

def field(
    hint: _T,
    *,
    default: Any = _NULL,
    init: bool = True,
    repr: bool = True,
    hash: bool = False,
    dict: bool = True,
    json: bool = True,
    kw_only: bool = False,
    frozen: bool = False,
    comparison: bool = True,
    class_lookup: bool = True,
    frozen_type: bool = False,
    auto_alias: bool = True,
    alias: str = _UN_SET,
    title: str = _UN_SET,
    examples: list[Any] = _UN_SET,
    serialization_alias: str = _UN_SET,
    default_factory: Callable[[], Any] = _UN_SET,
    json_schema_extra: Dict[str, Any] = _UN_SET,
    diff_key: str = _UN_SET,
    description: str = _UN_SET,
) -> _T:
    return Annotated[  # type: ignore
        hint,
        Field(
            default=default,
            init=init,
            repr=repr,
            hash=hash,
            dict=dict,
            json=json,
            kw_only=kw_only,
            frozen=frozen,
            comparison=comparison,
            class_lookup=class_lookup,
            frozen_type=frozen_type,
            auto_alias=auto_alias,
            alias=alias,
            title=title,
            examples=examples,
            serialization_alias=serialization_alias,
            default_factory=default_factory,
            json_schema_extra=json_schema_extra,
            diff_key=diff_key,
            description=description,
        ),
    ]

def as_dict(
    __obj: Any,
    *,
    as_json: bool = False,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_none: bool = False,
    use_custom: bool = True,
    context: Optional[Any] = None,
) -> Any:
    """Converts the object and all its attachments into a dictionary.
    For custom types, the `__as_dict__` method must be defined

    Args:
        as_json (bool): The output will only contain JSON serializable types.
        by_alias: Whether to use the field's alias in the dictionary key if defined.
        exclude_unset: Whether to exclude fields that have not been explicitly set.
        exclude_none: Whether to exclude fields that have a value of `None`.
        use_custom (bool): Whether to apply user-defined field serializers during conversion.
            This flag affects only subclasses of DataModel. Defaults to `True`.

    Example:
        class Point:
            def __init__(self, x: int, y: int) -> None:
                self.x = x
                self.y = y

            def __as_dict__(self) -> dict[str, int]:
                return {"x": self.x, "y": self.y}
    """

class Schema:
    """
    Representation of the data schema for models.

    Attributes:
        name (str): Field Name.
        type (Any): Data type.
        field (Field): Field Settings.
    """

    name: str
    type: Any
    field: Field

class SerializationInfo:
    """Provides contextual information used during model serialization.

    This object is automatically passed to field serializers and special
    serialization methods (`__as_dict__`, `__as_json__`) when they support an
    extended call signature.

    Usage with @field_serializer:
        If a serializer function defined with @field_serializer has three
        positional arguments (e.g., self, value, info), the third argument
        receives a SerializationInfo instance.
        If it has only two arguments, the info object is not passed.

    Usage with `__as_dict__` / `__as_json__`:
        If the special method defined on a type is a Python function and
        accepts two positional arguments, the second argument receives a
        SerializationInfo instance.
        If it accepts only one argument, info is not passed.
        If the method is not a Python function (for example, a built-in or
        C-implemented method), FrostTyping will call it with the default
        number of arguments:
            - one argument for `__as_dict__` and `__as_json__`;
            - two arguments for field serializers.

    Examples:

        Example 1 — Using SerializationInfo in a field serializer:
            ```
            from frost_typing import ValidModel, field_serializer, SerializationInfo

            class User(ValidModel):
                id: int
                created_at: datetime

                @field_serializer("created_at")
                def serialize_created_at(self, value, info: SerializationInfo) -> Union[str, int]:
                    if info.context and info.context.get("format") == "timestamp":
                        return int(value.timestamp())
                    return value.isoformat()
            ```

        Example 2 — Using `__as_dict__` in a model:
            ```
            class User(ValidModel):
                id: int
                name: str

                def __as_dict__(self, info: SerializationInfo) -> dict[str, Any]:
                    return {
                        "id": self.id,
                        "name": self.name.upper() if info.context.get("upper") else self.name
                    }
            ```

        Example 3 — Defining `__as_json__` on a custom type:
            ```
            class Point:
                def __init__(self, x: float, y: float):
                    self.x = x
                    self.y = y

                def __as_json__(self, info: SerializationInfo):
                    if info.context and info.context.get("compact"):
                        return [self.x, self.y]
                    return {"x": self.x, "y": self.y}

            # FrostTyping will automatically call Point.__as_json__
            # when serializing objects containing this type.
            ```

    Attributes:
        context (Optional[Any]):
            Custom user context provided during serialization.
        exclude_unset (bool):
            Whether to exclude fields that were not explicitly set.
        exclude_none (bool):
            Whether to exclude fields whose value is None.
        use_custom (bool):
            Whether to use custom field serializers defined via @field_serializer.
        by_alias (bool):
            Whether to serialize field names using their defined aliases.
    """

    def __new__(
        cls: Type[_T],
        context: Optional[Any] = None,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        use_custom: bool = True,
        by_alias: bool = True
        ) -> _T:
        ...

    def __init__(
        self,
        context: Optional[Any] = None,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        use_custom: bool = True,
        by_alias: bool = True
        ) -> None:
        ...

    @property
    def context(self) -> Optional[Any]: ...
    @property
    def exclude_unset(self) -> bool: ...
    @property
    def exclude_none(self) -> bool: ...
    @property
    def use_custom(self) -> bool: ...
    @property
    def by_alias(self) -> bool: ...

class MetaModel(ABCMeta):

    __schemas__: tuple[Schema, ...]
    __slots_offset__: int

    def json_schema(cls) -> dict[str, Any]:
        """Returns the JSON schema for the model."""

# @dataclass_transform(field_specifiers=(Field,))
class DataModel(metaclass=MetaModel):
    """Base class for data models with serialization support.
    Provides structured data handling, serialization, and comparison capabilities.
    """

    __config__: ClassVar[Config] = Config()
    """Configuration settings for the data model."""

    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

    def __post_init__(self, *args, **kwargs) -> None:
        """Hook method intended for overriding.
        Called after `__init__` to allow additional initialization logic.
        """

    def __setstate__(self, state: dict[str, Any]) -> None: ...
    def __getstate__(self) -> dict[str, Any]: ...
    def __getitem__(self, name: str) -> Any: ...
    def __repr__(self) -> str: ...
    def __hash__(self) -> int: ...
    def __eq__(self, obj: Any) -> bool: ...
    def __ne__(self, obj: Any) -> bool: ...
    def __lt__(self, obj: Any) -> bool: ...
    def __gt__(self, obj: Any) -> bool: ...
    def __le__(self, obj: Any) -> bool: ...
    def __ge__(self, obj: Any) -> bool: ...

    def __as_dict__(self, info: SerializationInfo = _UN_SET) -> dict[str, Any]:
        """Converts the object and its nested structures into a dictionary.

        This method provides a customizable way to serialize an object into a dictionary.
        Unlike `as_dict`, which is a public API, `__as_dict__` is intended for internal
        use and can be **redefined** to alter the dictionary representation.

        **Performance Note:**
        It is recommended to keep the default implementation whenever possible,
        as it uses optimized attribute access, significantly improving conversion speed.

        Returns:
            dict[str, Any]: A dictionary representation of the object.

        Example:
            ```python
            class Point(DataModel):
                x: int
                y: int

                def __as_dict__(self) -> dict[str, int]:
                    return {"x": self.x, "y": self.y, "total": self.x + self.y}

            point = Point(x=3, y=4)
            print(point.as_dict())
            # {'x': 3, 'y': 4, 'total': 7}
            ```
        """

    def __as_json__(self, info: SerializationInfo = _UN_SET) -> dict[str, Any]:
        """Converts the object into a JSON-serializable structure.

        This method can be overridden to customize how the object
        is represented in JSON format.

        **Note:**
        The default implementation provides **optimized attribute access**,
        significantly improving serialization performance.

        Returns:
            Any: A JSON-serializable representation of the object.

        Example:
            ```python
            class Point(DataModel):
                x: int
                y: int

                def __as_json__(self) -> dict[str, int]:
                    return {"x": self.x, "y": self.y, "total": self.x + self.y}

            point = Point(0, 0)
            print(point.as_json())
            # b'{"x":0,"y":0,"total":0}'
            ```
        """

    def __copy__(self: _T) -> _T:
        """Creates a complete copy of the object.

        This method can be overridden to implement custom copying behavior.
        By default, the built-in implementation efficiently copies the object's attributes
        and **also copies `__dict__`** if `__slots__ = ("__dict__",)` is used.

        **Performance Considerations:**
        - The default implementation uses **low-level copying**, which is significantly faster.
        - Overriding this method should be done **only when necessary**,
          as it may introduce additional overhead.

        **Returns:**
            _T: A new object that is a deep-copied of the original.

        **Example:**
            ```python
            class User(DataModel):
                user_id: int
                name: str

                def __copy__(self: "User") -> "User":
                    return type(self)(user_id=self.user_id + 1, name=f"copy_{self.name}")

            user = User(0, "Frostic")
            new_user = user.copy()  # User(user_id=1, name='copy_Frostic')
            ```
        """

    @classmethod
    def keys(cls) -> list[str]:
        """Returns a list of attributes"""

    @classmethod
    def json_schema(cls) -> dict[str, Any]:
        """Generates and returns a JSON schema for the model.
        Example:
            class User(DataModel):
                user_id: int
                name: str

            user = User(0, "Frostic")
            schema = user.json_schema()
            # {
            #     "type": "object",
            #     "required": ["user_id", "name"],
            #     "properties": {
            #         "user_id": {
            #             "type": "integer",
            #             "title": "User_Id",
            #         },
            #         "name": {
            #             "type": "string",
            #             "title": "Name",
            #         },
            #     },
            #     "title": "User",
            # }
        """

    @classmethod
    def from_json(cls: Type[_T], obj: UnionString, **redefinition: Any) -> _T:
        """
        Deserializes an object from JSON data.
        Example:
            class User(DataModel):
                user_id: int
                name: str

            user = User.from_json(b'{"name": "Frostic"}', user_id=1)
            user  # User(user_id=1, name='Frostic')
        Similarly:
            class User(DataModel):
                user_id: int
                name: str

            data = loads(b'{"name": "Frostic"}')
            data.update({"user_id": 1})
            user = User(**data)
            user  # User(user_id=1, name='Frostic')
        """

    def copy(self: _T, **update: Any) -> _T:
        """Performs a deep-copied of the object.

        This method calls `__copy__`, which can be overridden
        to customize the copying behavior.
        The copying process happens **without invoking the constructor**,
        ensuring high performance.

        **Implementation Details:**
        - If the object has a `__dict__`, it is copied at a low level.
        - The standard implementation provides **optimized copying**
          by bypassing unnecessary overhead.

        **Note:**
        Overriding `__copy__` allows customizing how the object is copied,
        but it is recommended to keep performance considerations in mind.

        Returns:
            _T: A new object that is a deep-copied of the original.

        Example:
            ```python
            class Point(DataModel):
                x: int
                y: int

                def __copy__(self) -> "Point":
                    return Point(self.x, self.y)

            point1 = Point(1, 2)
            point2 = point1.copy()

            print(point1 is point2)  # False
            print(point2.x, point2.y)  # 1 2
            ```
        """

    def as_json(
        self,
        *,
        include: Optional[set[str]] = None,
        exclude: Optional[set[str]] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        use_custom: bool = True,
        str_unknown: bool = False,
        context: Optional[Any] = None,
    ) -> bytes:
        """Serializes the object into a JSON-encoded byte string.

        This is the public API for JSON serialization.
        If you need to customize how the object is converted to JSON,
        consider overriding the `__as_json__` method.

        **Note:**
        This method automatically calls `__as_json__`, ensuring that custom
        serialization logic is respected when the object is nested.

        Args:
            include (Optional[set[str]]): A set of field names to include in the output.
                If `None`, all fields are included unless explicitly excluded.
            exclude (Optional[set[str]]): A set of field names to exclude from the output.
                If `None`, no fields are excluded.
            by_alias (bool): Whether to use field aliases as dictionary keys if defined.
                Defaults to `True`.
            exclude_unset (bool): Whether to exclude fields that have not been explicitly set.
                Defaults to `False`.
            exclude_none (bool): Whether to exclude fields that have a value of `None`.
                Defaults to `False`.
            use_custom (bool): Whether to apply user-defined field serializers during conversion.
                This flag affects only subclasses of DataModel. Defaults to `True`.
            str_unknown (bool): Whether to convert unknown (non-serializable) values to strings during JSON serialization.
                Defaults to `False`.
        Returns:
            bytes: A JSON-encoded byte string representation of the object.

        Example:
            ```python
            class User(DataModel):
                id: int
                name: str

            user = User(id=42, name="Alice")
            print(user.as_json())
            # b'{"user_id":42,"username":"Alice"}'
            ```
        """

    def as_dict(
        self,
        *,
        as_json: bool = False,
        include: Optional[set[str]] = None,
        exclude: Optional[set[str]] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_none: bool = False,
        use_custom: bool = True,
        context: Optional[Any] = None,
    ) -> dict[str, Any]:
        """Convert the model instance into a dictionary.
        This method serializes the model into a dictionary while allowing customization
        through various filtering options. The `include` and `exclude` parameters apply
        **only to the current model level** and do not propagate recursively.

        To customize dictionary serialization, it is recommended to override `__as_dict__`,
        as this method will be used when the object is nested inside another model.

        Args:
            as_json (bool): The output will only contain JSON serializable types.
            include (Optional[set[str]]): A set of field names to include in the output.
                If `None`, all fields are included (unless excluded explicitly).
            exclude (Optional[set[str]]): A set of field names to exclude from the output.
                If `None`, no fields are excluded.
            by_alias (bool): Whether to use the field's alias as the dictionary key
                if an alias is defined. Defaults to `True`.
            exclude_unset (bool): Whether to exclude fields that have not been explicitly set.
                Defaults to `False`.
            exclude_none (bool): Whether to exclude fields that have a value of `None`.
                Defaults to `False`.
            use_custom (bool): Whether to apply user-defined field serializers during conversion.
                This flag affects only subclasses of DataModel. Defaults to `True`.

        Returns:
            dict[str, Any]: A dictionary representation of the model instance.

        Example:
            ```python
            class User(DataModel):
                id: int
                name: str
                age: Optional[int] = None

            user = User(id=1, name="Alice")
            print(user.as_dict())
            # {'id': 1, 'name': 'Alice', 'age': None}

            print(user.as_dict(exclude_none=True))
            # {'id': 1, 'name': 'Alice'}

            print(user.as_dict(include={"id"}))
            # {'id': 1}
            ```
        """

    @classmethod
    def from_attributes(cls: Type[_T], __obj: Any, /) -> _T:
        """Create a model instance from an object with matching attributes.

        This method initializes a new instance of the model by extracting attributes
        from the given object and mapping them to the model's fields.

        Args:
            obj (Any): An object containing attributes that match the model's fields.

        Returns:
            An instance of the model populated with values from the given object.

        Example:
            ```python
            class User(DataModel):
                id: int
                name: str

            class ExternalUser:
                def __init__(self):
                    self.id = 1
                    self.name = "Alice"

            external_user = ExternalUser()
            user = User.from_attributes(external_user)
            print(user)  # User(id=1, name="Alice")
            ```
        """

    @classmethod
    def from_db_row(cls: Type[_T], kwnames: tuple[str, ...], args: Iterable[Any], /) -> _T:
        """A more efficient way to create a model instance from a database row, bypassing intermediate `dict` creation.

        This method is functionally equivalent to `Model(**dict(zip(kwnames, args)))`,
        but with significantly lower memory overhead and better performance
        (up to 3× faster in benchmarks).

        Intended for use with database drivers that return rows as value tuples
        along with column names (e.g., asyncpg, psycopg, sqlite, etc.).

        **Args**:
            kwnames: A tuple of field names corresponding to the values.
            args: A Iterable of values in the same order as `kwnames`.

        **Returns**:
            A new instance of the model and with minimal memory allocations.

        **Raises**:
            TypeError: If the lengths of `kwnames` and `args` do not match.

        **Example:**
        ```python
        class User(DataModel):
            id: int
            name: str
            active: bool

        row = (1, "Alice", True)
        columns = ("id", "name", "active")
        user = User.from_db_row(columns, row)
        user # User(id=1, name="Alice", active=True)
        ```
        """

def json_schema(__obj: Any, /) -> dict[str, Any]:
    """Generates and returns a JSON schema for a given annotation.

    This function analyzes the provided annotation (`__obj`) and constructs
    a JSON schema representation that describes its structure, data types,
    and validation constraints.

    **Args:**
        __obj (Any): The annotation or type hint to generate a JSON schema for.

    **Returns:**
        dict[str, Any]: A dictionary representing the JSON schema.

    **Example:**
        ```python
        from typing import List
        from frost_typing import json_schema

        schema = json_schema(List[int])
        print(schema)
        # Output: {'type': 'array', 'items': {'type': 'integer'}}
        ```

    **Note:**
    - It is particularly useful for API specifications, serialization, and documentation.
    """

class field_serializer:
    """A decorator for serializing specific fields in a data model.

    This decorator allows customizing how individual fields are serialized when converting
    the model to a dictionary (`as_dict`) or JSON (`as_json`). It provides control over
    formatting, transformations, and alternative representations.

    Example:
        ```python
        from frost_typing import DataModel, field_serializer

        class Model(DataModel):
            timestamp: datetime

            @field_serializer("timestamp")
            def serialize_timestamp(self, value: datetime) -> str:
                return value.isoformat()

        model = Model(timestamp=datetime(2024, 3, 3, 14, 30))
        assert model.as_dict() == {"timestamp": "2024-03-03T14:30:00"}
        ```

    Attributes:
        field (str): The primary field to be serialized.
        fields (tuple[str, ...]): Additional fields that the serializer should handle.
    """

    def __new__(cls, field: str, /, *fields: str):
        """Creates a new serializer for the specified field(s)."""

    def __get__(self, obj: Any, type: Optional[Type[Any]] = None) -> Callable[..., Any]: ...

    def __set_name__(self, owner: Type[_DataModel], name: str) -> None:
        """Registers the serializer within the data model class.
        Note:
            The `owner` class must inherit from `DataModel`.
        """

    def __call__(self: _T, func: Union[Callable[[_DataModel, Any], Any], Callable[[_DataModel, Any, SerializationInfo], Any]]) -> _T:
        """Registers the serialization function for the specified field(s).
        Warning:
            If `field_serializer` is applied to a non-existent field, an exception will be raised.
        """

class _computed_field(Generic[_DataModel, _V]):
    """Represents a computed field for a data model with caching.

    A computed field is a read-only property that is dynamically calculated
    based on other fields in the model. The computed value is **cached**
    after the first access to avoid redundant recalculations.

    Supported `Field` parameters:
        - "frozen"
        - "repr"
        - "hash"
        - "dict"
        - "json"
        - "title"
        - "examples"
        - "json_schema_extra"

    Fixed parameters:
        - `frozen_type=True`

    **Attributes:**
        __func__ (Callable[[Any], Any]): The function that computes the field's value.
        field (Field): Field metadata for serialization and schema generation.

    **Methods:**
        - `__call__(func)`: Registers the function that defines the computed field.
        - `__get__(instance, owner)`: Returns the cached value or computes and caches it.

    **Caching Behavior (cache=True):**
        - The first time the field is accessed, it is computed and stored.
        - Subsequent accesses return the cached value without recomputation.
        - If `frozen=False`, the computed field becomes **resettable** — its cache can be cleared manually using `del`,
          but **only after** the value has already been computed (i.e. the attribute was accessed at least once).


    **Example:**
        ```python
        from frost_typing import computed_field, DataModel, Field

        class User(DataModel):
            first_name: str
            last_name: str

            @computed_field(field=Field(frozen=False))
            def full_name(self) -> str:
                print("Computing full_name...")  # Debug log
                return f"{self.first_name} {self.last_name}"

        user = User(first_name="John", last_name="Doe")
        print(user.full_name)  # "Computing full_name..." -> "John Doe"
        print(user.full_name)  # Cached, no recomputation -> "John Doe"

        # Attempting to assign raises an AttributeError
        try:
            user.full_name = "Jane Doe"
        except AttributeError as e:
            print(e)  # "'User' object attribute 'full_name' is read-only"

        del user.full_name     # Reset the cache (only allowed after it was computed)
        print(user.full_name)  # "Computing full_name..." -> "John Doe"
        ```
    """
    field: Field
    cache: bool

    @property
    def __func__(self) -> Callable[[_DataModel], _V]: ...
    @overload
    def __get__(self: _T, instance: None, owner: Type[_DataModel]) -> _T: ...
    @overload
    def __get__(self, instance: _DataModel, owner: Type[_DataModel]) -> _V: ...

@overload
def computed_field(__callable: Callable[[_DataModel], _V]) -> _computed_field[_DataModel, _V]:
    """Decorator for defining computed fields in a data model with caching.

    A computed field is a property that dynamically derives its value
    based on other fields without storing any data initially.
    The computed value is **cached** after the first access.

    **Usage:**
        - When used without arguments, it directly registers the function.
        - When used with `field` metadata, it returns a decorator.

    **Example (Basic Usage):**
        ```python
        class Product(DataModel):
            price: float
            tax: float

            @computed_field
            def price_with_tax(self) -> float:
                print("Computing price_with_tax...")
                return self.price * (1 + self.tax)

        product = Product(price=100, tax=0.2)
        print(product.price_with_tax)  # "Computing price_with_tax..." -> 120.0
        print(product.price_with_tax)  # Cached, no recomputation -> 120.0
        ```

    **Example (With Field Metadata):**
        ```python
        class Order(DataModel):
            total: float

            @computed_field(field=Field(title="Total with discount"))
            def discounted_total(self) -> float:
                return self.total * 0.9
        ```

    **Returns:**
        `_computed_field`: A descriptor for the computed field.
    """

@overload
def computed_field(*, field: Field = Field(frozen_type=True, init=False, frozen=True, class_lookup=False), cache: bool = True) -> Callable[[Callable[[_DataModel], _V]], _computed_field[_DataModel, _V]]:
    """Decorator for defining computed fields with additional metadata and caching.

    **Args:**
        field (Field): Field metadata (only specific options are supported).
        cache (bool, default=True): If True, the computed value will be cached per instance.
            Subsequent accesses will return the cached value instead of recomputing it.

    **Example:**
        ```python
        class Item(DataModel):
            price: float

            @computed_field(field=Field(repr=True, title="Final Price"))
            def final_price(self) -> float:
                return self.price * 1.2
        ```
    """

@overload
def computed_field(__callable: Callable[[_DataModel], _V], *, field: Field = Field(frozen_type=True, init=False, frozen=True, class_lookup=False), cache: bool = True) -> _computed_field[_DataModel, _V]:
    """Decorator for defining computed fields in a data model with caching.

    A computed field is a property that dynamically derives its value
    based on other fields without storing any data initially.
    The computed value is **cached** after the first access.

    **Usage:**
        - When used without arguments, it directly registers the function.
        - When used with `field` metadata, it returns a decorator.

    **Example (Basic Usage):**
        ```python
        class Product(DataModel):
            price: float
            tax: float

            @computed_field
            def price_with_tax(self) -> float:
                print("Computing price_with_tax...")
                return self.price * (1 + self.tax)

        product = Product(price=100, tax=0.2)
        print(product.price_with_tax)  # "Computing price_with_tax..." -> 120.0
        print(product.price_with_tax)  # Cached, no recomputation -> 120.0
        ```

    **Example (With Field Metadata):**
        ```python
        class Order(DataModel):
            total: float

            @computed_field(field=Field(title="Total with discount"))
            def discounted_total(self) -> float:
                return self.total * 0.9
        ```

    **Returns:**
        `_computed_field`: A descriptor for the computed field.
    """

# =========================================================================== #
#                                 ValidModel                                  #
# =========================================================================== #
class FrostUserError(TypeError):
    """Exception raised for user errors in type annotations or model definitions.

    This exception is triggered when the user provides incorrect type hints,
    invalid configurations, or other mistakes that prevent proper model behavior.

    Inherits from `TypeError` because most issues involve incorrect types.

    Example:
        ```python
        from frost_typing import ValidModel

        class ExampleModel(ValidModel):
            value: "invalid_type"  # Incorrect annotation

        ExampleModel(value=1)
        # Raises FrostUserError: Unsupported annotation: 'invalid_type'
        ```
   """


class ErrorDetails(TypedDict):
    """
    A structured dictionary representing details of validation errors.

    Attributes:
        type (str): The error type identifier.
        loc (list[Union[str, int]]): The location of the error within the data structure.
        input (Any): The input value that caused the error.
        msg (str): A human-readable error message.
    """

    type: str
    loc: list[Union[str, int]]
    input: Any
    msg: str


@final
class ValidationError(Exception):
    """A special exception that is raised when data validation errors occur.

    Attributes:
        type (str): The error type identifier.
        loc (list[Union[str, int]]): The location of the error within the data structure.
        input_value (Any): The input value that caused the error.
        msg (str): A human-readable error message.
    """

    next_error: Optional["ValidationError"]
    loc: list[Union[str, int]]
    input_value: Any
    title: str
    type: str
    msg: str

    def __new__(cls, loc: list[Union[str, int]], input_value: Any, type: str, msg: str, title: str, next_error: "ValidationError" = _UN_SET) -> "ValidationError": ...
    def errors(self) -> list[ErrorDetails]: ...

    def as_json(self) -> bytes:
        """Returns a list[ErrorDetails] in JSON format."""

@final
class TypeAdapter(Generic[_T]):
    """A validator class for validating model data.

    Methods:
        validate: Calls the validator to validate the object.
        from_json: Deserializes an object from JSON and validates it.
    """

    def __new__(cls, __hint: _T, /) -> "TypeAdapter[_T]":
        """Creates a validator based on the annotation."""

    def validate(self, __obj: Any, /) -> _T:
        """Validates the object. In case of an error, it causes a ValidationError."""

    def from_json(self, __obj: UnionString, /) -> _T:
        """Deserializes and validates an object from a JSON string.
        In case of an error, it causes a ValidationError.
        """

class ValidSchema(Schema):
    validator: TypeAdapter


class ContextManager(Generic[_M]):
    """Validation context for generic models.

    This internal object provides access to the current validation context used
    during `__frost_validate__` execution. It links generic type variables (`TypeVar`)
    to their concrete types and holds all relevant metadata required for accurate
    validation of generic models.

    Attributes:
        __gtypes__ (tuple[TypeVar, ...]):
            A tuple of type variables as declared in the model, e.g., (T, U).

        __args__ (tuple[Any, ...]):
            A tuple of actual types passed into the model, e.g., (int, str) for `Model[int, str]`.

        __origin__ (Type[_M]):
            The original generic class before applying type arguments,
            e.g., `Model` in `Model[int]`.

    Methods:
        __getitem__(key: TypeVar) -> TypeAdapter:
            Return the corresponding TypeAdapter for a given TypeVar based on the current context.
    """

    __gtypes__: tuple[TypeVar, ...]
    __args__: tuple[Any, ...]
    __origin__: Type[_M]

    def __getitem__(self, key: TypeVar) -> TypeAdapter: ...
    def construct(self, *args: Any, **kwargs: Any) -> _M:
        """Proxy to `_M.construct`. Creates an instance of the generic model without full validation."""

    def from_attributes(self, obj: Union[dict[str, Any], Any]) -> _M:
        """Proxy to `_M.from_attributes`. Builds a model instance from a dictionary or arbitrary object."""

    def from_json(self, obj: UnionString, **redefinition: Any) -> _M:
        """Proxy to `_M.from_json`. Parses the model from a JSON string with optional overrides."""

    def from_db_row(self, kwnames: tuple[str, ...], args: Iterable[Any], /) -> _M:
        """Proxy to `_M.from_db_row`. Parses the model from database row columns and values."""

    def __frost_validate__(self, val: Any, context_manager: "ContextManager[_T]") -> _T:
        """Proxy to `_M.__frost_validate__`. Validates or converts an arbitrary input using the model logic."""

    def json_schema(self) -> dict[str, Any]:
        """Proxy to `_M.json_schema`. Returns the JSON Schema representation of the model."""


class _ContextProperty:
    @overload
    def __get__(self, instance: None, owner: Type[_M]) -> "ContextManager[_M]": ...
    @overload
    def __get__(self, instance: _M, owner: Type[Any]) -> "ContextManager[_M]": ...
    def __set__(self, instance: Any, value: ContextManager[_M]) -> NoReturn:
        raise AttributeError(f"attribute '__context__' of '{type(instance).__name__}' objects is not writable")


class MetaValidModel(MetaModel):
    __schemas__: tuple[ValidSchema, ...]  # type: ignore


# @dataclass_transform(kw_only_default=True, field_specifiers=(Field,))
class ValidModel(DataModel, metaclass=MetaValidModel):
    """A data validation model that ensures all provided data is properly validated.

    This class extends `DataModel` and performs strict validation of input data, ensuring that
    all fields conform to their expected types and constraints.

    Initialization:
        - Can be initialized with a dictionary (`data: dict[str, Any]`).
        - Can be initialized with keyword arguments (`**kwargs`).
        - Can be initialized with an arbitrary object (`obj: Any`), using `from_attributes`.

    Methods:
        construct:
            Creates an instance of the model with validated data. Default values are applied,
            but no additional validation is performed.

        __frost_validate__:
            A custom validation method that defines how an instance should be created from
            an arbitrary value. This method enables conversion logic and can be overridden
            to handle specific cases.

    Note:
        - `construct` should be used when creating instances without full validation.
        - Overriding `__frost_validate__` allows for custom parsing and conversion logic.
    """
    __config__: ClassVar[Config] = Config(fail_on_extra_init=False, kw_only=True)
    __context__: _ContextProperty

    @overload
    def __init__(self, data: dict[str, Any]) -> None: ...
    @overload
    def __init__(self, **kwargs: Any) -> None: ...

    @overload
    def __init__(self, obj: Any) -> None:
        """from_attributes will be used."""

    @classmethod
    def construct(cls: Type[_T], *args: Any, **kwargs: Any) -> _T:
        """Creates a new instance of the model with pre-validated data.

        Unlike the standard initialization, this method does not perform additional validation.

        This method is useful when working with already validated data, where performance is a priority.

        Returns:
            A new instance of the model with validated data.

        Note:
            - Fields are not revalidated; the provided data is assumed to be correct.

        Example:
            ```python
            from frost_typing import ValidModel

            class User(ValidModel):
                id: int
                name: str

            data = {"id": 1, "name": "Frostic"}
            user = User.construct(**data)

            print(user.id)   # 1
            print(user.name) # "Frostic"
            ```
        """

    @classmethod
    def __frost_validate__(cls: Type[_T], val: Any, context_manager: ContextManager[_T]) -> _T:
        """Validation hook invoked when the model is used as a nested field inside another model.

        This method is automatically called by the FrostTyping validation engine **only** when the
        current class is a nested field within a parent `ValidModel`. It is not triggered during direct
        instantiation (e.g., `User(id=1)`), and is primarily intended to handle transformation or
        pre-validation logic when parsing arbitrary input data into a valid model instance.

        The default implementation delegates to `cls(val)`, assuming the input is already a dictionary
        with valid types or an instance of the model itself.

        This method can be overridden to:
          - Apply pre-validation rules before standard field checks.
          - Handle polymorphic behavior, discriminators, or dynamic schema resolution.

        Args:
            val: The input value to be transformed into a model instance. Usually a `dict`, but can be
                 any type depending on the context (e.g., string, int, etc. for custom coercion).
            context_manager: Internal state tracker used during recursive validation. It provides
                             access to path tracking, error aggregation, and type override logic.

        Returns:
            An instance of the model, fully validated.

        Example:
            ```python
            from frost_typing import ValidModel, ContextManager

            class User(ValidModel):
                id: int
                name: str

                @classmethod
                def __frost_validate__(cls, val: Any, context_manager: ContextManager) -> "User":
                    # Apply custom transformation before validation
                    if isinstance(val, str):
                        val = {"id": int(val), "name": "Unknown"}
                    return super().__frost_validate__(val, context_manager)

            class Post(ValidModel):
                title: str
                author: User  # `User.__frost_validate__` will be called during nested validation
            ```

        Notes:
            - This method is **never called** for top-level model instantiation.
            - Use `super().__frost_validate__(val, context_manager)` to fallback to the default behavior.
            - Raise `ValueError` for malformed input that cannot be coerced or corrected.
            - Should not perform full validation logic manually — the framework will validate fields after
              instantiation based on the declared schema.
            - If discriminator logic is used, it should be handled here before delegating to `super()`.
        """

    def model_diff(
        self: _T,
        other: _T,
        skip_none: bool = False,
        copy_values: bool = False,
    ) -> dict[str, Any]:
        """Compute a recursive dictionary representing the differences between this model and another.

        Returns a dictionary containing only the fields that have different values in `other` compared to `self`.
        Useful for generating patches or updates compatible with `with_diff()`.

        Parameters:
            other (_T):
                The model instance to compare against.

            skip_none (bool, default=False):
                If True, fields with value None in the diff result will be omitted.

            copy_values (bool, default=False):
                If True, values in the resulting diff dictionary will be deep-copied
                (or copied using a fast copy function), ensuring the returned data is
                independent from the original objects.

        Returns:
            dict[str, Any]:
                A dictionary of fields with updated values, recursively including nested models.

        Notes:
            - Nested ValidModel instances are diffed recursively.
            - Lists and other non-ValidModel collections are compared as whole values.
            - The returned dict is compatible with `with_diff()` for easy model updating.
        """

    def with_diff(self: _T, diff: dict[str, Any], revert: bool = False) -> _T:
        """Recursively updates fields of the model and all nested models in-place.

        - Fields are updated via keyword arguments.
        - Extra fields that are not defined in the model will be ignored.
        - If a field is a nested DataModel, the corresponding value must be a dict.
          In that case, `with_diff` is called recursively on the nested model.

        - revert(bool) Applies a diff to the current model in-place.
            If revert=False (default), the model is updated with new values from the update dictionary.
            If revert=True, the model is reverted to previous values (i.e., values before the diff), effectively undoing the changes.

            Note:
                The update must be produced by model_diff(). Otherwise, the values will be replaced.

        Example:
            ```python
            class Settings(DataModel):
                theme: str

            class User(DataModel):
                name: str
                settings: Settings

            usr = User(name="", settings=Settings(theme="light"))
            usr # User(name='', settings=Settings(theme='light'))
            new = usr.with_diff({"name": ("", "Alice"), settings={"theme": ("light", "dark")}})
            new # User(name='Alice', settings=Settings(theme='dark'))
        """

class ArgsKwargs:
    """A construct used to store arguments and keyword arguments for a function call.
    This data structure is generally used to store information for core schemas associated with functions (like in an arguments schema).
    """

    def __new__(cls: Type[_T], args: tuple[Any, ...], kwargs: Optional[dict[str, Any]] = None) -> _T: ...
    def __init__(self, args: tuple[Any, ...], kwargs: Optional[dict[str, Any]] = None) -> None:
        """Initializes the `ArgsKwargs`.
        Arguments:
            args: The arguments (inherently ordered) for a function call.
            kwargs: The keyword arguments for a function call
        """

    @property
    def args(self) -> tuple[Any]:
        """The arguments (inherently ordered) for a function call."""

    @property
    def kwargs(self) -> Optional[dict[str, Any]]:
        """The keyword arguments for a function call."""

class _validated_func(Generic[_P, _V]):
    """A decorator that validates function arguments and return values.

    This decorator ensures that function inputs match their expected type annotations.
    It automatically converts values where possible and raises a `ValidationError` if
    conversion fails. The return value is also validated.

    Key features:
    - Automatically converts arguments to their expected types.
    - Ensures that the return value matches the declared return type.
    - Converts keyword arguments to positional if applicable.
    - Safely copies mutable default values.

    Example:
        ```python
        @validated_func
        def add(a: int, b: int) -> int:
            return a + b

        assert add("2", "3") == 5  # Automatic type conversion
        assert add(2, 3) == 5
        ```

    Note:
        This decorator provides lightweight validation without significant performance overhead.
    """

    __schemas__: tuple[ValidSchema, ...]
    __func__: Callable[_P, _V]
    fail_on_extra_init: bool
    allow_inf_nan: bool
    num_to_str: bool
    strict: bool

    def __new__(cls: Type[_T], func: Callable[_P, _V]) -> _T: ...

    def __class_getitem__(cls, item: Any) -> "Type[_validated_func]": ...
    def __getitem__(self, key: Any) -> "_validated_func[_P, _V]": ...

    def __call__(self, *args: _P.args, **kwargs: _P.kwargs) -> _V:
        """Calls the decorated function with validated arguments.

        This method ensures that all arguments conform to their expected types.
        If an argument cannot be converted, a `ValidationError` is raised.

        Args:
            *args: Positional arguments to be validated.
            **kwargs: Keyword arguments to be validated.

        Returns:
            The validated return value of the function.

        Example:
            ```python
            @validated_func
            def greet(name: str, age: int) -> str:
                return f"Hello {name}, {age} years old"

            assert greet("Alice", "30") == "Hello Alice, 30 years old"  # String converted to int
            ```
        """

    def from_attributes(self, obj: Union[dict[str, Any], Any]) -> _V:
        """Calls the function using arguments extracted from an object.

        This method is available on functions decorated with `@validated_func`.
        It allows you to call the function by passing an object (e.g. a dictionary
        or a class instance) that contains attributes matching the function’s parameter names.
        All arguments are automatically extracted, type-cast, and validated.

        Args:
            obj (Union[dict[str, Any], Any]): A dictionary or object with attributes matching the function’s parameters.

        Returns:
            The result of calling the function with the extracted arguments.

        Example:
            ```python
            @validated_func
            def create_user(name: str, age: int) -> str:
                return f"{name}, {age} years old"

            class IncomingUser:
                name = "Alice"
                age = 30

            # Using a dictionary
            result = create_user.from_attributes({"name": "Bob", "age": 25})
            print(result)  # "Bob, 25 years old"

            # Using an object with matching attributes
            result = create_user.from_attributes(IncomingUser)
            print(result)  # "Alice, 30 years old"
            ```
        """

    def from_json(self, obj: UnionString, **overload: dict[str, Any]) -> _V:
        """Deserializes function parameters from a JSON string and calls the function.

        This method allows calling the function with arguments extracted from a JSON input.
        Additional parameters can be provided using `overload`, which will override the
        values parsed from JSON.

        Args:
            obj: A JSON string or bytes containing the function's input parameters.
            overload: Additional arguments to override JSON values.

        Returns:
            The validated return value of the function.

        Example:
            ```python
            @validated_func
            def process(name: str, age: int) -> str:
                return f"{name} is {age} years old."

            assert process.from_json('{"name": "Alice", "age": 25}') == "Alice is 25 years old."
            ```

        Note:
            If a required argument is missing in the JSON input, a `ValidationError` is raised.
        """

    def from_db_row(self, kwnames: tuple[str, ...], args: Iterable[Any], /) -> _V:
        """A more efficient function call from a database string, bypassing the intermediate creation of a `dict'.

        This method is functionally equivalent to `func(**dict(zip(kwnames, args)))`,
        but with significantly lower memory overhead and better performance
        (up to 3× faster in benchmarks).

        Intended for use with database drivers that return rows as value tuples
        along with column names (e.g., asyncpg, psycopg, sqlite, etc.).

        **Args**:
            kwnames: A tuple of field names corresponding to the values.
            args: A Iterable of values in the same order as `kwnames`.

        **Returns**:
            The validated return value of the function.

        **Raises**:
            TypeError: If the lengths of `kwnames` and `args` do not match.

        **Example:**
        ```python
        @validated_func
        def greet(name: str, age: int) -> str:
            return f"Hello {name}, {age} years old"

        row = ("Alice", "30")
        columns = ("name", "age")
        assert greet.from_db_row(columns, row) == "Hello Alice, 30 years old"  # String converted to int
        ```
        """

    def json_schema(self) -> dict[str, Any]:
        """Returns a JSON schema representing the function's input parameters.

        This method generates a JSON Schema that describes the expected function arguments.
        It is useful for API documentation, validation, and automatic request parsing.

        Returns:
            A dictionary representing the JSON schema of the function's parameters.

        Example:
            ```python
            @validated_func
            def example(a: int, b: str) -> None:
                pass

            schema = example.json_schema()
            # {'type': 'object', 'properties': {'a': {'type': 'integer'}, 'b': {'type': 'string'}}}
            ```

        Note:
            This schema can be used for automatic validation in web frameworks or API clients.
        """


@overload
def validated_func(func: Callable[_P, _V]) -> _validated_func[_P, _V]:
    """A decorator that validates function arguments and return values.

    This decorator ensures that function inputs match their expected type annotations.
    It automatically converts values where possible and raises a `ValidationError` if
    conversion fails. The return value is also validated.

    Key features:
    - Automatically converts arguments to their expected types.
    - Ensures that the return value matches the declared return type.
    - Converts keyword arguments to positional if applicable.
    - Safely copies mutable default values.
    """

@overload
def validated_func(func: Callable[_P, _V], *, fail_on_extra_init: bool = False, allow_inf_nan: bool = True, num_to_str: bool = False, strict: bool = False) -> _validated_func[_P, _V]:
    """A decorator that validates function arguments and return values.

    This decorator ensures that function inputs match their expected type annotations.
    It automatically converts values where possible and raises a `ValidationError` if
    conversion fails. The return value is also validated.

    Key features:
    - Automatically converts arguments to their expected types.
    - Ensures that the return value matches the declared return type.
    - Converts keyword arguments to positional if applicable.
    - Safely copies mutable default values.

    Arguments:
        fail_on_extra_init (bool):
        - If True, raises TypeError on unexpected keyword arguments.
        - If False, extra arguments are ignored.

        num_to_str (bool): If `True`, allows numerical values (`int`, `float`) to be assigned to string fields.
            - Automatically converts numbers to strings when assigning them to `str`-typed fields.
            - Useful for handling input where numbers might be provided as raw values instead of strings.

        allow_inf_nan (bool): If `True` (default), allows `inf`, `-inf`, and `nan` as valid float values.
            - If `False`, raises a validation error when encountering such values.

        strict (bool): Enables strict validation mode, where type conversions are not allowed.
            - If `True`, input data must match the expected type exactly.
    """

@overload
def validated_func(*, fail_on_extra_init: bool = False, allow_inf_nan: bool = True, num_to_str: bool = False, strict: bool = False) -> Callable[[Callable[_P, _V]], _validated_func[_P, _V]]:
    """A decorator that validates function arguments and return values.

    This decorator ensures that function inputs match their expected type annotations.
    It automatically converts values where possible and raises a `ValidationError` if
    conversion fails. The return value is also validated.

    Key features:
    - Automatically converts arguments to their expected types.
    - Ensures that the return value matches the declared return type.
    - Converts keyword arguments to positional if applicable.
    - Safely copies mutable default values.

    Arguments:
        fail_on_extra_init (bool):
        - If True, raises TypeError on unexpected keyword arguments.
        - If False, extra arguments are ignored.

        num_to_str (bool): If `True`, allows numerical values (`int`, `float`) to be assigned to string fields.
            - Automatically converts numbers to strings when assigning them to `str`-typed fields.
            - Useful for handling input where numbers might be provided as raw values instead of strings.

        allow_inf_nan (bool): If `True` (default), allows `inf`, `-inf`, and `nan` as valid float values.
            - If `False`, raises a validation error when encountering such values.

        strict (bool): Enables strict validation mode, where type conversions are not allowed.
            - If `True`, input data must match the expected type exactly.
    """

class __field_validator(Generic[_R]):
    """A decorator for custom validation of model fields.

    This decorator allows defining validation functions for specific fields in a model.
    It supports different validation modes and ensures that fields meet custom-defined criteria.

    Example:
        ```python
        from frost_typing import ValidModel, field_validator

        class User(ValidModel):
            age: int

            @field_validator("age", mode="after")
            @classmethod
            def validate_age(cls, value: int) -> int:
                if value < 0:
                    raise ValueError("Age must be non-negative")
                return value


        class Order(ValidModel):
            quantity: int

            @field_validator("quantity", mode="wrap")
            @classmethod
            def validate_quantity(cls, value: int, handler: Callable[[Any], Any]) -> int:
                if isinstance(value, str):
                    raise ValueError("Quantity must be string")

                value = handler(value)
                if value <= 0:
                    raise ValueError("Quantity must be positive")
                return value
        ```

    Note:
        If `field_validator` is applied to a non-existent field, an exception is raised.
    """

    def __new__(cls, field: str, /, *fields: str, mode: FieldValidatorModes = "after"):
        """Creates a new validator for the specified field(s).

        Args:
            field: The primary field to validate.
            *fields: Additional fields to apply validation.
            mode: The validation mode (`"before"`, `"after"`, `"wrap"`).

        Returns:
            An instance of `__field_validator` that applies validation logic.

        Raises:
            ValueError: If the field does not exist in the model.

        Example:
            ```python
            @field_validator("email", mode="before")
            def validate_email(cls, value: str) -> str:
                if "@" not in value:
                    raise ValueError("Invalid email format")
                return value

            @field_validator("name", mode="wrap")
            def validate_name(cls, value: Any, handler: Callable[[Any], Any]) -> str:
                # A place for your code to be validated before type checking
                ...
                res = handler(value)
                ...
                # A place for your code to be validated after type checking
                return res
            ```
        """

    def __get__(self, obj: _T, type: Optional[Type[_T]] = None) -> Callable[..., Any]: ...

    def __set_name__(self, owner: Type[_ValidModel], name: str) -> None:
        """Registers validators in the valid model class.
        Note:
            The 'owner` class should derive from 'ValidModel'.
        Warning:
            If `field_validator` is applied to a non-existent field, an exception will be raised.
        """

    @overload
    def __call__(self, this: Type[_ValidModel], val: Any) -> _R:
        """Provides direct access to the decorated function"""

    @overload
    def __call__(self, this: Type[_ValidModel], val: Any, handler: Callable[[Any], Any]) -> _R:
        """Provides direct access to the decorated function"""

@overload
def field_validator(
    field: str, /, *fields: str, mode: Literal["before", "after"] = "after"
) -> Callable[[Callable[[Type[Any], Any], _R]], __field_validator[_R]]:
    """A decorator for custom validation of model fields.

    This version applies validation **before** the field value is processed.

    Args:
        field: The primary field to validate.
        *fields: Additional fields to apply validation.
        mode: `"before"` (ensures validation happens before assignment).
        mode: `"after"` (ensures validation happens after assignment).

    Important:
        @field_validator must be applied directly to the function, without any additional
        decorators on top (such as @classmethod, @staticmethod, etc.).
        Wrapping it in other decorators will break validator registration.

    Example:
        ```python
        @field_validator("username", mode="before")
        @classmethod
        def validate_username(cls, value: str) -> str:
            if not value:
                raise ValueError("Username cannot be empty")
            return value
        ```
    """

@overload
def field_validator(
    field: str, /, *fields: str, mode: Literal["wrap"]
) -> Callable[[Callable[[Type[Any], Any, Callable[[Any], Any]], _R]], __field_validator[_R]]:
    """A decorator for custom validation of model fields.

    Args:
        field: The primary field to validate.
        *fields: Additional fields to apply validation.
        mode: `"wrap"` (allows you to wrap the check).

    Important:
        @field_validator must be applied directly to the function, without any additional
        decorators on top (such as @classmethod, @staticmethod, etc.).
        Wrapping it in other decorators will break validator registration.

    Example:
        ```python
        @field_validator("username", mode="wrap")
        @classmethod
        def validate_username(cls, value: Any, handler: Callable[[Any], Any]) -> str:
            # Before validation
            res = handler(value)
            # After validation
            return res
        ```
    """

# =========================================================================== #
#                                     JSON                                    #
# =========================================================================== #

def dumps(
    __obj: Any,
    *,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_none: bool = False,
    use_custom: bool = True,
    str_unknown: bool = False,
    context: Optional[Any] = None,
) -> bytes:

    """Serializes the object in bytes of JSON format.

    This function converts a Python object into a JSON-formatted byte string.
    If the object is a custom type, it must implement the `__as_json__` method
    to return a JSON-serializable representation.

    Args:
        __obj: The object to serialize.
        by_alias: Whether to use the field's alias in the dictionary key if defined.
        exclude_unset: Whether to exclude fields that have not been explicitly set.
        exclude_none: Whether to exclude fields that have a value of `None`.
        use_custom (bool): Whether to apply user-defined field serializers during conversion.
            This flag affects only subclasses of DataModel. Defaults to `True`.
        str_unknown (bool): Whether to convert unknown (non-serializable) values to strings during JSON serialization.
            Defaults to `False`.

    Returns:
        bytes: A JSON-formatted byte string representing the object.

    Example:
        ```python
        from frost_typing import dumps

        class CustomType:
            def __init__(self, value: int):
                self.value = value

            def __as_json__(self):
                return {"custom_value": self.value}

        obj = CustomType(42)
        json_data = dumps(obj)
        print(json_data)  # b'{"custom_value": 42}'
        ```

    Note:
        - Objects that define a `__as_json__()` method will use its return value for serialization.
        - The `__as_json__()` method must return a JSON-compatible structure, such as:
          `dict`, `list`, `str`, `int`, `float`, `bool`, `set`, `frozenset`, `bytes`, `bytearray`, `defaultdict`, `UUID`, `Enum` or `None`.
        - Nested custom objects must also implement `__as_json__()`.
    """

def dump(
    __obj: Any,
    fp: BinaryIO,
    *,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_none: bool = False,
    use_custom: bool = True,
    str_unknown: bool = False,
    context: Optional[Any] = None,
) -> None:
    """Serializes a Python object to JSON and writes it to a BinaryIO stream.

    This function behaves similarly to `json.dump`.
    If the object is a custom type, it must implement the `__as_json__` method
    to return a JSON-serializable representation.

    Args:
        __obj: The object to serialize.
        fp: A writable binary stream (e.g. file opened in `'wb'` mode).
        by_alias: Whether to use the field's alias in the dictionary key if defined.
        exclude_unset: Whether to exclude fields that have not been explicitly set.
        exclude_none: Whether to exclude fields that have a value of `None`.
        use_custom (bool): Whether to apply user-defined field serializers during conversion.
            This flag affects only subclasses of DataModel. Defaults to `True`.
        str_unknown (bool): Whether to convert unknown (non-serializable) values to strings during JSON serialization.
            Defaults to `False`.

    Returns:
        None.

    Example:
        ```python
        from frost_typing import dump

        class CustomType:
            def __init__(self, value: int):
                self.value = value

            def __as_json__(self):
                return {"custom_value": self.value}

        obj = CustomType(42)
        with open("output.json", "wb") as f:
            dump(obj, f)

        # output.json will contain: {"custom_value":42}
        ```

    Note:
        - Objects that define a `__as_json__()` method will use its return value for serialization.
        - The `__as_json__()` method must return a JSON-compatible structure, such as:
          `dict`, `list`, `str`, `int`, `float`, `bool`, `set`, `frozenset`, `bytes`, `bytearray`, `defaultdict`, `UUID`, `Enum` or `None`.
        - Nested custom objects must also implement `__as_json__()`.
    """

def loads(__str: UnionString, /) -> Any:
    """Deserializes a JSON-formatted string or bytes into a Python object.

    This function parses a JSON string or byte sequence and converts it into a Python data structure.

    Args:
        __str: A JSON string or `bytes` containing serialized data.

    Returns:
        The deserialized Python object.

    Raises:
        JSONDecodeError: If the input is not a valid JSON format.

    Example:
        ```python
        from frost_typing import loads

        json_data = b'{"name": "Bob", "age": 30}'
        result = loads(json_data)
        print(result)  # {'name': 'Bob', 'age': 30}
        ```
    """

def load(__fp: Union[IO[str], IO[bytes]]) -> Any:
    """Deserializes JSON content read from a file-like object into a Python object.

    This function reads the entire content from the given file-like object,
    which can be opened in text or binary mode, and parses it as JSON.

    Args:
        __fp: A file-like object opened in text mode (`IO[str]`),
              binary mode (`IO[bytes]`), or with a `bytearray` interface (`IO[bytearray]`),
              containing JSON-formatted data.

    Returns:
        The deserialized Python object.

    Raises:
        JSONDecodeError: If the content is not valid JSON.

    Example:
        ```python
        from frost_typing import load

        with open("data.json", "r") as f:
            result = load(f)
        print(result)  # e.g. {'name': 'Bob', 'age': 30}

        import io
        bio = io.BytesIO(b'{"foo": "bar"}')
        result = load(bio)
        print(result)  # {'foo': 'bar'}
        ```
    """

class JsonEncodeError(Exception): ...
class JsonDecodeError(Exception): ...

# =========================================================================== #
#                                ComparisonCons                               #
# =========================================================================== #

class Discriminator:
    """A type helper for resolving Union fields dynamically based on the value of another field.

    This is useful in scenarios where the actual type of a field depends on the value of
    a separate "discriminator" field. The `Discriminator` allows precise type dispatching
    at runtime.

    Args:
        discriminator (str): The name of the field whose value will determine which type to use.
        mapping (dict[Any, Any]): A mapping of discriminator values to concrete types.
        raise_on_missing (bool): Flag to determine whether an exception should be raised if a mapping is missing for a given value.
                                  If set to `True`, a `ValidatioError` will be raised when a value is found in the discriminator field
                                  that does not exist in the `mapping`. If `False`, it will fall back to default behavior (e.g.,
                                  Union validation).

    Example:
        A typical use case is resolving request payloads depending on an operation type:

        ```python
        from enum import Enum
        from frost_typing import ValidModel, Field, Discriminator
        from typing import Union, Annotated

        class OperationType(str, Enum):
            CREATE = "create"
            DELETE = "delete"

        class CreatePayload(ValidModel):
            username: str
            email: str

        class DeletePayload(ValidModel):
            user_id: int

        class Request(ValidModel):
            operation: OperationType
            payload: Annotated[
                Union[CreatePayload, DeletePayload],
                Discriminator(
                    discriminator="operation",
                    mapping={
                        OperationType.CREATE: CreatePayload,
                        OperationType.DELETE: DeletePayload,
                    },
                ),
            ]

        # Usage example
        req = Request(
            operation="create",
            payload={"username": "alice", "email": "alice@example.com"}
        )
        assert isinstance(req.payload, CreatePayload)
        ```

    Note:
        The `Discriminator` can match any value, including Enums, strings, or other objects,
        by directly comparing values in the mapping.
    """

    discriminator: str
    raise_on_missing: bool
    mapping: dict[Any, Any]
    def __new__(cls, discriminator: str, mapping: dict[Any, Any], raise_on_missing: bool = False) -> "Discriminator":
        """Initializes a `Discriminator` instance.
        Args:
            discriminator (str): The field name to be used as the discriminator.
            mapping (dict): A dictionary mapping discriminator values to corresponding types.
            raise_on_missing (bool): Flag indicating whether to raise an exception if the mapping does not contain
                                      a given discriminator value.

        Returns:
            Discriminator: A new `Discriminator` instance with the provided parameters.
        """
    def __init__(self, discriminator: str, mapping: dict[Any, Any], raise_on_missing: bool = False) -> None: ...


class ComparisonConstraints:
    """A class for defining comparison constraints. It sets conditions for attributes
    that must be greater than (`gt`), greater than or equal to (`ge`), less than (`lt`),
    or less than or equal to (`le`).

    This should be used in type annotations with `Annotated` to enforce validation rules
    for data models.

    Constructor Arguments:
        gt (Any, optional): A value that the attribute must be greater than.
        ge (Any, optional): A value that the attribute must be greater than or equal to.
        lt (Any, optional): A value that the attribute must be less than.
        le (Any, optional): A value that the attribute must be less than or equal to.

    Example:
        ```python
        from typing import Annotated
        from frost_typing import ValidModel, ComparisonConstraints

        class Model(ValidModel):
            age: Annotated[int, ComparisonConstraints(gt=18, le=65)]

        model = Model()
        model.age = 20  # Valid value
        model.age = 70  # Error: value exceeds allowed limits (gt=18, le=65)
        ```

    Note:
        - All constraints (`gt`, `ge`, `lt`, `le`) must be applied through `Annotated`.
        - Using these constraints without `Annotated` does not guarantee enforcement during validation.
    """

    gt: Any
    ge: Any
    lt: Any
    le: Any

    def __new__(
        cls: Type[_T],
        gt: Any = None,
        ge: Any = None,
        lt: Any = None,
        le: Any = None,
    ) -> _T: ...

class SequenceConstraints:
    """A class for setting limits on the length of sequences. Defines the minimum and
    maximum length for fields that are sequences (e.g., lists or strings).

    This should be used in type annotations with `Annotated` to enforce validation rules
    for data models.

    Attributes:
        min_length (int, optional): The minimum length of the sequence.
        max_length (int, optional): The maximum length of the sequence.

    Example:
        ```python
        from typing import Annotated
        from frost_typing import ValidModel, SequenceConstraints

        class Model(ValidModel):
            name: Annotated[str, SequenceConstraints(min_length=3, max_length=50)]
            tags: Annotated[list[str], SequenceConstraints(min_length=1, max_length=10)]

        model = Model()
        model.name = "Hi"   # Error: min_length is 3
        model.name = "Hello"  # Valid
        model.tags = ["tag1"]  # Valid
        ```
     """

    min_length: int
    max_length: int

    def __new__(
        cls: Type[_T],
        min_length: int = -1,
        max_length: int = -1,
    ) -> _T: ...

class StringConstraints:
    """A class for setting constraints for string data.

    This should be used in type annotations with `Annotated` to enforce validation rules
    for string fields in data models.

    Attributes:
        strip_whitespace (bool): Whether to remove spaces from the beginning and end of the string.
        to_upper (bool): Whether to convert the string to uppercase.
        to_lower (bool): Whether to convert the string to lowercase.
        min_length (int, optional): The minimum length of the string.
        max_length (int, optional): The maximum length of the string.
        pattern (str, optional): A regular expression pattern for validating the string.
        is_printable (bool): Whether the string must contain only printable characters.
        is_ascii (bool): Should the string be ASCII.

    Example:
        ```python
        from typing import Annotated
        from frost_typing import ValidModel, StringConstraints

        class Model(ValidModel):
            username: Annotated[str, StringConstraints(min_length=3, max_length=20, strip_whitespace=True)]
            email: Annotated[str, StringConstraints(pattern="^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$")]

        Model(username="  user  ", email="test@mail.ru")
        model.username                 # Becomes "user" after stripping whitespace
        model.email = "invalid-email"  # Error: does not match pattern
        ```

    Note:
        - All constraints (`min_length`, `max_length`, `pattern`, etc.) must be applied through `Annotated`.
        - Using these constraints without `Annotated` does not guarantee enforcement during validation.
    """

    strip_whitespace: bool
    is_printable: bool
    to_upper: bool
    to_lower: bool
    is_ascii: bool
    min_length: int
    max_length: int
    pattern: Optional[str]

    def __new__(
        cls: Type[_T],
        strip_whitespace: bool = False,
        to_upper: bool = False,
        to_lower: bool = False,
        min_length: int = -1,
        max_length: int = -1,
        pattern: str = _UN_SET,
        is_printable: bool = False,
        is_ascii: bool = False,
    ) -> _T: ...


class __DateTimeConstraints:
    """Internal class used to represent datetime-related validation constraints
    for use with `Annotated`.

    These constraints enforce:
    - Timezone awareness (`tzinfo`) for `datetime` objects.
    - Temporal comparison against the current datetime (past or future).

    They are applied via `Annotated[...]` in a `ValidModel` and will raise
    a `ValidationError` during assignment or initialization if violated.

    Example constraints:
    - `AwareDatetime` ensures the value has `tzinfo`.
    - `NaiveDatetime` ensures the value has no `tzinfo`.
    - `FutureDatetime` requires the value to be in the future.
    - `PastDatetime` requires the value to be in the past.

    Example:
        ```python
            from datetime import datetime, timedelta
            from typing import Annotated
            from frost_typing import ValidModel
            from frost_typing.constraints import (
                AwareDatetime,
                NaiveDatetime,
                FutureDatetime,
                PastDatetime,
            )

            class EventModel(ValidModel):
                starts_at: Annotated[datetime, AwareDatetime]
                created_at: Annotated[datetime, NaiveDatetime]
                registration_deadline: Annotated[datetime, FutureDatetime]
                ended_at: Annotated[datetime, PastDatetime]

            # Example instance creation:
            event = EventModel(
                starts_at=datetime.now().astimezone(),  # must be timezone-aware
                created_at=datetime.utcnow(),           # must be naive
                registration_deadline=datetime.now().astimezone() + timedelta(hours=1),
                ended_at=datetime.now().astimezone() - timedelta(days=1)
            )
        ```
    """

#: Annotation that ensures `datetime` object is timezone-aware.
#: Validation will fail if `tzinfo` is None.
AwareDatetime = __DateTimeConstraints()

#: Annotation that ensures `datetime` object is naive (not timezone-aware).
#: Validation will fail if `tzinfo` is not None.
NaiveDatetime = __DateTimeConstraints()

#: Annotation that ensures the datetime is in the future (compared to `datetime.now()`).
#: Supports both `datetime`  objects.
FutureDatetime = __DateTimeConstraints()

#: Annotation that ensures the datetime is in the past (compared to `datetime.now()`).
#: Supports both `datetime` objects.
PastDatetime = __DateTimeConstraints()

def con_comparison(hint: _T, *, gt: Any = None, ge: Any = None, lt: Any = None, le: Any = None) -> _T:
    """Creates an annotated constraint for comparing values.

    This function wraps a type with `Annotated`, enforcing constraints such as greater than,
    greater than or equal to, less than, or less than or equal to.

    Arguments:
        hint (_T): The data type to which the restrictions apply.
        gt (Any, optional): The "greater than" constraint.
        ge (Any, optional): The "greater than or equal to" constraint.
        lt (Any, optional): The "less than" constraint.
        le (Any, optional): The "less than or equal to" constraint.

    Example:
        ```python
        from frost_typing import ValidModel, con_comparison

        class Model(ValidModel):
            age: con_comparison(int, gt=18, le=65)

        model = Model()
        model.age = 20  # Valid value
        model.age = 70  # Error: value exceeds allowed limits (gt=18, le=65)
        ```

    Note:
        - Constraints must be applied through `Annotated` for proper validation.
    """
    return Annotated[hint, ComparisonConstraints(gt=gt, ge=ge, lt=lt, le=le)]  # type: ignore[return-value]

def con_sequence(hint: _T, *, min_length: int = -1, max_length: int = -1) -> _T:
    """Creates an annotated constraint for sequences (e.g., lists or strings).

    This function ensures that a sequence meets the specified minimum and maximum length constraints.

    Arguments:
        hint (_T): The data type to which the restrictions apply.
        min_length (int, optional): The minimum length of the sequence.
        max_length (int, optional): The maximum length of the sequence.

    Example:
        ```python
        from frost_typing import ValidModel, con_sequence

        class Model(ValidModel):
            name: con_sequence(str, min_length=3, max_length=50)
            tags: con_sequence(list[str], min_length=1, max_length=10)

        model = Model()
        model.name = "Hi"   # Error: min_length is 3
        model.name = "Hello"  # Valid
        model.tags = ["tag1"]  # Valid
        ```

    Note:
        - Constraints must be applied through `Annotated` for proper validation.
    """
    return Annotated[hint, SequenceConstraints(min_length=min_length, max_length=max_length)]  # type: ignore[return-value]

def con_string(
    hint: Type[_S],
    *,
    strip_whitespace: bool = False,
    to_upper: bool = False,
    to_lower: bool = False,
    min_length: int = -1,
    max_length: int = -1,
    pattern: str = _UN_SET,
    is_printable: bool = False,
    is_ascii: bool = False,
) -> Type[_S]:
    """
    Creates an annotated constraint for strings.

    This function applies constraints to string values, including automatic case conversion,
    whitespace stripping, length constraints, and regex pattern validation.

    Arguments:
        hint (Type[_S]): The data type to which the restrictions apply (must be `str` or a subtype).
        strip_whitespace (bool): Whether to remove spaces from the beginning and end of the string.
        to_upper (bool): Whether to convert the string to uppercase.
        to_lower (bool): Whether to convert the string to lowercase.
        min_length (int, optional): The minimum length of the string.
        max_length (int, optional): The maximum length of the string.
        pattern (str, optional): A regular expression pattern for validating the string.
        is_printable (bool): Whether the string must contain only printable characters.
        is_ascii (bool): Should the string be ASCII.

    Example:
        ```python
        from frost_typing import ValidModel, StringConstraints

        class Model(ValidModel):
            username: con_string(str, min_length=3, max_length=20, strip_whitespace=True)
            email: con_string(str, pattern="^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$")

        model = Model(username="  user  ", email="test@mail.ru")
        model.username                 # Becomes "user" after stripping whitespace
        model.email = "invalid-email"  # Error: does not match pattern
        ```

    Note:
        - Constraints must be applied through `Annotated` for proper validation.
    """
    return Annotated[  # type: ignore[return-value]
        hint,
        StringConstraints(
            strip_whitespace=strip_whitespace,
            is_printable=is_printable,
            min_length=min_length,
            max_length=max_length,
            to_upper=to_upper,
            to_lower=to_lower,
            is_ascii=is_ascii,
            pattern=pattern,
        ),
    ]

# =========================================================================== #
#                                   DateTime                                  #
# =========================================================================== #

def parse_date(__obj: UnionString, /) -> date:
    """Parses a ISO string into a `date` object.
    The function accepts various date formats and converts them into a `datetime.date` object.
    Example:
        assert parse_date("2024-02-05") == date(2024, 2, 5)
    """

def parse_time(__obj: UnionString, /) -> time:
    """Parses a ISO string into a `time` object.
    The function supports different time formats and converts them into a `datetime.time` object.

    Example:
        assert parse_time("14:30:00") == time(14, 30, 0)
        assert parse_time("2:30Z") == time(2, 30, tzinfo=datetime.timezone.utc)
    """

def parse_datetime(__obj: UnionString, /) -> datetime:
    """Parses a ISO string into a `datetime` object.
    The function accepts various date-time formats and converts them into a `datetime.datetime` object.

    Example:
        assert parse_datetime("2024-02-05T14:30:00") == datetime(2024, 2, 5, 14, 30, 0)
        assert parse_datetime("2024-02-05T14:30:00Z") == datetime(2024, 2, 5, 14, 30, tzinfo=datetime.timezone.utc)
    """


def parse_timedelta(__obj: UnionString, /) -> timedelta:
    """Parses a ISO string into a `timedelta` object.
    The function accepts various timedelta formats and converts them into a `datetime.timedelta` object.

    Example:
        assert parse_timedelta("P3DT12H30M5S") == timedelta(days=3, seconds=45005)
        assert parse_timedelta("P3DT12H30M10S") == timedelta(days=3, seconds=45010)
    """
