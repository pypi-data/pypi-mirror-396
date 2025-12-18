from typing import (
    Annotated,
    get_origin,
    get_args,
    Union,
    Any,
    TypeVar,
    get_type_hints,
    Self,
)
from types import UnionType, NoneType
from pydantic import (
    BaseModel,
    create_model,
    BeforeValidator,
    ValidationError,
    PlainSerializer,
)
from mixam_sdk.item_specification.models.value_based import ValueBased
from mixam_sdk.item_specification.enums import ValueBasedSpecificationOptionEnum
from mixam_sdk.utils.enum_json import enum_by_name_or_value, enum_dump_name
from copy import deepcopy
from functools import cache

T = TypeVar("T", bound=BaseModel)


@cache
def text_based(cls: type[T]) -> type[T]:
    """Return a subclass of `cls` model where all ValueBased Enums are replaced by text_based().
    Recursively handles all nested models subclassing `BaseModel`.
    Do not use on enums, for which You should use their `text_based()` method instead."""
    if not issubclass(cls, BaseModel):
        return cls

    def _convert_union(union_args: tuple[Any, ...]) -> Any:
        """Return a new Union with all ValueBased Enums converted to TextBased."""
        new_members = [
            t.text_based()
            if isinstance(t, type) and issubclass(t, ValueBased)
            else text_based(t)
            for t in union_args
        ]
        new_members = tuple(dict.fromkeys(new_members))

        return Union[new_members]

    def _convert_annotation(annotation: Any) -> Any:
        def _unpack_annotated(args):
            base_type, meta = args[0], args[1:]
            base_origin = get_origin(base_type)
            base_args = get_args(base_type)

            if base_origin in (UnionType, Union):
                new_base = _convert_union(base_args)
            elif isinstance(base_type, type) and issubclass(base_type, ValueBased):
                new_base = base_type.text_based()
            else:
                new_base = base_type
            return meta, new_base

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is list:
            meta, new_base = _unpack_annotated(get_args(args[0]))
            return list[Annotated[new_base, *meta]]
        if origin is Annotated:
            meta, new_base = _unpack_annotated(args)
            return Annotated[new_base, *meta]

        elif origin in (UnionType, Union):
            return _convert_union(args)

        elif isinstance(annotation, type) and issubclass(annotation, ValueBased):
            return annotation.text_based()
        elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return text_based(annotation)
        return annotation

    def _extract_concrete_class(annotation):
        """Return the first concrete class inside a union or optional."""
        if len(args := get_args(annotation)) == 2:
            return next((t for t in args if not isinstance(t, NoneType)), annotation)
        return annotation

    def _convert_default(old_default: Any, new_annotation: Any) -> Any:
        """Return a default compatible with the new annotation."""

        if isinstance(old_default, ValueBasedSpecificationOptionEnum):
            target_cls = _extract_concrete_class(new_annotation)
            return target_cls[old_default.name]
        return old_default

    def _convert_default_factory(old_factory: Any, new_annotation: Any) -> Any:
        _old_factory_is_a_constructor = isinstance(old_factory, type) and issubclass(
            old_factory, BaseModel
        )
        if _old_factory_is_a_constructor:
            return new_annotation
        return old_factory

    def _update_annotation(
        type_hints: dict[str, Any], name: str, new_annotation: Any
    ) -> Annotated:
        def _args_to_text(arg: Any, new_annotation_concrete: Any) -> Any:
            if isinstance(arg, BeforeValidator):
                return enum_by_name_or_value(new_annotation_concrete)
            if isinstance(arg, PlainSerializer) and int in get_args(arg.return_type):
                return enum_dump_name  # TextBased have name == value
            return arg

        args = get_args(type_hints[name])[1:]
        if is_optional := (get_origin(new_annotation) is Union):
            new_annotation_concrete = _extract_concrete_class(new_annotation)
        else:
            new_annotation_concrete = new_annotation

        args = [_args_to_text(arg, new_annotation_concrete) for arg in args]
        new_annotation = (
            Annotated[new_annotation_concrete | None, *args]
            if is_optional
            else Annotated[new_annotation_concrete, *args]
        )
        return new_annotation

    new_fields = {}
    type_hints = get_type_hints(cls, include_extras=True)
    for name, field in cls.model_fields.items():
        new_field = deepcopy(field)

        new_annotation = _convert_annotation(field.annotation)
        new_field.default = _convert_default(field.default, new_annotation)
        new_field.default_factory = _convert_default_factory(
            field.default_factory, new_annotation
        )
        if get_origin(type_hints[name]) is Annotated:
            new_annotation = _update_annotation(type_hints, name, new_annotation)

        new_field.annotation = new_annotation
        new_fields[name] = (new_field.annotation, new_field)

    new_cls = create_model(
        f"{cls.__name__}TextBased",
        __base__=cls,
        **new_fields,
    )
    new_cls.model_rebuild(force=True)
    return deduplicate_metadata(new_cls)


def to_text_based(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: to_text_based(_obj) for key, _obj in obj.items()}
    elif isinstance(obj, list):
        return [to_text_based(_obj) for _obj in obj]
    elif isinstance(obj, ValueBasedSpecificationOptionEnum):
        return obj.to_text_based()
    else:
        return obj


def deduplicate_metadata(model_cls: type[T]) -> type[T]:
    for field in model_cls.model_fields.values():
        if any(isinstance(md, BeforeValidator) for md in field.metadata):
            field.metadata = field.metadata[len(field.metadata) // 2 :]

    model_cls.model_rebuild(force=True)
    return model_cls


class TextBasedMixin(BaseModel):
    @classmethod
    @cache
    def text_based(cls: type[T]) -> type[T]:
        return text_based(cls)

    @classmethod
    def from_text_based(cls: type[Self], text_based: Self) -> Self:
        return cls.model_validate(
            text_based.model_dump(mode="json")
            | (
                {"component_type": text_based.component_type}
                if hasattr(text_based, "component_type")
                else {}
            )
        )

    def to_text_based(self) -> Self:
        text_based_cls = type(self).text_based()
        new_obj = {}
        for name, field in self.model_dump().items():
            new_obj[name] = to_text_based(field)

        try:
            return text_based_cls.model_validate(new_obj)
        except ValidationError as e:
            print(e.errors(include_url=False))
            raise e

    def to_value_based(self):
        raise NotImplementedError("This method has to be overridden in the child class")
