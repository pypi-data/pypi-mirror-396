import asyncio
import json
import logging
import os
import threading
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from multilspy import multilspy_types
from multilspy.language_server import LanguageServer
from multilspy.lsp_protocol_handler import lsp_types as LSPTypes  # noqa: N812
from multilspy.lsp_protocol_handler.lsp_constants import LSPConstants
from multilspy.lsp_protocol_handler.server import (
    LanguageServerHandler,
    ProcessLaunchInfo,
)
from multilspy.multilspy_config import Language, MultilspyConfig
from multilspy.multilspy_exceptions import MultilspyException
from multilspy.multilspy_logger import MultilspyLogger


class CLLanguageServer(LanguageServer):
    """
    - Single file
    - Python (Jedi)
    """

    def __init__(
        self,
        config: MultilspyConfig | None = None,
        logger: MultilspyLogger | None = None,
    ):
        config = config or MultilspyConfig(
            code_language=Language.PYTHON,
            trace_lsp_communication=False,
        )
        logger = logger or MultilspyLogger()
        self.logger = logger
        self.server_started = False
        self.completions_available = asyncio.Event()

        # Mock paths
        self.repository_root_path = Path.cwd()
        # self.repository_root_path = "/mock_repo"
        self.relative_file_path = "src/mock_file.py"

        if config.trace_lsp_communication:

            def logging_fn(source, target, msg):
                self.logger.log(f"LSP: {source} -> {target}: {msg!s}", logging.DEBUG)

        else:

            def logging_fn(source, target, msg):
                pass

        # LanguageServerHandler provides the functionality to start the language server
        # and communicate with it
        self.server: LanguageServerHandler = LanguageServerHandler(
            ProcessLaunchInfo(
                cmd="jedi-language-server",
                cwd=self.repository_root_path,
            ),
            logger=logging_fn,
        )

        self.language_id = "python"

    def _get_initialize_params(self) -> LSPTypes.InitializeParams:
        """
        Returns the initialize params for the Jedi Language Server.

        Copy from jedi_server.py with repository_absolute_path hardcoded.
        """
        with (Path(__file__).parent / Path("jedi_initialize_params.json")).open(
            "r"
        ) as f:
            d = json.load(f)

        repository_absolute_path = "/mock_repo"

        del d["_description"]

        d["processId"] = os.getpid()
        assert d["rootPath"] == "$rootPath"
        d["rootPath"] = repository_absolute_path

        assert d["rootUri"] == "$rootUri"
        d["rootUri"] = Path(repository_absolute_path).as_uri()

        assert d["workspaceFolders"][0]["uri"] == "$uri"
        d["workspaceFolders"][0]["uri"] = Path(repository_absolute_path).as_uri()

        assert d["workspaceFolders"][0]["name"] == "$name"
        d["workspaceFolders"][0]["name"] = Path(repository_absolute_path).name

        return d

    @asynccontextmanager
    async def start_server(self) -> AsyncIterator["CLLanguageServer"]:
        """
        Starts the JEDI Language Server, waits for the server to be ready and yields
        the LanguageServer instance.

        Copy from jedi_server.py
        Usage:
        ```
        async with lsp.start_server():
            # LanguageServer has been initialized and ready to serve requests
            await lsp.request_definition(...)
            await lsp.request_references(...)
            # Shutdown the LanguageServer on exit from scope
        # LanguageServer has been shutdown
        ```
        """

        async def execute_client_command_handler(params):
            return []

        async def do_nothing(params):
            return

        async def check_experimental_status(params):
            if params["quiescent"]:
                self.completions_available.set()

        async def window_log_message(msg):
            self.logger.log(f"LSP: window/logMessage: {msg}", logging.INFO)

        async def print_diagnostics(params):
            print(params)

        self.server.on_request("client/registerCapability", do_nothing)
        self.server.on_notification("language/status", do_nothing)
        self.server.on_notification("window/logMessage", window_log_message)
        self.server.on_request(
            "workspace/executeClientCommand", execute_client_command_handler
        )
        self.server.on_notification("$/progress", do_nothing)
        # self.server.on_notification("textDocument/publishDiagnostics", do_nothing)
        self.server.on_notification(
            "textDocument/publishDiagnostics", print_diagnostics
        )
        self.server.on_notification("language/actionableNotification", do_nothing)
        self.server.on_notification(
            "experimental/serverStatus", check_experimental_status
        )

        # TODO: do we really need the context manager here?
        async with super().start_server():
            self.logger.log("Starting CLLanguageServer server process", logging.INFO)
            await self.server.start()
            initialize_params = self._get_initialize_params()

            self.logger.log(
                "Sending initialize request from LSP client to LSP server and "
                "awaiting response",
                logging.INFO,
            )
            init_response = await self.server.send.initialize(initialize_params)
            assert init_response["capabilities"]["textDocumentSync"]["change"] == 2
            assert "completionProvider" in init_response["capabilities"]
            assert init_response["capabilities"]["completionProvider"] == {
                "triggerCharacters": [".", "'", '"'],
                "resolveProvider": True,
            }

            self.server.notify.initialized({})

            yield self

            await self.server.shutdown()
            await self.server.stop()

    @contextmanager
    def open_file(self, contents: str) -> Iterator[None]:
        """
        Open a file in the Language Server. This is required before making any
        requests to the Language Server.

        Copy from language_server.py with uri hardcoded and contents directly
        passed in.

        :param contents: The source code of the file to open.
        """
        if not self.server_started:
            self.logger.log(
                "open_file called before Language Server started",
                logging.ERROR,
            )
            raise MultilspyException("Language Server not started")

        uri = (Path(self.repository_root_path) / Path("src/mock_file.py")).as_uri()

        self.server.notify.did_open_text_document(
            {
                LSPConstants.TEXT_DOCUMENT: {
                    LSPConstants.URI: uri,
                    LSPConstants.LANGUAGE_ID: self.language_id,
                    LSPConstants.VERSION: 0,
                    LSPConstants.TEXT: contents,
                }
            }
        )
        yield
        self.server.notify.did_close_text_document(
            {
                LSPConstants.TEXT_DOCUMENT: {
                    LSPConstants.URI: uri,
                }
            }
        )

    # async def request_document_symbols(self, contents: str) -> tuple[
    #     list[multilspy_types.UnifiedSymbolInformation],
    #     list[multilspy_types.TreeRepr] | None,
    # ]:
    async def request_document_symbols(
        self, contents: str
    ) -> list[LSPTypes.DocumentSymbol]:
        """
        Raise a [textDocument/documentSymbol](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_documentSymbol)
        request to the Language Server to find symbols in the given file. Wait for
        the response and return the result.

        :param contents: The contents of the file to find symbols in.

        :return tuple[
            list[multilspy_types.UnifiedSymbolInformation],
            list[multilspy_types.TreeRepr] | None,
        ]:
            A list of symbols in the file
            The tree representation of the symbols
        """
        with self.open_file(contents):
            response = await self.server.send.document_symbol(
                {
                    "textDocument": {
                        "uri": (
                            Path(self.repository_root_path)
                            / Path(self.relative_file_path)
                        ).as_uri()
                    }
                }
            )

        return response

        # ret: list[multilspy_types.UnifiedSymbolInformation] = []
        # l_tree = None
        # assert isinstance(response, list)
        # for item in response:
        #     assert isinstance(item, dict)
        #     assert LSPConstants.NAME in item
        #     assert LSPConstants.KIND in item

        #     if LSPConstants.CHILDREN in item:
        #         # TODO: l_tree should be a list of TreeRepr. Define the following
        #         # function to return TreeRepr as well

        #         def visit_tree_nodes_and_build_tree_repr(
        #             tree: LSPTypes.DocumentSymbol,
        #         ) -> list[multilspy_types.UnifiedSymbolInformation]:
        #             l: list[multilspy_types.UnifiedSymbolInformation] = []
        #             children = tree.get("children", [])
        #             if "children" in tree:
        #                 del tree["children"]
        #             l.append(multilspy_types.UnifiedSymbolInformation(**tree))
        #             for child in children:
        #                 l.extend(visit_tree_nodes_and_build_tree_repr(child))
        #             return l

        #         ret.extend(visit_tree_nodes_and_build_tree_repr(item))
        #     else:
        #         ret.append(multilspy_types.UnifiedSymbolInformation(**item))

        # return ret, l_tree

    async def request_hover(
        self,
        contents: str,
        line: int,
        column: int,
    ) -> multilspy_types.Hover | None:
        """
        Raise a [textDocument/hover](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_hover)
        request to the Language Server to find the hover information at the given line
        and column in the given file. Wait for the response and return the result.

        :param contents: The contents of the file that has the hover information
        :param line: The line number of the symbol
        :param column: The column number of the symbol

        :return None
        """
        with self.open_file(contents):
            response = await self.server.send.hover(
                {
                    "textDocument": {
                        "uri": (
                            Path(self.repository_root_path)
                            / Path(self.relative_file_path)
                        ).as_uri()
                    },
                    "position": {
                        "line": line,
                        "character": column,
                    },
                }
            )

        if response is None:
            return None

        assert isinstance(response, dict)

        return multilspy_types.Hover(**response)

    async def request_signature_help(
        self,
        contents: str,
        line: int,
        column: int,
    ) -> LSPTypes.SignatureHelp | None:
        """
        This only works when the cursor is inside the function call parentheses.
        Otherwise, it will return None.

        """
        with self.open_file(contents):
            response = await self.server.send.signature_help(
                {
                    "textDocument": {
                        "uri": (
                            Path(self.repository_root_path)
                            / Path(self.relative_file_path)
                        ).as_uri()
                    },
                    "position": {
                        "line": line,
                        "character": column,
                    },
                }
            )
        print(response is None)

        if response is None:
            return None

        assert isinstance(response, dict)

        return LSPTypes.SignatureHelp(**response)


# @ensure_all_methods_implemented(CLLanguageServer)
class SyncCLLanguageServer:
    """
    The SyncLanguageServer class provides a language agnostic interface to the Language
    Server Protocol.
    It is used to communicate with Language Servers of different programming languages.
    """

    def __init__(
        self,
        config: MultilspyConfig | None = None,
        logger: MultilspyLogger | None = None,
        timeout: int | None = None,
    ):
        self.language_server = CLLanguageServer(config, logger)
        self.loop = None
        self.loop_thread = None
        self.timeout = timeout

    @contextmanager
    def start_server(self) -> Iterator["SyncCLLanguageServer"]:
        """
        Starts the language server process and connects to it.
        """
        self.loop = asyncio.new_event_loop()
        loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)
        loop_thread.start()
        ctx = self.language_server.start_server()
        asyncio.run_coroutine_threadsafe(ctx.__aenter__(), loop=self.loop).result()
        yield self
        asyncio.run_coroutine_threadsafe(
            ctx.__aexit__(None, None, None), loop=self.loop
        ).result()
        self.loop.call_soon_threadsafe(self.loop.stop)
        loop_thread.join()

    @contextmanager
    def open_file(self, contents: str) -> Iterator[None]:
        """
        Open a file in the Language Server. This is required before making any
        requests to the Language Server.

        :param contents: The source code of the file to open.
        """
        with self.language_server.open_file(contents):
            yield

    # def request_document_symbols(self, contents: str) -> tuple[
    #     list[multilspy_types.UnifiedSymbolInformation],
    #     list[multilspy_types.TreeRepr] | None,
    # ]:
    def request_document_symbols(self, contents: str) -> list[LSPTypes.DocumentSymbol]:
        """
        Raise a [textDocument/documentSymbol] request to the Language Server to find
        symbols in the given file. Wait for the response and return the result.

        :param contents: The contents of the file to find symbols in.

        :return tuple[
            list[multilspy_types.UnifiedSymbolInformation],
            list[multilspy_types.TreeRepr] | None,
        ]:
            A list of symbols in the file
            The tree representation of the symbols
        """
        result = asyncio.run_coroutine_threadsafe(
            self.language_server.request_document_symbols(contents), self.loop
        ).result(timeout=self.timeout)
        return result

    def request_hover(
        self, contents: str, line: int, column: int
    ) -> multilspy_types.Hover | None:
        """
        Raise a textDocument/hover request to the Language Server to find the hover
        information at the given line and column in the given file. Wait for the
        response and return the result.

        :param contents: The contents of the file to find hover information in
        :param line: The line number of the symbol
        :param column: The column number of the symbol

        :return multilspy_types.Hover | None: The hover information at the given
                                              position, or None if no information
                                              is available
        """
        result = asyncio.run_coroutine_threadsafe(
            self.language_server.request_hover(contents, line, column), self.loop
        ).result(timeout=self.timeout)
        return result

    def request_signature_help(
        self, contents: str, line: int, column: int
    ) -> LSPTypes.SignatureHelp | None:
        result = asyncio.run_coroutine_threadsafe(
            self.language_server.request_signature_help(contents, line, column),
            self.loop,
        ).result(timeout=self.timeout)
        return result
