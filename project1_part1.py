# Import libraries.
from heapq_max import *
import networkx as nx
import random

# Define constants.
NUMBER_OF_NODES = 10
EDGE_PROBABILITY = 0.1
SMALL_TEST = True

# Read names from file.
if SMALL_TEST:
    names = ['orange','yellow','blue','green','grey']
    used_names = ['orange','yellow','blue','green','grey']
else:    
    #text_file = open('names.txt', 'r')
    text_file = open('names_short.txt', 'r')
    lines = text_file.readlines()
    text_file.close()
    
    # Put names in list and create set to store used ones.
    names = [line.split()[0] for line in lines]
    used_names = set()

if SMALL_TEST:
    # Create networks.
    network_1 = nx.DiGraph()
    network_1.add_edges_from([('n1_1', 'n1_2'),('n1_1', 'n1_3'), ('n1_2', 'n1_3')])
    network_2 = nx.DiGraph()
    network_2.add_edges_from([('n2_1', 'n2_3'),('n2_2', 'n2_1'), ('n2_3', 'n2_2')])
    network_3 = nx.DiGraph()
    network_3.add_edges_from([('n3_1', 'n3_2'),('n3_2', 'n3_3'), ('n3_2', 'n3_4'), ('n3_3', 'n3_4')])
else:
    # Generate random networks.
    network_1 = nx.fast_gnp_random_graph(NUMBER_OF_NODES, EDGE_PROBABILITY, seed = 1, directed = True)
    network_2 = nx.fast_gnp_random_graph(NUMBER_OF_NODES, EDGE_PROBABILITY, seed = 2, directed = True)
    network_3 = nx.fast_gnp_random_graph(NUMBER_OF_NODES, EDGE_PROBABILITY, seed = 3, directed = True)

# Put networks in a list.
networks = [network_1, network_2, network_3]

if SMALL_TEST:
    # TEST: Add node names for test data.
    network_1.node['n1_1']['name'] = 'orange'
    network_1.node['n1_2']['name'] = 'yellow'
    network_1.node['n1_3']['name'] = 'blue'
    
    network_2.node['n2_1']['name'] = 'green'
    network_2.node['n2_2']['name'] = 'yellow'
    network_2.node['n2_3']['name'] = 'blue'
    
    network_3.node['n3_1']['name'] = 'orange'
    network_3.node['n3_2']['name'] = 'grey'
    network_3.node['n3_3']['name'] = 'green'
    network_3.node['n3_4']['name'] = 'yellow'
    
    # TEST: Add node thresholds for test data.
    network_1.node['n1_1']['threshold'] = 0.4
    network_1.node['n1_2']['threshold'] = 0.7
    network_1.node['n1_3']['threshold'] = 0.2
    
    network_2.node['n2_1']['threshold'] = 0.3
    network_2.node['n2_2']['threshold'] = 0.6
    network_2.node['n2_3']['threshold'] = 0.5
    
    network_3.node['n3_1']['threshold'] = 0.5
    network_3.node['n3_2']['threshold'] = 0.1
    network_3.node['n3_3']['threshold'] = 0.2
    network_3.node['n3_4']['threshold'] = 0.5
    
    # TEST: Add edge weights for test data.
    network_1.edges['n1_1', 'n1_2']['weight'] = 0.5
    network_1.edges['n1_1', 'n1_3']['weight'] = 0.2
    network_1.edges['n1_2', 'n1_3']['weight'] = 0.1
    
    network_2.edges['n2_1', 'n2_3']['weight'] = 0.5
    network_2.edges['n2_3', 'n2_2']['weight'] = 0.6
    network_2.edges['n2_2', 'n2_1']['weight'] = 0.2
    
    network_3.edges['n3_1', 'n3_2']['weight'] = 0.1
    network_3.edges['n3_2', 'n3_3']['weight'] = 0.3
    network_3.edges['n3_2', 'n3_4']['weight'] = 0.4
    network_3.edges['n3_3', 'n3_4']['weight'] = 0.9
else:
    # Relabel network nodes.
    for network in networks:
        relabel_dict = {}
        for i in range(NUMBER_OF_NODES):
            relabel_dict[i] = 'n' + str(networks.index(network) + 1) + '_'  + str(i + 1)
        nx.relabel_nodes(network, relabel_dict, copy = False)

    # Add network node and edge attributes.
    for network in networks:
        for (u, v) in network.edges():
            network.edges[(u,v)]['weight'] = random.random()    
        
        names_temp = names.copy()
        name_dict = {}
        threshold_dict = {}
        
        for node in network.nodes:
            name = random.choice(names_temp)
            name_dict[node] = name
            used_names.add(name)
            names_temp.remove(name)
            threshold_dict[node] = random.random()
        
        nx.set_node_attributes(network,  name_dict, 'name')
        nx.set_node_attributes(network, threshold_dict, 'threshold')
        
        # Normalize edge weights so that all incoming edge will add up to 1 per node.
        for node in network.nodes:
            in_edge_sum = 0
            in_edges = network.in_edges(node)
            for edge in in_edges:
                in_edge_sum += network[edge[0]][edge[1]]['weight']
                
            for edge in in_edges:
                network[edge[0]][edge[1]]['weight'] /= in_edge_sum

# # Print for check.
# print('################# NETWORK 1 #################')
# print(network_1.nodes())
# print(network_1.edges())
# print(nx.get_edge_attributes(network_1, 'weight'))
# print(nx.get_node_attributes(network_1, 'name'))
# print(nx.get_node_attributes(network_1, 'threshold'))

# print('################# NETWORK 2 #################')
# print(network_2.nodes())
# print(network_2.edges())
# print(nx.get_edge_attributes(network_2, 'weight'))
# print(nx.get_node_attributes(network_2, 'name'))
# print(nx.get_node_attributes(network_2, 'threshold'))

# print('################# NETWORK 3 #################')
# print(network_3.nodes())
# print(network_3.edges())
# print(nx.get_edge_attributes(network_3, 'weight'))
# print(nx.get_node_attributes(network_3, 'name'))
# print(nx.get_node_attributes(network_3, 'threshold'))

# Combine networks.
combined_network = nx.compose_all(networks)

# Add new edges with gateway nodes with weight.
for name in used_names:
    for network in networks:
        for node, node_name in nx.get_node_attributes(network, 'name').items():
            if name == node_name:
                out_edges = []
                if len(network.out_edges(node)) > 0:
                    out_edges = network.out_edges(node)
                for edge in out_edges:
                    combined_network.remove_edge(edge[0],edge[1])
                    combined_network.add_edge(name, edge[1], attr_dict = {'weight': network.edges[(edge[0],edge[1])]['weight']})

# Add 0 threshold to gateway nodes.
for name in used_names:
    if name in combined_network:
        combined_network.node[name]['threshold'] = 1

# Add connections for same user in different networks.
# Representative nodes - gateway nodes connection.
for name in used_names:
    if name in combined_network:
        for node, node_name in nx.get_node_attributes(combined_network, 'name').items():
            if name == node_name:
                combined_network.add_edge(name, node, attr_dict = {'weight': combined_network.node[node]['threshold']})
                combined_network.add_edge(node, name, attr_dict = {'weight': 1})
                
# Representative nodes - representative nodes connection.
for name in used_names:
    for node, node_name in nx.get_node_attributes(combined_network, 'name').items():
        for node2, node_name2 in nx.get_node_attributes(combined_network, 'name').items():
            if node != node2 and node_name == node_name2 and not combined_network.has_edge(node, node2):
                combined_network.add_edge(node, node2, attr_dict = {'weight': combined_network.node[node2]['threshold']})
                combined_network.add_edge(node2, node, attr_dict = {'weight': combined_network.node[node]['threshold']})

# Add dummy nodes.
for name in used_names:
    is_in_network = ['False0', 'False1', 'False2']
    for network in networks:
        for node, node_name in nx.get_node_attributes(network, 'name').items():
            if name == node_name:
                is_in_network[networks.index(network)] = 'True' + str(networks.index(network))
                   
    for found in is_in_network:
        index = is_in_network.index(found)
        if ('False' + str(index)) == found:
            networks[index].add_node('n' + str(index + 1) + '_' + str(networks[index].number_of_nodes() + 1), attr_dict = {'name': name})
            combined_network.add_node('n' + str(index + 1) + '_' + str(networks[index].number_of_nodes()), attr_dict = {'name': name, 'threshold': 1})

# Print for check.
#print(combined_network.number_of_nodes())
#print(combined_network.number_of_edges())
#print(combined_network.nodes())
#print(combined_network.edges())
#for node, data in combined_network.nodes(data = True):
#    print(node, data)    
#for (u, v, wt) in combined_network.edges.data():
#    print(u, v, wt)

coupled_graph = combined_network

# Print for check.
#print(coupled_graph.nodes.data())
#print(coupled_graph.edges.data())

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
                activation =  coupled_graph.nodes[x]['attr_dict']['threshold']
                total_influence = 0
                if x not in activated:
                    #explored.append(x)
                    for y in list(coupled_graph.predecessors(x)):
                        if y in activated:
                            total_influence += coupled_graph.edges[(y,x)]['attr_dict']['weight']
                            if (total_influence >= activation):
                                activated.append(x)
                                explore.append(x)
                                break
        except Exception as e:
            continue
            
    if len(activated) > 1:
        print("F:",len(I), len(activated))
    return len(activated)


def greedy_algorithm(pourcentage_goal, T, R, verbose=False):
    print("\n### STARTING IMPROVED GREEDY ###")

    #C = list(range(len()))
    I = []
    nb = len(coupled_graph.nodes)
    counter = 0
    H = []
    for u in coupled_graph.nodes:
        heappush_max(H, (f(I,u), u))


    while f(I)/nb < pourcentage_goal:
        counter += 1
        if (verbose):
            print("ACTIVATED:",len(I), "; POURCENTAGE:", "{0:.2f}".format(f(I)/nb))

        if counter % R == 0:
            if (verbose):
                print("FULL ROUND !")
            for i in range(len(H)):
                if (verbose and i % 200 == 0):
                    print("POURCENTAGE:","{0:.2f}".format(i/len(H)))
                fu, u = heappop_max(H)
                heappush_max(H,(f(I,u), u))

        else:
            A = []
            for i in range(min(len(H), T)):
                fu, u = heappop_max(H)
                A.append(u)
            
            for u in A:
                heappush_max(H, (f(I,u), u))

        if len(H) > 0:
            fu, u = heappop_max(H)
            I.append(u)
        else:
            break
    
    print("RESULTS, NUMBER TO ACTIVATE:", len(I), "POURCENTAGE TO ACTIVATE:", len(I)/nb)
    if (verbose):
        print("NODE ACTIVATED:", I)
    return I


res = greedy_algorithm(0.25,50,25, True)