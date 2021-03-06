#!/usr/bin/env python
#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import azure.functions as func
from onefuzztypes.enums import ErrorCode
from onefuzztypes.job_templates import (
    JobTemplateCreate,
    JobTemplateDelete,
    JobTemplateUpdate,
)
from onefuzztypes.models import Error
from onefuzztypes.responses import BoolResult

from ..onefuzzlib.job_templates.templates import JobTemplateIndex
from ..onefuzzlib.request import not_ok, ok, parse_request


def get(req: func.HttpRequest) -> func.HttpResponse:
    templates = JobTemplateIndex.get_index()
    return ok(templates)


def post(req: func.HttpRequest) -> func.HttpResponse:
    request = parse_request(JobTemplateCreate, req)
    if isinstance(request, Error):
        return not_ok(request, context="JobTemplateCreate")

    entry = JobTemplateIndex(name=request.name, template=request.template)
    result = entry.save(new=True)
    if isinstance(result, Error):
        return not_ok(result, context="JobTemplateCreate")

    return ok(BoolResult(result=True))


def patch(req: func.HttpRequest) -> func.HttpResponse:
    request = parse_request(JobTemplateUpdate, req)
    if isinstance(request, Error):
        return not_ok(request, context="JobTemplateUpdate")

    entry = JobTemplateIndex.get(request.name)
    if entry is None:
        return not_ok(
            Error(code=ErrorCode.UNABLE_TO_UPDATE, errors=["no such job template"]),
            context="JobTemplateUpdate",
        )

    entry.template = request.template
    entry.save()
    return ok(BoolResult(result=True))


def delete(req: func.HttpRequest) -> func.HttpResponse:
    request = parse_request(JobTemplateDelete, req)
    if isinstance(request, Error):
        return not_ok(request, context="JobTemplateDelete")

    entry = JobTemplateIndex.get(request.name)
    return ok(BoolResult(result=entry is not None))


def main(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "GET":
        return get(req)
    elif req.method == "POST":
        return post(req)
    elif req.method == "DELETE":
        return delete(req)
    elif req.method == "PATCH":
        return patch(req)
    else:
        raise Exception("invalid method")
