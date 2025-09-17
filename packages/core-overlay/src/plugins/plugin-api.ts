export interface PluginDefinition {
  name: string;
  version: string;
  init: (api: CoreOverlayAPI) => void;
}

export interface CoreOverlayAPI {
  onEvent: (callback: (event: any) => void) => void;
  emitEvent: (event: any) => void;
}

export function registerPlugin(plugin: PluginDefinition) {
  console.log(`Plugin ${plugin.name} v${plugin.version} registered.`);
  // In a real scenario, this would add the plugin to a registry
  // and call its init method.
}


