import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', '5ff'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', '5ba'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', 'a2b'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', 'c3c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '156'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '88c'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '000'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', '3d7'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '25c'),
    routes: [
      {
        path: '/docs',
        component: ComponentCreator('/docs', '138'),
        routes: [
          {
            path: '/docs',
            component: ComponentCreator('/docs', '1cc'),
            routes: [
              {
                path: '/docs/architecture/base-shdl',
                component: ComponentCreator('/docs/architecture/base-shdl', 'dd2'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/compiler-internals',
                component: ComponentCreator('/docs/architecture/compiler-internals', '230'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/flattening-pipeline',
                component: ComponentCreator('/docs/architecture/flattening-pipeline', '76e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/overview',
                component: ComponentCreator('/docs/architecture/overview', '833'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/architecture/pyshdl-internals',
                component: ComponentCreator('/docs/architecture/pyshdl-internals', '4fb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/category/architecture',
                component: ComponentCreator('/docs/category/architecture', '6d1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/category/examples',
                component: ComponentCreator('/docs/category/examples', '04a'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/category/getting-started',
                component: ComponentCreator('/docs/category/getting-started', '4e8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/category/language-reference',
                component: ComponentCreator('/docs/category/language-reference', '1f3'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/category/shdb-debugger',
                component: ComponentCreator('/docs/category/shdb-debugger', 'd39'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/breakpoints',
                component: ComponentCreator('/docs/debugger/breakpoints', '3bf'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/commands',
                component: ComponentCreator('/docs/debugger/commands', '65e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/common-problems',
                component: ComponentCreator('/docs/debugger/common-problems', '1ff'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/debug-build',
                component: ComponentCreator('/docs/debugger/debug-build', 'bc7'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/getting-started',
                component: ComponentCreator('/docs/debugger/getting-started', '219'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/hierarchy',
                component: ComponentCreator('/docs/debugger/hierarchy', '065'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/inspection',
                component: ComponentCreator('/docs/debugger/inspection', '119'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/overview',
                component: ComponentCreator('/docs/debugger/overview', '8dc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/python-api',
                component: ComponentCreator('/docs/debugger/python-api', '89d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/scripting',
                component: ComponentCreator('/docs/debugger/scripting', '040'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/debugger/waveforms',
                component: ComponentCreator('/docs/debugger/waveforms', '953'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/examples/bit-adder',
                component: ComponentCreator('/docs/examples/bit-adder', 'c27'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/examples/comparator',
                component: ComponentCreator('/docs/examples/comparator', 'cfc'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/examples/decoder',
                component: ComponentCreator('/docs/examples/decoder', '1fb'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/examples/full-adder',
                component: ComponentCreator('/docs/examples/full-adder', '9ef'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/examples/half-adder',
                component: ComponentCreator('/docs/examples/half-adder', 'e44'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/examples/multiplexer',
                component: ComponentCreator('/docs/examples/multiplexer', 'df8'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/examples/register',
                component: ComponentCreator('/docs/examples/register', 'd92'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/getting-started/first-circuit',
                component: ComponentCreator('/docs/getting-started/first-circuit', '66f'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/getting-started/installation',
                component: ComponentCreator('/docs/getting-started/installation', '267'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/getting-started/using-pyshdl',
                component: ComponentCreator('/docs/getting-started/using-pyshdl', 'ace'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/intro',
                component: ComponentCreator('/docs/intro', '61d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/components',
                component: ComponentCreator('/docs/language-reference/components', '747'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/connections',
                component: ComponentCreator('/docs/language-reference/connections', 'b73'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/constants',
                component: ComponentCreator('/docs/language-reference/constants', '45e'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/errors',
                component: ComponentCreator('/docs/language-reference/errors', '816'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/generators',
                component: ComponentCreator('/docs/language-reference/generators', '721'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/imports',
                component: ComponentCreator('/docs/language-reference/imports', '68d'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/lexical-elements',
                component: ComponentCreator('/docs/language-reference/lexical-elements', '5f1'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/overview',
                component: ComponentCreator('/docs/language-reference/overview', '784'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/signals',
                component: ComponentCreator('/docs/language-reference/signals', '134'),
                exact: true,
                sidebar: "tutorialSidebar"
              },
              {
                path: '/docs/language-reference/standard-gates',
                component: ComponentCreator('/docs/language-reference/standard-gates', '50d'),
                exact: true,
                sidebar: "tutorialSidebar"
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'e5f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
