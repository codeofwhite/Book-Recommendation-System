from graphviz import Digraph

def plot_application_architecture():
    dot = Digraph(comment='Application Architecture and Deployment Diagram', format='png')
    dot.attr(rankdir='TB', splines='ortho') # Layout from Top to Bottom, orthogonal lines

    # User Layer
    with dot.subgraph(name='cluster_user') as c:
        c.attr(label='User', labelloc='t', style='filled', fillcolor='floralwhite')
        c.node('user', 'User', shape='Mdiamond', style='filled', fillcolor='gold')

    # Frontend Service
    with dot.subgraph(name='cluster_frontend') as c:
        c.attr(label='Frontend Service (Presentation Layer)', labelloc='b', style='filled', fillcolor='lightpink')
        c.node('vue_app', 'Vue.js Application', shape='component', style='filled', fillcolor='salmon')

    # Backend Services
    with dot.subgraph(name='cluster_backend') as c:
        c.attr(label='Backend Services (Business Logic Layer)', labelloc='b', style='filled', fillcolor='lightblue')
        c.node('api_gateway', 'API Gateway\n(Kubernetes Ingress/Load Balancer)', shape='cds', style='filled', fillcolor='lightgreen')
        c.node('user_service', 'User Service\n(Python/FastAPI)', shape='box', style='filled', fillcolor='cornflowerblue')
        c.node('book_service', 'Book Service\n(Python/FastAPI)', shape='box', style='filled', fillcolor='cornflowerblue')
        c.node('recommend_service', 'Recommendation Service\n(Python/FastAPI)', shape='box', style='filled', fillcolor='cornflowerblue')
        c.node('data_ingestion_service', 'Data Ingestion Service\n(Python/FastAPI)', shape='box', style='filled', fillcolor='cornflowerblue') # Optional

        c.node('redis_cache', 'Redis Cluster\n(Cache)', shape='cylinder', style='filled', fillcolor='lightgrey')
        c.node('kafka', 'Kafka\n(Message Queue)', shape='note', style='filled', fillcolor='lightgoldenrod')

        dot.edge('api_gateway', 'user_service', label='Auth/Authorization')
        dot.edge('api_gateway', 'book_service', label='Book Query')
        dot.edge('api_gateway', 'recommend_service', label='Get Recommendations')
        dot.edge('api_gateway', 'data_ingestion_service', label='User Behavior Upload') # If separate service

        dot.edge('user_service', 'redis_cache', label='Read/Write Cache')
        dot.edge('book_service', 'redis_cache', label='Read/Write Cache')
        dot.edge('recommend_service', 'redis_cache', label='Read Recommendation Results')
        dot.edge('data_ingestion_service', 'kafka', label='Write Behavior Logs')


    # Data Services
    with dot.subgraph(name='cluster_data') as c:
        c.attr(label='Data Services (Data Layer)', labelloc='b', style='filled', fillcolor='lightgray')
        c.node('mysql_db', 'MySQL Cluster\n(Core Business Data)', shape='cylinder', style='filled', fillcolor='lightblue')
        c.node('hbase_db', 'HBase Cluster\n(Big Data Storage)', shape='cylinder', style='filled', fillcolor='lightblue')
        c.node('es_cluster', 'Elasticsearch Cluster\n(Full-Text Search)', shape='box', style='filled', fillcolor='lightblue')
        c.node('pyspark_flink', 'PyFlink / PySpark\n(Data Processing/Model Training)', shape='box', style='filled', fillcolor='darkseagreen')

        dot.edge('user_service', 'mysql_db', label='User Data')
        dot.edge('book_service', 'mysql_db', label='Book Data')
        dot.edge('book_service', 'es_cluster', label='Update Index')

        dot.edge('recommend_service', 'hbase_db', label='Read Real-time Features/Recommendations')
        dot.edge('es_cluster', 'mysql_db', label='Sync Data', dir='back') # ES syncs from MySQL

        dot.edge('kafka', 'pyspark_flink', label='Consume Behavior Logs')
        dot.edge('pyspark_flink', 'hbase_db', label='Write Processed Results')
        dot.edge('pyspark_flink', 'mysql_db', label='Read Raw Data')


    # External Connections
    dot.edge('user', 'vue_app', label='Access')
    dot.edge('vue_app', 'api_gateway', label='Call API')


    dot.render('application_architecture', view=True) # view=True will automatically open the generated image

# Uncomment the line below to generate the diagram
plot_application_architecture()