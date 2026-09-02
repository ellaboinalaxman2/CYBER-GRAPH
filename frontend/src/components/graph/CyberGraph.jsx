import React, { useEffect, useRef, useState, useCallback } from 'react';
import cytoscape from 'cytoscape';
import { GraphControls } from './GraphControls';
import { GraphLegend } from './GraphLegend';
import { GraphFilters } from './GraphFilters';
import { NodeDetails } from './NodeDetails';
import { AttackPath } from './AttackPath';
import { transformToCytoscapeElements, filterGraphElements } from '../../utils/graphUtils';
import { NODE_TYPE_CONFIG } from '../../constants/nodeTypes';

export const CyberGraph = ({
  nodes = [],
  edges = [],
  activeAttackPath = null,
  onNodeSelect,
  className = '',
}) => {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  const [selectedNodeData, setSelectedNodeData] = useState(null);
  const [currentLayout, setCurrentLayout] = useState('cose');
  const [spacingMultiplier, setSpacingMultiplier] = useState(1.5); // 1.0 = compact, 1.5 = spacious, 2.0 = ultra-wide
  const [filters, setFilters] = useState({
    nodeType: 'ALL',
    severity: 'ALL',
    searchTerm: '',
  });
  const [activeStepIndex, setActiveStepIndex] = useState(0);

  // Helper to generate layout configuration with large spacing
  const getLayoutConfig = useCallback(
    (name, multiplier = 1.5) => {
      switch (name) {
        case 'concentric':
          return {
            name: 'concentric',
            animate: true,
            animationDuration: 500,
            padding: 80,
            spacingFactor: 2.2 * (multiplier / 1.5),
            minNodeSpacing: 100 * (multiplier / 1.5),
            concentric: (node) => (node.data('isSuspicious') || node.data('isInAttackPath') ? 2 : 1),
            levelWidth: () => 1,
          };
        case 'breadthfirst':
          return {
            name: 'breadthfirst',
            animate: true,
            animationDuration: 500,
            padding: 80,
            directed: true,
            spacingFactor: 2.4 * (multiplier / 1.5),
            circle: false,
          };
        case 'circle':
          return {
            name: 'circle',
            animate: true,
            animationDuration: 500,
            padding: 90,
            spacingFactor: 1.8 * (multiplier / 1.5),
          };
        case 'grid':
          return {
            name: 'grid',
            animate: true,
            animationDuration: 500,
            padding: 80,
            spacingFactor: 2.2 * (multiplier / 1.5),
          };
        case 'cose':
        default:
          return {
            name: 'cose',
            animate: true,
            animationDuration: 600,
            padding: 80,
            nodeRepulsion: () => 26000 * multiplier,
            idealEdgeLength: () => 180 * multiplier,
            edgeElasticity: () => 32,
            nestingFactor: 1.2,
            gravity: 0.15 / multiplier,
            numIter: 1000,
            initialTemp: 250,
            coolingFactor: 0.95,
            minTemp: 1.0,
          };
      }
    },
    []
  );

  // Initialize and update Cytoscape graph
  useEffect(() => {
    if (!containerRef.current) return;

    // Filter elements based on UI state
    const filtered = filterGraphElements(nodes, edges, filters);
    const elements = transformToCytoscapeElements(filtered.nodes, filtered.edges, activeAttackPath);

    if (!cyRef.current) {
      cyRef.current = cytoscape({
        container: containerRef.current,
        elements,
        boxSelectionEnabled: false,
        autounselectify: false,
        style: [
          // Base Node styles
          {
            selector: 'node',
            style: {
              'background-color': (ele) => {
                const type = ele.data('type');
                const isSuspicious = ele.data('isSuspicious');
                if (ele.data('isInAttackPath') || isSuspicious) return '#ef4444';
                return NODE_TYPE_CONFIG[type]?.color || '#06b6d4';
              },
              label: 'data(label)',
              color: '#f8fafc',
              'font-size': '12px',
              'font-weight': 'bold',
              'font-family': 'JetBrains Mono, monospace',
              'text-valign': 'bottom',
              'text-margin-y': 10,
              'text-background-color': '#090d16',
              'text-background-opacity': 0.92,
              'text-background-padding': '4px',
              'text-background-shape': 'roundrectangle',
              'text-border-color': '#1e293b',
              'text-border-width': 1,
              'text-border-opacity': 0.8,
              width: (ele) => (ele.data('isInAttackPath') ? 54 : 44),
              height: (ele) => (ele.data('isInAttackPath') ? 54 : 44),
              'border-width': 3,
              'border-color': (ele) => {
                if (ele.data('isInAttackPath')) return '#fca5a5';
                if (ele.data('isSuspicious')) return '#ef4444';
                return '#1e293b';
              },
              'border-opacity': 0.9,
              'overlay-opacity': 0,
              'transition-property': 'background-color, line-color, target-arrow-color, width, height, border-color, shadow-blur',
              'transition-duration': '0.3s',
            },
          },
          // Node selected / active state
          {
            selector: 'node:selected',
            style: {
              'border-width': 4,
              'border-color': '#22d3ee',
              'background-color': '#0891b2',
              'shadow-blur': 30,
              'shadow-color': '#06b6d4',
              'shadow-opacity': 0.9,
              width: 58,
              height: 58,
            },
          },
          // Hover state on node
          {
            selector: 'node:hover',
            style: {
              cursor: 'pointer',
              'border-color': '#38bdf8',
            },
          },
          // Edge styles
          {
            selector: 'edge',
            style: {
              width: (ele) => (ele.data('isInAttackPath') ? 4.5 : 2.5),
              'line-color': (ele) => (ele.data('isInAttackPath') ? '#ef4444' : '#334155'),
              'target-arrow-color': (ele) => (ele.data('isInAttackPath') ? '#ef4444' : '#64748b'),
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'control-point-step-size': 50,
              'arrow-scale': 1.4,
              label: 'data(label)',
              'font-size': '10px',
              'font-weight': '600',
              'font-family': 'JetBrains Mono, monospace',
              color: '#94a3b8',
              'text-rotation': 'autorotate',
              'text-margin-y': -9,
              'text-background-color': '#070a12',
              'text-background-opacity': 0.95,
              'text-background-padding': '3px',
              'text-background-shape': 'roundrectangle',
              'text-border-color': '#1e293b',
              'text-border-width': 1,
              'line-style': (ele) => (ele.data('isInAttackPath') ? 'dashed' : 'solid'),
            },
          },
          // Selected edge state
          {
            selector: 'edge:selected',
            style: {
              'line-color': '#06b6d4',
              'target-arrow-color': '#06b6d4',
              width: 4,
              color: '#22d3ee',
            },
          },
        ],
        layout: getLayoutConfig(currentLayout, spacingMultiplier),
      });

      // Tap event handler on node
      cyRef.current.on('tap', 'node', (evt) => {
        const node = evt.target;
        const rawNode = nodes.find((n) => n.id === node.id()) || node.data();
        setSelectedNodeData(rawNode);
        onNodeSelect?.(rawNode);
      });

      // Tap event on background (deselect)
      cyRef.current.on('tap', (evt) => {
        if (evt.target === cyRef.current) {
          setSelectedNodeData(null);
        }
      });
    } else {
      // Update elements smoothly
      cyRef.current.json({ elements });
      const layout = cyRef.current.layout(getLayoutConfig(currentLayout, spacingMultiplier));
      layout.run();
    }
  }, [nodes, edges, activeAttackPath, filters, currentLayout, spacingMultiplier, getLayoutConfig, onNodeSelect]);

  // Clean up Cytoscape instance on total component unmount
  useEffect(() => {
    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, []);

  const handleZoomIn = useCallback(() => {
    if (cyRef.current) {
      cyRef.current.zoom({
        level: cyRef.current.zoom() * 1.3,
        renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 },
      });
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    if (cyRef.current) {
      cyRef.current.zoom({
        level: cyRef.current.zoom() * 0.75,
        renderedPosition: { x: cyRef.current.width() / 2, y: cyRef.current.height() / 2 },
      });
    }
  }, []);

  const handleFit = useCallback(() => {
    if (cyRef.current) {
      cyRef.current.fit(undefined, 70);
    }
  }, []);

  const handleResetLayout = useCallback(() => {
    if (cyRef.current) {
      const layout = cyRef.current.layout(getLayoutConfig(currentLayout, spacingMultiplier));
      layout.run();
    }
  }, [currentLayout, spacingMultiplier, getLayoutConfig]);

  const handleToggleLayout = useCallback(() => {
    const layouts = ['cose', 'concentric', 'breadthfirst', 'circle', 'grid'];
    const next = layouts[(layouts.indexOf(currentLayout) + 1) % layouts.length];
    setCurrentLayout(next);
  }, [currentLayout]);

  const handleSpacingChange = useCallback((newMultiplier) => {
    setSpacingMultiplier(newMultiplier);
  }, []);

  return (
    <div
      className={`relative w-full h-[720px] bg-[#070a12] rounded-2xl border border-slate-800 overflow-hidden shadow-2xl ${className}`}
      style={{
        backgroundImage: `
          radial-gradient(circle at center, rgba(15, 23, 42, 0.8) 0%, #070a12 100%),
          linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px)
        `,
        backgroundSize: '100% 100%, 40px 40px, 40px 40px',
      }}
    >
      {/* Top Bar with Filters, Spacing and Controls */}
      <div className="absolute top-4 left-4 right-4 z-20 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 pointer-events-none">
        <div className="pointer-events-auto w-full md:w-auto">
          <GraphFilters
            filters={filters}
            onFilterChange={(newF) => setFilters((prev) => ({ ...prev, ...newF }))}
            onReset={() => setFilters({ nodeType: 'ALL', severity: 'ALL', searchTerm: '' })}
          />
        </div>

        <div className="pointer-events-auto self-end md:self-auto flex items-center gap-2">
          {/* Spacing Quick-Selector */}
          <div className="flex items-center gap-1 p-1 bg-slate-900/90 border border-slate-800 rounded-xl text-xs font-mono backdrop-blur-md">
            <span className="text-[10px] text-slate-400 uppercase px-1.5">Spacing:</span>
            {[
              { label: '1x', val: 1.0 },
              { label: '1.5x', val: 1.5 },
              { label: '2.2x', val: 2.2 },
            ].map((sp) => (
              <button
                key={sp.label}
                onClick={() => handleSpacingChange(sp.val)}
                className={`px-2 py-1 rounded-lg transition-all ${
                  spacingMultiplier === sp.val
                    ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/40'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {sp.label}
              </button>
            ))}
          </div>

          <GraphControls
            onZoomIn={handleZoomIn}
            onZoomOut={handleZoomOut}
            onFit={handleFit}
            onResetLayout={handleResetLayout}
            onToggleLayout={handleToggleLayout}
            currentLayout={currentLayout}
          />
        </div>
      </div>

      {/* Main Cytoscape Canvas */}
      <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />

      {/* Bottom Overlays */}
      <div className="absolute bottom-4 left-4 z-20 pointer-events-auto">
        <GraphLegend />
      </div>

      {/* Attack Path Stepper (if active) */}
      {activeAttackPath && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 pointer-events-auto w-11/12 max-w-xl">
          <AttackPath
            attackPath={activeAttackPath.path || []}
            timeline={activeAttackPath.timeline || []}
            activeStepIndex={activeStepIndex}
            onStepSelect={(idx) => {
              setActiveStepIndex(idx);
              const targetNodeId = activeAttackPath.path?.[idx];
              if (targetNodeId && cyRef.current) {
                const targetNode = cyRef.current.getElementById(targetNodeId);
                if (targetNode && targetNode.length > 0) {
                  cyRef.current.animate({
                    center: { eles: targetNode },
                    zoom: 1.3,
                    duration: 400,
                  });
                  targetNode.select();
                  const rawNode = nodes.find((n) => n.id === targetNodeId);
                  if (rawNode) setSelectedNodeData(rawNode);
                }
              }
            }}
          />
        </div>
      )}

      {/* Node Inspector Drawer */}
      {selectedNodeData && (
        <div className="absolute top-20 right-4 z-30 pointer-events-auto">
          <NodeDetails
            node={selectedNodeData}
            onClose={() => {
              setSelectedNodeData(null);
              if (cyRef.current) cyRef.current.$(':selected').unselect();
            }}
          />
        </div>
      )}
    </div>
  );
};

export default CyberGraph;
