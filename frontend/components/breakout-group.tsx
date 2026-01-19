"use client";

import { type Breakout, dismissBreakout } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { Trash2, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";
import { useState } from "react";

interface BreakoutGroupProps {
    title: string;
    breakouts: Breakout[];
    onDismiss: (symbol: string, exchange: string) => void;
}

type SortKey = 'breakout_level' | 'close_price' | 'breakout_pct';

export function BreakoutGroup({ title, breakouts, onDismiss }: BreakoutGroupProps) {
    const [sortConfig, setSortConfig] = useState<{ key: SortKey; direction: 'asc' | 'desc' } | null>(null);

    const handleSort = (key: SortKey) => {
        let direction: 'asc' | 'desc' = 'desc';
        if (sortConfig && sortConfig.key === key && sortConfig.direction === 'desc') {
            direction = 'asc';
        }
        setSortConfig({ key, direction });
    };

    const sortedBreakouts = [...breakouts].sort((a, b) => {
        if (!sortConfig) return 0;
        const { key, direction } = sortConfig;

        if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
        if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
        return 0;
    });

    const SortIcon = ({ column }: { column: SortKey }) => {
        if (sortConfig?.key !== column) return <ArrowUpDown className="ml-1 h-3 w-3 text-zinc-600 inline" />;
        return sortConfig.direction === 'asc'
            ? <ArrowUp className="ml-1 h-3 w-3 text-green-500 inline" />
            : <ArrowDown className="ml-1 h-3 w-3 text-green-500 inline" />;
    };

    return (
        <div className="rounded-xl border border-zinc-800 bg-zinc-900/30 overflow-hidden flex flex-col h-full">
            <div className="border-b border-zinc-800 bg-zinc-900/80 p-3 text-sm font-bold text-green-500 flex justify-between items-center">
                <span>{title}</span>
                <Badge variant="outline" className="text-xs border-zinc-700 text-zinc-400">
                    {breakouts.length}
                </Badge>
            </div>

            <div className="overflow-y-auto max-h-[400px]">
                {sortedBreakouts.length === 0 ? (
                    <div className="p-8 text-center text-xs text-zinc-500">No signals.</div>
                ) : (
                    <table className="w-full text-xs">
                        <thead className="bg-zinc-900/50 text-zinc-500 sticky top-0 backdrop-blur-sm">
                            <tr>
                                <th className="p-2 text-left font-medium">SYMBOL</th>
                                <th
                                    className="p-2 text-right font-medium cursor-pointer hover:text-zinc-300"
                                    onClick={() => handleSort('breakout_level')}
                                >
                                    LEVEL <SortIcon column="breakout_level" />
                                </th>
                                <th
                                    className="p-2 text-right font-medium cursor-pointer hover:text-zinc-300"
                                    onClick={() => handleSort('close_price')}
                                >
                                    PRICE <SortIcon column="close_price" />
                                </th>
                                <th
                                    className="p-2 text-right font-medium cursor-pointer hover:text-zinc-300"
                                    onClick={() => handleSort('breakout_pct')}
                                >
                                    PCT <SortIcon column="breakout_pct" />
                                </th>
                                <th className="p-2 text-center font-medium">CONF</th>
                                <th className="p-2 text-center font-medium">TIME</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sortedBreakouts.map((bo, i) => (
                                <tr key={`${bo.symbol}-${i}`} className="border-b border-zinc-800/30 hover:bg-zinc-800/50 transition-colors group">
                                    <td className="p-2 font-bold text-zinc-100 flex items-center gap-2">
                                        {bo.symbol}
                                        <button
                                            onClick={() => onDismiss(bo.symbol, bo.exchange)}
                                            className="opacity-0 group-hover:opacity-100 text-zinc-600 hover:text-red-500 transition-all"
                                            title="Dismiss"
                                        >
                                            <Trash2 className="h-3 w-3" />
                                        </button>
                                    </td>
                                    <td className="p-2 text-right font-mono text-zinc-500">{bo.breakout_level.toFixed(2)}</td>
                                    <td className="p-2 text-right font-mono text-zinc-300">{bo.close_price.toFixed(2)}</td>
                                    <td className={`p-2 text-right font-mono font-bold ${bo.breakout_pct >= 0 ? 'text-green-400' : 'text-red-500'}`}>
                                        {bo.breakout_pct > 0 ? "+" : ""}{bo.breakout_pct.toFixed(2)}%
                                    </td>
                                    <td className="p-2 text-center">
                                        {bo.volume_confirmation && (
                                            <div className="h-2 w-2 rounded-full bg-green-500 mx-auto" title="Confirmed Volume" />
                                        )}
                                    </td>
                                    <td className="p-2 text-center text-zinc-500 font-mono text-[10px]">
                                        {bo.detected_at ? new Date(bo.detected_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
