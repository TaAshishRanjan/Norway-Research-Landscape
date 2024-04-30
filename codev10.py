#!/usr/bin/env python
# coding: utf-8

# In[30]:


import pandas as pd
import re
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from collections import Counter

# Load the dataset
df = pd.read_excel('D:/BA/sem2_Sociel Network theory/Project idea/2022/Title2022.xlsx')

# Load excluded words from Excel
excluded_words_df = pd.read_excel('D:/BA/sem2_Sociel Network theory/Project idea/2023/excluded_words.xlsx')
english_stopwords = set(stopwords.words("english"))
excluded_words = list(excluded_words_df['Excluded Word']) + list(english_stopwords)



# In[31]:


# Define category keywords
category_keywords = {
    'marine': ['ocean', 'sea', 'marine', 'naval','salmon','arctic','water','fish','offshore','ice','ships','ship','blue','atlantiq'],
    
    'tech': ['technology', 'innovation', 'digital', 'engineering','communication','sensor','3d','ai','artificial','inteligence',
            'cyber','tool','space','quantum','molecular','ion','material','energy','power'],
    
    'sustainable': ['sustainable', 'renewable', 'green','hydrogen','co2','batteries','battery','circular','environmental','soil','climate','eco-friendly','land','farming','emission','solar','nature','zero','waste',
                      'ecological','field','co','earth','carbon','wind','organic','plants','bio','solid','plant'],
    
    'health' : ['cancer','treatment','brain','clinical','medicine','protein','health','heart','therapy','mental','disorders',
               'brain','patients'],
    
    'oil_and_gas': ['oil', 'gas', 'petroleum', 'drilling','industry'],
    
    'social':['child','school','violence','young','socirty','political','drug','education','clinical',
             'medicine','law','language','world','urban','market','muncipal','life','economy','family','age','culture',
             'animal','student','gender','women','enequality','society','policy','local','structure','teaching',
             'youth','politics','economy','species'],
    
    'general': []  # You can add general keywords if needed
}


# In[32]:


# Tokenize titles and filter stopwords and special words
all_titles = ' '.join(df['Title'])
words = re.findall(r'\b\w+\b', all_titles.lower())
filtered_words = [word for word in words if word not in excluded_words]

# Replace variations of sustainability and environment with a single token
filtered_words = ['sustainability' if word in ['sustainable', 'sustainability'] else word for word in filtered_words]
filtered_words = ['environment' if word in ['environment', 'environmental','environments'] else word for word in filtered_words]
filtered_words = ['health' if word in ['health', 'healthy'] else word for word in filtered_words]
filtered_words = ['battery' if word in ['battery', 'batteries'] else word for word in filtered_words]
filtered_words = ['children' if word in ['child', 'children'] else word for word in filtered_words]
filtered_words = ['ship' if word in ['ship', 'ships'] else word for word in filtered_words]
filtered_words = ['human' if word in ['human', 'people'] else word for word in filtered_words]
filtered_words = ['ocean' if word in ['sea', 'ocean'] else word for word in filtered_words]
# Count the occurrences of each word
word_counts = Counter(filtered_words)

# Extract the top 250 words
top_words = [word for word, _ in word_counts.most_common(250)]

co_occurrences_top250 = Counter()
for title in df['Title']:
    title_words = re.findall(r'\b\w+\b', title.lower())
    title_words_filtered = [word for word in title_words if word in top_words]
    for word1, word2 in itertools.combinations(set(title_words_filtered), 2):
        co_occurrences_top250[(word1, word2)] += 1

# Create a list of edges
edges = [(word1, word2, count) for (word1, word2), count in co_occurrences_top250.items()]

# Create a graph
G = nx.Graph()

# Add edges with weights to the graph
for edge in edges:
    word1, word2, weight = edge
    G.add_edge(word1, word2, weight=weight)
    
# Assign categories to nodes
node_categories = {}
for node in G.nodes:
    for category, keywords in category_keywords.items():
        if any(keyword in node for keyword in keywords):
            node_categories[node] = category
            break
    else:
        node_categories[node] = 'general'

# Calculate node sizes based on the number of repetitions
node_sizes = [word_counts[word] * 20 for word in G.nodes]

# Calculate centrality measures
degree_centrality = nx.degree_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
closeness_centrality = nx.closeness_centrality(G)

# Add centrality measures to the node data DataFrame
node_data = pd.DataFrame({'Id': list(G.nodes), 
                          'Label': list(G.nodes),
                          'Category': [node_categories[node] for node in G.nodes], 
                          'Size': node_sizes,
                          'Degree Centrality': [degree_centrality[node] for node in G.nodes],
                          'Betweenness Centrality': [betweenness_centrality[node] for node in G.nodes],
                          'Closeness Centrality': [closeness_centrality[node] for node in G.nodes]})


# Visualize the network with nodes colored by category
plt.figure(figsize=(16, 12))
pos = nx.spring_layout(G, k=0.15)
node_colors = {'marine': 'blue', 'tech': 'red', 'sustainable': 'green', 'oil_and_gas': 'orange', 'general': 'gray', 'social':'pink', 'health':'yellow'}
node_color = [node_colors[node_categories[node]] for node in G.nodes]
nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color=node_color, font_size=9, font_weight="bold", width=0.2, edge_color="gray", alpha=0.6)
plt.title("Keyword Co-occurrence Network (Top 250 Words)")
plt.show()


# In[33]:


# Export node data to Excel for Gephi
node_data.to_excel('gephi_nodesv122.xlsx', index=False)

# Create edge list for Gephi
edge_data = pd.DataFrame({'Source': [edge[0] for edge in edges], 'Target': [edge[1] for edge in edges], 'Weight': [edge[2] for edge in edges]})
edge_data.to_excel('gephi_edgesv122.xlsx', index=False)


# In[ ]:




