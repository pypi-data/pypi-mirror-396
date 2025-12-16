# A graphs interface to obviate demand transformation

- Authors: Sacha Verweij
- Reviewers: David Sanders, Ryan Gao, Huda Nassar, Kenton van Perseum
- Last Updated: September 2025
- Status: Draft

# Background

## Problem

1) The number of tuples in, and/or overall cost of evaluation of, some relations in the graph library nominally scales quadratically or worse with the number nodes and/or edges in the graph. `distance(u, v, d)` is a good example: It maps pairs of nodes `(u, v)` to the shortest path length between them. To the degree that the graph is strongly connected, the number of tuples `distance` contains approaches quadratic in the number of nodes. Such relations may be expensive or intractable to compute in full.

2) Moreoever, often the customer is interested in only a small subset of the tuples in such relations. For example, the customer may be interested in the `distance` from only a single node `u` to all other nodes `v`, or even between only a specific pair of nodes `(u, v)`. Where the customer tries to express that intent, they may reasonably expect the computation to be much -- i.e. asymptotically -- less expensive than computing the full relation.

3) A similar situation exists with smaller / less expensive relations. `degree(u, d)` is a good example: It maps nodes `u` to the node's degree `d`. While it is tractable and relatively inexpensive to compute, the customer may be interested in the degree of only a single node `u`, or small number of such nodes. Where the customer tries to express that intent, they may similarly reasonably expect the computation to be asymptotically less expensive than computing the full relation.

At the moment, the query builder graph library computes all relations in full, independent of the customer's expression. In combination with (1), this constrains practical customer use of the library's large/expensive relations to small graphs. In combination with (2) and (3), this can result in surprising or unsatisfying performance, without recourse.

## How does the previous version of the graph library (Rel/PyRel-v0) address this problem?

The previous version of the graph library (Rel/PyRel-v0) attempts to constrain the computed subset of some large / expensive relations like `distance` to the customer's interest. It does not provide a customer-facing mechanism to constrain computation of small / less expensive relations like `degree`.

For the former, it uses either demand transformation or inlining. Here we'll focus on demand transformation as the primary mechanism.

## How does demand transformation address this problem?

In broad strokes, demand transformation attempts to infer the customer's intent from context, and constrain computation to the inferred subset of interest of a given relation. It does this roughly as follows:

1) It attempts to infer the overall shape of the customer's interest. For example, in `distance(u, v, d)`, does the customer want to compute all `v` and `d` for some given set of `u`, or only the `d` for some given pairs `(u, v)`, or something else? This overall shape is called the _demand pattern_.

2) Given that inferred demand pattern, it attempts to infer the specifics of the customer's interest. For example, supposing that it inferred that the customer wants to compute all `v` and `d` for some given set of `u`, what is the set of `u` of interest? Let's call this specific interest the _demand set_.

3) Given that inferred demand pattern and set, it attempts to rewrite the generic algorithm it has for the relation, such that computation is constrained to the inferred demand.

## That sounds great. Why can't the query builder graph library do the same?

The query builder graph library could also use demand transformation to address parts of this problem. Exposing demand transform in query builder should be fairly straightforward. But demand transformation has some issues, and doesn't address all parts of this problem.

## What's the issue with demand transformation?

The tl;dr is that mind-reading is hard:

1) Demand transformation can fail to accurately infer the overall shape of the customer's intent. That is, it can select a demand pattern inconsistent with the customer's intent, leading to surprising and/or poor performance. For example, the customer may intend to compute `distance(u, v, d)` for a small set of `u`, while demand transformation infers that `distance(u, v, d)` should instead be computed for some set of `v`, without constraint on `u`.

2) Where demand transformation accurately infers the overall shape of the customer's intent, it can fail to infer the customer's specific intent. That is, it can select a demand set that (grossly) overapproximates the set of interest to the customer, leading to surprising and/or poor performance. For example, the customer may intend to compute `distance(u, v, d)` for some small number of combinations of `u` and `v`, while demand transformation infers a much larger set of combinations of `u` and `v`.

3) Demand transformation can introduce unnecessary and costly recursion.

Additionally, there are some outstanding soundness questions about demand transformation.

(1) and (2) have caused much customer pain, and pain on our side trying to resolve that pain. The outstanding soundness questions are also driving folks to remove demand transformation from the product.

# Design

## In the abstract

### What can we do instead, broadly speaking?

Consider that each relation allows the customer to ask a collection of questions. For example, among (many*) others, the `distance(u, v, d)` relation allows the customer to ask the following fairly common questions:

1) What is the distance from each node `u` to each node `v`? (No constraint.)
2) What is the distance from each node in a given set of nodes `u` to each node `v`? (Constrain `u`.)
3) What is the distance to each node in a given set of nodes `v` from each node `u`? (Constrain `v`.)
4) What is the distance from each node in a given set of nodes `u` to each node in a given set of nodes `v`? (Constrain `u` and `v`, separately.)
5) What is the distance between each pair of nodes `(u, v)` in a given set of pairs of nodes? (Constrain `u` and `v`, jointly, one to one.)

(Presently all of these questions are conflated in the name/spelling `distance(u, v, d)`, and the system tries to de-conflate those questions based on context with demand transformation.)

At a high level, we have two options:
A) attempt to infer the customer's intent, i.e. infer which question they are asking; or
B) allow the customer to specify their intent, i.e. explicitly express which question they are asking.

(A) leads back to something at least in spirit like demand transformation, with its attendant pitfalls/challenges.

With (B) we also have two options:
(B1) Allow the customer to specify their intent (demand pattern, demand set) via language-level features, and either add functionality under the hood to specialize generic logic to that intent, or allow libraries to provide specialized logic for given intents; or
(B2) Design this library's API to allow the customer to specify their intent.

Regarding (B1), it's not clear whether we want such language-level features, we do not have such features at this time, and the timescale for desiging and implementing such features is longer than the timescale on which we need to deliver a solid initial graphs library to customers. Fundamental feasibility of some aspects of this is not clear either.

(B2) is a pragmatic approach that will allow us to deliver something solid to customers on a reasonable timescale.

The design below takes approach (B2), allowing the customer to explicitly express common questions via the library's API.

### What about those many* other questions?

The list of questions above was far from exhaustive. For example, the customer could also ask any of:

6) What nodes are at given distance(s) `d` from each other? (Constrain `d`.)
7) What nodes `v` are at given distance(s) `d` from each node in a given set of nodes `u`? (Constrain `u` and `d`, separately.)
8) What nodes `u` have given distance(s) `d` to each node in a given set of nodes `v`? (Constrain `v` and `d`, separately.)
9) What (specified) pairs of nodes are at given distance(s) `d` from each other? (Constrain `u` and `v` jointly one to one, and `d` separately.)

and many more. Exposing means to distinctly express all such questions is probably neither practically possible (may require a constraint language in itself) nor, happily, necessary.

### Which questions do we bake directly into the API?

Three razors for which questions to bake directly into the API, and how:

(1) Common questions should be easy to ask, baked directly into the API. Uncommon questions should be possible to ask, but if asking them requires more work, is less graceful, or is less efficient, that seems reasonable; they don't need to be baked directly into the API.

(2) Make questions that we can answer efficiently easy to ask. Make questions that we cannot answer efficiently possible to ask, but perhaps less easily. If we can't answer a question efficiently, prompt the customer to think about the question they are asking / its cost, and nudge them towards efficient tools/questions.

(3) Like (2), but more extreme: Questions that involve potentially intractable or exorbitantly expensive computations are footguns if baked into the API without requiring pause-ACKs and/or injecting friction. (For example, being able to frictionlessly ask for the full `jaccard_similarity` or `distance` relation is a footgun.)

## Concrete

### How to spell the questions / express constraints on computed subsets.

The query builder graph library exposes relations through member methods of the `Graph` class, e.g. `graph.distance()`. There are at least two natural ways to allow the customer to make their intent explicit under that design:

1) provide separate method names for each supported question; and
2) provide arguments to these methods that distinguish the supported questions.

For example, suppose we directly support the following questions associated with `distance` mentioned above:

2) What is the distance from each node in a given set of nodes `u` to each node `v`? (Constrain `u`.)
3) What is the distance to each node in a given set of nodes `v` from each node `u`? (Constrain `v`.)
4) What is the distance from each node in a given set of nodes `u` to each node in a given set of nodes `v`? (Constrain `u` and `v`, separately.)
5) What is the distance between each pair of nodes `(u, v)` in a given set of pairs of nodes? (Constrain `u` and `v` jointly, one to one.)

What would we do in each case?

#### Approach (1): distinguish questions via method names.

Approach (1) might replace `.distance()` with four separate methods, each corresponding to one of the questions above, and accepting `Relationship` positional arguments containing the demand set(s) relevant to the question. To illustrate, considering `distance(u, v, d)`, these member methods might look like:
```
.distance_from(from: Relationship) # (Constrain `u` in the computed result to nodes in the argument.)
.distance_to(to: Relationship) # (Constrain `v` in the computed result to nodes in the argument.)
.distance_from_to(from: Relationship, to: Relationship) # (Separately constrain `u` and `v` in the computed result, to the nodes in the first and second arguments respectively.)
.distance_between(pairs: Relationship) # (Jointly constrain `u` and `v` in the computed result, to the pairs of nodes in the argument.)
```
These methods' arguments could be positional or keyword arguments. Each would yield a constrained `distance` relationship, backed by logic specialized to the question and provided demand set(s).

#### Approach (2): distinguish questions via keyword arguments.

Approach (2) might add keyword argument combinations to `.distance()`, each corresponding to one of the questions above, and accepting `Relationship` arguments containing the demand set(s) relevant to the question. To illustrate, considering `distance(u, v, d)`, these keyword argument combinations might look like:
```
.distance(from=Relationship) # (Constrain `u` in the computed result to nodes in keyword argument `from`.)
.distance(to=Relationship) # (Constrain `v` in the computed result to nodes in the keyword argument `to`.)
.distance(from=Relationship, to=Relationship) # (Separately constrain `u` and `v` in the computed result, to the nodes in the `from` and `to` keyword arguments respectively.)
.distance(pairs=Relationship) # (Jointly constrain `u` and `v` in the computed result, to the pairs of nodes in the `pairs` keyword argument.)
```

(Please note that in later sections we work through what approach (2) would look like for all relations presently in the library, in logical groups. Those sections are deferred to the end of this document for folks with less time/interest.)

#### Tradeoffs of these approaches.

Either of these approaches is viable. They have some tradeoffs:

a) Approach (1) requires a separate method name for each question, resulting in a potentially large set of methods of the `Graph` class. Groups of those methods will be related, as different questions associated with the same underlying relation, but that grouping will not be captured in the API's structure. In contrast, approach (2) naturally groups/consolidates related questions by method, i.e. the associated underlying relation. While the number of method-kwarg combinations in approach (2) matches the number of methods in approach (1), the API structure of approach (2) makes that complexity more manageable from both customer and developer perspectives.

b) The natural grouping/consolidation of questions in approach (2) significantly improves discoverability of related functionality relative to approach (1).

c) Related to discoverability, approach (2) allows the library to guide the customer to the functionality best for their use case: Suppose the customer calls `.distance()` with no arguments. Taking a soft stance, the library could issue a warning about cost, guiding the customer to constrain the computation via keyword arguments. Taking a hard stance, the library could throw an exception, directing the customer to constrain the computation via keyword arguments or, if they _really_ want to compute the full relation, use a slightly more verbose expression to do so. Approach (1) provides fewer opportunities in this direction: Either `.distance()` would not exist, impeding discoverability, or `.distance()` could exist, but only take the soft stance.

d) Adding a question under approach (1) requires adding a new method, whereas under approach (2) it requires extending an existing method with a new keyword argument or keyword-argument combination.

e) Approach (2) is consistent with and a natural extension of the existing API, where existing methods for parameterized algorithms accept keyword arguments that modify their behavior.

f) For relations that are not symmetric, for example `reachable(u, v)`, there is an open question around whether we should provide different permutations of that relation. The motivation being that different permutations of a given relation may be in/efficient to compute and/or use. For example, looking up `u` by `v` in `reachable(u, v)` is not efficient, whereas looking up `v` by `u` is; doing the former efficiently requires computing an additional index. Similar statements hold for computing `reachable(u, v)` for constraints on `v` versus `u`. It may be advantageous to expose both permutations of `reachable(u, v)`, e.g. as `reachable_from(u, v)`, and (assume a better name here) `can_be_reached_from(v, u)`. Under approach (1), adding that dimension results in a further (combinatorial) explosion of then relatively long and tricky names. Under approach (2), there are two options: separate a `.reachable(...kwargs...)` method into two methods with similar keyword arguments, or retain one such method but add a keyword argument, both of which seem more natural and manageable.

#### Which approach do we take?

Both the balance of tradeoffs and early polling seem to favor approach (2), which this design recommends.

##### Reviewer sentiments

- Favor approach (1):
- Favor approach (2): David Sanders, Huda Nassar, Kenton van Perseum, Ryan Gao.

##### Conclusion

Approach (2).

### How do we handle potentially intractable or exorbitantly expensive, but common, questions under this proposal?

Recall from the "Which questions do we bake directly into the API?" section above the following note:

> Questions that involve potentially intractable or exorbitantly expensive computations are footguns if baked into the API without requiring pause-ACKs and/or injecting friction.

For example, being able to frictionlessly ask for the full `distance(u, v, d)` relation is a footgun.

Injecting friction, however, requires careful balance. Consider the following use cases where minimizing friction is strongly advantageous:
1) the initial/learning experience, which we would like to make as friendly as possible;
2) exploratory use, or protoying upstream of scaling;
3) use solely on relatively small graphs (fairly common);
4) general low floor use.

How might we handle such questions while making the user experience as good as possible in use cases like 1-4?

Additional consideration: Some potentially non-scalable relations may benefit from guarding while not supporting constraints, e.g. `unique_triangle` (see section in relation-by-relation workthrough, below).

#### Initial options

Five initial options, roughly in descending order of the strength of the guard / pause-ACK involved:

##### Error to redirect.

When the customer calls `graph.distance()`, emit an error (early, at python execution time) that: 1) educates the customer about the potential cost of computing `distance` in full; 2) guides the user towards an appropriate constrained form of the call, with examples; and 3) notes that if the customer really wants to compute the full relation, they can do so using a constrained form, and shows them how to do it.

Upsides: Maximal guard against footgun. Maximal user education.
Downsides: Maximal friction. Least graceful when actually computing the full relation over small graphs.

##### Require an opt-in at call site.

Provide a keyword argument to each non-scalable relation, for sake of argument say `allow_nonscalable` defaulted to `False`, that allows the customer to control whether non-scalable relations compute or error over the given graph, per non-scalable.

When the customer calls `graph.distance()`, emit an error (early, at python execution time) that: 1) educates the user about the potential cost of computing `distance` in full; 2) guides the user towards an appropriate constrained form of the call, with examples; and 3) notes that if the customer really wants to compute the full relation, they can opt-in via `graph.distance(allow_nonscalable=True)`.

When the customer calls `graph.distance(allow_nonscalable=True)`, yield the full `distance` relation.

Upsides: Strong initial guard against the footgun. Strong user education. Risk of surprise on non-scalable computation from, e.g., setting a `Graph`-constructor-level flag (below), mitigated.
Downsides: While the initial guard against the footgun is strong, inevitably someone will opt-in, forget, and be surprised when they attempt to scale up (but seems like a reasonable/defensible risk). A bit less graceful when actually computing the full relation over small graphs.

##### Require an opt-in on Graph construction.

Provide a keyword argument to the `Graph` constructor, for sake of argument say `allow_nonscalable_relations` defaulted to `False`, that allows the customer to control whether non-scalable relations compute or error over the given graph.

With `allow_nonscalable_relations=False`, when the customer calls `graph.distance()`, emit an error (early, at python execution time) that: 1) educates the user about the potential cost of computing `distance` in full; 2) guides the user towards an appropriate constrained form of the call, with examples; and 3) notes that if the customer really wants to compute the full relation, they can opt-in via `allow_nonscalable_relations=True` on the `Graph` constructor.

With `allow_nonscalable_relations=True`, when the customer calls `graph.distance()`, yield the full `distance` relation.

Upsides: Strong initial guard against the footgun. Strong user education. Minimal friction and reasonably graceful once `allow_nonscalable_relations` is set at the `Graph` constructor level, when actually computing the full relation over small graphs.
Downsides: While the initial guard against the footgun is strong, inevitably someone will opt-in to non-scalable relations and then be surprised when some computation doesn't scale (either due to the relation for which they set the flag, or more likely due to another non-scalable relation).

##### Require an opt-in only over a certain scale.

Variation of either of the two preceding opt-in options, focused on the relation-level opt-in form for sake of argument.

When the opt-in flag is set (`graph.distance(allow_nonscalable=True)`), yield the `distance` relation in full.

When the opt-in flag is not set (`graph.distance()`), emit logic that checks graph scale prior to computing the full relation. (Note that this kind of logic can be a bit brittle, or at least was historically in Rel, given enforcing evaluation order of relations in a declarative expression can be tricky.) If the graph is below threshold scale, yield the `distance` relation in full. If the graph is above threshold scale, derive an error (necessarily late, at query evaluation time) that: 1) educates the user about the potential cost of computing `distance` in full; 2) guides the user towards an appropriate constrained form of the call, with examples; and 3) notes that if the customer really wants to compute the full relation, they can opt-in via `graph.distance(allow_nonscalable=True)`.

Upsides: Reasonable but weaker guard against the footgun, with feedback deferred from python execution to query evaluation time. Reasonable user education, but a bit later than otherwise. Least friction, maximal grace, when actually computing the full relation over small graphs.
Downsides: Feedback comes a bit later. Whether feedback comes is data-dependent, which could be quite surprising. Scale threshold selection may be tricky. Logic may have some brittleness, but also possibly not. A bit less graceful when actually computing the full relation over what the customer may perceive as small graphs that are over threshold. Maybe a bit mysterious/magical.

##### Warn to redirect, but proceed blithely.

When the customer calls `graph.distance()`, emit a warning (early, at python execution time) that: 1) educates the customer about the potential cost of computing `distance` in full; and 2) guides the user towards an appropriate constrained form of the call, with examples. But nonetheless return the full relation.

Upsides: Reasonable user education. Minimal friction, maximal grace if the customer really wants to compute the full relation.
Downsides: Risk of weak user education if (as is often the case) warnings/documentation are unread or ignored. Greatest risk of surprise. Greatest risk of expensive footgunning.

#### Additional options proposed during review

##### Require an opt-in on Graph construction, and choose your own adventure.

Kenton made the great observation that, as a user, he would like to be able to tell the library what controls / level of stricture he prefers for a given use case. Particularly, he would like a constructor-level argument that accepts, e.g., `nonscalable='error'`, `nonscalable='warn'`, and `nonscalable='allow'` (with `'error'` as the default). He characterized this approach as providing him "the best of both worlds", and noted that pandas does something along these lines with success.

##### Require an opt-in on Graph construction, choose your own adventure, and allow fine control at call sites.

Ryan and Sacha discussed layering call-site control on top of Kenton's suggestion.

#### Which option do we go with?

This author would like additional perspectives before making a recommendation.

##### Reviewer sentiments:

- David Sanders: Among the original options, David expressed preference for a combination of the opt-in approaches. Among the expanded options / after discussion, he expressed inclination to Kenton's suggestion IIRC, possibly with call-site control.
- Huda Nassar: Among the original options, "Error to redirect" was Huda's preference. Among the expanded options / after discussion, Huda expressed incliation to Kenton's proposal + call-site controls, but not without call-site controls.
- Ryan Gao: Among the original options, any of the middle three options (opt-in on construction, opt-in at call site, opt-in over certain scale) were Ryan's preference. Among the expanded options, he expressed preference for Kenton's suggestion, plus call-site control.
- Kenton van Perseum: Given the original options, Kenton suggested the first of the additional options above (require a constructor-level opt-in, and choose your own adventure). Among the expanded suggestions, IIRC he preferred to not provide `nonscalable='allow'` at the constructor level, and to not provide call-site control, at least upstream of discussion.

##### Conclusion

As of this writing, looks like constructor-level control (error, warn, allow) plus call-site control (local override).

### (High-level) implementation process considerations.

One of the virtues of the recommended approach is that, for all relations in the library that are scalable, it's an extension of the existing API that can be implemented lazily as customers need and developer bandwidth allows. For relations that are not scalable, adding pause-ACK mechanisms will be API breaking, pulling in implementation of which would be advantageous.

For whichever API changes are implemented at a given time, a phased approach is possible under the hood:

1) To start, constrained versions of a given relation can be implemented as shallow filters on the existing implementation of the full relation. This should allow for rapid, relatively inexpensive implementation of the API to pull in breakage, and for testing, feedback, and iteration.

2) Later, guided by customer need and given developer bandwidth, implementations specific to each constrained version can be written, enabling a level of (relatively predictable, reliable) performance that could not be achieved through demand transformation.

### Risks/downsides

1) This design does increase the level of complexity of the API. Excepting non-scalable relations, though, if the customer does not need that complexity (need the additional performance and control that it provides), they need not be aware of or manage it.

2) This design does ultimately require more implementations backing a given relation. That cost only need be paid, though, if/when the additional performance those tailored implementations provide is desired.

3) This design is less magical than a mechanism like demand transformation. On the other hand, that's also an upside, as are the associated performance, predictability, and reliability.

4) Reduction in reuse of relations: Everywhere the customer calls, e.g., `... = graph.distance()`, their computation hits the same, single computed relation; reuse is maximal. If the customer instead calls, e.g., `foo = graph.distance(from=some_nodes)`, the logic and computed relation are specialized to the `some_nodes` relation. The customer gets reuse everywhere they consume `foo`, but not with other `graph.distance` calls such as `graph.distance()` or `graph.distance(from=other_nodes)`. Whether the reuse or constraint is more advantageous depends on the use case, requiring some understanding and thought on part of the customer.

### Before details, what needs deciding?

#### Questions we need to answer now

1) Overall design, yay or nay?

*Reviewer sentiments*

- Ryan Gao: yay
- David Sanders: yay
- Huda Nassar: yay
- Kenton van Perseum: yay

*Conclusion*

As of this writing, appears yay.

2) Which option for handling non-scalable relations?

*Reviewer sentiments*

Please see dedicated section for reviewer sentiments.

*Conclusion*

At time of this writing, it looks like constructor-level control (error, warn, allow) plus call-site control (local override).

#### Questions that don't need to be answered in full now, but maybe partly

1) Do we want to expose different permutations of relations that aren't symmetric? Must be at least partially answered at this time, informing whether we, e.g., name the relevant relation `distance` or `distance_from` (to be paired with `distance_to`).

*Reviewer sentiments*

- David Sanders: nay
- Ryan Gao: nay
- Huda Nassar: nay
- Kenton van Perseum: nay

*Conclusion*

Consensus seems to be that the likely marginal potential performance upside is not worth the complexity and potential for confusion.

2) Which questions do we want to support? (Also see details below.) Can mostly be answered over time, informed by customer need/feedback.

### Relation-by-relation workthrough

Let's work through all relations in the graph library to develop a clearer sense of what this proposal entails. Those relations logically group by their handling under this design; we'll work through them in those logical groups, roughly from most straightforward to most tricky.

#### Logical groups

At a high level, there are two groups of relations:
1) relations that can only be computed in full; and
2) relations that can be computed in part.

This proposal does not apply to relations in group (1), which includes:
- num_nodes
- num_edges
- num_triangles
- is_connected
- diameter_range
- pagerank
- eigenvector_centrality
- betweenness_centrality
- average_clustering_coefficient
- louvain
- infomap
- label_propagation
- triangle_community

Group (2) consists of the following subgroups:

(2a): binary relations mapping each node to a single value
- degree
- indegree
- outdegree
- weighted_degree
- weighted_indegree
- weighted_outdegree
- degree_centrality
- local_clustering_coefficient
- triangle_count

(2b): binary relations mapping each node to a nominally small collection of nodes
- neighbor
- inneighbor
- outneighbor

(2c): ternary relations mapping pairs of nodes to single values, symmetric in nodes
- adamic_adar
- jaccard_similarity
- cosine_similarity
- preferential_attachment

(2d): ternary relation mapping pairs of nodes to a nominally small collection of nodes
- common_neighbor

(2e): binary relation mapping each node to an identifier, but somewhat special
- weakly_connected_component

(2f): binary relation mapping each node to a nominally large collection of nodes
- reachable_from

(2g): ternary relation mapping pairs of nodes to a single value, asymmetric in nodes
- distance

(2h): ternary relations of nodes, somewhat special
- triangle
- unique_triangle

#### Group (2a): binary relations mapping each node to a single value
- degree
- indegree
- outdegree
- weighted_degree
- weighted_indegree
- weighted_outdegree
- degree_centrality
- local_clustering_coefficient
- triangle_count

These are binary relations that map each node to a single associated value. Each tuple is efficiently computable separately.

##### Recommendation

At this time, do nothing, retaining present behavior of computing the full relation. When customers need and/or developer bandwidth allows, extend the method for each of these relations to support constraint on the set of nodes for which the relation is computed, e.g. via
```
graph.degree() # Yields the full relation, with reuse across .degree() calls.
graph.degree(nodes=Relationship) # Yields a relation specialized to the identified nodes.
```

##### Rationale

###### Computing the full relation

The number of tuples in each such relation being the number of nodes, and the cost of computing each tuple being small, computing these relations in full is reasonable even for large graphs. Consequently it seems reasonable to continue making that easy, e.g. allow `graph.degree()` to compute the full relation. Moreover, `graph.degree()` returning the full relation enables reuse; chances are this should be the default mode of use.

###### Computing subsets

**Is there is value in allowing customers to constrain these computations?**

Yes. Customers have made it clear that, with at least some of these relations (e.g. *degree), they want to be able to compute/lookup subsets of tuples in these relations without paying the cost of computing (or precomputing) the full relation.

**What questions may be worth supporting?**

Let's consider the common structure `relation(node, value)`. We can efficiently compute the result for constrained `node`. We cannot, in general, compute the result for constrained `value` meaningfully more efficiently than computing the entire relation. We cannot, in general, compute the result for `(node, value)` pairs meaningfully more efficiently than computing the tuple for `node`, i.e. constraining `node`. (There are special cases worth considering, e.g. for `value` zero or one, but such functionality would better be exposed through separate, dedicated relations such as `leaf_node`, `root_node`, `isolated_node`, and similar.) This makes constraining `node` potentially worth supporting, but probably not other constraints.

#### Group (2b): binary relations mapping each node to a nominally small collection of nodes

- neighbor
- inneighbor
- outneighbor

These are binary relations that map each of the subset of nodes with [in/out]neighbors to the nominally small collection of nodes constituting those [in/out]neighbors. Each tuple is efficiently computable separately.

##### Recommendation

At this time, do nothing, retaining present behavior of computing the full relation. When customers need and/or developer bandwidth allows, extend the method for each of these relations to support constraint on the set of (non-neighbor / first argument) nodes for which the relation is computed, e.g. via
```
graph.[in,out]neighbor() # Yields the full relation, with reuse across .[in,out]neighbor() calls.
graph.[in,out]neighbor(nodes=Relationship) # Yields a relation specialized to the identified nodes.
```

##### Rationale

###### Computing the full relation

The number of tuples in each such relation is typically proportional to the number of edges in the graph, and the cost of computing each tuple being small, computing these relations in full is typically reasonable even for large graphs. In other words, if we can work with the graph in full (i.e. its edge-list scale), we can work with these relations in full. Consequently it seems reasonable to continue making that easy, e.g. allow `graph.[in/out]neighor()` to compute the full relation. Moreover, `graph.[in/out]neighbor()` returning the full relation enables reuse; chances are this should be the default mode of use.

###### Computing subsets

**Is there value in allowing customers to constrain these computations?**

Yes. Customers have made it clear that they want to be able to compute/lookup subsets of tuples in these relations without paying the cost of computing (or precomputing) the full relation.

**What questions may be worth supporting?**

Let's consider the common structure `[in/out]neighbor(node, neigh)`. If we compute and cache a reversed edge list, we can efficiently compute the result for either of constrained `node` or `neigh` for any of these relations. Computing coupled `(node, neigh)` constrained subsets can be more efficient than either of the former in some cases, but it's not clear whether that efficiency improvement is meaningful or common enough to justify exposure.

Looking up the set of [in/out]neighbors for a given node is pretty common, i.e. constraining `node` seems reasonable. What about constraining `neigh`? `neighbor` is symmetric, so contraining `neigh` is redundant there. Computing the set of `node`s for given `neigh` in {in,out}neighbor is equivalent to computing the set of `neigh`s for given `node` in {out,in}neighbor, making this constraint somewhat redundant as well.

In sum, supporting constraint of `node` in each of these relations seems worthwhile, but other constraints are likely to be low value. Can be implemented piecemeal guided by customer feedback if need be.

#### Group (2c): ternary relations mapping pairs of nodes to single values, symmetric in nodes

- adamic_adar
- jaccard_similarity
- cosine_similarity
- preferential_attachment

These are ternary relations that map pairs of nodes to a single value. Each tuple is efficiently computable separately. Additionally, each of these relations is symmetric in the nodes in each tuple, i.e. `relation(u, v, f)` biconditionally implies `relation(v, u, f)`.

##### Recommendation

At this time, add the TBD guard/pause-ACK mechanism for non-scalable relations to calls without constraints, e.g. `graph.cosine_similarity()`.

Consider supporting constraint on `u`, on both `u` and `v` separately, and `u` and `v` jointly as pairs, in that priority order. E.g., modulo bikeshedding:
```
graph.cosine_similarity(from=Relationship)
graph.cosine_similarity(from=Relationship, to=Relationship)
graph.cosine_similarity(pairs=Relationship)
```
(Note that `from` and `to` don't seem quite right given the symmetry. Suggestions appreciated.)

##### Rationale

###### Computing the full relation

The number of tuples in each such relation can approach, or in some cases (`preferential_attachment`) always is, quadratic in the number of nodes. Over the graphs that we've encountered in practice, computing these relations in full for large graphs tends to be intractable or exorbitantly expensive, and should be guarded against.

###### Computing subsets

**Is there value in allowing customers to constrain these computations?**

Yes. Computing subsets of these relations is the nominal mode of exercise.

**What questions may be worth supporting?**

Let's consider the common structure `relation(u, v, f)`.

Given the symmetry of these relations, it makes sense to constrain `u`, or both `u` and `v` separately, or both `u` and `v` as `(u, v)` pairs, but not to constrain `v` alone (redundant with constraining `u` alone). We can efficiently compute all three of these constraint types, and all three seem common. We should probably support all three, and at least the first two out of the gate.

What about constraining `f`, or combinations of `f` and `v`? Some questions along these lines -- e.g., give me all the nodes whose cosine similarity to a given node is 1.0 -- may not be uncommon. And it's possible that we can compute some of them more efficiently than constraining on `u` and `v` and then filtering on `f` post. But this becomes tricky very fast, is likely out of scope for the foreseeable future, and likely can be added in a non-breaking way, so let's defer.

### Group (2d): ternary relation mapping pairs of nodes to a nominally small collection of nodes
- common_neighbor

This is a ternary relationship that maps pairs of nodes to a set of associated nodes. Each tuple (or subset of tuples for a given leading pair of nodes) is efficiently computable separately. Additionally, this relation is symmetric in the leading pairs of nodes in each tuple, i.e. `common_neighbor(u, v, w)` biconditionally implies `common_neighbor(v, u, w)`.

##### Recommendation

At this time, add the TBD guard/pause-ACK mechanism for non-scalable relations to calls without constraints (i.e. `graph.common_neighbor()`).

Consider supporting constraint on `u`, on both `u` and `v` separately, and `u` and `v` jointly as pairs, in that priority order. E.g., modulo bikeshedding:
```
graph.common_neighbor(from=Relationship)
graph.common_neighbor(from=Relationship, to=Relationship)
graph.common_neighbor(pairs=Relationship)
```
(Note that `from` and `to` don't seem quite right given the symmetry. Suggestions appreciated.)

Only implement constraint on all of `u`, `v`, and `w` if customers indicate need.

##### Rationale

###### Computing the full relation

The number of tuples in this relation can scale quadratically in the number of edges or even cubically in the number of nodes in the graph. Computing this relation in full for large graphs is often intractable or exorbitantly expensive.

###### Computing subsets

**Is there value in allowing customers to constrain these computations?**

Yes. The nominal mode of exercise of this relation is over a subset of the possible tuples.

**What questions may be worth supporting?**

Let's consider `common_neighbor(u, v, w)`.

Given the symmetry of this relation, it makes sense to constrain `u`, or both `u` and `v` separately, or both `u` and `v` as `(u, v)` pairs, or all of `u`, `v`, and `w` separately, or as a triplet `(u, v, w)`, but constraining `v` alone is redundant.

Does it make sense to constrain `w` alone? That's equivalent to asking for the outer product of `w`'s neighbors with that same set, so not really.

Does it make sense to constrain `w` and `u` without `v` (or `w` and `v` without `u`), separately or jointly? Those are equivalent to asking for the neighbors of `w` in a weird way, so not really.

We can efficiently compute constraining `u`, constraining both `u` and `v` separately, constraining both `u` and `v` as a pair `(u, v)`, and constraining `u`, `v`, and `w` as a triplet `(u, v, w)`. Constraining `u`, `v`, and `w` separately may be more efficiently computable than computing `u` and `v` separately and then filtering on `w`, but to the degree that it is more efficient, it may not be much more efficient, and the question may not be common.

#### Group (2e): binary relation mapping each node to an identifier, but somewhat special
- weakly_connected_component

This is a binary relationship that maps each node to a single value, where that single value happens to be another node identifying the leading node's weakly connected component.

##### Recommendation

At this time, do nothing, retaining present behavior of computing the full relation. If customers need and developer bandwidth allows, consider extending this relation's method to support constraint on the set of nodes for which the relation is computed, e.g. via
```
graph.weakly_connected_component() # Yields the full relation, with reuse across .weakly_connected_component() calls.
graph.weakly_connected_component(nodes=Relationship) # Yields a relation specialized to the identified nodes.
```

##### Rationale

###### Computing the full relation

The number of tuples in this relation matches the number of nodes in the graph. It can be computed in full fairly efficiently (at least in princple). Computing the full relation is the nominal mode of exercise.

###### Computing subsets

**Is there value in allowing customers to constrain these computations?**

Possibly, yes. May need more customer insight.

**What questions may be worth supporting?**

Constraining on the node (first argument, as opposed to component identifier, i.e. second argument) is likely the only constraint that makes sense in practice.

Computing a given tuple requires computation of all tuples associated with that given tuple's weakly connected component. This means there can be no upside to constraint (if the graph is weakly connected), or substantial upside to constraint (if it contains many separate components). In many cases the benefit of reuse makes constraint fraught, but in other use cases not using constraint will be fraught. Allowing constraint may be worthwhile as such.

#### Group (2f): binary relation mapping each node to a nominally large collection of nodes
- reachable_from

This is a binary relation that maps each of the subset of nodes with (out)edges to the collection of nodes that can be reached from that node. This relation is not symmetric.

##### Recommendation

At this time, add the TBD guard/pause-ACK mechanism for non-scalable relations to calls without constraints (i.e. `graph.reachable_from()`). Depending on decision on whether to expose different permutations of asymmetric relations, potentially rename accordingly.

Consider supporting constraint on `u` (for `reachable_from(u, v)`), constraint on `v`, constraint on both `u` and `v` separately, and constraint on `u` and `v` jointly as pairs, in that priority order. E.g., modulo bikeshedding:
```
graph.reachable(from=Relationship)
graph.reachable(to=Relationship)
graph.reachable(from=Relationship, to=Relationship)
graph.reachable(pairs=Relationship)
```

###### Other notes

Regarding asymmetry: In some cases `reachable_from(u, v)` is needed (or more descriptively, `nodes_downstream_of(u, v)`), and in other cases, say, `nodes_upstream_of(v, u)`. Not sure whether we want to separate those, given that generating one from the other is inexpensive. Perspectives appreciated.

In any case, if we add keyword arguments `from`, `to`, and `pairs`, or similar, the `_from` in `reachable_from` no longer seems right. Might want to call this something else. `reach` or `reachability` may be the most common terms, modulo (non-reflexive) `transitive_closure` outside the graph-specific world.

##### Rationale

###### Computing the full relation

The number of tuples in this relation can approach quadratic in the number of nodes in the graph, and computing it in full is often exorbitantly expensive or intractable for large graphs.

###### Computing subsets

**Is there value in allowing customers to constrain these computations?**

Yes. The nominal mode of exercise of this relation is with constraint to a subset of the possible tuples.

**What questions may be worth supporting?**

Let's consider `reachable_from(u, v)`.

It makes sense to constrain `u`, or `v`, or both `u` and `v` separately, or both `u` and `v` as `(u, v)` pairs; these all seem like reasonable and fairly common questions.

Efficiency perspective: Computing the full relation is `O(edges*(edges + nodes))` IIRC. Constraining `u` requires `O(|u|*(edges + nodes))` or so, and likewise for constraining `v`. Constraining `u` and `v` to pairs `(u, v)` requires roughly `O(|(u,v)|*(edges + nodes))` in the worst case, but in practice early termination can reduce that to roughly `|(u, v)|*O(distance(u, v))`. Constraining `u` and `v` separately hypothetically can be done a bit more efficiently than constraining `u` only. Each of these potentially has merit and could warrant its own implementation.

#### Group (2g): ternary relation mapping pairs of nodes to a single value, asymmetric in nodes
- distance

This is a ternary relation that maps pairs of nodes to the distance between them. This relation is not symmetric in its leading pair of nodes.

##### Recommendation

At this time, add the TBD guard/pause-ACK mechanism for non-scalable relations to calls without constraints (i.e. `graph.distance()`). Depending on decision on whether to expose different permutations of asymmetric relations, potentially rename accordingly.

Consider supporting constraint on `u` (for `distance(u, v, d)`), constraint on `v`, constraint on both `u` and `v` separately, and constraint on `u` and `v` jointly as pairs, in that priority order. E.g., modulo bikeshedding:
```
graph.distance(from=Relationship)
graph.distance(to=Relationship)
graph.distance(from=Relationship, to=Relationship)
graph.distance(pairs=Relationship)
```

Questions related to constraint on `d` probably warrant a separate method if supported; can be driven by customer demand.

##### Other notes:

Regarding the asymmetry: In some cases `distance_from(u, v)` is needed, and in other cases, say, `distance_to(v, u)`. Not sure whether we want to separate those, given that generating one from the other is inexpensive. Perspectives appreciated.

##### Rationale

###### Computing the full relation

The number of tuples in this relation can approach quadratic in the number of nodes in the graph, and computing it in full is often exorbitantly expensive or intractable for large graphs.

###### Computing subsets

**Is there value in allowing customers to constrain these computations?**

Yes. The nominal mode of exercise of this relation is with constraint to a subset of the possible tuples.

**What questions may be worth supporting?**

Let's consider `distance(u, v, d)`.

It makes sense to constrain `u`, or `v`, or both `u` and `v` separately, or both `u` and `v` as `(u, v)` pairs; these all seem like reasonable and fairly common questions.

What about constraining `d`? Some questions corresponding to constraining `d` (in combination with `u` and `v`) seem worth supporting. Particularly, constraining `u` and `d` is equivalent to asking "what is the d-shell of nodes from `u`", similar to looking for a ball around `u` with a given radius. `v` and `d` yields a similar question, for inbound paths. But it's probably best to expose these questions via other/dedicated relations/methods, as with `ball`, e.g. `shell`. Apart from that, constraining all of `u`, `v`, and `d` at once isn't particularly useful given constraint of `u` and `v` to a pair `(u, v)`, and constraining just `d` doesn't seem like a very common question ("yield all pairs of nodes in the graph separated by distance `d`").

#### Group (2h): ternary relations of nodes, somewhat special
- triangle
- unique_triangle

These are ternary relations of nodes that include all permutations (`triangle`) or unique ordered permutations (`unique_triangle`) of triangles in the graph.

##### Recommendation

Go outside.

###### `unique_triangle`

At this time, add the TBD guard/pause-ACK mechanism for non-scalable relations to calls without constraints. Do not plan to add calls with constraints later, in favor of adding them to `triangle` only.

###### `triangle`

At this time, add the TBD guard/pause-ACK mechanism for non-scalable relations to calls without constraints (i.e. `graph.triangle()`).

Consider supporting constraint on `u` (for `triangle(u, v, w)`), constraint on pairs `(u, v)`, and constraint on triples `(u, v, w)`. E.g., modulo bikeshedding:
```
graph.triangle(nodes=Relationship)
graph.triangle(pairs=Relationship)
graph.distance(triples=Relationship)
```

##### Rationale

It's nice outside.

###### Computing the full relation

Worst case number of triangles, and ergo tuples, is O(|E|^{3/2}), and likewise with computational complexity. Typical case is near linear. Computing the full relation is not an unreasonable ask in many cases, but can explode in others. Tricky middle-ground case. Perhaps best to err on the side of caution and require a pause-ACK, as long as the ACK mechanism remains easy to exercise.

###### Computing subsets

**Is there value in allowing customers to constrain these computations?**

Yes. For example, being able to ask "does this triplet of nodes form a triangle?" is a common question.

**What questions may be worth supporting?**

Let's consider `[unique_]triangle(u, v, w)`.

It's common to ask "is this triple a triangle?", which suggests allowing `triangle(triple=Relationship)` or similar.

It's common to ask "what triangles include this given node / these given nodes?", which suggests allowing `triangle(node=Relationship)` or similar.

It may not be uncommon to ask "what nodes form triangles with this given pair of nodes / these given pairs of nodes?", which suggests allowing `triangle(pair=Relationship)`.

Each of the three preceding questions can be answered meaningfully more efficiently than computing all triangles. Each of the three preceding questions is most relevant to `triangle`; asking them same questions through `unique_triangle` doesn't seem ergonomic, though it is possible.

#### Groups that don't exist yet but are worth mentioning

As of this writing, the library does not contain any unary relations that contain more than one tuple. But chances are it will at some point, e.g. `leaf_node`, `root_node`, `isolated_node`, and similar. Chances are these will all be of a kind where it's reasonable to compute the full relation without guards, to which the ability to constrain the computation can be added later if need be.

# Appendix

## A recent customer problem worked under this design

A customer ran into issues making a computation along the lines of the following efficient. The computation was roughly: For a given node, compute the set of nodes downstream (variant one) or upstream (variant two) of that node, and filter those nodes for (one case) leaves and (another case) roots. Under this design, specifically with at least constructor-level controls on allowing non-scalable relations with minimal friction, what would that look like, both in prototyping (low floor perspective) and refinement for production (high ceiling perspective)?

Let's focus on variant one, and to make the example a bit more challenging and interesting, let's allow multiple seed nodes.

Low floor use (prototyping):
```
# Given a seed node, find the leaf nodes downstream of that seed node.

model = Model(...)
graph = Graph(model, ..., nonscalable='allow')

seeds = model.Relationship("{Node} is of interest")
where(... graph.Node is of interest ...).define(seeds(graph.Node))

reachable = graph.reachable()
outdegree = graph.outdegree()

leaves_reachable_from_seed = model.Relationship("seed {Node} can reach leaf {Node}")

seed_node = graph.Node.ref()
reachable_leaf_node = graph.Node.ref()

define(
    leaves_reachable_from_seed(seed_node, reachable_leaf_node)
).where(
    seeds(seed_node),
    reachable(seed_node, reachable_leaf_node),
    outdegree(reachable_leaf_node, 0)
)
```
In prototyping / low-floor use, the user need not bother with constraints, definition and propagation of demand sets, and with `nonscalable='allow'` friction using non-scalable relations is minimized. On the other hand, `graph.reachable()` and `graph.outdegree()` are computed in full; i.e. this formulation is not efficient unless the cost of computing the reachable and outdegree relations in full is amortized over many instances of the above query (and that assumes that computiong the reachable relation is tractable at all).

High ceiling use (refinement for production):
```
# Given a seed node, find the leaf nodes downstream of that seed node.

model = Model(...)
graph = Graph(model, ...)

seeds = model.Relationship("{Node} is of interest")
where(... graph.Node is of interest ...).define(seeds(graph.Node))

reachable_from_seed = graph.reachable(from=seeds)
# yields Relationship("seed {Node} can reach {Node}")

reached_node = graph.Node.ref()
reached_nodes = model.Relationship("{Node} can be reached from some seed")
define(reached_nodes(reached_node)).where(reachable_from_seeds(graph.Node, reached_node))

reached_node_outdegree = graph.outdegree(of=reached_nodes)
# yields Relationship("{Node} reachable from some seed has {outdegree:Integer}")

leaves_reachable_from_seed = model.Relationship("seed {Node} can reach leaf {Node}")

seed_node = graph.Node.ref()
reached_leaf_node = graph.Node.ref()

define(
    leaves_reachable_from_seed(seed_node, reached_leaf_node)
).where(
    reachable_from_seed(seed_node, reached_leaf_node),
    reached_node_outdegree(reached_leaf_node, 0)
)
```
In refinement for production / high-ceiling use, the user must specify constraints, and define and propagate demand sets. On the other hand, only relevant subsets of `graph.reachable()` and `graph.outdegree()` are computed; i.e. this formulation is relatively efficient, and is computable even if the reachable relation is not tractable to comptue in full.
