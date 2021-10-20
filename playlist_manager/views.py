import io

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from django.contrib import messages
from django.core.files.images import ImageFile


import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure as plt_figure

from playlist_manager.models import TouristAttraction, Track, Graph
from playlist_manager.constants import ORDERING_CRITERIA_DICT
from playlist_manager.mapbox_client import MapboxClient
from playlist_manager.algorithms import dijkstra, knapsack, old_knapsack, print_selected_items, chunks


class HomePageView(TemplateView):
    template_name = "home.html"


class AttractionListView(ListView):
    template_name = "attraction_list.html"
    paginate_by = 10
    queryset = TouristAttraction.objects.all().order_by('-selected', '-origin', '-destination')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["enable_origin_selection"] = not TouristAttraction.objects.filter(origin=True).exists()
        context["enable_destination_selection"] = not TouristAttraction.objects.filter(destination=True).exists()
        return context

def remove_attraction(request, pk):
    attraction = TouristAttraction.objects.get(pk=pk)
    attraction.selected = False
    attraction.save()
    return redirect('/attractions')


def select_attraction(request, pk):
    attraction = TouristAttraction.objects.get(pk=pk)
    attraction.selected = True
    attraction.save()
    return redirect('/attractions')

def select_attraction_origin(request, pk):
    attraction = TouristAttraction.objects.get(pk=pk)
    attraction.origin = True
    attraction.save()
    return redirect('/attractions')

def remove_attraction_origin(request, pk):
    attraction = TouristAttraction.objects.get(pk=pk)
    attraction.origin = False
    attraction.save()
    return redirect('/attractions')

def select_attraction_destination(request, pk):
    attraction = TouristAttraction.objects.get(pk=pk)
    attraction.destination = True
    attraction.save()
    return redirect('/attractions')

def remove_attraction_destination(request, pk):
    attraction = TouristAttraction.objects.get(pk=pk)
    attraction.destination = False
    attraction.save()
    return redirect('/attractions')

def result_view(request):
    attractions = TouristAttraction.objects.filter(selected=True)
    origin = attractions.filter(origin=True).first()
    destination = attractions.filter(destination=True).first()

    if not origin or not destination:
        messages.add_message(
            request,
            messages.ERROR,
            'É necessário selecionar os pontos de origem e destino para visualizar os resultados'
        )
        return redirect(reverse('attraction-list'))

    coords = []
    if attractions and attractions.count() > 1:
        nodes = []
        for attraction in attractions:
            coords.append(
                [float(attraction.latitude), float(attraction.longitude), attraction.name]
            )
            nodes.append(attraction.name)

        existing_graph = Graph.objects.filter(
            nodes=nodes,
            origin=origin.name,
            destination=destination.name
        ).first()
        if existing_graph:
            tracks = Track.objects.all()[:20].values_list('duration', 'popularity')
            tracks_durations, tracks_popularities = zip(*tracks)
            capacity = int(existing_graph.duration) * 1000 # convert seconds to miliseconsd

            print(capacity, tracks_durations, tracks_popularities)

            knapsack(tracks_popularities, tracks_durations, capacity)
            res = old_knapsack(capacity, tracks_durations, tracks_popularities)
            print_selected_items(res, tracks_durations, capacity)

            return render(
                request,
                'results.html',
                {
                    'graph': existing_graph
                }
            )

        graph = {}
        mapbox_client = MapboxClient()
        for source in coords:
            source_lat, source_lng, source_name = source
            graph[source_name] = {}
            for neighbour in coords:
                neighbour_lat, neighbour_lng, neighbour_name = neighbour

                if neighbour != source:
                    weight = mapbox_client.duration_between_coords(
                        [source_lat, source_lng],
                        [neighbour_lat, neighbour_lng]
                    )
                    graph[source_name][neighbour_name] = weight

        print(graph)
        duration, shortest_path = dijkstra(graph, origin.name, destination.name)

        new_graph = {}

        for node in graph:
            new_graph[node] = {}
            for neighbour in graph[node]:
                new_graph[node][neighbour] = {'weight': graph[node][neighbour]}

        nx_graph = nx.from_dict_of_dicts(new_graph)
        pos = nx.spring_layout(nx_graph)
        labels = nx.get_edge_attributes(nx_graph, 'weight')
        shortest_path_chunks = chunks(shortest_path, 2)
        edge_colors = ['red' if set(edge) in shortest_path_chunks else 'black' for edge in nx_graph.edges]

        plt.figure(figsize=(7, 5,)) # Size in inches
        nx.draw_networkx(
            nx_graph,
            pos,
            node_size=[len(graph[node])*300 for node in graph],
            font_size=6,
            edge_color=edge_colors
        )
        nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=labels, font_size=6)

        figure = io.BytesIO()

        plt.savefig(figure, format="png")
        file_content = ImageFile(figure)
        graph = Graph(
            nodes = nodes,
            origin = origin.name,
            destination = destination.name,
            path=shortest_path,
            duration=duration
        )
        graph.image.save('graph.png', file_content)
        graph.save()

    return render(
        request,
        'results.html',
        {
            'coords':coords,
            'graph':graph
        }
    )

class TrackListView(ListView):
    template_name = "track_list.html"
    category = None
    paginate_by = 6

    def get_queryset(self):
        if "ordering" in self.request.GET and self.request.GET["ordering"] in ["nome música", "popularidade", "duração", "artistas"]:
            ordering_criteria = self.request.GET["ordering"]
            queryset = Track.objects.all().order_by(ORDERING_CRITERIA_DICT[ordering_criteria])
            return queryset
        else:
            queryset = Track.objects.all().order_by(ORDERING_CRITERIA_DICT["popularidade"])
            return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ordering_criteria = ["nome música", "popularidade", "duração", "artistas"]
        context["ordering_criteria"] = ordering_criteria
        if "ordering" in self.request.GET and self.request.GET["ordering"] in ["nome música", "popularidade", "duração", "artistas"]:
            context["ordering"] = self.request.GET["ordering"]
        else:
            context["ordering"] = "popularidade"
        return context
