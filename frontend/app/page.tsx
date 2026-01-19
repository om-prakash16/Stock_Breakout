"use client";

import { useEffect, useState } from "react";
import { getBreakouts, getSystemStatus, dismissBreakout, type Breakout, type SystemStatus } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowUpRight, Activity, Clock, Layers, EyeOff } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BreakoutGroup } from "@/components/breakout-group";
import { DismissedListDialog } from "@/components/dismissed-list-dialog";

export default function Dashboard() {
  const [breakouts, setBreakouts] = useState<Breakout[]>([]);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedExchange, setSelectedExchange] = useState<string>("NSE");
  const [searchQuery, setSearchQuery] = useState("");
  const [directionFilter, setDirectionFilter] = useState<'ALL' | 'BULL' | 'BEAR'>('ALL');

  const handleDismiss = async (symbol: string, exchange: string) => {
    try {
      await dismissBreakout(symbol, exchange);
      setBreakouts(prev => prev.filter(b => !(b.symbol === symbol && b.exchange === exchange)));
    } catch (e) {
      console.error("Dismiss failed", e);
    }
  };

  useEffect(() => {
    // Initial Fetch
    async function fetchData() {
      if (!status) setLoading(true);

      try {
        const [boData, sysData] = await Promise.all([
          getBreakouts(selectedExchange),
          getSystemStatus(),
        ]);
        setBreakouts(boData);
        setStatus(sysData);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchData();

    // WebSocket Connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//localhost:8000/ws`; // Assuming backend is on 8000
    let ws: WebSocket | null = null;
    let reconnectTimeout: NodeJS.Timeout;

    function connectWs() {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log("Connected to Real-Time Feed");
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'update') {
            // Re-fetch data on update signal
            fetchData();
          }
        } catch (e) {
          console.error(e);
        }
      };

      ws.onclose = () => {
        console.log("Feed disconnected, retrying...");
        reconnectTimeout = setTimeout(connectWs, 3000);
      };

      ws.onerror = (err) => {
        console.error("WS Error", err);
        ws?.close();
      };
    }

    connectWs();

    // Keep a slow poll just in case WS fails silently (fail-safe)
    const interval = setInterval(fetchData, 60000); // Poll every 60s as backup

    return () => {
      clearInterval(interval);
      clearTimeout(reconnectTimeout);
      ws?.close();
    };
  }, [selectedExchange]);

  // Helper to filter breakouts by type, direction, and search query
  const getBreakoutsByType = (type: string) => {
    let filtered = breakouts.filter(b => b.breakout_type === type);

    // 1. Search Filter (Symbol)
    if (searchQuery) {
      const q = searchQuery.toUpperCase();
      filtered = filtered.filter(b => b.symbol.includes(q));
    }

    // 2. Direction Filter
    if (directionFilter === 'BULL') filtered = filtered.filter(b => b.breakout_pct > 0);
    if (directionFilter === 'BEAR') filtered = filtered.filter(b => b.breakout_pct < 0);

    return filtered;
  };

  // Define Groups Order
  const GROUPS = [
    { id: '1 Day', type: 'TODAY' },
    { id: '2 Days', type: 'D2' },
    { id: '10 Days', type: 'D10' },
    { id: '30 Days', type: 'D30' },
    { id: '100 Days', type: 'D100' },
    { id: '52 Weeks', type: 'W52' },
    { id: 'All Time', type: 'ALL_TIME' },
  ];

  if (loading && !status) { // Only show full loader on initial load
    return (
      <div className="flex h-screen w-full items-center justify-center bg-zinc-950 text-zinc-50">
        <div className="animate-pulse text-lg font-mono">INITIALIZING TERMINAL...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-950 p-6 font-mono text-zinc-50">
      <header className="mb-6 flex items-center justify-between border-b border-zinc-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-green-500">
            QUANT TERMINAL <span className="text-zinc-500">//</span> BREAKOUT ANALYTICS
          </h1>
          <p className="mt-1 text-sm text-zinc-400">
            Real-time market scanning and breakout detection engine.
          </p>
        </div>
        <div className="flex gap-4 text-xs">
          <DismissedListDialog
            trigger={
              <button className="flex items-center gap-2 text-zinc-500 hover:text-zinc-300 transition-colors border border-zinc-800 rounded px-3 py-1 bg-zinc-900/50 hover:bg-zinc-800">
                <EyeOff className="h-3 w-3" />
                <span>HIDDEN</span>
              </button>
            }
          />

          <div className="flex flex-col items-end">
            <span className="text-zinc-500">SYSTEM TIME</span>
            <span className="font-bold tabular-nums">{status?.system_time ? new Date(status.system_time).toLocaleTimeString() : "--:--:--"}</span>
          </div>
          <div className="flex flex-col items-end">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              <span className="text-zinc-500 font-bold">LIVE</span>
            </div>
            <Badge variant="outline" className="border-zinc-700 bg-zinc-900 text-zinc-300 mt-1">
              {status?.market_state || "UNKNOWN"}
            </Badge>
          </div>
        </div>
      </header>

      <div className="mb-6 flex justify-between items-end">
        <Tabs defaultValue="NSE" className="w-[300px]" onValueChange={setSelectedExchange}>
          <TabsList className="grid w-full grid-cols-2 bg-zinc-900">
            <TabsTrigger value="NSE">NSE</TabsTrigger>
            <TabsTrigger value="BSE">BSE</TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="flex gap-4 items-center">
          {/* Search Bar */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search Symbol..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-zinc-900 border border-zinc-800 rounded-md px-3 py-1 text-sm text-zinc-100 placeholder:text-zinc-600 focus:outline-none focus:border-green-500 w-48 transition-colors"
            />
          </div>

          {/* Direction Filter */}
          <div className="flex bg-zinc-900 rounded-md p-1 border border-zinc-800">
            <button
              onClick={() => setDirectionFilter('ALL')}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${directionFilter === 'ALL' ? 'bg-zinc-700 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
              ALL
            </button>
            <button
              onClick={() => setDirectionFilter('BULL')}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${directionFilter === 'BULL' ? 'bg-green-900/50 text-green-400' : 'text-zinc-500 hover:text-green-500'}`}
            >
              LONG
            </button>
            <button
              onClick={() => setDirectionFilter('BEAR')}
              className={`px-3 py-1 text-xs font-medium rounded transition-colors ${directionFilter === 'BEAR' ? 'bg-red-900/50 text-red-500' : 'text-zinc-500 hover:text-red-500'}`}
            >
              SHORT
            </button>
          </div>

          <Badge variant="secondary" className="bg-zinc-900 text-green-400 border-green-500/20 h-8 flex items-center">
            TOTAL: {breakouts.length}
          </Badge>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-4 mb-6">
        <Card className="border-l-4 border-l-green-500 bg-zinc-900/50 p-4">
          <div className="text-xs font-medium text-zinc-400 mb-1">TOTAL SCANNED</div>
          <div className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            <Layers className="h-4 w-4 text-zinc-500" />
            {selectedExchange === "NSE" ? "2200+" : "4800+"}
          </div>
        </Card>

        <Card className="border-l-4 border-l-green-500 bg-zinc-900/50 p-4">
          <div className="text-xs font-medium text-zinc-400 mb-1">BREAKOUTS</div>
          <div className="text-xl font-bold text-green-400 flex items-center gap-2">
            <Activity className="h-4 w-4" />
            {breakouts.length}
          </div>
        </Card>

        <Card className="border-l-4 border-l-zinc-700 bg-zinc-900/50 p-4">
          <div className="text-xs font-medium text-zinc-400 mb-1">SESSION DATE</div>
          <div className="text-xl font-bold text-zinc-100 flex items-center gap-2">
            <Clock className="h-4 w-4 text-zinc-500" />
            {status?.trade_date || "--"}
          </div>
        </Card>
      </div>

      <div>
        <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-green-500 border-b border-zinc-800 pb-2">
          <ArrowUpRight className="h-4 w-4" /> {selectedExchange} SIGNAL FEED
        </h2>

        {/* 2-Column Grid Layout */}
        {loading && !status ? (
          <div className="p-12 text-center text-zinc-500 animate-pulse font-mono">SCANNING GRID...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {GROUPS.map((group) => (
              <BreakoutGroup
                key={group.id}
                title={group.id.toUpperCase()}
                breakouts={getBreakoutsByType(group.type)}
                onDismiss={handleDismiss}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
