#import <ScreenSaver/ScreenSaver.h>
#import <math.h>
#import <stdlib.h>
#import "Digits.h"
#import "Choreography.h"
#import "StyleSelection.h"

@interface ClockClock24View : ScreenSaverView {
    CCStyleSelection _styleSelection;
}
@end

@implementation ClockClock24View
- (instancetype)initWithFrame:(NSRect)frame isPreview:(BOOL)preview {
    self = [super initWithFrame:frame isPreview:preview];
    if (self) self.animationTimeInterval = 1.0 / 50.0;
    return self;
}
- (BOOL)isFlipped { return YES; }
- (void)animateOneFrame { [self setNeedsDisplay:YES]; }
- (void)drawRect:(NSRect)dirtyRect {
    (void)dirtyRect;
    [[NSColor whiteColor] setFill];
    NSRectFill(self.bounds);
    NSDate *now = [NSDate date];
    NSCalendar *calendar = [NSCalendar currentCalendar];
    NSDateComponents *current = [calendar components:NSCalendarUnitHour | NSCalendarUnitMinute | NSCalendarUnitSecond | NSCalendarUnitNanosecond fromDate:now];
    NSDateComponents *next = [calendar components:NSCalendarUnitHour | NSCalendarUnitMinute fromDate:[now dateByAddingTimeInterval:60]];
    NSInteger from[4] = {current.hour / 10, current.hour % 10, current.minute / 10, current.minute % 10};
    NSInteger to[4] = {next.hour / 10, next.hour % 10, next.minute / 10, next.minute % 10};
    // Keep a random choreography for the whole minute, including after wake.
    long long minute = (long long)floor(now.timeIntervalSince1970 / 60.0);
    int style = ccStyleForMinute(&_styleSelection, minute, arc4random_uniform);
    double elapsed = current.second + current.nanosecond / 1e9;
    double progress = ccClamp((elapsed - (60 - CC_TRANSITION_SECONDS)) / CC_TRANSITION_SECONDS);
    CGFloat radius = fmin(NSWidth(self.bounds) / 20.0, NSHeight(self.bounds) / 9.0);
    CGFloat spacing = radius * 2.15;
    CGFloat width = 2 * radius + 7 * spacing;
    CGFloat height = 2 * radius + 2 * spacing;
    CGFloat x0 = NSMidX(self.bounds) - width / 2 + radius;
    CGFloat y0 = NSMidY(self.bounds) - height / 2 + radius;
    NSRect panel = NSMakeRect(x0 - 1.5 * radius, y0 - 1.5 * radius, width + radius, height + radius);
    // Match the original main.py panel, including its box-shadow corner triangles.
    NSColor *grey = [NSColor colorWithSRGBRed:211.0/255 green:211.0/255 blue:211.0/255 alpha:1];
    NSColor *panelColor = [NSColor colorWithSRGBRed:250.0/255 green:250.0/255 blue:250.0/255 alpha:1];
    NSColor *faceColor = [NSColor colorWithSRGBRed:240.0/255 green:240.0/255 blue:240.0/255 alpha:1];
    NSColor *handColor = [NSColor colorWithSRGBRed:40.0/255 green:40.0/255 blue:40.0/255 alpha:1];
    [grey setFill];
    [grey setStroke];
    CGFloat boxOffset = radius * 0.5;
    NSBezierPath *shadow = [NSBezierPath bezierPathWithRect:NSOffsetRect(panel, -boxOffset, boxOffset)];
    shadow.lineWidth = 1;
    [shadow fill];
    [shadow stroke];
    // The view is flipped, so minY is the top and maxY is the bottom.
    NSBezierPath *topLeft = [NSBezierPath bezierPath];
    [topLeft moveToPoint:NSMakePoint(NSMinX(panel) - boxOffset, NSMinY(panel) + boxOffset)];
    [topLeft lineToPoint:NSMakePoint(NSMinX(panel), NSMinY(panel))];
    [topLeft lineToPoint:NSMakePoint(NSMinX(panel), NSMinY(panel) + boxOffset)];
    [topLeft closePath];
    topLeft.lineWidth = 1;
    [topLeft fill];
    [topLeft stroke];
    NSBezierPath *bottomRight = [NSBezierPath bezierPath];
    [bottomRight moveToPoint:NSMakePoint(NSMaxX(panel) - boxOffset, NSMaxY(panel) + boxOffset)];
    [bottomRight lineToPoint:NSMakePoint(NSMaxX(panel), NSMaxY(panel))];
    [bottomRight lineToPoint:NSMakePoint(NSMaxX(panel) - boxOffset, NSMaxY(panel))];
    [bottomRight closePath];
    bottomRight.lineWidth = 1;
    [bottomRight fill];
    [bottomRight stroke];
    NSBezierPath *panelPath = [NSBezierPath bezierPathWithRect:panel];
    [panelColor setFill];
    [panelPath fill];
    panelPath.lineWidth = 1;
    [panelPath stroke];
    for (int face = 0; face < 24; face++) {
        CGFloat x = x0 + (face / 3) * spacing;
        CGFloat y = y0 + (face % 3) * spacing;
        NSRect circle = NSMakeRect(x - radius, y - radius, radius * 2, radius * 2);
        CGFloat offset = radius * 0.06;
        NSBezierPath *faceShadow = [NSBezierPath bezierPathWithOvalInRect:NSOffsetRect(circle, -offset, offset)];
        [grey setFill];
        [grey setStroke];
        faceShadow.lineWidth = 1;
        [faceShadow fill];
        [faceShadow stroke];
        NSBezierPath *facePath = [NSBezierPath bezierPathWithOvalInRect:circle];
        [faceColor setFill];
        [facePath fill];
        facePath.lineWidth = fmax(1, radius / 30);
        [facePath stroke];
        CGFloat handWidth = fmax(1, radius * 0.1);
        [handColor setStroke];
        for (int hand = 0; hand < 2; hand++) {
            double angle = ccAngle(style, face, hand, digits[from[face / 6]][face % 6][hand],
                                   digits[to[face / 6]][face % 6][hand], progress) * M_PI / 180;
            NSBezierPath *path = [NSBezierPath bezierPath];
            path.lineWidth = handWidth;
            path.lineCapStyle = NSLineCapStyleButt;
            [path moveToPoint:NSMakePoint(x, y)];
            [path lineToPoint:NSMakePoint(x + sin(angle) * radius * 0.93555, y + cos(angle) * radius * 0.93555)];
            [path stroke];
        }
        [handColor setFill];
        [[NSBezierPath bezierPathWithOvalInRect:NSMakeRect(x - handWidth / 2, y - handWidth / 2, handWidth, handWidth)] fill];
    }
}
@end
