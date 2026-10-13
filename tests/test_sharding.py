import uuid

from vespera.common.sharding import shard_of


def test_same_id_same_shard():
    target_id = uuid.uuid4()
    assert shard_of(target_id, 2) == shard_of(target_id, 2)


def test_shard_in_range():
    for _ in range(100):
        assert 0 <= shard_of(uuid.uuid4(), 3) < 3


def test_even_distribution():
    counts = [0, 0]
    for _ in range(1000):
        counts[shard_of(uuid.uuid4(), 2)] += 1
    assert all(400 <= c <= 600 for c in counts)