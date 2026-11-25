#import <ScreenSaver/ScreenSaver.h>
#import <math.h>
#import <stdlib.h>
#import "Digits.h"
#import "Choreography.h"
#import "StyleSelection.h"

#ifndef CC_VIEW_CLASS
#define CC_VIEW_CLASS ClockClock24View
#endif
#ifndef CC_DARK_MODE
#define CC_DARK_MODE 0
#endif

static CGFloat ccFaceRadius(NSRect bounds) {
    return fmin(NSWidth(bounds) / 20.0, NSHeight(bounds) / 9.0);
}

static NSPoint ccFaceCenter(NSRect bounds, CGFloat radius, int face) {
    CGFloat spacing = radius * 2.15;
    return NSMakePoint(NSMidX(bounds) + (face / 3 - 3.5) * spacing,
                       NSMidY(bounds) + (face % 3 - 1) * spacing);
}

static NSRect ccCenteredRect(NSPoint center, CGFloat extent) {
    return NSMakeRect(center.x - extent, center.y - extent, 2 * extent, 2 * extent);
}

@interface CC_VIEW_CLASS : ScreenSaverView {
    CCStyleSelection _styleSelection;
    double _angles[24][2];
    BOOL _hasSample;
    CFAbsoluteTime _lastSampleTime;
    CFAbsoluteTime _nextSampleTime;
}
@end

@implementation CC_VIEW_CLASS
- (instancetype)initWithFrame:(NSRect)frame isPreview:(BOOL)preview {
    self = [super initWithFrame:frame isPreview:preview];
    if (self) self.animationTimeInterval = 1.0 / 50.0;
    return self;
}
- (BOOL)isFlipped { return YES; }
- (BOOL)isOpaque { return YES; }

- (void)setFrameSize:(NSSize)newSize {
    NSSize previousBoundsSize = self.bounds.size;
    [super setFrameSize:newSize];
    if (!NSEqualSizes(previousBoundsSize, self.bounds.size)) [self setNeedsDisplay:YES];
}

- (void)sampleAtTime:(CFAbsoluteTime)time {
    NSDate *now = [NSDate dateWithTimeIntervalSinceReferenceDate:time];
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
    // During a hold, refresh once a second to catch wall-clock and time-zone changes.
    _lastSampleTime = time;
    _nextSampleTime = elapsed < 60 - CC_TRANSITION_SECONDS
        ? floor(time) + 1 : time;

    NSRect bounds = self.bounds;
    CGFloat radius = ccFaceRadius(bounds);
    CGFloat handExtent = hypot(radius * 0.93555, fmax(1, radius * 0.1) / 2) + 1;
    for (int face = 0; face < 24; face++) {
        BOOL changed = NO;
        for (int hand = 0; hand < 2; hand++) {
            double angle = ccAngle(style, face, hand, digits[from[face / 6]][face % 6][hand],
                                   digits[to[face / 6]][face % 6][hand], progress);
            changed |= _angles[face][hand] != angle;
            _angles[face][hand] = angle;
        }
        if (_hasSample && changed) {
            [self setNeedsDisplayInRect:ccCenteredRect(ccFaceCenter(bounds, radius, face), handExtent)];
        }
    }
    if (!_hasSample) [self setNeedsDisplay:YES];
    _hasSample = YES;
}

- (void)startAnimation {
    [super startAnimation];
    @autoreleasepool {
        [self sampleAtTime:CFAbsoluteTimeGetCurrent()];
    }
}

- (void)animateOneFrame {
    if (!self.isAnimating || self.window == nil || self.isHiddenOrHasHiddenAncestor) return;
    CFAbsoluteTime time = CFAbsoluteTimeGetCurrent();
    if (time >= _lastSampleTime && time < _nextSampleTime) return;
    @autoreleasepool {
        [self sampleAtTime:time];
    }
}

- (void)drawRect:(NSRect)dirtyRect {
    @autoreleasepool {
        if (!_hasSample) [self sampleAtTime:CFAbsoluteTimeGetCurrent()];
        [self drawClockInRect:dirtyRect];
    }
}

- (void)drawClockInRect:(NSRect)dirtyRect {
#if CC_DARK_MODE
    NSColor *backgroundColor = [NSColor colorWithSRGBRed:12.0/255 green:12.0/255 blue:12.0/255 alpha:1];
    NSColor *grey = [NSColor colorWithSRGBRed:5.0/255 green:5.0/255 blue:5.0/255 alpha:1];
    NSColor *panelColor = [NSColor colorWithSRGBRed:28.0/255 green:28.0/255 blue:28.0/255 alpha:1];
    NSColor *faceColor = [NSColor colorWithSRGBRed:40.0/255 green:40.0/255 blue:40.0/255 alpha:1];
    NSColor *handColor = [NSColor colorWithSRGBRed:230.0/255 green:230.0/255 blue:230.0/255 alpha:1];
#else
    NSColor *backgroundColor = [NSColor whiteColor];
    NSColor *grey = [NSColor colorWithSRGBRed:211.0/255 green:211.0/255 blue:211.0/255 alpha:1];
    NSColor *panelColor = [NSColor colorWithSRGBRed:250.0/255 green:250.0/255 blue:250.0/255 alpha:1];
    NSColor *faceColor = [NSColor colorWithSRGBRed:240.0/255 green:240.0/255 blue:240.0/255 alpha:1];
    NSColor *handColor = [NSColor colorWithSRGBRed:40.0/255 green:40.0/255 blue:40.0/255 alpha:1];
#endif
    [backgroundColor setFill];
    NSRectFill(dirtyRect);
    NSRect bounds = self.bounds;
    CGFloat radius = ccFaceRadius(bounds);
    CGFloat spacing = radius * 2.15;
    CGFloat width = 2 * radius + 7 * spacing;
    CGFloat height = 2 * radius + 2 * spacing;
    CGFloat x0 = NSMidX(bounds) - width / 2 + radius;
    CGFloat y0 = NSMidY(bounds) - height / 2 + radius;
    NSRect panel = NSMakeRect(x0 - 1.5 * radius, y0 - 1.5 * radius, width + radius, height + radius);
    // Match the original main.py panel, including its box-shadow corner triangles.
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
    CGFloat handWidth = fmax(1, radius * 0.1);
    NSBezierPath *handPath = [NSBezierPath bezierPath];
    handPath.lineWidth = handWidth;
    handPath.lineCapStyle = NSLineCapStyleButt;
    for (int face = 0; face < 24; face++) {
        NSPoint center = ccFaceCenter(bounds, radius, face);
        CGFloat x = center.x;
        CGFloat y = center.y;
        NSRect circle = ccCenteredRect(center, radius);
        CGFloat offset = radius * 0.06;
        CGFloat faceExtent = radius + offset + fmax(1, radius / 30) / 2 + 1;
        if (!NSIntersectsRect(dirtyRect, ccCenteredRect(center, faceExtent))) continue;
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
        [handColor setStroke];
        for (int hand = 0; hand < 2; hand++) {
            double angle = _angles[face][hand] * M_PI / 180;
            [handPath removeAllPoints];
            [handPath moveToPoint:center];
            [handPath lineToPoint:NSMakePoint(x + sin(angle) * radius * 0.93555, y + cos(angle) * radius * 0.93555)];
            [handPath stroke];
        }
        [handColor setFill];
        [[NSBezierPath bezierPathWithOvalInRect:NSMakeRect(x - handWidth / 2, y - handWidth / 2, handWidth, handWidth)] fill];
    }
}
@end
