import networkx as nx
from heapq_max import *
from random import *


def generate_easy_sample():
    #Create the Facebook Graph
    facebook_nodes = [0, 1, 2]
    facebook_act = {0:0.4,1:0.2,2:0.7}
    facebook_edges = {0:{1:0.2, 2:0.5}, 2:{1:0.1}}

    facebook = nx.DiGraph()
    facebook.add_nodes_from(facebook_nodes)
    for i in facebook_nodes:
        facebook.nodes[i]['activation'] = facebook_act[i]

    for i in facebook_edges:
        for j in facebook_edges[i]:
            facebook.add_edge(i, j, influence=facebook_edges[i][j])


    #Create the Twitter Graph
    twitter_nodes = [1, 2, 3]
    twitter_act = {1:0.5,2:0.6, 3:0.3}
    twitter_edges = {1:{2:0.6}, 2:{3:0.2}, 3:{1:0.5}}

    twitter = nx.DiGraph()
    twitter.add_nodes_from(twitter_nodes)
    for i in twitter_nodes:
        twitter.nodes[i]['activation'] = twitter_act[i]

    for i in twitter_edges:
        for j in twitter_edges[i]:
            twitter.add_edge(i, j, influence=twitter_edges[i][j])
    
    return facebook, twitter

def generate_complex_sample(n_total_users, n_users, n_graph, n_edges):
    res = []
    for loop in range(n_graph):
        graph = nx.DiGraph()
        nodes = list(range(n_total_users))
        shuffle(nodes)
        nodes = nodes[:n_users]
        graph.add_nodes_from(nodes)
        for i in nodes:
            graph.nodes[i]['activation'] = random()
        for i in range(n_edges):
            x = randint(0, n_users - 1)
            y = randint(0, n_users - 1)
            graph.add_edge(nodes[x],nodes[y], influence=random())

        res.append(graph)
    return res


def lossy(graph_list, verbose=False):
    graphs = graph_list

    final = nx.DiGraph()
    
    nx.set_node_attributes(final, 'easiness', 0.4)
    
    i = 0
    
    for g in graphs:
        i += 1
        for n in g.nodes:
            easiness = 0
            for u, v, w in g.in_edges(n, data=True):
                if n in final.nodes:
                    final.nodes[n]['activation'] += g[u][v]['influence']
                else:
                    final.add_node(n, activation=g[u][v]['influence'])
                easiness += g[u][v]['influence']
            easiness = easiness / g.nodes[n]['activation']
            g.nodes[n]['easiness'+str(i)] = easiness

    i = 0
    for g in graphs:
        i += 1
        for n in g.edges:
            x,y = n
            final.add_edge(x, y, influence=(g.edges[n]['influence'] * g.nodes[y]['easiness'+str(i)]))
                
    if verbose:
        print("### RESULT ###")
        print("Nodes:", final.nodes.data())
        print("Edges:", final.edges.data())

    return final

graph1,graph2 = generate_easy_sample()
coupled_graph = lossy([graph1,graph2], True)

