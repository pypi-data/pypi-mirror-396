"""Kafka backend for topic/consumer observability."""

from dataclasses import dataclass

from ..config import get_config


@dataclass
class TopicInfo:
    """Information about a Kafka topic."""

    name: str
    partitions: int
    messages: int


@dataclass
class ConsumerGroupInfo:
    """Information about a consumer group."""

    group_id: str
    offsets: dict  # topic[partition] -> offset


@dataclass
class ConsumerLag:
    """Consumer lag information."""

    group_id: str
    total_lag: int
    details: list[str]  # Per-partition lag details


def _get_kafka_client():
    """Get Kafka admin client, raising helpful error if not installed."""
    try:
        from kafka.admin import KafkaAdminClient
        return KafkaAdminClient
    except ImportError:
        raise RuntimeError(
            "kafka-python not installed. Run: pip install adjoint-lgtm-observe[kafka]"
        )


def _get_kafka_consumer():
    """Get Kafka consumer class."""
    try:
        from kafka import KafkaConsumer
        return KafkaConsumer
    except ImportError:
        raise RuntimeError(
            "kafka-python not installed. Run: pip install adjoint-lgtm-observe[kafka]"
        )


def list_topics() -> list[TopicInfo]:
    """
    List Kafka topics with message counts.

    Returns:
        List of TopicInfo objects
    """
    config = get_config()
    admin_cls = _get_kafka_client()
    consumer_cls = _get_kafka_consumer()

    try:
        from kafka import TopicPartition

        admin = admin_cls(bootstrap_servers=config.kafka_bootstrap)
        topics = admin.list_topics()

        # Filter out internal topics
        user_topics = [t for t in topics if not t.startswith("_")]

        consumer = consumer_cls(bootstrap_servers=config.kafka_bootstrap)

        results = []
        for topic in sorted(user_topics):
            partitions = consumer.partitions_for_topic(topic)
            if partitions:
                tps = [TopicPartition(topic, p) for p in partitions]
                consumer.assign(tps)
                end_offsets = consumer.end_offsets(tps)
                total = sum(end_offsets.values())
                results.append(TopicInfo(
                    name=topic,
                    partitions=len(partitions),
                    messages=total,
                ))
            else:
                results.append(TopicInfo(name=topic, partitions=0, messages=0))

        consumer.close()
        admin.close()

        return results

    except Exception as e:
        raise RuntimeError(f"Error connecting to Kafka: {e}") from e


def list_consumers() -> list[ConsumerGroupInfo]:
    """
    List Kafka consumer groups and their offsets.

    Returns:
        List of ConsumerGroupInfo objects
    """
    config = get_config()
    admin_cls = _get_kafka_client()

    try:
        admin = admin_cls(bootstrap_servers=config.kafka_bootstrap)
        groups = admin.list_consumer_groups()

        results = []
        for group_id, _ in groups:
            try:
                offsets = admin.list_consumer_group_offsets(group_id)
                if offsets:
                    offset_dict = {}
                    for tp, offset_meta in offsets.items():
                        key = f"{tp.topic}[{tp.partition}]"
                        offset_dict[key] = offset_meta.offset
                    results.append(ConsumerGroupInfo(
                        group_id=group_id,
                        offsets=offset_dict,
                    ))
            except Exception:
                results.append(ConsumerGroupInfo(
                    group_id=group_id,
                    offsets={},
                ))

        admin.close()
        return results

    except Exception as e:
        raise RuntimeError(f"Error connecting to Kafka: {e}") from e


def get_lag() -> list[ConsumerLag]:
    """
    Get consumer lag for all consumer groups.

    Returns:
        List of ConsumerLag objects
    """
    config = get_config()
    admin_cls = _get_kafka_client()
    consumer_cls = _get_kafka_consumer()

    try:
        admin = admin_cls(bootstrap_servers=config.kafka_bootstrap)
        consumer = consumer_cls(bootstrap_servers=config.kafka_bootstrap)

        groups = admin.list_consumer_groups()

        results = []
        for group_id, _ in groups:
            try:
                offsets = admin.list_consumer_group_offsets(group_id)
                if not offsets:
                    continue

                total_lag = 0
                details = []

                for tp, offset_meta in offsets.items():
                    consumer.assign([tp])
                    end_offsets = consumer.end_offsets([tp])
                    end = end_offsets.get(tp, 0)
                    current = offset_meta.offset
                    lag = end - current

                    if lag > 0:
                        details.append(f"{tp.topic}[{tp.partition}]: {lag} behind")
                    total_lag += lag

                results.append(ConsumerLag(
                    group_id=group_id,
                    total_lag=total_lag,
                    details=details,
                ))

            except Exception:
                continue

        consumer.close()
        admin.close()

        return results

    except Exception as e:
        raise RuntimeError(f"Error connecting to Kafka: {e}") from e


def format_topics(topics: list[TopicInfo]) -> str:
    """Format topics for display."""
    if not topics:
        return "No topics found"

    lines = [f"Kafka Topics ({len(topics)}):\n"]
    for t in topics:
        lines.append(f"  {t.name}: {t.messages} messages ({t.partitions} partitions)")

    return "\n".join(lines)


def format_consumers(consumers: list[ConsumerGroupInfo]) -> str:
    """Format consumer groups for display."""
    if not consumers:
        return "No consumer groups found"

    lines = [f"Consumer Groups ({len(consumers)}):\n"]
    for c in consumers:
        lines.append(f"  {c.group_id}:")
        for key, offset in c.offsets.items():
            lines.append(f"    {key}: offset {offset}")

    return "\n".join(lines)


def format_lag(lag_results: list[ConsumerLag]) -> str:
    """Format consumer lag for display."""
    if not lag_results:
        return "No consumer groups found"

    lines = ["Consumer Lag:\n"]
    for lag in lag_results:
        if lag.total_lag > 0:
            lines.append(f"  {lag.group_id}: {lag.total_lag} total lag")
            for d in lag.details:
                lines.append(f"    {d}")
        else:
            lines.append(f"  {lag.group_id}: caught up")

    return "\n".join(lines)
