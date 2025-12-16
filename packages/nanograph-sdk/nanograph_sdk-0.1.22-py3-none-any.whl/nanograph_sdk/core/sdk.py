import asyncio
from typing import List, Callable, Optional, Coroutine, Any, Union, TYPE_CHECKING, BinaryIO
import json, os
from pathlib import Path

# TYPE_CHECKING block can be removed if Observer type hint relies on string literal + type:ignore
# if TYPE_CHECKING:
#     from watchdog.observers import Observer
    # WatchdogObserver = Observer # Removing alias

from .interfaces import NanoSDKConfig, NodeDefinition, NodeInstance, NodeDefinitionsMessage
from .node_registry import NodeRegistry
from .server import ServerInstance, create_server
from .message_handler import MessageHandler
from .file_watcher import start_file_watcher
from .asset_resolver import (
    resolve_asset as _resolve_asset,
    get_asset_download_url as _get_asset_download_url,
    get_asset_presigned_url as _get_asset_presigned_url,
    ResolveAssetOptions
)
from .asset_uploader import (
    upload_asset as _upload_asset,
    UploadAssetOptions,
    AssetUploadResult
)
from .logger import StructuredLogger

class NanoSDK:
    _instance: Optional['NanoSDK'] = None
    _pre_registered_nodes: List[NodeInstance] = []

    def __init__(self):
        if NanoSDK._instance is not None:
            # This could be a warning or an error depending on desired behavior
            # print("[NanoSDK] Warning: NanoSDK already initialized. Overwriting existing instance.")
            pass # Allow re-initialization for now, useful in some dev scenarios

        json_path = Path.cwd() / 'nanoserver.json'
        if not json_path.exists():
            raise ValueError("nanoserver.json file is required but was not found in the current directory")
            
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        config = {
            'domain': os.environ.get('DOMAIN') or data.get('domain') or 'nanocore.local',
            'server_display_name': os.environ.get('SERVER_DISPLAY_NAME') or data.get('serverDisplayName') or 'NanoServer',
            'server_uid': os.environ.get('SERVER_UID') or data.get('serverUid'),
            'server_package_id': os.environ.get('SERVER_PACKAGE_ID') or data.get('serverPackageId'),
            'language': data.get('language') or 'python',
            'port': int(os.environ.get('PORT', 3017)),
            'nodes_path': data.get('nodesPath', 'nodes'),
            'auto_watch': data.get('autoWatch', True),
            'watch_debounce_time': data.get('watchDebounceTime', 500)
        }

        # Validate required environment variables
        if not config['server_uid']:
            raise ValueError("SERVER_UID environment variable is required")
        if not config['server_package_id']:
            raise ValueError("SERVER_PACKAGE_ID environment variable or 'serverPackageId' in nanoserver.json is required")
        if not config['domain']:
            raise ValueError("DOMAIN environment variable is required")
        if not config['language']:
            raise ValueError("LANGUAGE in nanoserver.json is required")
        
        # Validate language
        if config['language'] not in ['python', 'javascript']:
            raise ValueError("'language' in nanoserver.json must be either 'python' or 'javascript'")

        # Ensure env PORT overrides
        config['port'] = int(os.environ.get('PORT', config.get('port', 3017)))

        self.config: NanoSDKConfig = config
        
        self.logger = StructuredLogger(f"NanoSDK@{self.config['server_uid']}")

        self.registry = NodeRegistry(self.config['server_uid'], self.logger.child('Registry'))
        self.server: Optional[ServerInstance] = None
        self.message_handler: Optional[MessageHandler] = None
        self.observer: Optional['Observer'] = None # type: ignore[name-defined] # Revert to string literal and add type ignore
        self.shutdown_handlers: List[Callable[[], Union[None, Coroutine[Any, Any, None]]]] = []

        NanoSDK._instance = self

        for node_instance in NanoSDK._pre_registered_nodes:
            self.registry.register_node(node_instance, silent=True) # Register silently
        NanoSDK._pre_registered_nodes.clear() # Clear after registration
        
        self.logger.success(
            f"Initialized Python NanoServer '{self.config['server_display_name']}' (UID: {self.config['server_uid']})"
        )

    @staticmethod
    def register_node(definition: NodeDefinition) -> NodeInstance:
        # Basic validation of definition structure could be added here
        node_instance: NodeInstance = {
            'definition': {**definition, 'type': 'server'}, # Ensure type is server
            'execute': lambda ctx: {} # Default empty execute, user must override
        }
        if NanoSDK._instance:
            NanoSDK._instance.registry.register_node(node_instance)
            NanoSDK._instance.logger.debug(
                f"Statically registered node: {definition['name']} ({definition['uid']})"
            )
        else:
            NanoSDK._pre_registered_nodes.append(node_instance)
        return node_instance

    async def load_node_definitions(self, silent_reload: bool = False) -> None:
        # When reloading via file watcher, initial_load_complete will be true in registry
        # The registry's load_node_definitions handles clearing if it's not a silent (initial) load.
        # For file watcher triggered reloads (not silent_reload), the registry should clear before loading.
        if not silent_reload and self.registry.initial_load_complete:
            self.logger.debug("File watcher triggered reload. Clearing dynamic nodes from registry before loading.")
            # This is tricky. If we clear all, pre-registered static nodes are gone.
            # NodeRegistry.load_node_definitions handles this by not clearing if it's a silent/initial load.
            # For explicit reload (e.g. by file watcher), we want to re-evaluate all files.
            # The current NodeRegistry.load_node_definitions behavior is to only clear if it's a non-silent subsequent load.
            # This means pre-registered nodes persist unless their files are re-processed.
            # To ensure a full refresh from files on watcher events:
            self.registry.clear_nodes() # Clears all, then loads. This means static nodes in files get re-added.
                                      # Nodes registered only via NanoSDK.register_node and not in a scanned file might be lost on reload.
                                      # This matches NodeJS SDK where reload means re-scan from disk.

        await self.registry.load_node_definitions(self.config['nodes_path'], silent_reload)

    async def _broadcast_definitions_update(self, message: NodeDefinitionsMessage):
        # Ensure serverPackageId is included for clients (NanoCore expects it)
        if 'serverPackageId' not in message or not message['serverPackageId']:
            message['serverPackageId'] = self.config['server_package_id']
        if self.server:
            await self.server.broadcast(message)
        else:
            self.logger.warn("Cannot broadcast definitions update: server not initialized")

    def _start_file_watcher_internal(self) -> None:
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=1) # Wait for the observer thread to stop
            self.logger.debug("Stopped existing file watcher")
            self.observer = None

        if not self.config['auto_watch']:
            self.logger.info("Auto-watch disabled. File watcher not started")
            return

        if not self.server: # Should not happen if called from start()
            self.logger.error("Cannot start file watcher: server not available")
            return

        self.observer = start_file_watcher(
            domain=self.config['domain'],
            server_uid=self.config['server_uid'],
            nodes_path=self.config['nodes_path'],
            # For reload_nodes_fn, we want to do a non-silent reload
            reload_nodes_fn=lambda: self.load_node_definitions(silent_reload=False),
            get_definitions_for_client_fn=self.registry.get_all_definitions_for_client,
            broadcast_fn=self._broadcast_definitions_update,
            debounce_time=self.config.get('watch_debounce_time', 500),  # Default to 500ms if not specified
            logger=self.logger.child('FileWatcher')
        )
        if not self.observer:
            self.logger.warn("File watcher setup failed (directory not found)")

    async def start(self) -> None:
        self.logger.debug("Bootstrapping NanoSDK server components")
        preregistered_count = self.registry.get_node_count()
        if preregistered_count > 0:
            self.logger.debug(f"Detected {preregistered_count} statically registered node(s)")

        # Load nodes from directory (silent=True because it's part of initial startup)
        # Pre-registered nodes are already in, this adds/updates from files.
        await self.load_node_definitions(silent_reload=True)
        self.logger.debug("Initial node definitions loaded")

        self.message_handler = MessageHandler(
            server_uid=self.config['server_uid'],
            node_registry=self.registry.nodes_map, # Pass the actual map
            logger=self.logger.child('MessageHandler')
        )

        self.server = create_server(
            domain=self.config['domain'],
            server_display_name=self.config['server_display_name'],
            server_uid=self.config['server_uid'],
            server_package_id=self.config['server_package_id'],
            port=self.config['port'],
            get_definitions_fn=self.registry.get_all_definitions_for_client,
            message_handler=self.message_handler,
            logger=self.logger.child('Server')
        )

        await self.server.start()
        
        if self.config['auto_watch']:
            self._start_file_watcher_internal()
        
        auto_watch_label = 'enabled' if self.config['auto_watch'] else 'disabled'
        self.logger.success(
            f"Server '{self.config['server_display_name']}' (UID: {self.config['server_uid']}) listening on port {self.config['port']}"
        )
        self.logger.info(
            f"Serving {self.registry.get_node_count()} node(s); auto-watch {auto_watch_label}"
        )

        # Signal that the server is ready after all components are initialized
        if self.server:
            self.server.emit_ready()

    async def stop(self) -> None:
        self.logger.info("Server stopping...")

        if self.observer:
            self.logger.debug("Stopping file watcher...")
            self.observer.stop()
            self.observer.join(timeout=1) # Wait for thread to finish
            self.observer = None
            self.logger.debug("File watcher stopped")

        if self.server:
            await self.server.stop()
            self.server = None
        
        # Call shutdown handlers
        self.logger.debug(f"Executing {len(self.shutdown_handlers)} shutdown handler(s)...")
        for handler in self.shutdown_handlers:
            try:
                result = handler()
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                self.logger.error(f"Error in shutdown handler: {e}")
        self.logger.debug("Shutdown handlers executed")
        self.logger.info(f"Server '{self.config['server_display_name']}' (UID: {self.config['server_uid']}) stopped.")
        NanoSDK._instance = None # Allow re-creation of SDK after stop

    def on_shutdown(self, handler: Callable[[], Union[None, Coroutine[Any, Any, None]]]) -> None:
        self.shutdown_handlers.append(handler)

    def get_node_definitions(self) -> List[NodeDefinition]:
        return self.registry.get_all_definitions_for_client()

    # Asset-related methods
    async def resolve_asset(
        self,
        ref: str,
        options: Optional[ResolveAssetOptions] = None
    ) -> Union[BinaryIO, bytes]:
        """
        Resolve an asset reference to either a stream or buffer of data.
        This is an instance method that uses the SDK's configuration.
        """
        return await _resolve_asset(ref, options)

    def get_asset_download_url(self, ref: str) -> str:
        """
        Get the direct download URL for an asset.
        This is an instance method that uses the SDK's configuration.
        """
        return _get_asset_download_url(ref)

    async def get_asset_presigned_url(self, ref: str) -> dict:
        """
        Get a presigned URL for accessing an asset.
        This is an instance method that uses the SDK's configuration.
        """
        return await _get_asset_presigned_url(ref)

    async def upload_asset(
        self,
        file: Union[str, bytes, BinaryIO],
        options: Optional[UploadAssetOptions] = None
    ) -> AssetUploadResult:
        """
        Upload an asset to the nanocore asset server.
        This is an instance method that uses the SDK's configuration.
        """
        return await _upload_asset(file, options)

    # Static asset methods for convenience
    @staticmethod
    async def resolve_asset_static(
        ref: str,
        options: Optional[ResolveAssetOptions] = None
    ) -> Union[BinaryIO, bytes]:
        """Static method for resolving assets without an SDK instance."""
        return await _resolve_asset(ref, options)

    @staticmethod
    def get_asset_download_url_static(ref: str) -> str:
        """Static method for getting asset download URL without an SDK instance."""
        return _get_asset_download_url(ref)

    @staticmethod
    async def get_asset_presigned_url_static(ref: str) -> dict:
        """Static method for getting presigned URLs without an SDK instance."""
        return await _get_asset_presigned_url(ref)

    @staticmethod
    async def upload_asset_static(
        file: Union[str, bytes, BinaryIO],
        options: Optional[UploadAssetOptions] = None
    ) -> AssetUploadResult:
        """Static method for uploading assets without an SDK instance."""
        return await _upload_asset(file, options) 
