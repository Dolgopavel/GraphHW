import spacy
nlp = spacy.load("ru_core_news_sm")
import ru_core_news_sm
nlp = ru_core_news_sm.load()
nlp.add_pipe('sentencizer')
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from networkx.algorithms import community

# Считываем текст

def read_paragraphs(filename):
    with open(filename, "r", encoding="ANSI") as f:
        
        for line in f:
            line = line.strip()


braslet = 'C:/Users/dolgp/OneDrive/Документы/VSCode/2026-2027/granatovyy-braslet.txt'

with open(braslet, "r", encoding="ANSI") as f:
    text = f.read()

# Обрабатываем текст с помощью spaCy

doc = nlp(text)

#  Создаём граф

G = nx.DiGraph()

ROOT = "лежать"

G.add_node(
    ROOT,
    label="лежать",
    level=0,
    color="blue"
)


# Цвет вершины (красным - пунктуация, предлоги и союзы; синим - всё остальное)

def node_color(token):

    if token.is_punct:
        return "red"

    if token.pos_ in {"ADP", "CCONJ", "SCONJ"}:
        return "red"

    return "blue"


# Добавление агрегированной связи

def add_edge_aggregated(
    parent_lemma,
    child_lemma,
    child_color,
    level
):

    # Создаём вершину ребёнка, если её ещё нет

    if child_lemma not in G:

        G.add_node(
            child_lemma,
            label=child_lemma,
            level=level,
            color=child_color
        )

    # Если такое ребро уже есть — увеличиваем счётчик

    if G.has_edge(parent_lemma, child_lemma):

        G[parent_lemma][child_lemma]["count"] += 1

    # Если ребра ещё нет — создаём его

    else:

        G.add_edge(
            parent_lemma,
            child_lemma,
            count=1
        )


# Рекурсивный обход зависимостей

def process_children(
    token,
    parent_lemma,
    level,
    max_level=2
):

    if level > max_level:
        return

    for child in token.children:

        # Добавляем связь по леммам

        add_edge_aggregated(
            parent_lemma=parent_lemma,
            child_lemma=child.lemma_,
            child_color=node_color(child),
            level=level
        )

        # Переходим к детям ребёнка

        process_children(
            child,
            child.lemma_,
            level + 1,
            max_level
        )


# Находим все вхождения "лежать"

for token in doc:

    if token.lemma_ == "лежать":

        process_children(
            token,
            ROOT,
            level=1,
            max_level=2
        )

# Толщина рёбер (зависит от количества идентичных связей, то есть связей между одной и той же парой лемм)

def edge_width(count):

    return count

# Spring layout

pos = nx.spring_layout(
    G,
    k=2.5,
    iterations=200,
    seed=42
)

# Цвета вершин

node_colors = [
    data["color"]
    for node, data in G.nodes(data=True)
]

# Размеры вершин

node_sizes = []

for node, data in G.nodes(data=True):

    if node == ROOT:
        node_sizes.append(3500)

    elif data["level"] == 1:
        node_sizes.append(2200)

    else:
        node_sizes.append(1600)

# Рисуем вершины

plt.figure(figsize=(16, 12))

nx.draw_networkx_nodes(
    G,
    pos,

    node_color=node_colors,
    node_size=node_sizes,

    edgecolors="black",
    linewidths=1
)

#  Рисуем рёбра


edges = list(G.edges())

widths = [
    edge_width(G[u][v]["count"])
    for u, v in edges
]


nx.draw_networkx_edges(
    G,
    pos,

    edgelist=edges,
    width=widths,

    arrows=True,
    arrowsize=18,

    connectionstyle="arc3,rad=0.05"
)

#  Подписи вершин

labels = {
    node: data["label"]
    for node, data in G.nodes(data=True)
}


nx.draw_networkx_labels(
    G,
    pos,

    labels=labels,

    font_size=11,
    font_weight="bold"
)

#  Финальные настройки

plt.axis("off")
plt.tight_layout()
plt.show()

density = nx.density(G)
print(f"density = {density}")

communities = community.louvain_communities(
    G,
    weight = 'count',
    seed = 24
)

for i, comm in enumerate(communities, 1):
    print(f"Community {i}:")
    print(sorted(comm))