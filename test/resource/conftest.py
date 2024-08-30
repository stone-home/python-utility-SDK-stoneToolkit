import pytest


@pytest.fixture(scope="function")
def dataset_template_cifar():
    return {
        "name": "cifar10_1",
        "label_key": "label",
        "tags": ["Digit Recognition", "Micro", "Auto-cache"],
        "split": {
            "train": {"name": "test", "size": 2021},
            "test": {"name": "test", "size": 2021},
        },
        "url": "https://github.com/modestyachts/CIFAR-10.1",
        "image_size": [32, 32, 3],
        "cache": True,
    }


@pytest.fixture(scope="function")
def dataset_input_config():
    return {
        "name": "cifar10_1",
        "shuffle_buffer_size": 100,
        "prefetch_buffer_size": 10,
        "batch_size": 10,
        "image_size": [100, 100],
        "cache": True,
        "auto_shard": True,
    }


@pytest.fixture(scope="function")
def TF_CONFIG():
    return {
        "cluster": {"worker": ["localhost:12345", "localhost:23456"]},
        "task": {"type": "worker", "index": 0},
    }
