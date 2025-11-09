from collections.abc import Callable, Coroutine, Sequence
from enum import Enum
from typing import Any, Generic, TypeVar

import fastapi
from dependency_injector import containers
from dependency_injector.wiring import inject
from fastapi import params, routing
from fastapi.applications import AppType
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.params import Depends
from fastapi.routing import APIRoute
from fastapi.types import IncEx
from fastapi.utils import generate_unique_id, get_value_or_default
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import BaseRoute
from starlette.types import Lifespan


class CustomAPIRouter(fastapi.APIRouter):
    """
    Обвязка для fastapi.APIRouter, для кастомизации роутеров и доп. валидации

    Что делает обвязка:

    * оборачивает каждую функцию в inject, позволяя dependency_injector
      библиотеки подгружать зависимости в Provide[] значения
    """

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        response_model: Any = Default(None),
        status_code: int | None = None,
        tags: list[str | Enum] | None = None,
        dependencies: Sequence[params.Depends] | None = None,
        summary: str | None = None,
        description: str | None = None,
        response_description: str = "Successful Response",
        responses: dict[int | str, dict[str, Any]] | None = None,
        deprecated: bool | None = None,
        methods: set[str] | list[str] | None = None,
        operation_id: str | None = None,
        response_model_include: IncEx | None = None,
        response_model_exclude: IncEx | None = None,
        response_model_by_alias: bool = True,
        response_model_exclude_unset: bool = False,
        response_model_exclude_defaults: bool = False,
        response_model_exclude_none: bool = False,
        include_in_schema: bool = True,
        response_class: type[Response] | DefaultPlaceholder = Default(
            JSONResponse,
        ),
        name: str | None = None,
        route_class_override: type[APIRoute] | None = None,
        callbacks: list[BaseRoute] | None = None,
        openapi_extra: dict[str, Any] | None = None,
        generate_unique_id_function: (
            Callable[[APIRoute], str] | DefaultPlaceholder
        ) = Default(generate_unique_id),
    ) -> None:
        route_class = route_class_override or self.route_class
        responses = responses or {}
        combined_responses = {**self.responses, **responses}
        current_response_class = get_value_or_default(
            response_class,
            self.default_response_class,
        )
        current_tags = self.tags.copy()
        if tags:
            current_tags.extend(tags)
        current_dependencies = self.dependencies.copy()
        if dependencies:
            current_dependencies.extend(dependencies)
        current_callbacks = self.callbacks.copy()
        if callbacks:
            current_callbacks.extend(callbacks)
        current_generate_unique_id = get_value_or_default(
            generate_unique_id_function,
            self.generate_unique_id_function,
        )
        route = route_class(
            self.prefix + path,
            endpoint=inject(endpoint),
            response_model=response_model,
            status_code=status_code,
            tags=current_tags,
            dependencies=current_dependencies,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=combined_responses,
            deprecated=deprecated or self.deprecated,
            methods=methods,
            operation_id=operation_id,
            response_model_include=response_model_include,
            response_model_exclude=response_model_exclude,
            response_model_by_alias=response_model_by_alias,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_defaults=response_model_exclude_defaults,
            response_model_exclude_none=response_model_exclude_none,
            include_in_schema=include_in_schema and self.include_in_schema,
            response_class=current_response_class,
            name=name,
            dependency_overrides_provider=self.dependency_overrides_provider,
            callbacks=current_callbacks,
            openapi_extra=openapi_extra,
            generate_unique_id_function=current_generate_unique_id,
        )
        self.routes.append(route)


DIContainerType = TypeVar("DIContainerType", bound=containers.DeclarativeContainer)


class CustomApp(fastapi.FastAPI, Generic[DIContainerType]):
    """
    Обвязка для создания инстанса API

    Обвязка имеет следующие особенности:

    * требует, чтобы все роутеры были унаследованы от CustomAPIRouter, чтобы DI работал по умолчанию везде
    * добавляет типизацию для .container свойства

    P.S.: автоматическое применение @inject работает только на роуты в CustomAPIRouter,
    если вы добавляете роуты напрямую в app, это требуется делать вручную.
    """

    container: DIContainerType

    def __init__(
        self: "CustomApp[DIContainerType]",
        *,
        container: DIContainerType,
        debug: bool = False,
        routes: list[BaseRoute] | None = None,
        title: str = "FastAPI",
        description: str = "",
        version: str = "0.1.0",
        openapi_url: str | None = "/openapi.json",
        openapi_tags: list[dict[str, Any]] | None = None,
        servers: list[dict[str, str | Any]] | None = None,
        dependencies: Sequence[Depends] | None = None,
        default_response_class: type[Response] = Default(JSONResponse),
        docs_url: str | None = "/docs",
        redoc_url: str | None = "/redoc",
        swagger_ui_oauth2_redirect_url: str | None = "/docs/oauth2-redirect",
        swagger_ui_init_oauth: dict[str, Any] | None = None,
        middleware: Sequence[Middleware] | None = None,
        exception_handlers: (
            dict[
                int | type[Exception],
                Callable[[Request, Any], Coroutine[Any, Any, Response]],
            ]
            | None
        ) = None,
        on_startup: Sequence[Callable[[], Any]] | None = None,
        on_shutdown: Sequence[Callable[[], Any]] | None = None,
        lifespan: Lifespan[AppType] | None = None,
        terms_of_service: str | None = None,
        contact: dict[str, str | Any] | None = None,
        license_info: dict[str, str | Any] | None = None,
        openapi_prefix: str = "",
        root_path: str = "",
        root_path_in_servers: bool = True,
        responses: dict[int | str, dict[str, Any]] | None = None,
        callbacks: list[BaseRoute] | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        swagger_ui_parameters: dict[str, Any] | None = None,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(
            generate_unique_id,
        ),
        **extra: Any,
    ) -> None:
        super().__init__(
            debug=debug,
            routes=routes,
            title=title,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=openapi_tags,
            servers=servers,
            dependencies=dependencies,
            default_response_class=default_response_class,
            docs_url=docs_url,
            redoc_url=redoc_url,
            swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
            swagger_ui_init_oauth=swagger_ui_init_oauth,
            middleware=middleware,
            exception_handlers=exception_handlers,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            terms_of_service=terms_of_service,
            contact=contact,
            license_info=license_info,
            openapi_prefix=openapi_prefix,
            root_path=root_path,
            root_path_in_servers=root_path_in_servers,
            responses=responses,
            callbacks=callbacks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            swagger_ui_parameters=swagger_ui_parameters,
            generate_unique_id_function=generate_unique_id_function,
            **extra,
        )
        self.container = container

    def include_router(
        self,
        router: routing.APIRouter,
        *,
        prefix: str = "",
        tags: list[str | Enum] | None = None,
        dependencies: Sequence[Depends] | None = None,
        responses: dict[int | str, dict[str, Any]] | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        default_response_class: type[Response] = Default(JSONResponse),
        callbacks: list[BaseRoute] | None = None,
        generate_unique_id_function: Callable[[routing.APIRoute], str] = Default(
            generate_unique_id,
        ),
    ) -> None:
        if not isinstance(router, CustomAPIRouter):
            msg = (
                f"Все роутеры приложения должны создаваться через shared.utils.fastapi.{CustomAPIRouter.__name__}, "
                f"таким образом обеспечивается поддержка DI в приложении. Для этого достаточно заменить "
                f"вызов fastapi.APIRouter на CustomRouter"
            )
            raise TypeError(msg)

        super().include_router(
            router,
            prefix=prefix,
            tags=tags,
            dependencies=dependencies,
            responses=responses,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            default_response_class=default_response_class,
            callbacks=callbacks,
            generate_unique_id_function=generate_unique_id_function,
        )
