import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import structlog
from confluent_kafka.schema_registry import SchemaRegistryClient
from django.conf import settings
from django.core.management.base import BaseCommand
from fastavro.schema import load_schema, to_parsing_canonical_form

from payla_utils.kafka import RegisterOnlyAvroSerializer
from payla_utils.settings import payla_utils_settings
from payla_utils.streaming import TopicManager

logger = structlog.get_logger(__name__)


def validate_topic_name(topic: str, topic_name_pattern: str) -> str:
    """
    Validates the topic name according to conformity pattern and extracts topic version.

    Args:
        topic: The Kafka topic name to validate.
        topic_name_pattern: Regex pattern for validating topic names.

    Returns:
        The topic version extracted from the topic name.

    Raises:
        NameError: If the topic name does not match the conformity pattern.
    """
    topic_pattern_match = re.search(topic_name_pattern, topic)
    if not topic_pattern_match:
        raise NameError(f"Kafka topic name does not match conformity pattern. Name: {topic}")
    return topic_pattern_match["topic_version"]


def load_message_schema(schema_filename: str, topic_version: str, avro_schema_dir: Path) -> dict:
    """
    Loads message schema from the Avro schema directory.

    Args:
        schema_filename: The filename of the schema to load.
        topic_version: The version of the topic (used to locate the schema directory).
        avro_schema_dir: The base directory containing Avro schemas.

    Returns:
        The loaded message schema.

    Raises:
        FileNotFoundError: If the schema version folder does not exist.
        NotImplementedError: If the schema could not be loaded.
    """
    schema_dir = avro_schema_dir / topic_version
    if not schema_dir.is_dir():
        raise FileNotFoundError(f"Folder for schema version {topic_version} not found: {schema_dir}")

    message_schema = load_schema(avro_schema_dir / topic_version / schema_filename)
    if not message_schema:
        raise NotImplementedError("Message schema could not be loaded.")
    return message_schema


class Command(BaseCommand):
    """
    Management command for registering Kafka schemas.

    Reads configuration from PAYLA_UTILS settings.
    """

    help = 'Register Kafka schemas with the schema registry and create topics.'

    @property
    def producer_topic_names(self) -> dict[str, list[str]]:
        return payla_utils_settings.STREAMING_PRODUCER_TOPIC_NAMES

    @property
    def topics_schemas_mapping(self) -> dict[str, str]:
        return payla_utils_settings.STREAMING_TOPICS_SCHEMAS_MAPPING

    @property
    def avro_schema_dir(self) -> Path:
        schema_dir = payla_utils_settings.STREAMING_AVRO_SCHEMA_DIR
        return Path(schema_dir) if schema_dir else Path()

    @property
    def topic_name_pattern(self) -> str:
        return payla_utils_settings.STREAMING_TOPIC_NAME_PATTERN

    @property
    def custom_dynamic_topics_and_schemas_callback(self) -> Callable[..., dict[str, str]]:
        return payla_utils_settings.STREAMING_CUSTOM_DYNAMIC_TOPICS_AND_SCHEMAS_CALLBACK or (dict)

    def create_topic(self, topic_name: str) -> None:
        """Creates a single Kafka topic using TopicManager."""
        cleanup_policy = 'compact' if '.cdc.' in topic_name else 'delete'
        TopicManager([topic_name], {'cleanup.policy': cleanup_policy}).init_topics()

    def create_topics(self) -> None:
        """Creates all topics from producer_topic_names."""
        for key, value in self.producer_topic_names.items():
            if key.startswith('tests_'):
                continue
            assert isinstance(value, list)
            for topic_name in value:
                self.create_topic(topic_name)

    def register_schema(
        self,
        topic: str,
        schema_name: str,
        schema_registry_client: SchemaRegistryClient,
    ) -> None:
        """Registers a schema for a topic."""
        topic_version = validate_topic_name(topic, self.topic_name_pattern)
        versioned_schema_name = schema_name.replace('<version>', topic_version)
        message_schema = load_message_schema(versioned_schema_name, topic_version, self.avro_schema_dir)
        schema_serializer = RegisterOnlyAvroSerializer(
            schema_registry_client, to_parsing_canonical_form(message_schema)
        )
        schema_serializer.register(topic)

    def handle(self, *args: Any, **options: Any) -> None:
        self.create_topics()

        schema_registry_client = SchemaRegistryClient({'url': settings.KAFKA_SCHEMA_REGISTRY})
        for topic, schema_name in self.topics_schemas_mapping.items():
            self.register_schema(topic, schema_name, schema_registry_client)

        for topic, schema_name in self.custom_dynamic_topics_and_schemas_callback().items():
            self.create_topic(topic)
            self.register_schema(topic, schema_name, schema_registry_client)

        if schema_registry_client:
            schema_registry_client.__exit__()
