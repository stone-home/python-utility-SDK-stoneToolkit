import pytest
from stone_lib.data_structure.bi_directional_links import CircularDoublyLinkedList, NonCircularDoublyLinkedNode


class TestCircularDoublyLinkedList:
    @pytest.fixture
    def setup_node(self):
        return CircularDoublyLinkedList("node1")

    @pytest.fixture
    def setup_two_nodes(self):
        node1 = CircularDoublyLinkedList("node1")
        node2 = CircularDoublyLinkedList("node2")
        node1.insert_after(node2)
        return node1, node2

    def test_initial_node(self, setup_node):
        node = setup_node
        assert node.value == "node1"
        assert node.prev == node
        assert node.next == node

    def test_insert_after(self, setup_node):
        node1 = setup_node
        node2 = CircularDoublyLinkedList("node2")
        node1.insert_after(node2)
        assert node1.next == node2
        assert node2.prev == node1
        assert node2.next == node1
        assert node1.prev == node2

    def test_insert_before(self, setup_node):
        node1 = setup_node
        node2 = CircularDoublyLinkedList("node2")
        node1.insert_before(node2)
        assert node1.prev == node2
        assert node2.next == node1
        assert node2.prev == node1
        assert node1.next == node2

    def test_remove(self, setup_two_nodes):
        node1, node2 = setup_two_nodes
        node2.remove()
        assert node1.next == node1
        assert node1.prev == node1
        assert node2.prev == node2
        assert node2.next == node2

    def test_search_existing_value(self, setup_two_nodes):
        node1, node2 = setup_two_nodes
        found_node = node1.search("node2")
        assert found_node == node2

    def test_search_non_existing_value(self, setup_two_nodes):
        node1, _ = setup_two_nodes
        found_node = node1.search("node3")
        assert found_node is None

    def test_equality(self, setup_two_nodes):
        node1, node2 = setup_two_nodes
        node3 = CircularDoublyLinkedList("node1")
        assert node1 != node2
        assert node1 != node3
        assert node1 == node1

    def test_str_and_repr(self, setup_node):
        node = setup_node
        assert str(node) == "node1"
        assert repr(node) == "CircularDoublyLinkedList(node1)"


# Run the test file with: pytest test_your_module.py  # Replace 'test_your_module.py' with the actual filename.

class TestNonCircularDoublyLinkedNode:
    @pytest.fixture
    def setup_node(self):
        return NonCircularDoublyLinkedNode("node1")

    @pytest.fixture
    def setup_two_nodes(self):
        node1 = NonCircularDoublyLinkedNode("node1")
        node2 = NonCircularDoublyLinkedNode("node2")
        node1.insert_after(node2)
        return node1, node2

    def test_initial_node(self, setup_node):
        node = setup_node
        assert node.value == "node1"
        assert node.prev is None
        assert node.next is None

    def test_insert_after(self, setup_node):
        node1 = setup_node
        node2 = NonCircularDoublyLinkedNode("node2")
        node1.insert_after(node2)
        assert node1.next == node2
        assert node2.prev == node1
        assert node2.next is None
        assert node1.prev is None

    def test_insert_before(self, setup_node):
        node1 = setup_node
        node2 = NonCircularDoublyLinkedNode("node2")
        node1.insert_before(node2)
        assert node1.prev == node2
        assert node2.next == node1
        assert node2.prev is None
        assert node1.next is None

    def test_remove(self, setup_two_nodes):
        node1, node2 = setup_two_nodes
        node2.remove()
        assert node1.next is None
        assert node1.prev is None
        assert node2.prev is None
        assert node2.next is None

    def test_search_existing_value(self, setup_two_nodes):
        node1, node2 = setup_two_nodes
        found_node = node1.search("node2")
        assert found_node == node2

    def test_search_non_existing_value(self, setup_two_nodes):
        node1, _ = setup_two_nodes
        found_node = node1.search("node3")
        assert found_node is None

    def test_str_and_repr(self, setup_node):
        node = setup_node
        assert str(node) == "node1"
        assert repr(node) == "DoublyLinkedNode(node1)"
