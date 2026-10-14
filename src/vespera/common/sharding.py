import uuid

def shard_of(target_id: uuid.UUID, shard_count: int) -> int:
    return target_id.int % shard_count