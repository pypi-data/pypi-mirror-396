from contextlib import asynccontextmanager
from datetime import datetime
from typing import (
    Annotated,
    Any,
    AsyncGenerator,
    Generic,
    TypeAlias,
    TypeVar,
    cast,
    get_args,
    overload,
)

from bson.objectid import ObjectId
from pydantic import BeforeValidator, Field, field_serializer
from pymongo import (
    ASCENDING,
    DESCENDING,
    GEO2D,
    GEOSPHERE,
    HASHED,
    TEXT,
    AsyncMongoClient,
    IndexModel,
)
from pymongo.asynchronous.client_session import AsyncClientSession
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from typing_extensions import Self

from .alias import CamelCaseAliasedBaseModel
from .logging import LoggerFactory

__all__ = [
    "ASCENDING",
    "AggregatedDocument",
    "AsyncClientSession",
    "DESCENDING",
    "Document",
    "EmbeddedDocument",
    "Field",
    "GEO2D",
    "GEOSPHERE",
    "HASHED",
    "IndexManager",
    "IndexModel",
    "MongoDBManager",
    "MongoDBObjectId",
    "ObjectId",
    "ProjectedDocument",
    "RepositoryBase",
    "TEXT",
    "validate_object_id",
]


class MongoDBManager:
    def __init__(self, connection_string: str, db: str | None = None):
        self._client = AsyncMongoClient(connection_string)
        self._db = self._client.get_database(db)
        self._logger = LoggerFactory.get_logger("mongodb_manager")

    async def connect(self) -> None:
        await self._client.aconnect()

        host = "localhost"
        port = 27017
        address = await self._client.address

        if address is not None:
            host, port = address

        self._logger.info("connected to mongodb server `%s:%s`", host, port)

    async def disconnect(self) -> None:
        await self._client.aclose()
        self._logger.info("disconnected from mongodb")

    @property
    def client(self) -> AsyncMongoClient:
        return self._client

    @property
    def db(self) -> AsyncDatabase:
        return self._db

    @asynccontextmanager
    async def transactional(self) -> AsyncGenerator[AsyncClientSession, None]:
        async with self.client.start_session() as session:
            async with await session.start_transaction():
                yield session

    def __getitem__(self, document: type["Document"]) -> AsyncCollection:
        return self._db.get_collection(document.get_collection_name())


class TimeStampMixin(CamelCaseAliasedBaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_serializer("updated_at", when_used="always")
    def serialize_updated_at(self, _: datetime) -> datetime:
        return datetime.now()


def validate_object_id(value: Any) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise ValueError(f"{value} is not valid objectid")

    return ObjectId(value)


MongoDBObjectId: TypeAlias = Annotated[
    ObjectId, BeforeValidator(validate_object_id)
]


class Document(CamelCaseAliasedBaseModel):
    id: MongoDBObjectId = Field(alias="_id", default_factory=ObjectId)

    @classmethod
    def get_collection_name(cls) -> str:
        collection_name = getattr(cls, "__collection_name__", None)

        if collection_name is None:
            collection_name = cls.__name__

        return collection_name

    @classmethod
    def get_indexes(cls) -> list[IndexModel] | None:
        return getattr(cls, "__indexes__", None)

    @classmethod
    def from_raw_document(cls, document: Any, **kwargs: Any) -> Self:
        return cast(Self, cls.model_validate(document, **kwargs))


class EmbeddedDocument(CamelCaseAliasedBaseModel):
    @classmethod
    def from_raw_embedded_document(
        cls, embedded_document: Any, **kwargs: Any
    ) -> Self:
        return cast(Self, cls.model_validate(embedded_document, **kwargs))


class ProjectedDocument(CamelCaseAliasedBaseModel):
    @classmethod
    def from_raw_projected_document(
        cls, projected_document: Any, **kwargs: Any
    ) -> Self:
        return cast(Self, cls.model_validate(projected_document, **kwargs))

    @classmethod
    def get_projection(cls) -> list[str] | dict[str, Any]:
        projection = getattr(cls, "__projection__", None)

        if projection is None:
            projection = cls._projection_from_field_info()

        return cast(list[str] | dict[str, Any], projection)

    @classmethod
    def _projection_from_field_info(cls) -> list[str]:
        cls.__projection__ = [
            field_info.alias or field_name
            for field_name, field_info in cls.model_fields.items()
        ]

        return cls.__projection__


class AggregatedDocument(CamelCaseAliasedBaseModel):
    @classmethod
    def from_raw_aggregated_document(cls, obj: Any, **kwargs: Any) -> Self:
        return cast(Self, cls.model_validate(obj, **kwargs))

    @classmethod
    def get_pipeline(cls) -> list[Any]:
        projection = getattr(cls, "__pipeline__", None)

        if projection is None:
            raise ValueError(
                f"__pipeline__ is not defined for aggregated document {cls.__name__}"
            )

        return cast(list[Any], projection)


class IndexManager:
    def __init__(
        self, db: MongoDBManager, documents: list[type[Document]]
    ) -> None:
        self._db = db
        self._documents = documents

    async def create_indexes(self) -> None:
        for document in self._documents:
            indexes = document.get_indexes()

            if indexes is None:
                continue

            await self._db[document].create_indexes(indexes)

    async def get_indexes(self, collection_name: str) -> list[str]:
        document = self._get_document(collection_name)
        indexes = []

        async with await self._db[document].list_indexes() as cursor:
            async for index in cursor:
                indexes.append(index.get("name"))

        return indexes

    async def drop_indexes(
        self, collection_names: list[str] | None = None
    ) -> None:
        for document in self._documents:
            if (
                collection_names is not None
                and document.get_collection_name() not in collection_names
            ):
                continue

            await self._db[document].drop_indexes()

    async def drop_index(self, collection_name: str, index_name: str) -> None:
        document = self._get_document(collection_name)

        await self._db[document].drop_index(index_name)

    def _get_document(self, collection_name: str) -> type[Document]:
        document = None

        for document in self._documents:
            if document.get_collection_name() == collection_name:
                break

        if document is None:
            raise ValueError(
                f"collection with name {collection_name} not found"
            )

        return document


T = TypeVar("T", bound=Document)
P = TypeVar("P", bound=ProjectedDocument)
A = TypeVar("A", bound=AggregatedDocument)
S = TypeVar("S")


class RepositoryBase(Generic[T]):
    def __init__(self, db: MongoDBManager) -> None:
        self._db = db
        self._session = None
        self._document_type = None

    @property
    def db(self) -> MongoDBManager:
        return self._db

    @property
    def collection(self) -> AsyncCollection:
        return self._db[self.document_type]

    @property
    def session(self) -> AsyncClientSession | None:
        return self._session

    @session.setter
    def session(self, session: AsyncClientSession) -> None:
        if session.has_ended:
            raise RuntimeError(
                f"session with id {session.session_id} has already ended"
            )

        self._session = session

    @property
    def document_type(self) -> type[T]:
        document_type = self._document_type

        if document_type is None:
            orig_bases = getattr(self, "__orig_bases__", None)

            if not orig_bases:
                raise RuntimeError("generic variable T is not specified")

            *_, orig_class = orig_bases
            *_, self._document_type = get_args(orig_class)

        return cast(type[T], self._document_type)

    async def insert(
        self, document: T, session: AsyncClientSession | None = None
    ) -> ObjectId | str:
        inserted_one_result = await self.collection.insert_one(
            document=document.model_dump(by_alias=True),
            session=session or self.session,
        )

        return inserted_one_result.inserted_id

    async def insert_many(
        self, documents: list[T], session: AsyncClientSession | None = None
    ) -> list[ObjectId] | list[str]:
        insert_many_result = await self.collection.insert_many(
            documents=[
                document.model_dump(by_alias=True) for document in documents
            ],
            session=session or self.session,
        )

        return cast(list[ObjectId] | list[str], insert_many_result.inserted_ids)

    @overload
    async def find_by_id(
        self,
        *,
        id: Any,
        skip: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> T | None:
        pass

    @overload
    async def find_by_id(
        self,
        *,
        id: Any,
        projection: type[P],
        skip: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> P | None:
        pass

    async def find_by_id(self, *_: Any, **kwargs: Any) -> Any:
        return await self._find_one(
            filter={"_id": kwargs["id"]},
            projection=kwargs.get("projection"),
            skip=kwargs.get("skip", 0),
            sort=kwargs.get("sort"),
            session=kwargs.get("session"),
        )

    @overload
    async def find_by_filter(
        self,
        *,
        filter: dict[str, Any],
        skip: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> T | None:
        pass

    @overload
    async def find_by_filter(
        self,
        *,
        filter: dict[str, Any],
        projection: type[P],
        skip: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> P | None:
        pass

    async def find_by_filter(self, *_: Any, **kwargs: Any) -> Any:
        return await self._find_one(
            filter=kwargs["filter"],
            projection=kwargs.get("projection"),
            skip=kwargs.get("skip", 0),
            sort=kwargs.get("sort"),
            session=kwargs.get("session"),
        )

    async def _find_one(
        self,
        filter: dict[str, Any],
        projection: type[P] | None = None,
        skip: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> T | P | None:
        if projection is not None:
            document = await self.collection.find_one(
                filter=filter,
                projection=projection.get_projection(),
                skip=skip,
                sort=sort,
                session=session or self.session,
            )
        else:
            document = await self.collection.find_one(
                filter=filter,
                skip=skip,
                sort=sort,
                session=session or self.session,
            )

        if document is None:
            return None

        if projection is not None:
            return projection.from_raw_projected_document(document)

        return self.document_type.from_raw_document(document)

    async def replace(
        self, replacement: T, session: AsyncClientSession | None = None
    ) -> None:
        await self.collection.replace_one(
            filter={"_id": replacement.id},
            replacement=replacement.model_dump(by_alias=True),
            session=session or self.session,
        )

    @overload
    def find_all(
        self,
        *,
        skip: int = 0,
        limit: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> AsyncGenerator[T, None]:
        pass

    @overload
    def find_all(
        self,
        *,
        projection: type[P],
        skip: int = 0,
        limit: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> AsyncGenerator[P, None]:
        pass

    async def find_all(
        self, *_: Any, **kwargs: Any
    ) -> AsyncGenerator[Any, None]:
        async for document in self._find(
            projection=kwargs.get("projection"),
            skip=kwargs.get("skip", 0),
            limit=kwargs.get("limit", 0),
            sort=kwargs.get("sort"),
            session=kwargs.get("session"),
        ):
            yield document

    @overload
    def find_all_by_filter(
        self,
        *,
        filter: dict[str, Any],
        skip: int = 0,
        limit: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> AsyncGenerator[T, None]:
        pass

    @overload
    def find_all_by_filter(
        self,
        *,
        filter: dict[str, Any],
        projection: type[P] | None = None,
        skip: int = 0,
        limit: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> AsyncGenerator[T, None]:
        pass

    async def find_all_by_filter(
        self, *_: Any, **kwargs: Any
    ) -> AsyncGenerator[Any, None]:
        async for document in self._find(
            filter=kwargs.get("filter"),
            projection=kwargs.get("projection"),
            skip=kwargs.get("skip", 0),
            limit=kwargs.get("limit", 0),
            sort=kwargs.get("sort"),
            session=kwargs.get("session"),
        ):
            yield document

    async def _find(
        self,
        filter: dict[str, Any] | None = None,
        projection: type[P] | None = None,
        skip: int = 0,
        limit: int = 0,
        sort: dict[str, int] | None = None,
        session: AsyncClientSession | None = None,
    ) -> AsyncGenerator[T | P, None]:
        if projection:
            async with self.collection.find(
                filter=filter,
                projection=projection.get_projection(),
                skip=skip,
                limit=limit,
                sort=sort,
                session=session or self.session,
            ) as cursor:
                async for document in cursor:
                    yield projection.from_raw_projected_document(document)

            return

        async with self.collection.find(
            filter=filter,
            skip=skip,
            limit=limit,
            sort=sort,
            session=session or self.session,
        ) as cursor:
            async for document in cursor:
                yield self.document_type.from_raw_document(document)

    @overload
    async def exists(
        self,
        *,
        id: Any,
        session: AsyncClientSession | None = None,
    ) -> bool:
        pass

    @overload
    async def exists(
        self,
        *,
        filter: dict[str, Any],
        session: AsyncClientSession | None = None,
    ) -> bool:
        pass

    async def exists(self, *_: Any, **kwargs: Any) -> bool:
        id = kwargs.get("id")
        filter = kwargs.get("filter")

        if id is not None:
            filter = {"_id": id}

        return (
            await self.collection.find_one(
                filter=filter,
                projection={"_id": True},
                session=kwargs.get("session") or self.session,
            )
            is not None
        )

    async def count(
        self,
        filter: dict[str, Any] | None = None,
        skip: int | None = None,
        limit: int | None = None,
        session: AsyncClientSession | None = None,
    ) -> int:
        if filter is not None or skip is not None or limit is not None:
            options = {}

            if skip is not None:
                options["skip"] = skip

            if limit is not None and limit > 0:
                options["limit"] = limit

            return cast(
                int,
                await self.collection.count_documents(
                    filter=filter or {},
                    **options,
                    session=session or self.session,
                ),
            )

        return cast(int, await self.collection.estimated_document_count())

    @overload
    def aggregate(
        self,
        *,
        aggregation: type[A],
        let: dict[str, Any] | None = None,
        session: AsyncClientSession | None = None,
    ) -> AsyncGenerator[A, None]:
        pass

    @overload
    def aggregate(
        self,
        *,
        aggregation: type[A],
        pipeline: list[Any],
        let: dict[str, Any] | None = None,
        session: AsyncClientSession | None = None,
    ) -> AsyncGenerator[A, None]:
        pass

    async def aggregate(
        self, *_: Any, **kwarg: Any
    ) -> AsyncGenerator[Any, None]:
        aggregation = cast(AggregatedDocument, kwarg.get("aggregation"))
        pipeline = kwarg.get("pipeline")

        if pipeline is None:
            pipeline = aggregation.get_pipeline()

        async with await self.collection.aggregate(
            pipeline=pipeline,
            let=kwarg.get("let"),
            session=kwarg.get("session") or self.session,
        ) as cursor:
            async for document in cursor:
                yield aggregation.from_raw_aggregated_document(document)
