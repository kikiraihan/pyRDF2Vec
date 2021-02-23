from collections import defaultdict
from typing import DefaultDict, Tuple

import attr

from pyrdf2vec.graphs import KG, Vertex
from pyrdf2vec.samplers import Sampler


@attr.s
class ObjFreqSampler(Sampler):
    """Defines the Object Frequency Weight sampling strategy.

    This sampling strategy is a node-centric object frequency approach. With
    this strategy, entities which have a high in degree get visisted more
    often.

    Attributes:
        inverse: True if Inverse Object Frequency Weight sampling strategy
            must be used, False otherwise.
            Defaults to False.
        split: True if Split Object Frequency Weight sampling strategy must
            be used, False otherwise.
            Defaults to False.
        random_state: The random_state to use to ensure ensure random
            determinism to generate the same walks for entities.
            Defaults to None.

    """

    _counts: DefaultDict[str, int] = attr.ib(
        init=False, repr=False, factory=lambda: defaultdict(dict)
    )

    def fit(self, kg: KG) -> None:
        """Fits the embedding network based on provided Knowledge Graph.

        Args:
            kg: The Knowledge Graph.

        """
        super().fit(kg)
        for vertex in kg._vertices:
            if not vertex.predicate:
                self._counts[vertex.name] = len(
                    kg.get_neighbors(vertex, is_reverse=True)
                )

    def get_weight(self, hop: Tuple[Vertex, Vertex]):
        """Gets the weight of a hop in the Knowledge Graph.

        Args:
            hop: The hop (pred, obj) to get the weight.

        Returns:
            The weight for this hop.

        """
        if len(self._counts) == 0:
            raise ValueError(
                "You must call the `fit(kg)` function before get the weight of"
                + " a hop."
            )
        return self._counts[hop[1].name]


@attr.s
class PredFreqSampler(Sampler):
    """Defines the Predicate Frequency Weight sampling strategy.

    This sampling strategy is an edge-centric approach. With this strategy,
    edges with predicates which are commonly used in the dataset are more often
    followed.
    Attributes:
        inverse: True if Inverse Predicate Frequency Weight sampling strategy
            must be used, False otherwise. Default to False.
        split: True if Split Predicate Frequency Weight sampling strategy
            must be used, False otherwise. Default to False.

    """

    _counts: DefaultDict[str, int] = attr.ib(
        init=False, repr=False, factory=lambda: defaultdict(dict)
    )

    def fit(self, kg: KG) -> None:
        """Fits the embedding network based on provided Knowledge Graph.

        Args:
            kg: The Knowledge Graph.

        """
        super().fit(kg)
        for vertex in kg._vertices:
            if vertex.predicate:
                if vertex.name in self._counts:
                    self._counts[vertex.name] += 1
                else:
                    self._counts[vertex.name] = 1

    def get_weight(self, hop: Tuple[Vertex, Vertex]):
        """Gets the weight of a hop in the Knowledge Graph.

        Args:
            hop: The hop (pred, obj) to get the weight.

        Returns:
            The weight for this hop.

        """
        if len(self._counts) == 0:
            raise ValueError(
                "You must call the `fit(kg)` function before get the weight of"
                + " a hop."
            )
        return self._counts[hop[0].name]


@attr.s
class ObjPredFreqSampler(Sampler):
    """Defines the Predicate-Object Frequency Weight sampling strategy.

    This sampling strategy is a edge-centric approach. This strategy is similar
    to the Predicate Frequency Weigh sampling strategy, but differentiates
    between the objects as well.

    Args:
        inverse: True if Inverse Predicate-Object Frequency Weight sampling
            strategy must be used, False otherwise.
            Defaults to False.
         split: True if Split Predicate-Object Frequency Weight sampling
            strategy must be used, False otherwise.
            Defaults to False.

    """

    _counts: DefaultDict[Tuple[str, str], int] = attr.ib(
        init=False, repr=False, factory=lambda: defaultdict(dict)
    )

    def fit(self, kg: KG) -> None:
        """Fits the embedding network based on provided Knowledge Graph.

        Args:
            kg: The Knowledge Graph.

        """
        super().fit(kg)
        for vertex in kg._vertices:
            if vertex.predicate:
                neighbors = list(kg.get_neighbors(vertex))
                if len(neighbors) > 0:
                    obj = neighbors[0]
                    if (vertex.name, obj.name) in self._counts:
                        self._counts[(vertex.name, obj.name)] += 1
                    else:
                        self._counts[(vertex.name, obj.name)] = 1

    def get_weight(self, hop: Tuple[Vertex, Vertex]):
        """Gets the weight of a hop in the Knowledge Graph.

        Args:
            hop: The hop (pred, obj) to get the weight.

        Returns:
            The weight for this hop.

        """
        if len(self._counts) == 0:
            raise ValueError(
                "You must call the `fit(kg)` function before get the weight of"
                + " a hop."
            )
        return self._counts[(hop[0].name, hop[1].name)]
