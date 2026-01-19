"use client";

import { useEffect, useState } from "react";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X, RotateCcw } from "lucide-react";
import { getDismissedList, restoreBreakout } from "@/lib/api";
import { Badge } from "@/components/ui/badge";

const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;
const DialogPortal = DialogPrimitive.Portal;

function DialogOverlay({ className, ...props }: DialogPrimitive.DialogOverlayProps) {
    return (
        <DialogPrimitive.Overlay
            className={`fixed inset-0 z-50 bg-black/80  data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 ${className}`}
            {...props}
        />
    );
}

function DialogContent({ className, children, ...props }: DialogPrimitive.DialogContentProps) {
    return (
        <DialogPortal>
            <DialogOverlay />
            <DialogPrimitive.Content
                className={`fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border border-zinc-800 bg-zinc-950 p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg ${className}`}
                {...props}
            >
                {children}
                <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
                    <X className="h-4 w-4 text-zinc-400" />
                    <span className="sr-only">Close</span>
                </DialogPrimitive.Close>
            </DialogPrimitive.Content>
        </DialogPortal>
    );
}

export function DismissedListDialog({ trigger }: { trigger: React.ReactNode }) {
    const [dismissed, setDismissed] = useState<string[]>([]);
    const [open, setOpen] = useState(false);

    useEffect(() => {
        if (open) {
            getDismissedList().then(setDismissed);
        }
    }, [open]);

    const handleRestore = async (id: string) => {
        const [exchange, symbol] = id.split(":");
        try {
            await restoreBreakout(symbol, exchange);
            setDismissed(prev => prev.filter(item => item !== id));
        } catch (e) {
            console.error("Failed to restore", e);
        }
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                {trigger}
            </DialogTrigger>
            <DialogContent>
                <div className="flex flex-col space-y-1.5 text-center sm:text-left">
                    <h2 className="text-lg font-semibold leading-none tracking-tight text-zinc-100">Hidden Stocks</h2>
                    <p className="text-sm text-zinc-400">
                        Manage your dismissed breakout signals. Restore them to add them back to the feed.
                    </p>
                </div>

                <div className="mt-4 max-h-[300px] overflow-y-auto border border-zinc-800 rounded-md p-2">
                    {dismissed.length === 0 ? (
                        <div className="text-center py-8 text-zinc-500 text-sm">No hidden stocks.</div>
                    ) : (
                        <ul className="space-y-2">
                            {dismissed.map(id => (
                                <li key={id} className="flex items-center justify-between p-2 rounded bg-zinc-900/50 border border-zinc-800/50">
                                    <span className="font-mono text-sm text-zinc-300">{id}</span>
                                    <button
                                        onClick={() => handleRestore(id)}
                                        className="flex items-center gap-1 text-xs text-green-500 hover:text-green-400 hover:underline"
                                    >
                                        <RotateCcw className="h-3 w-3" />
                                        Restore
                                    </button>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
