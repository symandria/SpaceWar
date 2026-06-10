import random
from spacewar.roguelike.encounters import NodeType


class MapNode:
    def __init__(self, node_id, node_type, tier, row, col):
        self.node_id = node_id
        self.node_type = node_type
        self.tier = tier
        self.row = row
        self.col = col
        self.connections = []
        self.completed = False
        self.visible = False

    def __repr__(self):
        return f"Node({self.node_id}, {self.node_type.value}, t{self.tier})"


class SectorMap:
    def __init__(self):
        self.nodes = {}
        self.current_node = None
        self.tier = 1

    def generate(self, tier):
        self.tier = tier
        self.nodes = {}
        next_id = 0

        rows_per_tier = 5
        cols = 3

        start = MapNode(next_id, NodeType.START, tier, 0, 1)
        start.visible = True
        start.completed = True
        self.nodes[next_id] = start
        self.current_node = start
        next_id += 1

        prev_row_nodes = [start]

        type_pool = self._build_type_pool(tier)

        for row in range(1, rows_per_tier):
            if row == rows_per_tier - 1:
                positions = [1]
            else:
                num_nodes = random.randint(2, cols)
                positions = sorted(random.sample(range(cols), num_nodes))
            row_nodes = []

            for col_idx in positions:
                if row == rows_per_tier - 1:
                    ntype = NodeType.BOSS
                else:
                    ntype = random.choice(type_pool)

                node = MapNode(next_id, ntype, tier, row, col_idx)
                self.nodes[next_id] = node
                row_nodes.append(node)
                next_id += 1

            for prev_node in prev_row_nodes:
                closest = min(row_nodes, key=lambda n: abs(n.col - prev_node.col))
                if closest not in prev_node.connections:
                    prev_node.connections.append(closest)
                    closest.visible = True

                for node in row_nodes:
                    if abs(node.col - prev_node.col) <= 1 and random.random() < 0.5:
                        if node not in prev_node.connections:
                            prev_node.connections.append(node)
                            node.visible = True

            prev_row_nodes = row_nodes

    def _build_type_pool(self, tier):
        pool = [NodeType.BATTLE, NodeType.BATTLE, NodeType.BATTLE]
        pool.append(NodeType.ELITE)
        pool.append(NodeType.SHOP)
        pool.append(NodeType.SALVAGE)
        pool.append(NodeType.EVENT)
        if tier >= 2:
            pool.append(NodeType.ELITE)
            pool.append(NodeType.BATTLE)
        pool.append(NodeType.REST)
        return pool

    def get_available_nodes(self):
        if self.current_node is None:
            return []
        return self.current_node.connections

    def move_to(self, node):
        self.current_node = node
        node.completed = True
        for connected in node.connections:
            connected.visible = True

    def is_tier_complete(self):
        for node in self.nodes.values():
            if node.node_type == NodeType.BOSS and node.completed:
                return True
        return False

    def get_display_data(self):
        rows = {}
        for node in self.nodes.values():
            if node.row not in rows:
                rows[node.row] = []
            rows[node.row].append(node)
        for row_nodes in rows.values():
            row_nodes.sort(key=lambda n: n.col)
        return rows
