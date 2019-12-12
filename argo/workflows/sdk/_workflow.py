import pprint
import six
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from inflection import dasherize
from inflection import underscore

from typing import Any
from typing import Dict
from typing import Callable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

from argo.workflows.client.models import V1alpha1Template
from argo.workflows.client.models import V1alpha1Workflow
from argo.workflows.client.models import V1alpha1WorkflowSpec
from argo.workflows.client.models import V1alpha1WorkflowStatus
from argo.workflows.client.models import V1ObjectMeta

from . import _utils

__all__ = ["Workflow"]


class WorkflowMeta(type):

    __model__ = V1alpha1Workflow

    def __new__(
        cls,
        name: Union[str, Type["Workflow"]],
        bases: Tuple[Type["Workflow"], ...],
        props: Dict[str, Any],
        **kwargs,
    ):
        workflow_name = dasherize(underscore(name))

        props["kind"] = "Workflow"
        props["api_version"] = "argoproj.io/v1alpha1"

        metadata_dict = dict(name=workflow_name,
                             generate_name=f"{workflow_name}-")
        metadata_dict.update(props.get("__metadata__", {}))

        props["metadata"]: V1ObjectMeta = V1ObjectMeta(**metadata_dict)

        templates: List[V1alpha1Template] = []
        for key, prop in props.items():
            try:
                model = getattr(prop, "__model__", None)

                if model is not None and issubclass(model, V1alpha1Template):
                    template, objs = prop.__call__()
                    if template is not None:
                        templates.append(template)

            except AttributeError:
                pass

        spec_dict = {}
        spec_dict["entrypoint"] = props.get("entrypoint", "")
        spec_dict["templates"] = templates

        props["spec"]: V1alpha1WorkflowSpec = V1alpha1WorkflowSpec(**spec_dict)

        # Required field
        props["status"]: V1alpha1WorkflowStatus = {}

        bases = (*bases, cls.__model__)

        klass = super().__new__(cls, name, bases, props)

        return klass


class Workflow(metaclass=WorkflowMeta):
    """"""

    def __init__(self):
        """"""

    def to_yaml(self, **kwargs) -> str:
        """Returns the Workflow manifest as a YAML."""
        d: dict = self.to_dict(omitempty=True)

        opts = dict(default_flow_style=False)
        opts.update(kwargs)

        serialized = yaml.dump(d, Dumper=Dumper, **opts)

        return serialized

    def to_dict(self, omitempty=True) -> Dict[str, Union[str, Dict]]:
        """Returns the Workflow manifest as a dict.

        :param omitempty: bool, whether to omit empty values
        """
        result = V1alpha1Workflow.to_dict(self)

        if omitempty:
            return _utils.omitempty(result)

        return result
