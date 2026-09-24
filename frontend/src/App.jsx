import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import Header from './components/Header';
import MetricCard from './components/MetricCard';
import ZoneCard from './components/ZoneCard';
import RiskMap from './components/RiskMap';
import WarningPanel from './components/WarningPanel';
import SensorCharts from './components/SensorCharts';
import MLPanel from './components/MLPanel';
import AlertFeed from './components/AlertFeed';
import SensorTable from './components/SensorTable';
import SystemStatus from './components/SystemStatus';
import Login from './components/Login';
import AdminPanel from './components/AdminPanel';
import { useWebSocket } from './hooks/useWebSocket';
import { useAuth } from './context/AuthContext';
import {
  getLatestSensors,
  getAlerts,
  getSystemStatus,
  getSensorHistory,
  acknowledgeAlert
} from './services/api';
import { Radio, Layers, AlertTriangle, Clock, ShieldAlert } from 'lucide-react';

export default function App() {
  const { user, role, isAuthenticated, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [nodes, setNodes] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [selectedNodeId, setSelectedNodeId] = useState('ALL');
  const [systemStatus, setSystemStatus] = useState(null);
  const [lastSync, setLastSync] = useState(null);
  const [isDataLoading, setIsDataLoading] = useState(true);

  // WebSocket Message Handler
  const handleWsMessage = useCallback((payload) => {
    if (!payload || !payload.type) return;

    if (payload.type === 'initial_state' && payload.data) {
      if (Array.isArray(payload.data.nodes)) setNodes(payload.data.nodes);
      if (Array.isArray(payload.data.alerts)) setAlerts(payload.data.alerts);
      if (payload.data.system_status) setSystemStatus(payload.data.system_status);
      setLastSync(new Date().toLocaleTimeString());
      setIsDataLoading(false);
    } else if (payload.type === 'sensor_update' && payload.data) {
      const reading = payload.data;
      const nowStr = new Date().toLocaleTimeString();
      setLastSync(nowStr);
      setIsDataLoading(false);

      // Update specific node in state
      setNodes((prevNodes) => {
        const safeNodes = Array.isArray(prevNodes) ? prevNodes : [];
        const index = safeNodes.findIndex((n) => n?.node_id === reading.node_id);
        if (index >= 0) {
          const updated = [...safeNodes];
          updated[index] = { ...updated[index], ...reading };
          return updated;
        }
        return [...safeNodes, reading];
      });

      // Append to rolling chart points
      setChartData((prev) => {
        const safePrev = Array.isArray(prev) ? prev : [];
        const newPoint = {
          node_id: reading.node_id,
          time: new Date(reading.timestamp || Date.now()).toLocaleTimeString(),
          tilt: reading.tilt,
          vibration: reading.vibration,
          crack_displacement: reading.crack_displacement
        };
        const updated = [...safePrev, newPoint];
        return updated.slice(-60); // Keep last 60 readings
      });
    } else if (payload.type === 'alert' && payload.data) {
      const newAlert = payload.data;
      setAlerts((prev) => {
        const safeAlerts = Array.isArray(prev) ? prev : [];
        if (safeAlerts.some((a) => a?.alert_id === newAlert.alert_id)) return safeAlerts;
        return [newAlert, ...safeAlerts.slice(0, 49)];
      });
    }
  }, []);

  // Connect WebSocket only when authenticated
  const { connectionStatus } = useWebSocket(isAuthenticated ? handleWsMessage : null);

  // Reset all dashboard state when logged out
  useEffect(() => {
    if (!isAuthenticated) {
      setNodes([]);
      setAlerts([]);
      setChartData([]);
      setSelectedNodeId('ALL');
      setLastSync(null);
      setSystemStatus(null);
      setIsDataLoading(true);
    }
  }, [isAuthenticated]);

  // Initial Data Hydration when authenticated
  useEffect(() => {
    if (!isAuthenticated) return;

    let isMounted = true;

    async function hydrate() {
      setIsDataLoading(true);
      try {
        const [sys, initialNodes, initialAlerts, history] = await Promise.all([
          getSystemStatus(),
          getLatestSensors(),
          getAlerts(15),
          getSensorHistory(null, null, 30)
        ]);

        if (!isMounted) return;

        if (sys) setSystemStatus(sys);
        if (Array.isArray(initialNodes)) setNodes(initialNodes);
        if (Array.isArray(initialAlerts)) setAlerts(initialAlerts);

        if (Array.isArray(history) && history.length > 0) {
          const points = history.map((r) => ({
            node_id: r.node_id,
            time: new Date(r.timestamp || Date.now()).toLocaleTimeString(),
            tilt: r.tilt,
            vibration: r.vibration,
            crack_displacement: r.crack_displacement
          }));
          setChartData(points);
        }
        if (Array.isArray(initialNodes) && initialNodes.length > 0) {
          setLastSync(new Date().toLocaleTimeString());
        }
      } catch (err) {
        console.warn('[Hydration Warning]:', err);
      } finally {
        if (isMounted) {
          setIsDataLoading(false);
        }
      }
    }

    hydrate();

    // Regular system status poll
    const pollTimer = setInterval(async () => {
      const sys = await getSystemStatus();
      if (sys && isMounted) setSystemStatus(sys);
    }, 10000);

    return () => {
      isMounted = false;
      clearInterval(pollTimer);
    };
  }, [isAuthenticated]);

  const handleAcknowledgeAlert = async (alertId) => {
    const res = await acknowledgeAlert(alertId);
    if (res) {
      setAlerts((prev) =>
        (Array.isArray(prev) ? prev : []).map((a) =>
          a.alert_id === alertId ? { ...a, status: 'ACKNOWLEDGED' } : a
        )
      );
    }
  };

  // Safe aggregated metrics
  const safeNodes = Array.isArray(nodes) ? nodes : [];
  const safeAlerts = Array.isArray(alerts) ? alerts : [];

  const activeNodesCount = safeNodes.filter((n) => n?.status !== 'OFFLINE').length;
  const criticalAlertsCount = safeAlerts.filter(
    (a) => (a?.severity === 'CRITICAL' || a?.severity === 'HIGH') && a?.status !== 'ACKNOWLEDGED'
  ).length;

  const highestRiskNode = useMemo(() => {
    if (safeNodes.length === 0) return null;
    return safeNodes.reduce((max, n) => ((n?.risk_score ?? 0) > (max?.risk_score ?? 0) ? n : max), safeNodes[0]);
  }, [safeNodes]);

  const zoneA = useMemo(() => safeNodes.filter((n) => n?.zone === 'ZONE A'), [safeNodes]);
  const zoneB = useMemo(() => safeNodes.filter((n) => n?.zone === 'ZONE B'), [safeNodes]);
  const zoneC = useMemo(() => safeNodes.filter((n) => n?.zone === 'ZONE C'), [safeNodes]);

  const focusedNode = useMemo(() => {
    if (selectedNodeId !== 'ALL') {
      const found = safeNodes.find((n) => n?.node_id === selectedNodeId);
      if (found) return found;
    }
    return highestRiskNode;
  }, [selectedNodeId, safeNodes, highestRiskNode]);

  // Loading Screen while session is being verified
  if (authLoading) {
    return (
      <div className="min-h-screen bg-[#F5F7FA] flex flex-col items-center justify-center p-4 text-[#0F172A]">
        <div className="flex flex-col items-center space-y-3">
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-2xl text-[#00A884]">
            <ShieldAlert className="w-10 h-10 animate-pulse" />
          </div>
          <div className="font-mono font-bold text-xl text-[#0F172A]">NAHIDA</div>
          <p className="text-xs text-[#64748B]">Verifying operational credentials...</p>
        </div>
      </div>
    );
  }

  // Dashboard Page Component
  const DashboardView = () => (
    <div className="min-h-screen bg-[#F5F7FA] text-[#0F172A] flex flex-col">
      <Header
        systemStatus={systemStatus}
        wsStatus={connectionStatus}
        currentView="dashboard"
        onNavigate={(view, tab) => {
          if (view === 'admin') {
            navigate(tab ? `/${tab}` : '/admin');
          } else {
            navigate('/dashboard');
          }
        }}
      />

      <main className="flex-1 max-w-[1920px] w-full mx-auto p-4 space-y-4">
        {/* Row 1: Top 4 KPI Metric Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            icon={Radio}
            label="Active Monitored Nodes"
            value={isDataLoading ? 'Loading...' : `${activeNodesCount} / ${safeNodes.length}`}
            subtext={safeNodes.length > 0 ? 'Telemetry: Real-time' : 'No active telemetry'}
            indicatorColor={activeNodesCount > 0 ? 'emerald' : 'slate'}
            statusBadge={activeNodesCount > 0 ? 'ONLINE' : 'WAITING'}
          />
          <MetricCard
            icon={Layers}
            label="Subsidence Zones Monitored"
            value={isDataLoading ? 'Loading...' : '3'}
            subtext="Zone A (Highwall), B (Dump), C (Shaft)"
            indicatorColor="sky"
            statusBadge="ACTIVE"
          />
          <MetricCard
            icon={AlertTriangle}
            label="High & Critical Alerts"
            value={isDataLoading ? 'Loading...' : criticalAlertsCount}
            subtext={criticalAlertsCount > 0 ? 'Active threshold breaches' : 'Zero active critical alerts'}
            indicatorColor={criticalAlertsCount > 0 ? 'rose' : 'emerald'}
            statusBadge={criticalAlertsCount > 0 ? 'ATTENTION' : 'NORMAL'}
          />
          <MetricCard
            icon={Clock}
            label="Last Telemetry Sync"
            value={lastSync || (isDataLoading ? 'Connecting...' : 'No telemetry available')}
            subtext="WebSocket Real-Time Broadcast"
            indicatorColor={lastSync ? 'emerald' : 'slate'}
            statusBadge={lastSync ? 'LIVE' : 'STANDBY'}
          />
        </section>

        {/* Row 2: 3 Zone Overview Cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ZoneCard
            zoneName="ZONE A"
            zoneNodes={zoneA}
            onSelectNode={(id) => setSelectedNodeId(id)}
          />
          <ZoneCard
            zoneName="ZONE B"
            zoneNodes={zoneB}
            onSelectNode={(id) => setSelectedNodeId(id)}
          />
          <ZoneCard
            zoneName="ZONE C"
            zoneNodes={zoneC}
            onSelectNode={(id) => setSelectedNodeId(id)}
          />
        </section>

        {/* Row 3: Central Operations Grid */}
        <section className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          {/* Left Column (2/3 width on XL displays) */}
          <div className="xl:col-span-2 space-y-4 flex flex-col">
            {/* Interactive Mine Risk Map */}
            <div className="min-h-[460px] lg:h-[490px]">
              <RiskMap
                nodes={safeNodes}
                selectedNodeId={selectedNodeId}
                onSelectNode={(id) => setSelectedNodeId(id)}
              />
            </div>

            {/* Real-time Telemetry Charts */}
            <div className="flex-1">
              <SensorCharts
                chartData={chartData}
                nodes={safeNodes}
                selectedNodeId={selectedNodeId}
                onSelectNode={(id) => setSelectedNodeId(id)}
              />
            </div>
          </div>

          {/* Right Column (1/3 width on XL displays) */}
          <div className="space-y-4 flex flex-col">
            {/* Early Warning Panel */}
            <div className="min-h-[290px]">
              <WarningPanel
                highestRiskNode={highestRiskNode}
                activeAlerts={safeAlerts}
                hasNodes={safeNodes.length > 0}
                onSelectNode={(id) => setSelectedNodeId(id)}
              />
            </div>

            {/* AI Anomaly Monitor */}
            <div>
              <MLPanel focalNode={focusedNode} />
            </div>

            {/* Live Alert Feed */}
            <div className="flex-1">
              <AlertFeed
                alerts={safeAlerts}
                userRole={role || 'worker'}
                onAcknowledgeAlert={handleAcknowledgeAlert}
                onSelectNode={(id) => setSelectedNodeId(id)}
              />
            </div>
          </div>
        </section>

        {/* Row 4: Comprehensive Telemetry Table */}
        <section>
          <SensorTable
            nodes={safeNodes}
            selectedNodeId={selectedNodeId}
            onSelectNode={(id) => setSelectedNodeId(id)}
          />
        </section>

        {/* Bottom System Status Footer */}
        <SystemStatus systemStatus={systemStatus} wsStatus={connectionStatus} />
      </main>
    </div>
  );

  // Admin Area Wrapper Component
  const AdminViewWrapper = ({ defaultTab = 'users' }) => (
    <div className="min-h-screen bg-[#F5F7FA] text-[#0F172A] flex flex-col">
      <Header
        systemStatus={systemStatus}
        wsStatus={connectionStatus}
        currentView="admin"
        onNavigate={(view, tab) => {
          if (view === 'dashboard') {
            navigate('/dashboard');
          } else {
            navigate(tab ? `/${tab}` : '/admin');
          }
        }}
      />
      <main className="flex-1 max-w-[1920px] w-full mx-auto p-4 space-y-4">
        <AdminPanel
          onBackToDashboard={() => navigate('/dashboard')}
          initialTab={defaultTab}
        />
        <SystemStatus systemStatus={systemStatus} wsStatus={connectionStatus} />
      </main>
    </div>
  );

  return (
    <Routes>
      {/* Public Login Route */}
      <Route
        path="/login"
        element={
          isAuthenticated ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Login onLoginSuccess={() => navigate('/dashboard')} />
          )
        }
      />

      {/* Protected Dashboard Route */}
      <Route
        path="/dashboard"
        element={
          isAuthenticated ? (
            <DashboardView />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />

      {/* Protected Administrative Routes */}
      <Route
        path="/admin"
        element={
          !isAuthenticated ? (
            <Navigate to="/login" replace />
          ) : role === 'administrative' ? (
            <AdminViewWrapper defaultTab="users" />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />

      <Route
        path="/users"
        element={
          !isAuthenticated ? (
            <Navigate to="/login" replace />
          ) : role === 'administrative' ? (
            <AdminViewWrapper defaultTab="users" />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />

      <Route
        path="/settings"
        element={
          !isAuthenticated ? (
            <Navigate to="/login" replace />
          ) : role === 'administrative' ? (
            <AdminViewWrapper defaultTab="config" />
          ) : (
            <Navigate to="/dashboard" replace />
          )
        }
      />

      {/* Root redirect */}
      <Route
        path="/"
        element={<Navigate to="/dashboard" replace />}
      />

      {/* Catch-all route */}
      <Route
        path="*"
        element={<Navigate to="/dashboard" replace />}
      />
    </Routes>
  );
}
