import React from 'react';
import { cn } from '@/lib/utils';

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'rounded-xl border border-border bg-card text-card-foreground shadow-soft hover:shadow-soft-lg transition-shadow duration-200',
      className
    )}
    {...props}
  />
));
Card.displayName = 'Card';

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-2 p-6 pb-4', className)}
    {...props}
  />
));
CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-xl font-serif font-semibold leading-tight tracking-tight text-primary-dark',
      className
    )}
    {...props}
  >
    {children}
  </h3>
));
CardTitle.displayName = 'CardTitle';

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-foreground/70 leading-relaxed', className)}
    {...props}
  />
));
CardDescription.displayName = 'CardDescription';

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
));
CardContent.displayName = 'CardContent';

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0 border-t border-border/50 bg-muted/30 rounded-b-xl', className)}
    {...props}
  />
));
CardFooter.displayName = 'CardFooter';

// Additional Card variants for specific use cases
const CardStats = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    value: string | number;
    label: string;
    icon?: React.ReactNode;
    trend?: 'up' | 'down' | 'neutral';
    trendValue?: string;
  }
>(({ className, value, label, icon, trend, trendValue, ...props }, ref) => (
  <Card
    ref={ref}
    className={cn('p-6 bg-gradient-to-br from-card to-muted/20', className)}
    {...props}
  >
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-foreground/60">{label}</p>
        <p className="text-3xl font-serif font-bold text-primary-dark">{value}</p>
        {trendValue && (
          <p className={cn(
            'text-xs font-medium mt-1',
            trend === 'up' && 'text-success',
            trend === 'down' && 'text-destructive',
            trend === 'neutral' && 'text-foreground/60'
          )}>
            {trendValue}
          </p>
        )}
      </div>
      {icon && (
        <div className="p-3 bg-primary/10 rounded-lg">
          {icon}
        </div>
      )}
    </div>
  </Card>
));
CardStats.displayName = 'CardStats';

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent, CardStats }; 