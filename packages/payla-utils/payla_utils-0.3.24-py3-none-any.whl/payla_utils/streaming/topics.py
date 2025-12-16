import structlog
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.error import KafkaError, KafkaException
from django.conf import settings

logger = structlog.get_logger(__name__)


class TopicManager:
    """
    Manages Kafka topics creation and existence checks.

    Usage examples::

        from payla_utils.streaming import TopicManager

        # Create topics
        TopicManager(['aws.core.fct.orderlifecycles.v1'], {'cleanup.policy': 'delete'}).init_topics()
        TopicManager(['aws.core.cdc.bankinstructions.v0'], {'cleanup.policy': 'compact'}).init_topics()

        # Check if topics exist
        TopicManager(['aws.core.fct.orderlifecycles.v0']).check_topics_exists()
    """

    def __init__(self, topics: list[str], config: dict | None = None) -> None:
        self.topics = topics
        self.config = config
        conf = {'bootstrap.servers': ','.join(settings.KAFKA_SERVERS)}
        if settings.KAFKA_USE_SSL:
            conf.update(
                {
                    'security.protocol': 'SASL_SSL',
                    'sasl.mechanism': 'SCRAM-SHA-512',
                    'sasl.username': settings.KAFKA_USERNAME,
                    'sasl.password': settings.KAFKA_PASSWORD,
                    'enable.ssl.certificate.verification': 'false',
                }
            )
        self.admin = AdminClient(conf)

    def init_topics(self) -> None:
        """
        Create Kafka topics.

        Note: In a multi-cluster production scenario it is more typical
        to use a replication_factor of 3 for durability.
        """
        if self.config is None:
            raise ValueError("config must not be None")

        new_topics = [
            NewTopic(
                topic,
                num_partitions=settings.KAFKA_DEFAULT_PARTITION_COUNT,
                config=self.config,
                replication_factor=min(len(settings.KAFKA_SERVERS), 3),
            )
            for topic in self.topics
        ]

        # Call create_topics to asynchronously create topics.
        # A dict of <topic,future> is returned.
        fs = self.admin.create_topics(new_topics)

        # Wait for each operation to finish.
        for topic, f in fs.items():
            try:
                f.result()  # The result itself is None
                logger.info("Topic %s created", topic)
            except KafkaException as e:  # noqa: PERF203
                if e.args and isinstance(e.args[0], KafkaError) and e.args[0].code() == KafkaError.TOPIC_ALREADY_EXISTS:
                    logger.info("Topic %s already exists", topic)
                else:
                    raise

    def check_topics_exists(self) -> bool:
        """Check if all Kafka topics exist."""
        timeout = 0.5 if settings.TESTING else 5
        try:
            topics = self.admin.list_topics(timeout=timeout).topics
        except KafkaException:
            logger.info("Something went wrong while fetching topics list", exc_info=True)
            return False

        missing_topics = [topic for topic in self.topics if topic not in topics]
        if missing_topics:
            logger.info("Missing topics: %s", missing_topics, found_topics=topics)
            return False
        return True
