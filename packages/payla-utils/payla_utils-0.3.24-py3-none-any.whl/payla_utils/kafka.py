from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import MessageField, SerializationContext


class RegisterOnlyAvroSerializer(AvroSerializer):
    """
    A specialized AvroSerializer that only registers schemas without serializing data.

    This is useful for pre-registering schemas with the schema registry before
    any messages are produced.
    """

    def register(self, topic: str) -> None:
        """
        Register the schema with the schema registry for the given topic.

        Args:
            topic: The Kafka topic name to register the schema for.
        """
        # See SerializingProducer.produce
        ctx = SerializationContext(topic, MessageField.KEY)
        ctx.field = MessageField.VALUE

        # See AvroSerializer.__call__
        subject = self._subject_name_func(ctx, self._schema_name)

        if subject in self._known_subjects:
            return

        if self._use_latest_version:
            latest_schema = self._registry.get_latest_version(subject)
            self._schema_id = latest_schema.schema_id
        # Check to ensure this schema has been registered under subject_name.
        elif self._auto_register:
            # The schema name will always be the same. We can't however register
            # a schema without a subject so we set the schema_id here to handle
            # the initial registration.
            self._schema_id = self._registry.register_schema(subject, self._schema)
        else:
            registered_schema = self._registry.lookup_schema(subject, self._schema)
            self._schema_id = registered_schema.schema_id

        self._known_subjects.add(subject)
