import { PluginDefinition, CoreOverlayAPI, registerPlugin } from './plugin-api'

const webFetchPlugin: PluginDefinition = {
  name: 'web-fetch',
  version: '0.1.0',
  init: (api: CoreOverlayAPI) => {
    api.onEvent(evt => {
      if (evt.type === 'banterTrigger' && evt.payload.key === 'fetch.page') {
        const targetUrl = evt.payload.url || window.location.href
        fetch(`http://localhost:8000/fetch?url=${encodeURIComponent(targetUrl)}`)
          .then(res => res.json())
          .then(data => api.emitEvent({ type: 'pageContent', payload: data }))
          .catch(err => api.emitEvent({ type: 'aiError', payload: err.message }))
      }
    })
  }
}

registerPlugin(webFetchPlugin)


