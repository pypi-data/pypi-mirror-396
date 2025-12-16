"""
Core abstractions shared by all generated entities.
"""
from __future__ import annotations

from collections.abc import Mapping, MutableSequence
from copy import deepcopy
import json
from pathlib import Path
from typing import Any, ClassVar, Generic, Literal, Sequence, TypeVar, cast, get_args, get_origin

from jsonschema import Draft202012Validator, ValidationError as JsonSchemaValidationError  # type: ignore[import-untyped]
from pydantic import BaseModel, ConfigDict, ValidationError as PydanticValidationError

from .multilang import MultiLangList, deep_wrap_multilang
from tidas_sdk.schemas import load_schema, schema_exists


class TidasBaseModel(BaseModel):
    """
    Base configuration for every generated Pydantic model.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=False,
        extra="allow",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )


ModelT = TypeVar("ModelT", bound=TidasBaseModel)

ValidationMode = Literal["pydantic", "jsonschema", "both"]


class TidasEntity(Generic[ModelT]):
    """
    Runtime wrapper around generated Pydantic models.
    """

    schema_name: ClassVar[str | None] = None
    _model_cls: type[ModelT]
    _model: ModelT
    _last_pydantic_error: PydanticValidationError | None
    _last_jsonschema_errors: list[str] | None

    def __init__(
        self,
        model_cls: type[ModelT],
        initial_data: Mapping[str, Any] | ModelT | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        object.__setattr__(self, "_model_cls", model_cls)
        payload: Mapping[str, Any]
        if isinstance(initial_data, model_cls):
            object.__setattr__(self, "_model", initial_data)
        else:
            payload = cast(Mapping[str, Any], initial_data or {})
            wrapped = deep_wrap_multilang(deepcopy(payload))
            if validate_on_init:
                model = model_cls.model_validate(wrapped)
            else:
                prepared = self._prepare_partial_payload(model_cls, wrapped)
                model = model_cls.model_construct(**prepared)
            object.__setattr__(self, "_model", model)
        object.__setattr__(self, "_last_pydantic_error", None)
        object.__setattr__(self, "_last_jsonschema_errors", None)
        self.ensure_defaults()

    @property
    def model(self) -> ModelT:
        """
        Expose the underlying Pydantic model for advanced scenarios.
        """
        return self._model

    # -- mutation helpers -----------------------------------------------------------------

    def update(self, data: Mapping[str, Any]) -> None:
        """
        Merge incoming dict-like data into the entity, bypassing validation.
        """
        for key, value in data.items():
            setattr(self, key, deep_wrap_multilang(value))

    def to_json(self, *, by_alias: bool = True, exclude_none: bool = True) -> dict[str, Any]:
        """
        Convert entity contents to a JSON serialisable dict.
        """
        result = self._model.model_dump(by_alias=by_alias, exclude_none=exclude_none)
        return result

    def to_json_string(self, **kwargs: Any) -> str:
        """
        Convenience helper for writing JSON payloads.
        """
        payload = self.to_json(**kwargs)
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def to_xml(self) -> str:
        """
        Convert entity contents to ILCD XML.
        """
        from tidas_sdk.xml.serializer import dataset_to_xml

        return dataset_to_xml(self.to_json())

    def ensure_defaults(self) -> None:  # pragma: no cover - overridden by subclasses
        """
        Hook for subclasses to set required namespaces or default structures.
        """

    # -- validation -----------------------------------------------------------------------

    def validate(self, *, mode: ValidationMode = "pydantic") -> bool:
        """
        Run validation using either Pydantic, JSON Schema, or both.
        """
        data = self.to_json(by_alias=True, exclude_none=False)
        success = True

        if mode in ("pydantic", "both"):
            success = self._validate_with_pydantic(data) and success
        else:
            object.__setattr__(self, "_last_pydantic_error", None)

        if mode in ("jsonschema", "both"):
            success = self._validate_with_jsonschema(data) and success
        else:
            object.__setattr__(self, "_last_jsonschema_errors", None)

        return success

    def last_validation_error(self) -> PydanticValidationError | None:
        """
        Access the cached validation error from the previous run (if any).
        """
        return cast(PydanticValidationError | None, getattr(self, "_last_pydantic_error", None))

    def jsonschema_errors(self) -> list[str] | None:
        """
        Access JSON Schema validation errors from the previous run.
        """
        return cast(list[str] | None, getattr(self, "_last_jsonschema_errors", None))

    def _validate_with_pydantic(self, data: Mapping[str, Any]) -> bool:
        try:
            payload = self._payload_for_validation()
            self._model_cls.model_validate(payload)
        except PydanticValidationError as exc:
            object.__setattr__(self, "_last_pydantic_error", exc)
            return False
        object.__setattr__(self, "_last_pydantic_error", None)
        return True

    def _validate_with_jsonschema(self, data: Mapping[str, Any]) -> bool:
        schema_name = self.schema_name
        if not schema_name:
            object.__setattr__(
                self,
                "_last_jsonschema_errors",
                ["Entity does not declare a schema_name for JSON Schema validation."],
            )
            return False

        if not schema_exists(schema_name):
            object.__setattr__(
                self,
                "_last_jsonschema_errors",
                [f"Schema '{schema_name}' not found in packaged resources."],
            )
            return False

        try:
            schema = load_schema(schema_name)
            validator = Draft202012Validator(schema)
            errors = sorted(validator.iter_errors(data), key=lambda err: list(err.path))
        except Exception as exc:
            object.__setattr__(
                self,
                "_last_jsonschema_errors",
                [f"Schema validation failed to execute: {exc}"],
            )
            return False

        if errors:
            messages = []
            for error in errors:
                path = self._format_error_path(error)
                messages.append(f"{path}: {error.message}")
            object.__setattr__(self, "_last_jsonschema_errors", messages)
            return False

        object.__setattr__(self, "_last_jsonschema_errors", [])
        return True

    @staticmethod
    def _format_error_path(error: JsonSchemaValidationError) -> str:
        path_segments = [str(segment) for segment in error.path]
        return "/".join(path_segments) if path_segments else "<root>"

    # -- loading helpers ------------------------------------------------------------------

    @classmethod
    def from_json(
        cls,
        model_cls: type[ModelT],
        data: str | bytes | Path | Mapping[str, Any],
        *,
        validate_on_init: bool = False,
    ) -> "TidasEntity[ModelT]":
        """
        Build an entity from either a mapping or a JSON payload.
        """
        payload: Mapping[str, Any]
        if isinstance(data, (str, bytes, Path)):
            payload = cls._parse_file_or_string(data)
        else:
            payload = data
        return cls(model_cls, payload, validate_on_init=validate_on_init)

    @classmethod
    def from_xml(
        cls,
        model_cls: type[ModelT],
        data: str | bytes | Path,
        *,
        validate_on_init: bool = False,
    ) -> "TidasEntity[ModelT]":
        """
        Build an entity from an ILCD XML payload.
        """
        from tidas_sdk.xml.parser import dataset_from_xml

        payload = dataset_from_xml(data)
        return cls(model_cls, payload, validate_on_init=validate_on_init)

    # -- python protocol ------------------------------------------------------------------

    def __getattr__(self, item: str) -> Any:
        return getattr(self._model, item)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            wrapped = deep_wrap_multilang(value)
            setattr(self._model, key, wrapped)

    # -- internal helpers -----------------------------------------------------------------

    @staticmethod
    def _parse_file_or_string(data: str | bytes | Path) -> Mapping[str, Any]:
        if isinstance(data, Path):
            content = data.read_text(encoding="utf-8")
        else:
            content = data.decode("utf-8") if isinstance(data, bytes) else data
        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            raise ValueError("JSON payload must represent an object.")
        return cast(Mapping[str, Any], parsed)

    def _prepare_partial_payload(
        self,
        model_cls: type[TidasBaseModel],
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for key, value in payload.items():
            field_name = self._field_name_for_key(model_cls, key)
            output[field_name] = self._maybe_wrap_nested(model_cls, field_name, value)
        return output

    @staticmethod
    def _field_name_for_key(model_cls: type[TidasBaseModel], key: str) -> str:
        fields = model_cls.model_fields
        for name, field in fields.items():
            if field.alias == key:
                return name
        return key

    def _maybe_wrap_nested(
        self,
        model_cls: type[TidasBaseModel],
        field_name: str,
        value: Any,
    ) -> Any:
        fields = model_cls.model_fields
        field = fields.get(field_name)
        if field is None:
            return value
        annotation = field.annotation
        nested_model = self._resolve_nested_model(annotation)
        if nested_model and isinstance(value, Mapping):
            return nested_model.model_construct(
                **self._prepare_partial_payload(nested_model, value)
            )
        if self._is_sequence_of_models(annotation) and isinstance(value, list):
            args = get_args(annotation)
            nested_cls = self._resolve_nested_model(args[0]) if args else None
            if nested_cls is None:
                return value
            return [
                nested_cls.model_construct(
                    **self._prepare_partial_payload(nested_cls, cast(Mapping[str, Any], item))
                )
                if isinstance(item, Mapping)
                else item
                for item in value
            ]
        return value

    @staticmethod
    def _resolve_nested_model(annotation: Any) -> type[TidasBaseModel] | None:
        if isinstance(annotation, type) and issubclass(annotation, TidasBaseModel):
            return annotation
        origin = get_origin(annotation)
        if origin in (list, MutableSequence):
            args = get_args(annotation)
            if args:
                return TidasEntity._resolve_nested_model(args[0])
        return None

    @staticmethod
    def _is_sequence_of_models(annotation: Any) -> bool:
        origin = get_origin(annotation)
        if origin not in (list, MutableSequence):
            return False
        args = get_args(annotation)
        if not args:
            return False
        inner = args[0]
        return isinstance(inner, type) and issubclass(inner, TidasBaseModel)

    # -- validation helpers -------------------------------------------------------------

    def _payload_for_validation(self) -> dict[str, Any]:
        return self._collect_runtime_payload(self._model)

    def _collect_runtime_payload(self, model: TidasBaseModel) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        fields = model.model_fields
        for field_name, field in fields.items():
            alias = field.alias or field_name
            try:
                value = getattr(model, field_name)
            except AttributeError:
                continue
            payload[alias] = self._normalize_runtime_value(value)
        return payload

    def _normalize_runtime_value(self, value: Any) -> Any:
        if isinstance(value, MultiLangList):
            return value
        if isinstance(value, TidasBaseModel):
            return self._collect_runtime_payload(value)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            items: list[Any] = []
            for item in value:
                if isinstance(item, MultiLangList):
                    items.append(item)
                    continue
                if isinstance(item, TidasBaseModel):
                    items.append(self._collect_runtime_payload(item))
                else:
                    items.append(item)
            return items
        return value
