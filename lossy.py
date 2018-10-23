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
    twitter_edges = {1:{2:0.6}, 2:{1:0.2}, 3:{1:0.5}}

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
    #alpha = [1,1,1,1,1]
    alpha = 1

    for g in graphs:
        for n in g.nodes:
            if n in final.nodes:
                #print("Exist", final.nodes[n]['activation'], alpha[n] * g.nodes[n]['activation'])
                final.nodes[n]['activation'] = final.nodes[n]['activation'] + alpha * g.nodes[n]['activation']
            else:
                final.add_node(n, activation=(alpha * g.nodes[n]['activation']))

    for g in graphs:
        for n in g.edges:
            x,y = n
            if n in final.edges:
                #print("Exist", n, final.edges[n]['influence'])
                final.edges[n]['influence'] = final.edges[n]['influence'] + alpha * g.edges[n]['influence']
            else:
                final.add_edge(x, y, influence=(alpha * g.edges[n]['influence']))

    if verbose:
        print("### RESULT ###")
        print("Nodes:", final.nodes.data())
        print("Edges:", final.edges.data())

    return final

#graph1,graph2 = generate_easy_sample()
#coupled_graph = lossy([graph1,graph2], True)

res = generate_complex_sample(1000, 60, 4, 20)
coupled_graph = lossy(res, True)

def f(I,x=None):
    #print("Start", I, x)
    if x is None:
        explore = I + []
        activated = I + []
    else:
        explore = I + [x]
        activated = I + [x]
    explored = []
    while len(explore) > 0:
        i = explore.pop(0)
        try:
            for x in list(coupled_graph.successors(i)):
                #print(explored)
                activation =  coupled_graph.nodes[x]['activation']
                total_influence = 0
                if x not in activated:
                    #explored.append(x)
                    for y in list(coupled_graph.predecessors(x)):
                        if y in activated:
                            total_influence += coupled_graph.edges[(y,x)]['influence']
                            if (total_influence > activation):
                                activated.append(x)
                                explore.append(x)
                                break
        except:
            continue
            
                

    #print("activated", activated, explored)
    return len(activated)


def greedy_algorithm(pourcentage_goal, T, R):
    print("\n### STARTING IMPROVED GREEDY ###")
    #C = list(range(len()))
    I = []
    nb = len(coupled_graph.nodes)
    counter = 0
    H = []
    for u in coupled_graph.nodes:
        heappush_max(H, (f(I,u), u))

    while len(I) < int(pourcentage_goal*nb) :
        counter += 1
        print("TURN:",counter,"; ACTIVATED:",len(I), I)

        if counter % R == 0:
            for i in range(len(H)):
                fu, u = heappop_max(H)
                heappush_max(H,(f(I,u), u))

        else:
            A = []
            for i in range(min(len(H), T)):
                fu, u = heappop_max(H)
                A.append(u)
            
            for u in A:
                H.append((u, f(I,u)))

        if len(H) > 0:
            fu, u = heappop_max(H)
            I.append(u)
        else:
            break
    
    return I

res = greedy_algorithm(0.75,15,5)
print("RESULTS:", res, f(res))





        
