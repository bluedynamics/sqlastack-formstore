import loadable from '@loadable/component';

const applyConfig = (config) => {
  // Volto 19 removed these core loadables; volto-subblocks still injects them.
  config.settings.loadables = {
    ...config.settings.loadables,
    reactDnd: loadable.lib(() => import('react-dnd')),
    reactDndHtml5Backend: loadable.lib(() => import('react-dnd-html5-backend')),
  };
  return config;
};

export default applyConfig;
