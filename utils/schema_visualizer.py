"""Schema visualization utilities"""
import networkx as nx
import plotly.graph_objects as go
from typing import Dict, List, Tuple

class SchemaVisualizer:
    """Visualizes database schema and relationships"""
    
    def __init__(self, schema: Dict):
        self.schema = schema
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        """Build network graph from schema"""
        if not self.schema or 'tables' not in self.schema:
            return

        # Add nodes for tables
        for table_name, table_info in self.schema['tables'].items():
            self.graph.add_node(table_name, type='table')
            
            # Add nodes for columns
            if 'columns' in table_info:
                for col_name, col_info in table_info['columns'].items():
                    node_id = f"{table_name}.{col_name}"
                    self.graph.add_node(node_id, 
                                      type='column',
                                      data_type=col_info.get('type'))
                    self.graph.add_edge(table_name, node_id)

            # Add relationships
            if 'relationships' in table_info:
                for rel in table_info['relationships']:
                    self.graph.add_edge(
                        table_name,
                        rel['referenced_table'],
                        type='relationship'
                    )

    def get_plotly_figure(self) -> go.Figure:
        """Generate interactive Plotly figure"""
        pos = nx.spring_layout(self.graph)
        
        # Create edges trace
        edge_x = []
        edge_y = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
        edges_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Create nodes trace
        node_x = []
        node_y = []
        node_text = []
        node_color = []
        
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(str(node))
            node_color.append('#1f77b4' if self.graph.nodes[node]['type'] == 'table' 
                            else '#ff7f0e')

        nodes_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition='bottom center',
            marker=dict(
                size=20,
                color=node_color,
                line_width=2
            )
        )

        # Create figure
        fig = go.Figure(data=[edges_trace, nodes_trace],
                       layout=go.Layout(
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           title='Database Schema Visualization',
                           annotations=[dict(
                               text="Database Schema",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0, y=-0.1
                           )]
                       ))
        
        return fig
