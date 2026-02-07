'use client';

import { cn } from '@workspace/ui/lib/utils';
import { Monitor, Smartphone, Square, RectangleVertical } from 'lucide-react';
import { ASPECT_RATIO_CONFIG, ASPECT_RATIO_OPTIONS, type AspectRatio } from '../lib/aspect-ratios';

interface AspectRatioSelectorProps {
  selected: AspectRatio;
  onChange: (ratio: AspectRatio) => void;
  disabled?: boolean;
  className?: string;
}

const RATIO_ICONS: Record<AspectRatio, React.ReactNode> = {
  '9:16': <Smartphone className="w-5 h-5" />,
  '1:1': <Square className="w-5 h-5" />,
  '4:5': <RectangleVertical className="w-5 h-5" />,
  '16:9': <Monitor className="w-5 h-5" />,
};

/**
 * AspectRatioSelector Component
 *
 * Grid of clickable cards for selecting the output aspect ratio.
 * Used in both Video Wizard and Subtitle Generator flows.
 */
export function AspectRatioSelector({
  selected,
  onChange,
  disabled = false,
  className,
}: AspectRatioSelectorProps) {
  return (
    <div className={cn('grid grid-cols-2 md:grid-cols-4 gap-3', className)}>
      {ASPECT_RATIO_OPTIONS.map((ratio) => {
        const config = ASPECT_RATIO_CONFIG[ratio];
        const isSelected = selected === ratio;

        return (
          <button
            key={ratio}
            type="button"
            onClick={() => onChange(ratio)}
            disabled={disabled}
            className={cn(
              'flex flex-col items-center gap-2 rounded-lg border-2 p-4 transition-all',
              'hover:border-primary/50 hover:bg-muted/50',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              isSelected ? 'border-primary bg-primary/5 shadow-sm' : 'border-border bg-card'
            )}
          >
            {/* Ratio visual preview */}
            <div className="flex items-center justify-center w-full h-12">
              <div
                className={cn(
                  'border-2 rounded-sm',
                  isSelected ? 'border-primary' : 'border-muted-foreground/40'
                )}
                style={{
                  aspectRatio: `${config.width} / ${config.height}`,
                  height: ratio === '16:9' ? '28px' : '48px',
                }}
              />
            </div>

            {/* Icon and label */}
            <div className="flex items-center gap-1.5">
              <span className={cn(isSelected ? 'text-primary' : 'text-muted-foreground')}>
                {RATIO_ICONS[ratio]}
              </span>
              <span
                className={cn(
                  'text-sm font-medium',
                  isSelected ? 'text-primary' : 'text-foreground'
                )}
              >
                {config.label}
              </span>
            </div>

            {/* Dimensions */}
            <span className="text-xs text-muted-foreground">
              {config.width} x {config.height}
            </span>

            {/* Use case */}
            <span className="text-[10px] text-muted-foreground/70">{config.description}</span>
          </button>
        );
      })}
    </div>
  );
}
