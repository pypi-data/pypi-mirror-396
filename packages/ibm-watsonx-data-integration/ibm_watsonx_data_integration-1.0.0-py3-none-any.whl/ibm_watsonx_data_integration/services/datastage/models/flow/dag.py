"""DAG is the underlying graph structure of a batch flow."""

import copy
import inspect
import pydantic
from abc import ABC
from collections.abc import Callable, Iterator
from ibm_watsonx_data_integration.cpd_models.connections_model import Connection
from ibm_watsonx_data_integration.services.datastage.models.schema import Schema
from typing import Any, ClassVar


class Node(ABC):
    """The node class represents nodes in the DAG, which are typically stages."""

    def __init__(self, dag: "DAG") -> None:
        """Initializes a node in a DAG."""
        self._dag = dag
        self.metadata: dict[str, Any] = {}

        try:
            self.var_name = inspect.stack()[-1].code_context[0].split("=")[0].strip()
        except Exception:
            self.var_name = "node"

    def connect_output_to(self, node: "Node") -> "Link":
        """Connects the output of this node to the input of another node.

        Args:
            node: The destination node to connect to.

        Returns:
            A Link object representing the connection.
        """
        dag = self._parent_dag if isinstance(self, SuperNode) else self._dag
        link = Link(dag)
        link.src = self
        link.dest = node
        dag.add_link(link)
        return link

    def connect_input_to(self, node: "Node") -> "Link":
        """Connects the input of this node to the output of another node.

        Args:
            node: The source node to connect from.

        Returns:
            A Link object representing the connection.
        """
        link = Link(self._dag)
        link.src = node
        link.dest = self
        self._dag.add_link(link)
        return link

    def disconnect_output_from(self, dest: "Node") -> list["Link"]:
        """Disconnects the output of this node from the input of another node.

        Args:
            dest: The destination node to disconnect from.

        Returns:
            The list of Links that were removed.
        """
        links = self._dag.remove_link(self, dest, self.get_link(dest).name)
        if not links:
            raise ValueError(f"No link found between {self} and {dest}")
        return links

    def disconnect_input_from(self, src: "Node") -> list["Link"]:
        """Disconnects the input of this node from the output of another node.

        Args:
            src: The source node to disconnect from.

        Returns:
            The list of Links that were removed.
        """
        links = self._dag.remove_link(src, self, self.get_link(src).name)
        if not links:
            raise ValueError(f"No link found between {src} and {self}")
        return links

    def get_link(self, dest: "Node") -> "Link":
        """Returns links that have the specified destination."""
        links = self.get_links_to(dest)
        if links == 0:
            raise ValueError(f"No links found between {self} and {dest}")
        if len(links) > 1:
            raise ValueError(f"Multiple links found between {self} and {dest}")
        return links[0]

    def get_links_to(self, dest: "Node") -> list["Link"]:
        """Returns: All links between this node and the destination node."""
        return self._dag.get_links_between(self, dest)

    def _get_min_primary_inputs(self) -> int:
        """Returns: The minimum number of primary inputs for this node. -1 indicates no limit."""
        return -1

    def _get_max_primary_inputs(self) -> int:
        """Returns: The maximum number of primary inputs for this node. -1 indicates no limit."""
        return -1

    def _get_min_primary_outputs(self) -> int:
        """Returns: The minimum number of primary outputs for this node. -1 indicates no limit."""
        return -1

    def _get_max_primary_outputs(self) -> int:
        """Returns: The maximum number of primary outputs for this node. -1 indicates no limit."""
        return -1

    def _get_min_reject_outputs(self) -> int:
        """Returns: The minimum number of reject outputs for this node. -1 indicates no limit."""
        return -1

    def _get_max_reject_outputs(self) -> int:
        """Returns: The maximum number of reject outputs for this node. -1 indicates no limit."""
        return -1

    def _get_min_reference_inputs(self) -> int:
        """Returns: The minimum number of reference inputs for this node. -1 indicates no limit."""
        return -1

    def _get_max_reference_inputs(self) -> int:
        """Returns: The maximum number of reference inputs for this node. -1 indicates no limit."""
        return -1


class Link:
    """The link class represents links between nodes in a DAG."""

    def __init__(self, dag: "DAG", name: str = None) -> None:
        """Initializes a link."""
        self._dag = dag
        self.name = name
        self.type = "PRIMARY"
        self.schema: Schema | None = None
        self.maps_to_link: str | None = None
        self.maps_from_link: str | None = None
        self.__src = None
        self.__dest = None

    @property
    def src(self) -> Node | None:
        """Return source of link."""
        return self.__src

    @src.setter
    def src(self, new_left: Node) -> None:
        """Set source of link."""
        self.__src = new_left

    @property
    def dest(self) -> Node | None:
        """Return destination of link."""
        return self.__dest

    @dest.setter
    def dest(self, new_right: Node) -> None:
        """Set destination of link."""
        self.__dest = new_right

    def set_name(self, name: str) -> "Link":
        """Set link name."""
        self.name = name
        return self

    def primary(self) -> "Link":
        """Sets the link type to primary. Modifies the current link object.

        Returns:
            The current link object.
        """
        self.type = "PRIMARY"
        return self

    def reference(self) -> "Link":
        """Sets the link type to reference. Modifies the current link object.

        Returns:
            The current link object.
        """
        self.type = "REFERENCE"
        return self

    def reject(self) -> "Link":
        """Sets the link type to reject. Modifies the current link object.

        Returns:
            The current link object.
        """
        self.type = "REJECT"
        return self

    def map_to_link(self, link_name: str) -> "Link":
        """Set map to link to the link name."""
        self.maps_to_link = link_name
        return self

    def map_from_link(self, link_name: str) -> "Link":
        """Set map from link to the link name."""
        self.maps_from_link = link_name
        return self

    def create_schema(self) -> "Schema":
        """Initializes the schema that the link uses.

        Returns:
            The new link object.
        """
        self.schema = Schema()
        return self.schema


class DAG:
    """DAG to represent the graph structure of a batch flow."""

    def __init__(self) -> None:
        """Initializes a DAG to represent the graph structure of a batch flow."""
        self.adj: dict[Node, dict[Node, list[Link]]] = {}
        self.is_metadata_computed = False

    def stages(self) -> Iterator[Node]:
        """Return stages in the DAG."""
        for stage in self.adj.keys():
            yield stage

    def nodes(self) -> Iterator[Node]:
        """Return nodes in the dag."""
        for node in self.adj.keys():
            yield node

    def links(self) -> Iterator[Link]:
        """Returns all links in the dag in any order."""
        for from_node, to_dict in self.adj.items():
            for to_node, links in to_dict.items():
                yield from links

    def get_link_by_name(self, name: str) -> Link | None:
        """Gets a link by name."""
        for link in self.links():
            if link.name == name:
                return link
        return None

    def links_stable(self) -> Iterator[Link]:
        """Returns links using stable sort."""
        top_order = self.get_topological_ordering(stages_only=True)
        for node in top_order:
            to_nodes = list(self.adj[node].keys())
            to_nodes.sort(key=lambda n: top_order.index(n))
            for to_node in to_nodes:
                yield from self.adj[node][to_node]

    def get_links_between(self, src: "Node", dest: "Node") -> list[Link]:
        """Get links between two nodes."""
        return self.adj.get(src, {}).get(dest, [])

    def add_node(self, node: "Node") -> "Node":
        """Add a node to the DAG."""
        self.adj.setdefault(node, {})
        return node

    def replace_node(self, old_node: Node, new_node: Node) -> None:
        """Replace a node in the DAG."""
        if old_node not in self.adj:
            raise ValueError(f"Node {old_node.label} not found in DAG")

        self.adj[new_node] = self.adj.pop(old_node)

        for from_node, to_dict in self.adj.items():
            if old_node in to_dict:
                to_dict[new_node] = to_dict.pop(old_node)

        for to_node, links in self.adj[new_node].items():
            for link in links:
                if link.src == old_node:
                    link.src = new_node
        for from_node, links in self.adj.items():
            for to_node, links in self.adj[from_node].items():
                for link in links:
                    if link.dest == old_node:
                        link.dest = new_node

        if hasattr(old_node, "metadata"):
            new_node.metadata = old_node.metadata.copy()
            new_node.metadata["var_name"] = old_node.var_name
        else:
            new_node.metadata = {"var_name": old_node.var_name}
        self.remove_node(old_node)

    def remove_node(self, node: "Node") -> None:
        """Remove a node from DAG."""
        if node in self.adj:
            del self.adj[node]
        for from_node, to_dict in self.adj.items():
            if node in to_dict:
                del to_dict[node]

    def add_link(self, link: "Link") -> None:
        """Add a link to the DAG."""
        from_node = self.add_node(link.src)
        to_node = self.add_node(link.dest)

        if link in self.adj.get(from_node, {}).get(to_node, []):
            return

        self.adj[from_node].setdefault(to_node, [])
        self.adj[from_node][to_node].append(link)

    def remove_link(self, src: "Node", dest: "Node", link_name: str) -> list[Link]:
        """Remove a link from DAG."""
        removed = []
        if src in self.adj and dest in self.adj[src]:
            kept = []
            for link in self.adj[src][dest]:
                if link.name == link_name:
                    removed.append(link)
                else:
                    kept.append(link)
            if not kept:
                del self.adj[src][dest]
            else:
                self.adj[src][dest] = kept
        return removed

    def remove_links(self, src: "Node", dest: "Node") -> list[Link]:
        """Remove links from DAG."""
        if src in self.adj and dest in self.adj[src]:
            links = self.adj[src][dest]
            del self.adj[src][dest]
            return links
        return []

    def get_topological_ordering(self, *, stages_only: bool) -> list:
        """Get topological ordering."""
        if stages_only:
            in_degrees = self.__compute_in_degrees(lambda n: isinstance(n, StageNode))
        else:
            in_degrees = self.__compute_in_degrees()

        # Queue of nodes with in-degree 0
        queue: list[Node] = [node for node, in_degree in in_degrees.items() if in_degree == 0]

        # Perform topological sorting of nodes using Kahn's algorithm
        top_order = []
        while queue:
            node = queue.pop(0)
            top_order.append(node)
            for to_node, links in self.adj[node].items():
                if to_node in in_degrees:
                    in_degrees[to_node] -= len(links)
                    if in_degrees[to_node] == 0:
                        queue.append(to_node)

        # Check if graph has cycle
        if len(top_order) != len(self.adj):
            raise ValueError(f"Graph contains cycle {self.__print_cycle(self.adj)}")

        return top_order

    def compute_metadata(self) -> None:
        """Get metadata."""
        in_degrees_stages = self.__compute_in_degrees(lambda n: isinstance(n, StageNode))
        out_degrees_stages = self.__compute_out_degrees(lambda n: isinstance(n, StageNode))

        for node in self.nodes():
            node.metadata["in_degree"] = in_degrees_stages[node]
            node.metadata["out_degree"] = out_degrees_stages[node]
            node.metadata["parents"] = []
            node.metadata["children"] = []

        top_order = self.get_topological_ordering(stages_only=False)

        # Check if graph has cycle
        if len(top_order) != len(self.adj):
            raise ValueError(f"Graph contains cycle {self.__print_cycle(self.adj)}")

        # Compute parents of each node
        for link in self.links():
            if "parents" not in link.dest.metadata:
                link.dest.metadata["parents"] = []
            if "children" not in link.src.metadata:
                link.src.metadata["children"] = []

            # If link src is already in dest's parents, skip (this can happen due to multi-links between 2 nodes)
            if link.src not in link.dest.metadata["parents"]:
                link.dest.metadata["parents"].append(link.src)
            # Do the same for src's children
            if link.dest not in link.src.metadata["children"]:
                link.src.metadata["children"].append(link.dest)

        # Compute cardinality
        for node in self.nodes():
            if not isinstance(node, StageNode):
                continue

            node.metadata["primary_inputs"] = 0
            node.metadata["primary_outputs"] = 0
            node.metadata["reference_inputs"] = 0
            node.metadata["reference_outputs"] = 0
            node.metadata["reject_inputs"] = 0
            node.metadata["reject_outputs"] = 0

            for parent in node.metadata["parents"]:
                if not isinstance(parent, StageNode):
                    continue

                links = self.adj[parent][node]
                for link in links:
                    match link.type:
                        case "PRIMARY":
                            node.metadata["primary_inputs"] += 1
                        case "REFERENCE":
                            node.metadata["reference_inputs"] += 1
                        case "REJECT":
                            node.metadata["reject_inputs"] += 1
                        case _:
                            raise ValueError(f"Unknown link type {link.type}")

            for child in node.metadata["children"]:
                if not isinstance(child, StageNode):
                    continue

                links = self.adj[node][child]
                for link in links:
                    match link.type:
                        case "PRIMARY":
                            node.metadata["primary_outputs"] += 1
                        case "REFERENCE":
                            node.metadata["reference_outputs"] += 1
                        case "REJECT":
                            node.metadata["reject_outputs"] += 1
                        case _:
                            raise ValueError(f"Unknown link type {link.type}")

        # Assign each node to a layer based on topological order
        for node in top_order:
            if not node.metadata["parents"]:
                # Source nodes reside in layer 0
                node.metadata["layer"] = 0
            else:
                # Non-source nodes reside in layer 1 + max(parents' layers)
                node.metadata["layer"] = max(parent.metadata["layer"] for parent in node.metadata["parents"]) + 1

        self.is_metadata_computed = True

    def get_connected_subgraphs(self) -> list:
        """Get connected subgraphs."""
        subgraphs: list[DAG] = []
        if not self.adj:
            return subgraphs

        # Compute mapping from nodes to their parents
        parents: dict[Node, list[Node]] = {}

        for parent_node, children_dict in self.adj.items():
            parents.setdefault(parent_node, [])
            for child_node, links in children_dict.items():
                parents.setdefault(child_node, [])
                parents[child_node].append(parent_node)

        visited = set()

        def dfs(cur_node: Node, dag: DAG) -> None:
            if cur_node in visited:
                return

            visited.add(cur_node)
            dag.adj[cur_node] = self.adj[cur_node]

            # DFS downstream
            for n in self.adj[cur_node].keys():
                dfs(n, dag)
            # DFS upstream
            for n in parents.get(cur_node):
                dfs(n, dag)

        for node in self.nodes():
            subgraph = DAG()
            dfs(node, subgraph)
            if subgraph.adj:
                subgraphs.append(subgraph)

        return subgraphs

    def get_dag_from_nodes(self, nodes: set[Node]) -> "DAG":
        """Creates a dag object only including the specified nodes.

        Returns:
            DAG: subgraph including the specified nodes
        """
        subflow_dag = DAG()
        entry_node_counter, exit_node_counter = 0, 0
        incoming, outgoing, internal = [], [], []

        for source, children_dict in self.adj.items():
            for destination, links in children_dict.items():
                # flow -> subflow
                if source not in nodes and destination in nodes:
                    incoming.append((source, destination, links))
                # subflow -> flow
                elif source in nodes and destination not in nodes:
                    outgoing.append((source, destination, links))
                # subflow -> subflow
                elif source in nodes and destination in nodes:
                    internal.append((source, destination, links))

        # internal nodes do not need to be handled specially
        for source, destination, links in internal:
            for link in links:
                subflow_dag.add_link(link)

        # for each unique incoming node, we need to create an entry node
        entry_node_counter += 1
        for source, destination, links in incoming:
            for link in links:
                entry_node = EntryNode(dag=subflow_dag, label=f"Entry node_{entry_node_counter}")
                entry_node_link = copy.deepcopy(link)  # Link(subflow_dag, name=link.name)
                entry_node_link.src = entry_node
                entry_node_link.dest = destination

                subflow_dag.add_link(entry_node_link)
                link.map_to_link(entry_node_link.name)

            subflow_dag.add_node(destination)

        # for each unique outgoing node, we need to create an exit node
        exit_node_counter += 1
        for source, destination, links in outgoing:
            for link in links:
                exit_node = ExitNode(dag=subflow_dag, label=f"Exit node_{exit_node_counter}", parent_link=link)
                exit_node_link = copy.deepcopy(link)  # Link(subflow_dag, name=link.name)
                exit_node_link.src = source
                exit_node_link.dest = exit_node

                subflow_dag.add_link(exit_node_link)
                link.map_from_link(exit_node_link.name)

        return subflow_dag

    def replace_nodes_with_supernode(self, supernode: "Node", nodes: set[Node]) -> None:
        """Replaces references of nodes with a SuperNode (used for subflow replacement).

        Args:
            supernode (SuperNode): super node to replace the set of nodes with
            nodes (set[Node]): set of nodes to replace
            outgoing (tuple[Node, Node, list[Link]]): outgoing connections from the subflow to main flow
        """
        new_dag = DAG()

        new_dag.add_node(supernode)
        for source, children_dict in self.adj.items():
            if source in nodes:
                new_dag.add_node(supernode)
                for destination, links in children_dict.items():
                    if destination not in nodes:
                        for link in links:
                            link.src = supernode
                            new_dag.add_link(link)
            else:
                new_dag.add_node(source)
                for destination, links in children_dict.items():
                    for link in links:
                        if destination in nodes:
                            link.dest = supernode
                        new_dag.add_link(link)

        self.adj = new_dag.adj

    def _merge(self, supernode: "SuperNode") -> None:
        """De-collapses supernode back into parent graph.

        Args:
            supernode (SuperNode): SuperNode object to merge back into parent.

        Raises:
            ValueError: if SuperNode object does not exist in the parent.
        """
        if supernode not in self.stages():
            raise ValueError(f"{supernode} not found in parent flow")

        # find all edges going from parent -> supernode
        incoming_edges: list[tuple[Node, Link]] = []
        for source, destinations in self.adj.items():
            if source == supernode:
                continue
            if supernode in destinations:
                for link in destinations[supernode]:
                    incoming_edges.append((source, link))

        # find all outgoing edges supernode -> parent
        outgoing_edges: dict[Node, list[Link]] = self.adj.get(supernode, {})

        # remove supernode and its edges
        self.adj.pop(supernode, None)
        for source, destinations in self.adj.items():
            destinations.pop(supernode, None)

        # restore internal nodes (nodes and links exclusively in subflow, nothing going in and out)
        for inner_source, inner_destinations in supernode._dag.adj.items():
            if isinstance(inner_source, EntryNode | ExitNode):
                continue

            self.add_node(inner_source)
            for inner_destination, links in inner_destinations.items():
                if isinstance(inner_destination, EntryNode | ExitNode):
                    continue
                self.adj.setdefault(inner_destination, {})
                # self.adj[inner_source].setdefault(inner_destination, []).extend(links)
                for link in links:
                    self.add_link(link)

        # remove all supernode references
        self.remove_node(supernode)

        # connect parent -> subnode edges
        for outside_source, outside_link in incoming_edges:
            if outside_link.maps_to_link is not None:
                outside_link.dest = supernode._dag.get_link_by_name(outside_link.maps_to_link).dest
                self.add_link(outside_link)

        # connect subflow -> parent edges
        for outside_destination, links in outgoing_edges.items():
            for link in links:
                # self.remove_link(outside_link.src, outside_link.dest, outside_link.name)
                if link.maps_from_link is not None:
                    link.src = supernode._dag.get_link_by_name(link.maps_from_link).src
                    self.add_link(link)

    def __compute_in_degrees(self, condition: Callable[[Node], bool] = lambda _: True) -> dict:
        """Compute in degrees."""
        in_degrees = {node: 0 for node in self.nodes()}
        for link in self.links():
            # local subflows do not guarantee the link destination occurs in the same DAG object
            if link.dest in in_degrees:
                in_degrees[link.dest] += 1 if condition(link.src) else 0
        return in_degrees

    def __compute_out_degrees(self, condition: Callable[[Node], bool] = lambda _: True) -> dict:
        """Compute out degrees."""
        out_degrees = {node: 0 for node in self.nodes()}
        for link in self.links():
            # local subflows do not guarantee the link source occurs in the same DAG object
            if link.src in out_degrees:
                out_degrees[link.src] += 1 if condition(link.dest) else 0
        return out_degrees

    def __str__(self) -> str:
        """Returns a string representation of dag links."""
        out = ""
        for link in self.links():
            out += f"{link.src} -> {link.dest}\n"
        return out

    def __print_cycle(self, adj: dict) -> str:
        """Returns a string for dag cycles.

        nodes: a list of nodes
        adj: a dict as adjacency graph
        output: string.
        """
        nodes = adj.keys()
        nodes_not_lead_to_deadend = set()

        for node in nodes:
            stack = [(node, [])]

            while len(stack) != 0:
                curr_node, visited = stack.pop()

                if curr_node in nodes_not_lead_to_deadend:
                    # since this node will not lead to any deadend, we ignore this node
                    continue

                if curr_node in visited:
                    # if current node is already visited in current path, we detected a cycle.
                    path = visited + [curr_node]
                    cycle = path[path.index(path[-1]) :]
                    cycle = [n.var_name for n in cycle]
                    cycle[0] = "\033[31m" + cycle[0] + "\033[0m"
                    cycle[-1] = "\033[31m" + cycle[-1] + "\033[0m"
                    return "[" + " >> ".join(cycle) + "]"

                if len(adj[node]) == 0:
                    # if this node has no outdegree. we ignore
                    nodes_not_lead_to_deadend.add(node)
                    continue

                for adj_node in adj[curr_node]:
                    if adj_node not in nodes_not_lead_to_deadend:
                        stack.append((adj_node, visited + [curr_node]))

        # if we got this far, this means our algorithm didn't detect any cycle. Though this shouldn't be the case.
        return ""


class StageNode(Node):
    """Stage node for a dag."""

    def __init__(
        self,
        dag: "DAG",
        configuration: pydantic.BaseModel,
        *,
        label: str = None,
    ) -> None:
        """Initializes a stage node."""
        super().__init__(dag)
        self.label = label
        self.configuration = configuration

    def _get_node_type(self) -> str | None:
        return self.configuration.node_type

    def _get_node_label(self) -> str | None:
        return self.label

    def _get_op_name(self) -> str | None:
        return self.configuration.op_name

    def _get_image(self) -> str:
        return self.configuration.image

    def _get_node_params(self) -> dict[str, Any] | None:
        return self.configuration._get_parameters_props()

    def _get_advanced_params(self) -> dict[str, Any] | None:
        return self.configuration._get_advanced_props()

    def _get_input_port_params(self, link: str | None = None) -> dict[str, Any] | None:
        if link:
            return self.configuration._get_input_ports_props(link)
        return self.configuration._get_input_ports_props()

    def _get_output_port_params(self, link: str | None = None) -> dict[str, Any] | None:
        if link:
            return self.configuration._get_output_ports_props(link)
        return self.configuration._get_output_ports_props()

    def _get_source_connection_params(self) -> dict[str, Any] | None:
        return self.configuration._get_source_props()

    def _get_target_connection_params(self) -> dict:
        return self.configuration._get_target_props()

    def _get_max_primary_inputs(self) -> int:
        in_card = self.configuration._get_input_cardinality()
        return in_card["max"]

    def _get_min_primary_inputs(self) -> int:
        in_card = self.configuration._get_input_cardinality()
        return in_card["min"]

    def _get_max_primary_outputs(self) -> int:
        out_card = self.configuration._get_output_cardinality()
        return out_card["max"]

    def _get_min_primary_outputs(self) -> int:
        out_card = self.configuration._get_output_cardinality()
        return out_card["min"]

    def _get_min_reject_outputs(self) -> int:
        try:
            return self.configuration._get_app_data_props()["datastage"]["minRejectOutputs"]
        except (AttributeError, KeyError):
            return super()._get_min_reject_outputs()

    def _get_max_reject_outputs(self) -> int:
        try:
            return self.configuration._get_app_data_props()["datastage"]["maxRejectOutputs"]
        except (AttributeError, KeyError):
            return super()._get_max_reject_outputs()

    def _get_min_reference_inputs(self) -> int:
        try:
            return self.configuration._get_app_data_props()["datastage"]["minReferenceInputs"]
        except (AttributeError, KeyError):
            return super()._get_min_reference_inputs()

    def _get_max_reference_inputs(self) -> int:
        try:
            return self.configuration._get_app_data_props()["datastage"]["maxReferenceInputs"]
        except (AttributeError, KeyError):
            return super()._get_max_reference_inputs()

    def _get_rcp(self) -> bool | None:
        return self.configuration.runtime_column_propagation

    def _get_acp(self) -> bool | None:
        if hasattr(self.configuration, "auto_column_propagation"):
            return self.configuration.auto_column_propagation

    def _get_connection_params(self, location: str) -> dict[str, Any] | None:
        if location == "both":
            return {
                **self.configuration._get_source_props(),
                **self.configuration._get_target_props(),
            }
        elif location == "source":
            return self.configuration._get_source_props()
        elif location == "target":
            return self.configuration._get_target_props()
        return None

    def _get_connection_name(self) -> str | None:
        return self.configuration.connection.name

    def _get_project_id(self) -> str | None:
        return self.configuration.connection.proj_id

    def _get_connection_id(self) -> str | None:
        return self.configuration.connection.asset_id

    def __str__(self) -> str:
        """Returns a string representation of the stage node."""
        return f"<{type(self).__name__}>"

    def use_connection(self, connection: Connection) -> None:
        """Adds a project-level connection to this connector stage."""
        raise NotImplementedError("Stages must override this method")


class bad_node(pydantic.BaseModel):
    """Configuration for BadNode."""

    pass


class BadNode(StageNode):
    """Represents a node that failed to generate from a batch flow json definition."""

    def __init__(self, dag: "DAG", *, label: str = None) -> None:
        """Initializes a BadNode."""
        super().__init__(dag, bad_node(), label=label)


class super_node(pydantic.BaseModel):
    """Super node configuration."""

    input_count: int | None = pydantic.Field(0, alias="input_count")
    output_count: int | None = pydantic.Field(1, alias="output_count")
    op_name: ClassVar[str] = None

    def _get_input_cardinality(self) -> dict:
        return {"min": 0, "max": -1}

    def _get_output_cardinality(self) -> dict:
        return {"min": 0, "max": -1}

    def _get_input_ports_props(self) -> dict:
        return {}

    def _get_output_ports_props(self) -> dict:
        return {}


class SuperNode(StageNode):
    """Super node that represents a subflow."""

    from ibm_watsonx_data_integration.services.datastage.models.flow_stages import FlowComposer

    def __init__(
        self,
        subflow_dag: "DAG",
        *,
        name: str = None,
        is_local: bool = False,
        label: str = None,
        # parameter_sets: List[ParameterSet] = None,
        # local_parameters: LocalParameters = None,
        rcp: bool = False,
        parent_dag: "DAG" = None,
        pipeline_id: str = None,
        url: str = None,
        parent_fc: "FlowComposer" = None,
    ) -> None:
        """Initializes a super node that represents a subflow."""
        super().__init__(subflow_dag, super_node(), label=label)

        self.name = name
        self.is_local = is_local
        self.pipeline_id: str | None = pipeline_id
        self.url: str | None = url
        # self.parameter_sets = parameter_sets or []
        # self.local_parameters = local_parameters
        self._parent_dag = parent_dag
        self.rcp = rcp
        self._parent_fc = parent_fc

    @property
    def exit_nodes(self) -> Iterator["ExitNode"]:
        """Returns an iterator containing the exit nodes in the supernode."""
        if self._dag.nodes() is not None:
            return filter(
                lambda node: isinstance(node, ExitNode),
                self._dag.nodes(),
            )
        return iter([])

    @property
    def entry_nodes(self) -> Iterator["EntryNode"]:
        """Returns an iterator containing the entry nodes in the supernode."""
        if self._dag.nodes() is not None:
            return filter(
                lambda node: isinstance(node, EntryNode),
                self._dag.nodes(),
            )
        return iter([])

    def _get_image(self) -> str | None:
        return "/data-intg/flows/graphics/flows/localsubflow.svg"

    def _get_node_type(self) -> str:
        return "super_node"


class SuperNodeRef(StageNode):
    """Node that references an external subflow."""

    def __init__(
        self,
        dag: "DAG",
        name: str,
        label: str = None,
        local_parameter_values: dict | None = None,
        subflow_id: str | None = None,
        url: str | None = None,
    ) -> None:
        """Initializes a super node reference of a subflow."""
        super().__init__(dag, label)
        self.name = name
        self.rcp: bool = False
        self._local_parameter_values = local_parameter_values if local_parameter_values is not None else {}
        self.subflow_id = subflow_id
        self.url = url

    def _get_image(self) -> str | None:
        return "/data-intg/flows/graphics/flows/subflow.svg"

    def _get_node_type(self) -> str:
        return "super_node"


class entry_node(pydantic.BaseModel):
    """Entry node configuration."""

    input_count: int | None = pydantic.Field(0, alias="input_count")
    output_count: int | None = pydantic.Field(1, alias="output_count")
    op_name: ClassVar[str] = None

    def _get_input_cardinality(self) -> dict:
        return {"min": 0, "max": 0}

    def _get_output_cardinality(self) -> dict:
        return {"min": 1, "max": 1}

    def _get_parameters_props(self) -> dict:
        return {}

    def _get_advanced_props(self) -> dict:
        return {}

    def _get_input_ports_props(self) -> dict:
        return {}

    def _get_output_ports_props(self) -> dict:
        return {}


class EntryNode(StageNode):
    """Entry node of a subflow."""

    def __init__(self, dag: "DAG", *, label: str = None, parent_link: Link = None) -> None:
        """Initializes an entry node of a subflow."""
        super().__init__(dag, entry_node())
        self.label = label or "Entry node"

        # used in local subflows to point to parent link for help with deconstruction
        self.parent_link = parent_link

    def _get_node_label(self) -> str | None:
        return self.label

    def _get_image(self) -> str | None:
        return "/data-intg/flows/graphics/palette/Input.svg"

    def _get_node_type(self) -> str:
        return "binding"


class exit_node(pydantic.BaseModel):
    """Exit node configuration."""

    input_count: int | None = pydantic.Field(1, alias="input_count")
    output_count: int | None = pydantic.Field(0, alias="output_count")
    op_name: ClassVar[str] = None

    def _get_input_cardinality(self) -> dict:
        return {"min": 1, "max": 1}

    def _get_output_cardinality(self) -> dict:
        return {"min": 0, "max": 0}

    def _get_parameters_props(self) -> dict:
        return {}

    def _get_advanced_props(self) -> dict:
        return {}

    def _get_input_ports_props(self) -> dict:
        return {}

    def _get_output_ports_props(self) -> dict:
        return {}


class ExitNode(StageNode):
    """Exit node of a subflow."""

    def __init__(self, dag: "DAG", *, label: str = None, parent_link: Link = None) -> None:
        """Initializes an exit node of a subflow."""
        super().__init__(dag, exit_node())
        self.label = label or "Exit node"

        # used in local subflows to point to parent link for help with deconstruction
        self.parent_link = parent_link

    def _get_node_label(self) -> str | None:
        return self.label

    def _get_image(self) -> str | None:
        return "/data-intg/flows/graphics/palette/Output.svg"

    def _get_node_type(self) -> str:
        return "binding"
