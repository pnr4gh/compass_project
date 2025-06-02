tags = {
    "Arrays":"Array",
    "binary search":"Binary Search",
    "bitmasks": "Bitmask",
    "BFS":"Breadth-First Search",
    "combinatorics":"Combinatorics",
    "DFS": "Depth-First Search",
     "dfs and similar":"Depth-First Search",
    "divide and conquer":"Divide and Conquer",
    "doubly-linked-list":"Doubly-Linked List",
    "dp":"Dynamic Programming",
    "games":"Game Theory",
    "geometry":"Geometry",
    "Geometric":"Geometry",
    "graphs":"Graph",
    "Hash":"Hash Table",
    "hashing":"Hash Table",
    "Heap":"Heap (Priority Queue)",
    "math":"Math",
    "Mathematical":"Math",
    "matrices":"Matrix",
    "number-theory": "Number Theory",
    "number theory": "Number Theory",
     "prefix-sum":"Prefix Sum",
    "probabilities":"Probability and Statistics",
    "Segment-Tree":"Segment Tree",
    "shortest paths":"Shortest Path",
    "sliding-window":"Sliding Window",
    "sortings":"Sorting",
    "Strings":"String",
    "strings":"String",
    "trees":"Tree",
    "two-pointer-algorithm":"Two Pointers",
    "two pointers":"Two Pointers",
    "union-find":"Union Find",
    "constructive algorithms":"constructive algo",
    "data structures" : "Data Structures",
    "dsu" : "Disjoint Set"
}

def get_cf_level(score):
    if score <= 1500:
        return "Easy"
    elif score > 1500 and score <= 2500:
        return "Medium"
    elif score > 2500:
        return "Hard"


