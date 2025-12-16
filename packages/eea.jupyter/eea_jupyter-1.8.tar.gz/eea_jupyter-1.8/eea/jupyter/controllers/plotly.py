"""PlotlyController
"""
from urllib.parse import urlparse
from uuid import uuid4
import getpass
import requests
import plotly

from .data_sources import get_plotly_data_sources


class PlotlyController:
    """
    PlotlyController class for managing Plotly visualizations.
    """
    session = None
    auth_token = None
    resources = {}
    metadata = {}
    extract_data_sources = True

    def __init__(self, **kwargs):
        """
        Initializes the instance with optional keyword arguments.
        """
        if "url" in kwargs:
            self.init(**kwargs)

    def init(self, **kwargs):
        """
        Initialize the controller with the given parameters.
        """
        self.api_url = kwargs.get("api_url", None)
        url = kwargs.get("url", None)
        fig = kwargs.get("fig", None)
        title = kwargs.get("title", None)
        _id = kwargs.get("id", None)
        topics = kwargs.get("topics", None)
        temporal_coverage = kwargs.get("temporal_coverage", None)
        geo_coverage = kwargs.get("geo_coverage", None)
        data_provenance = kwargs.get("data_provenance", None)
        self.extract_data_sources = kwargs.get("extract_data_sources", True)

        if url is not None and not isinstance(url, str):
            return "URL must be a string and cannot be empty"
        if fig is not None and not isinstance(
                fig, plotly.graph_objs.Figure) and not isinstance(
                fig, dict):
            return "Figure must be a Plotly Figure object or a dictionary"
        if title is not None and not title:
            return "Title cannot be empty"
        if _id is not None and not _id:
            return "Id cannot be empty"
        if topics is not None and not isinstance(topics, list):
            return "Topics must be a list"
        if temporal_coverage is not None and not isinstance(
                temporal_coverage, list):
            return "Temporal coverage must be a list"
        if geo_coverage is not None and not isinstance(
                geo_coverage, list):
            return "Geo coverage must be a list"
        if data_provenance is not None and not isinstance(
                data_provenance, list):
            return "Data provenance must be a list"

        self.api_url = self.api_url
        if url:
            self.url_tuple = urlparse(url)
            self.host = self.url_tuple.scheme + "://" + self.url_tuple.netloc
            self.path = self.__sanitize_path(self.url_tuple.path)
            self.path_parts = self.path.split('/')
            self.parent_path = '/'.join(self.path_parts[:-1])
            self.api_url = self.api_url or "%s://%s/admin/++api++" % (
                self.url_tuple.scheme, self.url_tuple.netloc
            )

        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.session.headers.update({'Content-Type': 'application/json'})

        err = self.authenticate(**kwargs)
        if err:
            return err

        err = self.__parse_topics(topics)
        if err:
            return err

        self.__parse_temporal_coverage(temporal_coverage)

        err = self.__parse_geo_coverage(geo_coverage)
        if err:
            return err

        err = self.__parse_data_provenance(data_provenance)
        if err:
            return err

        return None

    def authenticate(self, **kwargs):
        """
        Authenticates the user using the provided authentication
        token or credentials.
        """
        self.auth_token = kwargs.get("auth_token", None)
        auth_provider = kwargs.get("auth_provider", "basic")

        if isinstance(auth_provider, str):
            auth_provider = auth_provider.lower()
        else:
            auth_provider = "basic"

        if self.auth_token is None:
            if auth_provider == "microsoft":
                self.auth_token = input(
                    "Enter your Microsoft authentication token: ")
            else:
                username = input('Enter username: ')
                password = getpass.getpass(prompt='Enter password: ')
                response = self.session.post(
                    self.api_url + '/@login',
                    json={'login': username, 'password': password})

                if response.status_code == 200:
                    self.auth_token = response.json().get("token", None)
                else:
                    return "Could not authenticate. Reason: %s" % (
                        get_err_msg(response))

        if self.auth_token:
            if auth_provider == "microsoft":
                self.session.cookies.set(
                    kwargs.get("__ac__key", "__ac"),
                    self.auth_token)
            else:
                self.session.headers.update(
                    {'Authorization': 'Bearer %s' % self.auth_token})

            return None

        return "Could not authenticate"

    def upload_plotly(self, **kwargs):
        """
        Uploads or updates a Plotly visualization to the API.
        """
        visualization = kwargs.get("visualization", None)

        if not isinstance(visualization, dict):
            return "Visualization neeeds to be a dict"

        session = self.session
        response = session.get(
            self.api_url + self.parent_path)

        if response.status_code != 200:
            return "Parent %s could not be reached. Reason: %s" % (
                (self.host + self.parent_path),
                get_err_msg(response))

        response = session.get(
            self.api_url + self.path)

        if response.status_code == 404:
            metadata = self.get_metadata(**kwargs)
            metadata["@type"] = "visualization"

            if self.extract_data_sources:
                [data_sources, _] = get_plotly_data_sources(
                    visualization["data"],
                    visualization["layout"],
                    (visualization["dataSources"]
                     if "dataSources" in visualization else {}))

                visualization["dataSources"] = data_sources

            metadata["visualization"] = visualization
            if metadata.get("id", None) is None:
                metadata["id"] = self.path_parts[-1]
            response = session.post(
                self.api_url + self.parent_path,
                json=metadata)
            if response.status_code in [200, 201]:
                print("Visualization %s created succesfuly!" %
                      (self.host + self.path))
            else:
                return "Visualization %s could not be created. Reason %s" % (
                    (self.host + self.path),
                    get_err_msg(response))
        elif response.status_code == 200:
            metadata = self.get_metadata(**kwargs)

            if self.extract_data_sources:
                [
                    data_sources, _] = get_plotly_data_sources(
                    visualization["data"],
                    visualization["layout"],
                    (visualization["dataSources"]
                     if "dataSources" in visualization else {}))

                visualization["dataSources"] = data_sources

            metadata["visualization"] = visualization
            response = session.patch(
                self.api_url + self.path,
                json=metadata)
            if response.status_code in [200, 204]:
                print("Visualization %s updated succesfuly!" %
                      (self.host + self.path))
            else:
                return "Visualization %s could not be updated. Reason: %s" % (
                    (self.host + self.path),
                    get_err_msg(response))
        else:
            return "Visualization %s could not be reached. Reason: %s" % (
                (self.host + self.path),
                get_err_msg(response))

        return None

    def get_theme(self, name):
        """
        Retrieves the theme from the API.
        """
        if not name:
            return [None, "Theme id cannot be empty"]

        response = self.session.get(
            self.api_url + "/@plotly_settings")
        if response.status_code == 200:
            themes = response.json().get("themes", [])
            for theme in themes:
                if theme.get("id") == name:
                    return [theme, None]
            return [None, (
                f"\"{name}\" is not a valid theme. "
                f"Allowed values are: {[theme.get('id') for theme in themes]}"
            )]
        return [None, "Could not retrieve theme. Reason: %s" % (
            get_err_msg(response)
        )]

    def get_template(self, name):
        """
        Retrieves the theme from the API.
        """
        if not name:
            return [None, "Theme id cannot be empty"]

        response = self.session.get(
            self.api_url + "/@plotly_settings")
        if response.status_code == 200:
            templates = response.json().get("templates", [])
            for template in templates:
                if template.get("label") == name:
                    return [template.get("visualization", {}), None]
            return [None, (
                f"\"{name}\" is not a valid template. "
                f"Allowed values are: "
                f"{[template.get('label') for template in templates]}"
            )]
        return [None, "Could not retrieve template. Reason: %s" % (
            get_err_msg(response)
        )]

    def __parse_topics(self, topics):
        """
        Parses the topics.
        """
        self.metadata["topics"] = []
        if topics is None or topics and len(topics) == 0:
            return None
        if self.resources.get("topics") is None:
            response = self.session.get(
                self.api_url +
                "/@vocabularies/collective.taxonomy.eeatopicstaxonomy?b_size=1000")  # noqa: E501  # pylint: disable=line-too-long
            if response.status_code == 200:
                self.resources["topics"] = response.json().get("items", [])
            else:
                return "Could not retrieve topics taxonomy. Reason: %s" % (
                    get_err_msg(response))
        topics_titles = [topic.get("title", "")
                         for topic in self.resources["topics"]]
        for topic in topics:
            if topic not in topics_titles:
                return (
                    f"\"{topic}\" is not a valid topic. "
                    f"Allowed values are: {topics_titles}"
                )
            try:
                topic_index = topics_titles.index(topic)
                self.metadata["topics"].append(
                    self.resources["topics"][topic_index])
            except ValueError:
                return (
                    f"\"{topic}\" is not a valid topic. "
                    f"Allowed values are: {topics_titles}"
                )
        return None

    def __parse_temporal_coverage(self, temporal_coverage):
        """
        Parses the temporal coverage.
        """
        self.metadata["temporal_coverage"] = {
            "temporal": []
        }
        if temporal_coverage is None or temporal_coverage and len(
                temporal_coverage) == 0:
            return None
        for temporal in temporal_coverage:
            self.metadata["temporal_coverage"]["temporal"].append(
                {"label": str(temporal), "value": str(temporal)})
        return None

    def __parse_geo_coverage(self, geo_coverage):
        """
        Parses the geo coverage.
        """
        self.metadata["geo_coverage"] = {
            "geolocation": []
        }
        if geo_coverage is None or geo_coverage and len(geo_coverage) == 0:
            return None
        if self.resources.get("geo_coverage") is None:
            response = self.session.get(self.api_url + "/@geodata")
            if response.status_code == 200:
                self.resources["geo_coverage"] = {}
                response = response.json()
                biotags = response.get("biotags", [])
                geotags = response.get("geotags", {})
                for tag in biotags:
                    self.resources["geo_coverage"][biotags[tag]["title"]] = {
                        "label": biotags[tag]["title"],
                        "value": tag
                    }
                for geotag in geotags:
                    for tag in geotags[geotag]:
                        location = geotags[geotag][tag]
                        current_location = self.resources["geo_coverage"].get(
                            location)
                        if current_location is not None:
                            continue
                        self.resources["geo_coverage"][location] = {
                            "label": location,
                            "value": tag
                        }
            else:
                return (
                    "Could not retrieve geo coverage taxonomy. Reason: %s" % (
                        get_err_msg(response)))
        for location in geo_coverage:
            if location not in self.resources["geo_coverage"]:
                keys = list(self.resources['geo_coverage'].keys())
                return (
                    f"\"{location}\" is not a valid geo coverage. "
                    f"Allowed values are: {keys}"
                )
            self.metadata["geo_coverage"]["geolocation"].append(
                self.resources["geo_coverage"][location])
        return None

    def __parse_data_provenance(self, data_provenance):
        """
        Parses the data provenance.
        """
        self.metadata["data_provenance"] = {
            "data": []
        }
        if data_provenance is None or data_provenance and len(
                data_provenance) == 0:
            return None
        for provenance in data_provenance:
            isDict = isinstance(provenance, dict)
            hasTitle = isDict and provenance.get("title") is not None
            hasOrganization = isDict and provenance.get(
                "organisation") is not None
            hasLink = isDict and provenance.get("link") is not None
            if not hasTitle or not hasOrganization or not hasLink:
                return (
                    "Invalid data provenance. "
                    "Must contain title, organisation "
                    f"and link, got: {provenance}"
                )
            self.metadata["data_provenance"]["data"].append({
                "@id": str(uuid4()),
                **provenance
            })
        return None

    def get_metadata(self, **kwargs):
        """
        Filters out specific keys from the provided keyword arguments.
        """
        # fig = kwargs.get("fig")
        # png = None
        # if not isinstance(fig, plotly.graph_objs.Figure):
        #     real_fig = pio.from_json(json.dumps(fig), skip_invalid=True)
        #     png = base64.b64encode(real_fig.to_image()).decode('ascii')
        # else:
        #     png = base64.b64encode(fig.to_image()).decode('ascii')

        return {
            **{k: v for k, v in kwargs.items() if k not in [
                'url',
                'api_url',
                'fig',
                'chart_data',
                'auth_provider',
                'auth_token',
                'extract_data_sources',
                '__ac__key'
            ]},
            # "preview_image": {
            #     "content-type": "image/png",
            #     "encoding": "base64",
            #     "filename": "preview.png",
            #     "data": png
            # },
            "topics": self.metadata.get("topics", []),
            "temporal_coverage": self.metadata.get(
                "temporal_coverage", {"temporal": []}
            ),
            "geo_coverage": self.metadata.get(
                "geo_coverage",
                {"geolocation": []}
            ),
            "data_provenance": self.metadata.get(
                "data_provenance",
                {"data": []}
            )
        }

    def __sanitize_path(self, path):
        """
        Sanitize the given path by removing specific
        substrings and trailing slashes.
        """
        return path.replace("/edit", "").replace("/add", "").rstrip('/')


def get_err_msg(response):
    """
    Extracts and returns an error message from an HTTP response.
    """
    try:
        error = response.json()
        return error.get(
            "error", {}).get(
            "message", "") or error.get(
            "message", "")
    except Exception:
        return response.text


# def get_visualization(chart_data):
#     """
#     Processes the given chart data to generate a visualization configuration.
#     """
#     visualization = {
#         "use_data_source": True
#     }
#     keys = ["x", "y", "z", "values", "labels"]
#     occurrences = {}
#     data = {}

#     for trace in chart_data.get("data", []):
#         for key in keys:
#             sources = trace.get(f"{key}src")

#             # Check if the trace has a key and if it's a list
#             if key not in trace or not isinstance(trace[key], list):
#                 continue

#             # Check if sources is defined and if it's a string
#             if isinstance(sources, str):
#                 occurrences[sources] = occurrences.get(sources, 0) + 1
#                 data[sources] = list(trace[key])
#                 continue

#             # Check if sources is defined and if it's a list
#             if isinstance(sources, list):
#                 for index, source in enumerate(sources):
#                     occurrences[source] = occurrences.get(source, 0) + 1
#                     if len(sources) > 1:
#                         data[source] = list(trace[key][index])
#                     else:
#                         data[source] = list(trace[key])
#                 continue

#             # If sources is not defined, define the data
#             for handled_key, handled_data in data.items():
#                 if all(
#                         value == handled_data[idx] for idx,
#                         value in enumerate(trace[key])):
#                     trace[f"{key}src"] = handled_key
#                     break

#             name = f"{key}"
#             occurrences[name] = occurrences.get(name, 0) + 1
#             data[f"{name}{occurrences[name]}"] = list(trace[key])
#             trace[f"{key}src"] = f"{name}{occurrences[name]}"

#     visualization["chartData"] = chart_data
#     visualization["data_source"] = data

#     return visualization
