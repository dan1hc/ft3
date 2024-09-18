"""Api server objects."""

__all__ = (
    'Server',
    )

from .. import events

from . import lib


class Server(lib.http.server.BaseHTTPRequestHandler):  # pragma: no cover
    """A very basic HTTP server."""

    handler: events.Handler

    def log_message(*args: lib.t.Any, **kwargs: lib.t.Any) -> None:  # noqa
        pass

    def respond(self, response: events.Response) -> None:
        """Respond to requestor."""

        self.send_response(response.status_code)
        for header, value in response.headers.items():
            self.send_header(header, str(value))
        self.end_headers()
        if response.body is not None:
            serialized_response = response.serialize()
            if isinstance(serialized_response, bytes):
                self.wfile.write(serialized_response)
            else:
                self.wfile.write(serialized_response.encode())

    def get_request(self) -> events.Request:
        """Get current request."""

        parsed = lib.urllib.parse.urlparse(self.path)

        if (content := self.headers.get('Content-Length')):
            if (
                data := self.rfile.read(int(content)).decode(errors='replace')
                ):
                body = lib.json.loads(data)
            else:
                body = {}
        else:
            body = None

        return events.Request(
            url=parsed.geturl(),
            path=parsed.path,
            body=body,
            headers=dict(self.headers),
            method=self.command,
            )

    def do_DELETE(self) -> None:
        """Handle a `DELETE` request."""

        request = self.get_request()
        response = self.handler(request)
        self.respond(response)

        return None

    def do_GET(self) -> None:
        """Handle a `GET` request."""

        request = self.get_request()
        response = self.handler(request)
        self.respond(response)

        return None

    def do_OPTIONS(self) -> None:
        """Handle a `OPTIONS` request."""

        request = self.get_request()
        response = self.handler(request)
        self.respond(response)

        return None

    def do_PATCH(self) -> None:
        """Handle a `PATCH` request."""

        request = self.get_request()
        response = self.handler(request)
        self.respond(response)

        return None

    def do_POST(self) -> None:
        """Handle a `POST` request."""

        request = self.get_request()
        response = self.handler(request)
        self.respond(response)

        return None

    def do_PUT(self) -> None:
        """Handle a `PUT` request."""

        request = self.get_request()
        response = self.handler(request)
        self.respond(response)

        return None
