const API_BASE_URL = "http://localhost:8000/api/v1";

export interface Breakout {
    symbol: string;
    exchange: string;
    breakout_type: string;
    close_price: number;
    breakout_level: number;
    breakout_pct: number;
    volume: number;
    volume_confirmation: boolean;
    detected_at?: string;
}

export async function dismissBreakout(symbol: string, exchange: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/dismiss`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, exchange }),
    });
    if (!res.ok) {
        throw new Error('Failed to dismiss breakout');
    }
}

export async function restoreBreakout(symbol: string, exchange: string): Promise<void> {
    const res = await fetch(`${API_BASE_URL}/restore`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol, exchange }),
    });
    if (!res.ok) {
        throw new Error('Failed to restore breakout');
    }
}

export async function getDismissedList(): Promise<string[]> {
    const res = await fetch(`${API_BASE_URL}/dismissed`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
}

export interface SystemStatus {
    system_time: string;
    market_state: string;
    trade_date: string;
    is_market_open: boolean;
}

export async function getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE_URL}/system/status`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch system status");
    return res.json();
}

export async function getBreakouts(exchange?: string): Promise<Breakout[]> {
    const params = new URLSearchParams();
    if (exchange) params.append("exchange", exchange);

    const res = await fetch(`${API_BASE_URL}/breakouts?${params.toString()}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch breakouts");
    return res.json();
}
