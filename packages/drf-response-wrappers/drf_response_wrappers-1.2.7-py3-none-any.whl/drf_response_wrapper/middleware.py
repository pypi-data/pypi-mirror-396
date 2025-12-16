# from django.utils.deprecation import MiddlewareMixin
# from rest_framework.response import Response

# class APIResponseWrapperMiddleware(MiddlewareMixin):
#     def process_template_response(self, request, response):
#         """
#         Handles TemplateResponse or DRF Response safely.
#         """
#         if isinstance(response, Response):
#             if response.data is not None and not all(
#                 k in response.data for k in ("success", "message", "status", "data")
#             ):
#                 response.data = {
#                     "success": 200 <= response.status_code < 300,
#                     "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
#                     "status": response.status_code,
#                     "data": response.data,
#                 }
#         return response

#     def process_response(self, request, response):
#         """
#         Fallback for normal HttpResponse (non-DRF).
#         """
#         try:
#             if hasattr(response, "data"):
#                 # DRF Response already handled in process_template_response
#                 return response

#             # Regular HttpResponse
#             if response.get("Content-Type", "").startswith("application/json"):
#                 import json
#                 data = json.loads(response.content.decode("utf-8"))
#                 if not all(k in data for k in ("success", "message", "status", "data")):
#                     wrapped = {
#                         "success": 200 <= response.status_code < 300,
#                         "message": "Request successful" if 200 <= response.status_code < 300 else "Something went wrong",
#                         "status": response.status_code,
#                         "data": data,
#                     }
#                     response.content = json.dumps(wrapped).encode("utf-8")
#             return response
#         except Exception:
#             return response


from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
import json


class APIResponseWrapperMiddleware(MiddlewareMixin):
    def _wrap_response(self, data, http_status):
        success = 200 <= http_status < 300
        message = None

        # 🔴 Handle DRF validation / auth errors
        if not success and isinstance(data, dict):
            error_messages = []

            for field, errors in data.items():
                if isinstance(errors, list):
                    for err in errors:
                        if field == "non_field_errors":
                            error_messages.append(str(err))
                        else:
                            # Make field name human-readable
                            field_name = field.replace("_", " ").capitalize()
                            error_messages.append(f"{field_name} {err.lower()}")
                elif isinstance(errors, str):
                    error_messages.append(errors)

            if error_messages:
                message = ". ".join(error_messages) + "."

        # 🟢 Custom success message from view
        if success and isinstance(data, dict) and "message" in data:
            message = data.pop("message")

        return {
            "success": success,
            "message": message or (
                "Request successful" if success else "Something went wrong"
            ),
            "status": http_status,
            "data": {} if not success else (data if isinstance(data, dict) else {"data": data}),
        }

    #With fiel name detailed error messages
    # def _wrap_response(self, data, http_status):
    #     """
    #     Central response formatter.
    #     - All success & error messages go to `message`
    #     - `data` contains only valid response data
    #     """
    #     success = 200 <= http_status < 300
    #     message = None

    #     # 🔴 ERROR HANDLING (Validation, Auth, Permission, etc.)
    #     if not success and isinstance(data, dict):
    #         error_messages = []

    #         for field, errors in data.items():
    #             if isinstance(errors, list):
    #                 for err in errors:
    #                     error_messages.append(f"{field}: {err}")
    #             elif isinstance(errors, str):
    #                 error_messages.append(f"{field}: {errors}")

    #         if error_messages:
    #             message = " | ".join(error_messages)

    #     # 🟢 SUCCESS MESSAGE FROM VIEW
    #     if success and isinstance(data, dict) and "message" in data:
    #         message = data.pop("message")

    #     return {
    #         "success": success,
    #         "message": message or (
    #             "Request successful" if success else "Something went wrong"
    #         ),
    #         "status": http_status,
    #         "data": data if success and isinstance(data, dict) else {},
    #     }
    def process_template_response(self, request, response):
        """
        Wrap DRF Response safely.
        """
        if isinstance(response, Response):
            if response.data is not None and not all(
                k in response.data for k in ("success", "message", "status", "data")
            ):
                response.data = self._wrap_response(response.data, response.status_code)
        return response

    def process_response(self, request, response):
        try:
            # ✅ Skip admin/static/media pages
            if request.path.startswith("/admin") or request.path.startswith("/static") or request.path.startswith("/media"):
                return response

            # ✅ Skip HTML responses (e.g. 404 debug pages, templates)
            if response.get("Content-Type", "").startswith("text/html"):
                return response

            # DRF Response already wrapped above
            if hasattr(response, "data"):
                return response

            # ✅ JSON HttpResponse
            if response.get("Content-Type", "").startswith("application/json"):
                try:
                    data = json.loads(response.content.decode("utf-8"))
                except Exception:
                    data = {}
                wrapped = self._wrap_response(data, response.status_code)
                return JsonResponse(wrapped, status=response.status_code)

            # ✅ Non-JSON HttpResponse (plain text etc.)
            if isinstance(response, HttpResponse):
                content = response.content.decode("utf-8") if response.content else ""
                try:
                    data = json.loads(content)
                except Exception:
                    data = {"data": content}
                wrapped = self._wrap_response(data, response.status_code)
                return JsonResponse(wrapped, status=response.status_code)

            return response

        except Exception as e:
            wrapped = self._wrap_response({"message": str(e)}, 500)
            return JsonResponse(wrapped, status=500)

